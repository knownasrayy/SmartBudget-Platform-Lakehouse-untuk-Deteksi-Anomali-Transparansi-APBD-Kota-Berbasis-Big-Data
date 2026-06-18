import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI(title="SmartBudget Lakehouse API")

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Paths
BASE_DIR = Path(__file__).resolve().parents[2]
GOLD_DIR = BASE_DIR / "data" / "gold"
DASHBOARD_DIR = BASE_DIR / "src" / "dashboard"

# Helper function to read CSV and convert to dict list
def read_csv_to_dict(filename):
    file_path = GOLD_DIR / filename
    if not file_path.exists():
        return []
    try:
        # fillna to handle NaN values which cannot be JSON serialized properly
        df = pd.read_csv(file_path).fillna("")
        return df.to_dict(orient='records')
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return []

@app.get("/api/summary")
def get_summary():
    """Mengembalikan ringkasan anggaran SKPD (KPI 1)"""
    data = read_csv_to_dict("gold_skpd_summary.csv")
    return JSONResponse(content=data)

@app.get("/api/anomalies")
def get_anomalies():
    """Mengembalikan data proyek terdeteksi anomali (KPI 2 & Heatmap)"""
    data = read_csv_to_dict("apbd_scored.csv")
    return JSONResponse(content=data)

@app.get("/api/sentiment")
def get_sentiment():
    """Mengembalikan hasil analisis sentimen opini publik (KPI 3)"""
    data = read_csv_to_dict("sentiment_results.csv")
    return JSONResponse(content=data)

@app.get("/api/vendors")
def get_vendors():
    """Mengembalikan daftar jejaring vendor pengadaan"""
    data = read_csv_to_dict("gold_jejaring_vendor.csv")
    return JSONResponse(content=data)

# Mount the static dashboard files to the root ("/")
app.mount("/", StaticFiles(directory=str(DASHBOARD_DIR), html=True), name="dashboard")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)
