@echo off
title Generador de Ejecutable PDF
cd /d "%~dp0"

echo ===================================================
echo    GENERANDO INSTALADOR PORTABLE (EXE)
echo ===================================================
echo.
echo [1/3] Instalando librerias necesarias...
python -m pip install pyinstaller flask-socketio --quiet

echo [2/3] Creando ejecutable (esto puede tardar un minuto)...
:: --onefile: Crea un solo archivo .exe
:: --windowed: No abre una ventana de consola negra al iniciar
:: --icon: Le pone el icono que descargaste
:: --add-data: Incluye la carpeta de iconos dentro del .exe
:: Usamos "python -m PyInstaller" que es mas seguro si el PATH no esta configurado
python -m PyInstaller --noconfirm --onefile --windowed ^
    --icon "favicon_io (1)/favicon.ico" ^
    --add-data "favicon_io (1);favicon_io (1)" ^
    --hidden-import engineio.async_drivers.threading ^
    --hidden-import socketio.async_drivers.threading ^
    --name "PDF_Compressor_Pro" ^
    app.py

echo.
echo [3/3] Proceso terminado!
echo.
echo Tu herramienta esta lista en la carpeta: dist\PDF_Compressor_Pro.exe
echo Puedes copiar ese archivo y pasarselo a tus compañeros.
echo.
pause
