import requests
import urllib3
urllib3.disable_warnings()

ckan_url = 'https://ckan.surabaya.go.id/api/3/action'
datasets = ['z011-9141-63', 'z011-6059-63', 'z011-6058-63', 'z011-5090-63']

for ds in datasets:
    try:
        res = requests.get(f'{ckan_url}/package_show?id={ds}', verify=False).json()
        if res.get('success'):
            r_list = res['result'].get('resources', [])
            print(f'Dataset {ds} has {len(r_list)} resources.')
            if len(r_list) > 0:
                search = requests.get(f'{ckan_url}/datastore_search?resource_id={r_list[0]["id"]}&limit=1', verify=False).json()
                if search.get('success'):
                    fields = [f["id"] for f in search["result"]["fields"]]
                    print(f'  Sample fields: {fields}')
    except Exception as e:
        print(e)
