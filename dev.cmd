@echo off
rem ============================================================
rem  MedConnect - demarrage quotidien (Windows)
rem  Installe ce qui manque, puis lance backend + frontend
rem  et ouvre http://localhost:3000
rem ============================================================
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1" -Start %*
exit /b %ERRORLEVEL%
