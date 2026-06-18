import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

r = requests.get('https://ckan.surabaya.go.id/api/3/action/package_show?id=z011-9242-63', verify=False)
data = r.json()
resources = data['result']['resources']

print(f"Found {len(resources)} resources.")
for i, res in enumerate(resources[:3]):
    print(f"[{i}] {res['name']} - {res['format']} - {res['url']}")

if resources:
    csv_url = resources[0]['url']
    print(f"\nFetching sample from {csv_url}")
    csv_resp = requests.get(csv_url, verify=False)
    print("--- SAMPLE DATA ---")
    print(csv_resp.text[:1000])
