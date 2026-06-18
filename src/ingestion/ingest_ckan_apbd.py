import requests
import json
import pandas as pd
import urllib3
import os
import uuid
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Define directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BRONZE_DIR = BASE_DIR / "data" / "bronze"
BRONZE_DIR.mkdir(parents=True, exist_ok=True)

CKAN_BASE_URL = "https://ckan.surabaya.go.id/api/3/action"
DATASET_ID = "z011-9242-63" # Realisasi APBD

def fetch_dataset_resources(dataset_id: str):
    """Fetch all resource IDs from a CKAN dataset."""
    print(f"Fetching metadata for dataset: {dataset_id}...")
    url = f"{CKAN_BASE_URL}/package_show?id={dataset_id}"
    resp = requests.get(url, verify=False)
    if resp.status_code != 200:
        raise Exception(f"Failed to fetch dataset. Status: {resp.status_code}")
    
    data = resp.json()
    if not data.get("success"):
        raise Exception("CKAN API returned success=False")
    
    return data["result"]["resources"]

def fetch_datastore_records(resource_id: str, limit: int = 1000):
    """Fetch all records from a specific CKAN datastore resource."""
    print(f"  -> Fetching records for resource {resource_id}...")
    url = f"{CKAN_BASE_URL}/datastore_search?resource_id={resource_id}&limit={limit}"
    
    try:
        resp = requests.get(url, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                return data["result"]["records"]
    except Exception as e:
        print(f"  -> Error fetching resource: {e}")
    
    return []

def run_ckan_ingestion():
    """Main function to orchestrate CKAN APBD ingestion."""
    print("==============================================")
    print("=  STARTING CKAN APBD INGESTION (BRONZE)     =")
    print("==============================================")
    
    resources = fetch_dataset_resources(DATASET_ID)
    print(f"Found {len(resources)} resources.")
    
    all_records = []
    
    for idx, res in enumerate(resources):
        # Extract year and month from name/URL if possible
        # Format usually: data-z011-9242-63-3-2022.csv -> Month 3, Year 2022
        url = res.get("url", "")
        parts = url.split("-")
        
        # Default fallback
        year = "2023"
        month = "1"
        
        if len(parts) >= 2:
            try:
                year = parts[-1].replace(".csv", "")
                month = parts[-2]
            except:
                pass
                
        records = fetch_datastore_records(res["id"])
        
        # Inject metadata
        for rec in records:
            rec["_source_resource"] = res["name"]
            rec["_extracted_year"] = year
            rec["_extracted_month"] = month
            
        all_records.extend(records)
        
    print(f"\nTotal records fetched: {len(all_records)}")
    
    # Save to Bronze
    if all_records:
        df = pd.DataFrame(all_records)
        output_path = BRONZE_DIR / "ckan_apbd_raw.csv"
        df.to_csv(output_path, index=False)
        print(f"✅ Successfully saved {len(df)} records to {output_path}")
        return df
    else:
        print("❌ No records found!")
        return None

if __name__ == "__main__":
    run_ckan_ingestion()
