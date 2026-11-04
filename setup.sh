#!/usr/bin/env bash
# ============================================================
#  MedConnect - mise en place du developpement (WSL / macOS / Linux)
#
#  Usage :
#    bash setup.sh              -> installe tout (idempotent)
#    bash setup.sh --reset      -> reinitialise la base demo
#    bash setup.sh --start      -> installe puis demarre backend + frontend
# ============================================================
set -euo pipefail
cd "$(dirname "$0")"

ROOT="$PWD"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV="$BACKEND/.venv"
REQ="$BACKEND/requirements.txt"
REQ_HASH="$VENV/.requirements.sha1"
DB="$BACKEND/db.sqlite3"

step() { printf '\n==> %s\n' "$1"; }
ok()   { printf '    [OK] %s\n' "$1"; }
fail() { printf '\n    [ECHEC] %s\n' "$1" >&2; exit 1; }

START=0; RESET=0; SEED=0
for arg in "$@"; do
  case "$arg" in
    --start)  START=1 ;;
    --reset)  RESET=1 ;;
    --seed)   SEED=1 ;;
    *) fail "Option inconnue : $arg (attendu : --start --reset --seed)" ;;
  esac
done

# ---------------------------------------------------------- 1. prerequis
step "Prerequis"
command -v python3 >/dev/null 2>&1 || fail "python3 introuvable (apt install python3 python3-venv)."
ok "python3 $(python3 --version 2>&1)"
command -v node >/dev/null 2>&1 || fail "Node.js 18+ introuvable -> https://nodejs.org/"
command -v npm  >/dev/null 2>&1 || fail "npm introuvable."
ok "node $(node --version) / npm $(npm --version)"

# --------------------------------------------------------------- 2. venv
if [ ! -x "$VENV/bin/python" ]; then
  step "Creation de l'environnement virtuel (backend/.venv)"
  python3 -m venv "$VENV"
  ok "venv cree"
else
  ok "venv existant (reutilise)"
fi

# ------------------------------------------------------- 3. dependances py
step "Dependances Python"
hash_now="$(sha256sum "$REQ" | cut -d' ' -f1)"
hash_old=""
[ -f "$REQ_HASH" ] && hash_old="$(cat "$REQ_HASH")"
if [ "$hash_now" = "$hash_old" ] && [ -d "$VENV/lib" ] && \
   [ -n "$(find "$VENV/lib" -maxdepth 3 -type d -name django 2>/dev/null | head -1)" ]; then
  ok "requirements.txt inchange -> pip ignore"
else
  "$VENV/bin/python" -m pip install --quiet --disable-pip-version-check -r "$REQ"
  printf '%s' "$hash_now" > "$REQ_HASH"
  ok "dependances installees"
fi

# ------------------------------------------------------------- 4. base + seed
FRESH=0
[ -f "$DB" ] || FRESH=1
if [ "$RESET" = "1" ] && [ "$FRESH" = "0" ]; then
  step "Reinitialisation de la base (--reset)"
  rm -f "$DB"
  FRESH=1
  ok "db.sqlite3 supprimee"
fi

step "Migrations + verification Django"
cd "$BACKEND"
"$VENV/bin/python" manage.py migrate --noinput
"$VENV/bin/python" manage.py check --fail-level ERROR
ok "base a jour, sante du projet : OK"

if [ "$FRESH" = "1" ] || [ "$SEED" = "1" ]; then
  step "Donnees de demonstration (fictives)"
  "$VENV/bin/python" scripts/seed_demo.py
  ok "comptes de demo prets"
else
  ok "base existante conservee (--reset pour tout reinitialiser)"
fi
cd "$ROOT"

# ---------------------------------------------------------- 5. frontend
if [ ! -d "$FRONTEND/node_modules/next" ]; then
  step "Dependances Node (frontend)"
  (cd "$FRONTEND" && npm install --no-fund --no-audit)
  ok "frontend installe"
else
  ok "node_modules a jour"
fi

# --------------------------------------------------------------- 6. bilan
cat <<'EOF'

============================================================
  MedConnect est pret a developper.
============================================================
  Backend   cd backend && .venv/bin/python manage.py runserver
            -> http://localhost:8000   (API + /admin/)
  Frontend  cd frontend && npm run dev
            -> http://localhost:3000
  Tests     cd backend && .venv/bin/python manage.py test tests
  Demo      admin / medecin / secretaire / patient1 / patient2
            mot de passe : MedConnect2026!
  Reinit    bash setup.sh --reset
EOF

# ------------------------------------------------------------- 7. --start
if [ "$START" = "1" ]; then
  step "Demarrage du backend (port 8000)"
  (cd "$BACKEND" && "$VENV/bin/python" manage.py runserver 127.0.0.1:8000 >/tmp/medconnect-backend.log 2>&1 &)
  step "Demarrage du frontend (port 3000)"
  (cd "$FRONTEND" && npm run dev >/tmp/medconnect-frontend.log 2>&1 &)

  up=0
  for _ in $(seq 1 20); do
    sleep 1
    if curl -fsS -m 2 http://127.0.0.1:8000/api/health/ >/dev/null 2>&1; then
      up=1; break
    fi
  done
  if [ "$up" = "1" ]; then ok "API repond sur http://localhost:8000/api/health/"
  else echo "    [!] API pas encore prete (logs : /tmp/medconnect-backend.log)"; fi
  echo "  Arret : pkill -f 'manage.py runserver' ; pkill -f 'next dev'"
  echo ""
fi
