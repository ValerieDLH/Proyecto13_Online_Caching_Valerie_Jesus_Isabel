@echo off
title Proyecto 13 - Online Caching Simulator
echo ================================================
echo   Proyecto 13 - Online Caching Simulator
echo ================================================
echo.
python -m streamlit run app.py
if errorlevel 1 (
    echo.
    echo No se pudo iniciar con "python".
    echo Intentando con "py"...
    py -m streamlit run app.py
)
pause
