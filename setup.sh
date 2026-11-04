#!/usr/bin/env bash
# ==============================================================
#  MedConnect - moteur d'installation / demarrage de l'equipe
#
#  Interface recommandee (voir Makefile) :
#      make setup | make start | make stop | make test | make reset
#  Equivalent direct :
#      bash setup.sh [--start] [--stop] [--test] [--reset] [--seed]
#
#  Fonctionne sous : Windows (Git bash), WSL, macOS, Linux.
#  Idempotent : relancer n'importe quand est sur et rapide.
# ==============================================================
set -euo pipefail
cd "$(dirname "$0")"

ROOT="$PWD"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV="$BACKEND/.venv"
REQ="$BACKEND/requirements.txt"
REQ_HASH="$VENV/.requirements.hash"
DB="$BACKEND/db.sqlite3"
LOG_B="$ROOT/.backend.log"
LOG_F="$ROOT/.frontend.log"

step() { printf '\n==> %s\n' "$1"; }
ok()   { printf '    [OK] %s\n' "$1"; }
fail() { printf '\n    [ECHEC] %s\n' "$1" >&2; exit 1; }

START=0 STOP=0 TEST=0 RESET=0 SEED=0
for arg in "$@"; do
  case "$arg" in
    --start)  START=1 ;;
    --stop)   STOP=1 ;;
    --test)   TEST=1 ;;
    --reset)  RESET=1 ;;
    --seed)   SEED=1 ;;
    -h|--help) sed -n '3,15p' "$0"; exit 0 ;;
    *) fail "Option inconnue : $arg (attendu : --start --stop --test --reset --seed)" ;;
  esac
done

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) IS_WINDOWS=1 ;;
  *) IS_WINDOWS=0 ;;
esac

# ------------------------------------------------------- STOP (prioritaire)
if [ "$STOP" = 1 ]; then
  step "Arret des serveurs (ports 8000 / 3000)"
  if [ "$IS_WINDOWS" = 1 ]; then
    # On ne tue QUE les processus qui ecoutent sur nos deux ports.
    powershell.exe -NoProfile -Command '8000,3000 | ForEach-Object { Get-NetTCPConnection -LocalPort $_ -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue } }' >/dev/null 2>&1 || true
  else
    pkill -f "runserver 127.0.0.1:8000" 2>/dev/null || true
    pkill -f "node_modules/next" 2>/dev/null || true
  fi
  ok "serveurs arretes"
  exit 0
fi

# ----------------------------------------------------------- 1. prerequis
step "Prerequis"
# On ecarte le raccourci Microsoft Store : il repond mais n'est pas Python.
PYBIN=""
for cand in python3 python py; do
  if command -v "$cand" >/dev/null 2>&1 && "$cand" -c "import sys" >/dev/null 2>&1; then
    PYBIN="$cand"
    break
  fi
done
if [ -z "$PYBIN" ]; then
  fail "Python introuvable -> https://www.python.org/downloads/ (cocher 'Add python.exe to PATH', pas le raccourci Microsoft Store)"
fi
command -v node >/dev/null 2>&1 || fail "Node.js introuvable -> https://nodejs.org/"
command -v npm  >/dev/null 2>&1 || fail "npm introuvable (reinstaller Node.js)."
PYVER="$($PYBIN --version 2>&1)"
ok "$PYVER / node $(node --version) / npm $(npm --version)"

# executable du venv : bin/ sous Unix, Scripts/ sous Windows
VPY="$VENV/bin/python"
[ "$IS_WINDOWS" = 1 ] && VPY="$VENV/Scripts/python.exe"

# --------------------------------------------------------------- 2. venv
step "Environnement virtuel"
if [ -f "$VPY" ]; then
  ok "venv existant (reutilise)"
else
  "$PYBIN" -m venv "$VENV"
  [ -f "$VPY" ] || fail "venv cree mais $VPY introuvable."
  ok "venv cree dans backend/.venv"
fi

# -------------------------------------------------------- 3. dependances py
step "Dependances Python"
now="$(sha256sum "$REQ" | cut -d' ' -f1)"
old="$(cat "$REQ_HASH" 2>/dev/null || true)"
if [ "$now" = "$old" ] && "$VPY" -c "import django, rest_framework, channels" 2>/dev/null; then
  ok "requirements.txt inchange -> pip ignore"
else
  "$VPY" -m pip install --quiet --disable-pip-version-check -r "$REQ"
  printf '%s' "$now" > "$REQ_HASH"
  ok "dependances installees"
fi

# --------------------------------------------------- 4. base de donnees/seed
FRESH=0
if [ ! -f "$DB" ]; then FRESH=1; fi
if [ "$RESET" = 1 ] && [ "$FRESH" = 0 ]; then
  step "Reinitialisation de la base (--reset)"
  rm -f "$DB"
  FRESH=1
  ok "db.sqlite3 supprimee"
fi

step "Migrations + verification Django"
cd "$BACKEND"
"$VPY" manage.py migrate --noinput
"$VPY" manage.py check --fail-level ERROR
ok "base a jour, sante du projet : OK"
if [ "$FRESH" = 1 ] || [ "$SEED" = 1 ]; then
  step "Donnees de demonstration (fictives)"
  "$VPY" scripts/seed_demo.py
  ok "comptes de demo prets"
else
  ok "base existante conservee (--reset pour reinitialiser)"
fi
cd "$ROOT"

# ------------------------------------------------------------- 5. tests
if [ "$TEST" = 1 ]; then
  step "Tests Django"
  cd "$BACKEND"
  "$VPY" manage.py test tests -v 1
  cd "$ROOT"
  exit 0
fi

# ------------------------------------------------------------ 6. frontend
if [ -d "$FRONTEND/node_modules/next" ]; then
  ok "node_modules a jour"
else
  step "Dependances Node (frontend)"
  cd "$FRONTEND"
  npm install --no-fund --no-audit
  cd "$ROOT"
  ok "frontend installe"
fi

if [ "$START" = 0 ] && [ "$SEED" = 0 ] && [ "$RESET" = 0 ]; then
  printf '\n[OK] MedConnect est installe -> "make start" pour lancer le projet\n\n'
  exit 0
fi

# ------------------------------------------------------------- 7. start
if [ "$START" = 1 ]; then
  step "Demarrage du backend (http://localhost:8000)"
  (cd "$BACKEND" && "$VPY" manage.py runserver 127.0.0.1:8000 >"$LOG_B" 2>&1 &)

  step "Demarrage du frontend (http://localhost:3000)"
  (cd "$FRONTEND" && npm run dev >"$LOG_F" 2>&1 &)

  step "Attente de l'API"
  i=0
  until curl -fsS -m 2 http://127.0.0.1:8000/api/health/ >/dev/null 2>&1; do
    i=$((i + 1))
    if [ "$i" -ge 30 ]; then
      echo "    [ECHEC] API absente -> voir .backend.log (port 8000 pris ?)"
      exit 1
    fi
    sleep 1
  done
  ok "API prete"

  if [ "${OPEN:-1}" != "0" ]; then
    case "$(uname -s)" in
      MINGW*|MSYS*|CYGWIN*) explorer.exe "http://localhost:3000" >/dev/null 2>&1 || true ;;
      Darwin) open "http://localhost:3000" || true ;;
      *) xdg-open "http://localhost:3000" >/dev/null 2>&1 || true ;;
    esac
  fi
  printf '  Logs : .backend.log / .frontend.log   Arret : "make stop"\n\n'
  exit 0
fi
