import requests, base64

key = 'dummySecretKey'
URL = 'http://192.168.1.145:8010/mobikul/splashPageData'
# URL = 'http://192.168.1.145:8010/web'
b64Val = base64.b64encode(key+":"+key)
headers={"Authorization": "Basic %s" % b64Val}
headers={"Authorization": "Basic %s" % b64Val,'mobikul_db':'mobikul_fresh'}
result = requests.post(URL, headers=headers,data={})
print result.text