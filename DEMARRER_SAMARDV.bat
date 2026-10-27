@echo off
chcp 65001 >nul
cd /d "%~dp0"
title SamaRDV - Django
 echo ==========================================
 echo       SamaRDV - Demarrage Windows
 echo ==========================================
if not exist .venv (
  echo Creation de l'environnement Python...
  py -3.12 -m venv .venv
  if errorlevel 1 py -3 -m venv .venv
)
if not exist .venv\Scripts\python.exe (
  echo ERREUR : Python est introuvable. Installez Python 3.11 ou 3.12 puis recommencez.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto erreur
.venv\Scripts\python.exe manage.py makemigrations rdv
.venv\Scripts\python.exe manage.py migrate
if errorlevel 1 goto erreur
.venv\Scripts\python.exe manage.py seed_demo
 echo.
 echo Site : http://127.0.0.1:8000/
 echo Admin: http://127.0.0.1:8000/admin/
 echo Pour creer le compte admin, lancez CREER_ADMIN.bat dans une autre fenetre.
 echo.
.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
pause
exit /b 0
:erreur
echo Une erreur est survenue. Lisez le message ci-dessus.
pause
exit /b 1
