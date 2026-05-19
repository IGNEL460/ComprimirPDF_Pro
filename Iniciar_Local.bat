@echo off
title PDF Compressor Local
cd /d "%~dp0"

echo ===================================================
echo    PDF COMPRESSOR PRO - MODO LOCAL
echo ===================================================
echo.
echo [1/2] Verificando entorno...
python -m pip install flask pymupdf --quiet

echo [2/2] Iniciando aplicacion local...
start http://localhost:5000
python app.py

pause
