@echo off
title Akilli Restoran Menu AI Sistemi

echo Sistem baslatiliyor...

:: Python kontrol
where python >nul 2>nul
if errorlevel 1 (
    echo Python bulunamadi!
    pause
    exit
)

:: requests kontrol
python -m pip show requests >nul 2>nul
if errorlevel 1 (
    echo requests yukleniyor...
    python -m pip install requests
)

:: Ollama kontrol
where ollama >nul 2>nul
if errorlevel 1 (
    echo Ollama kurulu degil!
    echo https://ollama.com/download adresinden indir.
    pause
)

echo Program baslatiliyor...
start "" pythonw main.pyw
exit
