<#
.SYNOPSIS
    MedConnect - mise en place du developpement en UNE commande.

.DESCRIPTION
    Script idempotent : le relancer n'importe quand est sur et rapide
    (seules les etapes qui ont besoin de tourner sont executees).

    .\setup.cmd           -> installe tout (venv, dependances, base, frontend)
    .\setup.cmd -Reset    -> reinitialise la base de demonstration
    .\setup.cmd -Seed     -> force la re-importation des donnees de demo
    .\dev.cmd             -> installe si besoin puis demarre backend + frontend

.NOTES
    Equipe MedConnect - ENSIM 4A. Windows / PowerShell 5.1+.
#>
param(
    [switch]$Start,      # demarrer backend + frontend a la fin
    [switch]$Reset,      # supprimer db.sqlite3 puis migrer + reseed
    [switch]$Seed,       # re-executer scripts/seed_demo.py
    [switch]$NoBrowser   # ne pas ouvrir le navigateur (CI / tests)
)

$ErrorActionPreference = "Stop"
$Root     = $PSScriptRoot
$Backend  = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$VenvDir  = Join-Path $Backend ".venv"
$VenvPy   = Join-Path $VenvDir "Scripts\python.exe"
$ReqFile  = Join-Path $Backend "requirements.txt"
$ReqHash  = Join-Path $VenvDir ".requirements.hash"
$DbFile   = Join-Path $Backend "db.sqlite3"

function Step($m) { Write-Host "`n==> $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "    [OK] $m" -ForegroundColor Green }
function Warn($m) { Write-Host "    [!] $m" -ForegroundColor Yellow }
function Fail($m) { Write-Host "`n    [ECHEC] $m" -ForegroundColor Red; exit 1 }

# ------------------------------------------------------------- 1. prerequis
Step "Prerequis"
if (Get-Command python -ErrorAction SilentlyContinue) {
    $Py = "python"; $PyPrefix = @()
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $Py = "py"; $PyPrefix = @("-3")
} else {
    Fail "Python 3.10+ introuvable. Installez-le : https://www.python.org/downloads/ (cocher 'Add python.exe to PATH')."
}
$pyVer = & $Py @PyPrefix --version 2>&1
if ($LASTEXITCODE -ne 0) { Fail "Python ne repond pas." }
Ok "$pyVer"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Fail "Node.js 18+ introuvable. Installez la version LTS : https://nodejs.org/"
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Fail "npm introuvable. Reinstaller Node.js."
}
Ok "Node $(node --version) / npm $(npm --version)"

# --------------------------------------------------- 2. environnement virtuel
if (-not (Test-Path $VenvPy)) {
    Step "Creation de l'environnement virtuel (backend/.venv)"
    & $Py @PyPrefix -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { Fail "Impossible de creer le venv." }
    Ok "venv cree dans backend/.venv"
} else {
    Ok "venv existant (reutilise)"
}

# ------------------------------------------------------ 3. dependances Python
Step "Dependances Python"
$hash = (Get-FileHash $ReqFile -Algorithm SHA256).Hash
$previous = if (Test-Path $ReqHash) { (Get-Content $ReqHash -Raw).Trim() } else { "" }
$djangoPresent = Test-Path (Join-Path $VenvDir "Lib\site-packages\django")
if ($previous -eq $hash -and $djangoPresent) {
    Ok "requirements.txt inchange -> pip ignore"
} else {
    & $VenvPy -m pip install --quiet --disable-pip-version-check -r $ReqFile
    if ($LASTEXITCODE -ne 0) { Fail "pip install en echec (verifier le reseau)." }
    Set-Content -Path $ReqHash -Value $hash -NoNewline
    Ok "dependances installees"
}

# --------------------------------------------------- 4. base de donnees + seed
$freshDb = -not (Test-Path $DbFile)
if ($Reset -and -not $freshDb) {
    Step "Reinitialisation de la base (-Reset)"
    Remove-Item $DbFile -Force
    $freshDb = $true
    Ok "db.sqlite3 supprimee"
}

Step "Migrations + verification Django"
Push-Location $Backend
try {
    & $VenvPy manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) { Fail "migrate en echec." }
    & $VenvPy manage.py check --fail-level ERROR
    if ($LASTEXITCODE -ne 0) { Fail "manage.py check en echec." }
    Ok "base a jour, sante du projet : OK"

    if ($freshDb -or $Seed) {
        Step "Donnees de demonstration (fictives)"
        & $VenvPy scripts\seed_demo.py
        if ($LASTEXITCODE -ne 0) { Fail "seed en echec." }
        Ok "comptes de demo prets"
    } else {
        Ok "base existante conservee (-Reset pour tout reinitialiser)"
    }
}
finally {
    Pop-Location
}

# --------------------------------------------------- 5. dependances frontend
if (-not (Test-Path (Join-Path $Frontend "node_modules\next"))) {
    Step "Dependances Node (frontend)"
    Push-Location $Frontend
    try {
        npm install --no-fund --no-audit
        if ($LASTEXITCODE -ne 0) { Fail "npm install en echec (verifier le reseau)." }
    }
    finally {
        Pop-Location
    }
    Ok "frontend installe"
} else {
    Ok "node_modules a jour"
}

# ----------------------------------------------------------------- 6. bilan
Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "  MedConnect est pret a developper." -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host @"
  Backend   cd backend ; .\.venv\Scripts\python.exe manage.py runserver
            -> http://localhost:8000   (API + /admin/)
  Frontend  cd frontend ; npm run dev
            -> http://localhost:3000
  Tests     cd backend ; .\.venv\Scripts\python.exe manage.py test tests
  Demo      admin / medecin / secretaire / patient1 / patient2
            mot de passe : MedConnect2026!
  Reinit    .\setup.cmd -Reset
"@

# ------------------------------------------------------------- 7. -Start mode
if ($Start) {
    Step "Demarrage du backend (port 8000)"
    Start-Process -FilePath $VenvPy `
        -ArgumentList "manage.py", "runserver", "127.0.0.1:8000" `
        -WorkingDirectory $Backend -WindowStyle Minimized

    Step "Demarrage du frontend (port 3000)"
    Start-Process -FilePath "cmd.exe" `
        -ArgumentList "/k", "npm run dev" `
        -WorkingDirectory $Frontend

    $up = $false
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Seconds 1
        try {
            $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health/" `
                -UseBasicParsing -TimeoutSec 2
            if ($r.StatusCode -eq 200) { $up = $true; break }
        } catch { }
    }
    if ($up) { Ok "API repond sur http://localhost:8000/api/health/" }
    else { Warn "API pas encore prete : verifier qu'aucun autre processus n'utilise le port 8000." }

    if (-not $NoBrowser) { Start-Process "http://localhost:3000" }
    Write-Host "  Arret : fermer les fenetres 'runserver' et 'npm run dev'." -ForegroundColor DarkGray
    Write-Host ""
}
