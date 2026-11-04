#!/usr/bin/env python3
# =============================================================================
#  MedConnect — moteur d'installation / demarrage de l'equipe
#  Multiplateforme : Windows (cmd / PowerShell), macOS, Linux, WSL.
#
#  Utilisation (terminal, pas de PowerShell necessaire) :
#      python setup.py              # installe tout (idempotent)
#      python setup.py --start      # installe + demarre backend (:8000) + frontend (:3000)
#      python setup.py --stop       # arrete les serveurs (ports 8000/3000 uniquement)
#      python setup.py --test       # lance les tests Django
#      python setup.py --reset      # reinitialise la base de demonstration
#      python setup.py --seed       # re-importe les donnees de demo
#      python setup.py --health     # verifie que les serveurs repondent
#      python setup.py --logs       # affiche la fin des logs
#
#  Avec make (recommande) :
#      make setup && make start
# =============================================================================
from __future__ import annotations

import hashlib
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = BACKEND / ".venv"
REQ = BACKEND / "requirements.txt"
REQ_HASH = VENV / ".requirements.hash"
DB = BACKEND / "db.sqlite3"
LOG_B = ROOT / ".backend.log"
LOG_F = ROOT / ".frontend.log"

PY = None  # interpreteur Python detecte
VPY = None  # interpreteur du venv

# --------------------------------------------------------------------------- helpers


def step(msg: str) -> None:
    print(f"\n==> {msg}")


def ok(msg: str) -> None:
    print(f"    [OK] {msg}")


