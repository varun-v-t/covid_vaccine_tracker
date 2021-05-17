import http.client
import json
conn = http.client.HTTPSConnection("cdn-api.co-vin.in")
payload = ''
headers = {}
conn.request("GET", "/api/v2/appointment/sessions/public/findByDistrict?district_id=294&date=11-05-2021", payload, headers)
res = conn.getresponse()
data = res.read()
print(json.loads(data.decode('utf-8'))['sessions'])