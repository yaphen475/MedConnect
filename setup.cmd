@echo off
rem ============================================================
rem  MedConnect - installation en une commande (Windows)
rem  Usage :  setup.cmd            -> installe tout
rem           setup.cmd -Reset     -> reinitialise la base demo
rem           setup.cmd -Seed      -> re-importe les donnees demo
rem ============================================================
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" %*
exit /b %ERRORLEVEL%
