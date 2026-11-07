@echo off
title Instalar dependencias - Proyecto 13
echo Instalando dependencias...
python -m pip install -r requirements.txt
if errorlevel 1 (
    py -m pip install -r requirements.txt
)
echo.
echo Instalacion terminada.
pause
