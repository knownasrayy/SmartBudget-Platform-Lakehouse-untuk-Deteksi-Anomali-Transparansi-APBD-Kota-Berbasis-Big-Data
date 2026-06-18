@echo off
:: ============================================================
::  SmartBudget — Auto Ingestion Scheduler (Windows)
::  Jalankan file ini untuk trigger ingestion pipeline Adel
:: ============================================================

set PROJECT_DIR=D:\SmartBudget-Platform-Lakehouse-untuk-Deteksi-Anomali-Transparansi-APBD-Kota-Berbasis-Big-Data
set SCRIPT=src\ingestion\ingest_apbd.py
set LOG_DIR=%PROJECT_DIR%\logs
set LOG_FILE=%LOG_DIR%\ingestion_%date:~-4,4%%date:~-7,2%%date:~0,2%.log

:: Buat folder logs kalau belum ada
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo [%date% %time%] Memulai ingestion pipeline... >> "%LOG_FILE%"

cd /d "%PROJECT_DIR%"
python %SCRIPT% >> "%LOG_FILE%" 2>&1

echo [%date% %time%] Ingestion selesai. >> "%LOG_FILE%"
echo Ingestion selesai! Cek folder data\bronze\raw\ dan logs\