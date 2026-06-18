import requests
import json
import urllib3
urllib3.disable_warnings()

url = "https://ckan.surabaya.go.id/api/3/action/organization_show?id=bapenda&include_datasets=true"
r = requests.get(url, verify=False)
data = r.json()

if data.get("success"):
    org = data["result"]
    datasets = org.get("packages", [])
    print(f"Organisasi: {org.get('title')} ({org.get('name')})")
    print(f"Total Dataset: {len(datasets)}\n")
    
    for i, ds in enumerate(datasets):
        print(f"[{i+1}] {ds.get('title')} (ID: {ds.get('name')})")
        print(f"    Deskripsi: {ds.get('notes', '')[:100]}...")
        print(f"    Format Resources: {', '.join(set([res.get('format', '') for res in ds.get('resources', [])]))}")
        print()
else:
    print("Failed to fetch data:", data)
