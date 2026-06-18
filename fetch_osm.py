import urllib.request
import urllib.parse
import json

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json][timeout:25];
area["name"="Surabaya"]["admin_level"="5"]->.searchArea;
relation["admin_level"="6"](area.searchArea);
out geom;
"""
data = urllib.parse.urlencode({'data': overpass_query}).encode('utf-8')
req = urllib.request.Request(overpass_url, data=data, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print(f"Got {len(result.get('elements', []))} elements")
        if len(result.get('elements', [])) > 0:
            print(result['elements'][0]['tags']['name'])
        
        with open('surabaya_osm.json', 'w', encoding='utf-8') as f:
            json.dump(result, f)
            print("Saved to surabaya_osm.json")
except Exception as e:
    print(e)