def fail(msg: str) -> None:
    print(f"\n[ECHEC] {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=check)


def find_python() -> str:
    import shutil

    for name in ("python", "python3", "py"):
        path = shutil.which(name)
        if path and _is_real_python(path):
            return path
    fail("Python introuvable -> https://www.python.org/downloads/ (cocher 'Add python.exe a PATH')")


def _is_real_python(path: str) -> bool:
    """Ecarte le raccourci Microsoft Store qui repond sans etre Python."""
    try:
        out = subprocess.run(
            [path, "-c", "import sys; print(sys.version.split()[0])"],
            capture_output=True, text=True, timeout=10,
        )
        return out.returncode == 0 and out.stdout.strip() and "Store" not in out.stdout + out.stderr
    except Exception:
        return False


def venv_python() -> str:
    return str(VENV / "Scripts" / "python.exe") if sys.platform == "win32" else str(VENV / "bin" / "python")


def pids_on_port(port: int) -> list[str]:
    """Retourne les PID ecoutant sur le port donne (sans tuer autre chose)."""
    if sys.platform == "win32":
        res = subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
        pids = []
        for line in res.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line.upper():
                parts = line.split()
                if parts:
                    pids.append(parts[-1])
        return pids
    # macOS / Linux : lsof
    res = subprocess.run(["lsof", "-ti", f":{port}"], capture_output=True, text=True)
    return [p for p in res.stdout.split() if p]


def kill_pids(pids: list[str]) -> None:
    for pid in set(pids):
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/PID", pid, "/F"], capture_output=True)
            else:
                os.kill(int(pid), signal.SIGTERM)
        except Exception:
            pass


def wait_for_health(timeout: int = 30) -> bool:
    url = "http://127.0.0.1:8000/api/health/"
    for _ in range(timeout):
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


def open_browser(url: str = "http://localhost:3000") -> None:
    try:
        if sys.platform == "win32":
            os.startfile(url)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", url], capture_output=True)
        else:
            subprocess.run(["xdg-open", url], capture_output=True)
    except Exception:
        pass


# --------------------------------------------------------------------------- etapes


def npm() -> list[str]:
    """Commande npm adaptee a la plateforme (Windows a besoin du .cmd resolu)."""
    import shutil

    npm_path = shutil.which("npm")
    if not npm_path:
        fail("npm introuvable (reinstaller Node.js).")
    return [npm_path]


def node() -> str:
    import shutil

    node_path = shutil.which("node")
    if not node_path:
        fail("Node.js introuvable (reinstaller Node.js).")
    return node_path


def prerequisites() -> None:
    global PY
    step("Prerequis")
    PY = find_python()
    node_path = node()
    npm_path = npm()[0]
    pyver = subprocess.run([PY, "--version"], capture_output=True, text=True).stdout.strip()
    nodever = subprocess.run([node_path, "--version"], capture_output=True, text=True).stdout.strip()
    npmver = subprocess.run(npm() + ["--version"], capture_output=True, text=True).stdout.strip()
    ok(f"{pyver} / {nodever} / {npmver}")


def create_venv() -> None:
    global VPY
    step("Environnement virtuel")
    VPY = venv_python()
    if VPY and os.path.isfile(VPY):
        ok("venv existant (reutilise)")
        return
    run([PY, "-m", "venv", str(VENV)])
    VPY = venv_python()
    if not os.path.isfile(VPY):
        fail("venv cree mais introuvable.")
    ok("venv cree dans backend/.venv")


def install_python_deps() -> None:
    step("Dependances Python")
    now = hashlib.sha256(REQ.read_bytes()).hexdigest()
    previous = REQ_HASH.read_text().strip() if REQ_HASH.exists() else ""
    django_ok = False
    try:
        run([VPY, "-c", "import django, rest_framework, channels"], check=False)
        django_ok = True
    except Exception:
        django_ok = False
    if previous == now and django_ok:
        ok("requirements.txt inchange -> pip ignore")
        return
    run([VPY, "-m", "pip", "install", "--quiet", "--disable-pip-version-check", "-r", str(REQ)])
    REQ_HASH.write_text(now)
    ok("dependances installees")


def migrate_and_check(fresh: bool, reset: bool, seed: bool) -> None:
    step("Migrations + verification Django")
    run([VPY, "manage.py", "migrate", "--noinput"], cwd=BACKEND)
    run([VPY, "manage.py", "check", "--fail-level", "ERROR"], cwd=BACKEND)
    ok("base a jour, sante du projet : OK")
    if fresh or seed or reset:
        step("Donnees de demonstration (fictives)")
        run([VPY, "scripts/seed_demo.py"], cwd=BACKEND)
        ok("comptes de demo prets")
    else:
        ok("base existante conservee (--reset pour reinitialiser)")


def install_node_deps() -> None:
    if (FRONTEND / "node_modules" / "next").exists():
        ok("node_modules a jour")
        return
    step("Dependances Node (frontend)")
    run(npm() + ["install", "--no-fund", "--no-audit"], cwd=FRONTEND)
    ok("frontend installe")


def run_tests() -> None:
    prerequisites()
    create_venv()
    step("Tests Django")
    run([VPY, "manage.py", "test", "tests", "-v", "1"], cwd=BACKEND)
    sys.exit(0)


# --------------------------------------------------------------------------- commandes


def cmd_setup(reset: bool = False, seed: bool = False) -> None:
    prerequisites()
    create_venv()
    install_python_deps()
    fresh = not DB.exists()
    if reset and not fresh:
        step("Reinitialisation de la base (--reset)")
        DB.unlink(missing_ok=True)
        fresh = True
    migrate_and_check(fresh, reset, seed)
    install_node_deps()
    print("\n[OK] MedConnect est installe -> 'make start' ou 'python setup.py --start' pour lancer le projet\n")


def cmd_start(open_browser_flag: bool = True) -> None:
    prerequisites()
    create_venv()
    install_python_deps()
    migrate_and_check(not DB.exists(), False, False)
    install_node_deps()

    step("Demarrage du backend (http://localhost:8000)")
    with open(LOG_B, "ab") as f:
        subprocess.Popen(
            [VPY, "manage.py", "runserver", "127.0.0.1:8000"],
            cwd=BACKEND, stdout=f, stderr=f,
        )

    step("Demarrage du frontend (http://localhost:3000)")
    with open(LOG_F, "ab") as f:
        subprocess.Popen(
            npm() + ["run", "dev"],
            cwd=FRONTEND, stdout=f, stderr=f,
        )

    step("Attente de l'API")
    if not wait_for_health():
        fail("API absente -> verifier .backend.log (port 8000 pris ?)")
    ok("API prete")

    if open_browser_flag:
        open_browser()

    print("  Logs : .backend.log / .frontend.log   Arret : 'make stop' ou 'python setup.py --stop'\n")


def cmd_stop() -> None:
    step("Arret des serveurs (ports 8000 / 3000)")
    for port in (8000, 3000):
        pids = pids_on_port(port)
        kill_pids(pids)
        ok(f"port {port} : {'arrete' if pids else 'deja libre'}")


def cmd_health() -> None:
    import urllib.request as req
    try:
        print(req.urlopen("http://127.0.0.1:8000/api/health/", timeout=5).read().decode())
    except Exception as e:
        fail(f"backend : {e}")
    try:
        r = req.urlopen("http://127.0.0.1:3000/", timeout=5)
        print(f"frontend : HTTP {r.status}")
    except Exception as e:
        fail(f"frontend : {e}")


def cmd_logs() -> None:
    for log in (LOG_B, LOG_F):
        if log.exists():
            print(f"\n--- {log} ---")
            print(log.read_text(errors="replace")[-4000:])


# --------------------------------------------------------------------------- main


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] in ("-h", "--help"):
        print("Usage: python setup.py [--setup|--start|--stop|--test|--reset|--seed|--health|--logs] [--no-browser] [--reset] [--seed]")
        print("")
        print("  --setup     Installe tout (venv, pip, migrations, seed, npm)  [par defaut]")
        print("  --start     Installe si besoin, puis demarre backend + frontend")
        print("  --stop      Arrete les serveurs (ports 8000/3000 uniquement)")
        print("  --test      Lance les tests Django")
        print("  --reset     Reinitialise la base de demonstration")
        print("  --seed      Re-importe les donnees de demonstration")
        print("  --health    Verifie que les serveurs repondent")
        print("  --logs      Affiche la fin des logs des serveurs")
        print("  --no-browser Avec --start : n'ouvre pas le navigateur")
        sys.exit(0)

    reset = "--reset" in args
    seed = "--seed" in args
    open_browser_flag = "--no-browser" not in args

    if "--setup" in args or not any(a.startswith("--") for a in args):
        cmd_setup(reset=reset, seed=seed)
    elif "--start" in args:
        cmd_start(open_browser_flag=open_browser_flag)
    elif "--stop" in args:
        cmd_stop()
    elif "--test" in args:
        run_tests()
    elif "--health" in args:
        cmd_health()
    elif "--logs" in args:
        cmd_logs()
    else:
        fail(f"Option inconnue : {args[0]}")


if __name__ == "__main__":
    main()
