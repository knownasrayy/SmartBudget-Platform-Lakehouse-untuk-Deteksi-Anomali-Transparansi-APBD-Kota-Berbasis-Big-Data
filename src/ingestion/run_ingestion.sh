#!/bin/bash
# ============================================================
#  SmartBudget — Auto Ingestion Scheduler (Linux/Mac)
#  Jalankan: bash src/ingestion/run_ingestion.sh
# ============================================================

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="src/ingestion/ingest_apbd.py"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/ingestion_$(date +%Y%m%d).log"

mkdir -p "$LOG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Memulai ingestion pipeline..." | tee -a "$LOG_FILE"

cd "$PROJECT_DIR"
python "$SCRIPT" 2>&1 | tee -a "$LOG_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Ingestion selesai." | tee -a "$LOG_FILE"