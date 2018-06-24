import requests,json

API_KEY='API_KEY'
url = 'https://myheat.ca/getHouses?c=calgary'
url_geo='https://maps.googleapis.com/maps/api/geocode/json?key='+API_KEY+'&address='

dy=0.00200399707
dx=0.00152349472

def get_coords(a):
    r=requests.get(url_geo+a)
    return json.loads(r.text)["results"][0]["geometry"]["location"]
try:
    while(True):
        address=input("Enter an address: ")
        coords=get_coords(address)
        print(coords)
except KeyboardInterrupt as e:
    print("Exiting..")
