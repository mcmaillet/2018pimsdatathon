import requests,json,re,csv
from decimal import Decimal
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
app_token="APP_TOKEN"
url_sites="https://data.calgary.ca/resource/vd97-7a2g.json?$$app_token="+app_token
url_prod_get_count="https://data.calgary.ca/resource/u7by-kwjh.json?$$app_token="+app_token+"&$WHERE=date%20BETWEEN {0} AND {1}&id={2}&$SELECT=count(*)"
url_prod_query="https://data.calgary.ca/resource/u7by-kwjh.json?$$app_token="+app_token+"&$WHERE=date%20BETWEEN {0} AND {1}&id={2}&$LIMIT={3}&$OFFSET={4}"
url_bounds="https://data.calgary.ca/api/views/surr-xmvs/rows.json?accessType=DOWNLOAD"
re_polygon=re.compile("POLYGON \\(\\(([^\\)]+)\\)\\)")
def get_csv_header():
    return ['test']
class Poly:
    def __init__(self,id,name,region,poly):
        self.id=id
        self.name=name
        self.region=region
        self.poly=poly
    def __str__(self):
        return "\nID: "+str(self.id)+"\nName: "+str(self.name)+"\nRegion: "+str(self.region)
class Site:
    def __init__(self,id,lat,lng,name):
        self.id=id
        self.lat=lat
        self.lng=lng
        self.name=name
    def setSolarProduction(self,solprod):
        self.solprod=solprod
    def setCommunity(self,community):
        self.community=community
    def getCsv(self):
        try:
            prod=[]
            for p in self.solprod:
                prod.append([p.y,p.m_array])
            return [self.id,self.name,self.lat,self.lng,self.community,prod]
        except:
            return ['','','','','','']
    def __str__(self):
        return "\nID: "+str(self.id)+"\nLatitude: "+str(self.lat)+"\nLongitude: "+str(self.lng)+"\nName: "+str(self.name)
class Production:
    def __init__(self,y,m_array):
        self.y=y
        self.m_array=m_array
def get_coords(c):
    cs=[]
    for cc in c:
        cs.append((Decimal(cc.Lt),Decimal(cc.Lg)))
    return cs
def get_sites():
    s=[]
    js=json.loads(requests.get(url_sites).text)
    for j in js:
        id=""
        lat=0.0
        lng=0.0
        name=""
        if j['id']:
            id=j['id']
        if j['latitude']:
            lat=Decimal(j['latitude'])
        if j['longitude']:
            lng=Decimal(j['longitude'])
        if j['name']:
            name=j['name']
        s.append(Site(id,lat,lng,name))
    return s
def get_community_for_site(s):
    for p in polys:
        point = Point(s.lng,s.lat)
        polygon=Polygon(p.poly)
        if(polygon.contains(point)):
            return p.name
    return "N/A"
def get_prod_for_site(s):
    MAX_RESULTS=100
    p_years=[]#kWh for years with months
    if s.id and s.id!='null':
        for y in range(START_YEAR,END_YEAR+1):
            p=[]
            for m in range(1,13):
                sum=0.0
                u_count=url_prod_get_count.format(get_date(y,m),get_date(y,m+1),s.id)
                count=int(json.loads(requests.get(u_count).text)[0]['count'])
                offset=0
                while(offset<=count):
                    u=url_prod_query.format(get_date(y,m),get_date(y,m+1),s.id,MAX_RESULTS,offset)
                    js=json.loads(requests.get(u).text)
                    for j in js:
                        sum+=float(j['kwh'])
                    p.append(round(sum,6))
                    print("site:"+s.name+"year: "+str(y)+"month: "+str(m)+"sum: "+str(sum))
                    offset+=MAX_RESULTS
            p_years.append(Production(y,p))
    for py in p_years:
        print(py.y)
        print(py.m_array)
    return p_years
def get_date(y,m):
    if m==13:
        return "\""+str(y+1)+"-01-01\""
    return "\""+str(y)+"-"+str(m)+"-01\""
##
##
##
##
##
START_YEAR=2015
END_YEAR=2018
sites=get_sites()
c=1
for s in sites:
    print("#"+str(c)+"/"+str(len(sites))+": "+s.name)
    s.setSolarProduction(get_prod_for_site(s))
    c+=1
rs=json.loads(requests.get(url_bounds).text)
polys=[]
for r in rs['data']:
    coords_for_poly=[]
    m=re_polygon.match(r[8])
    for c in re.findall("([^\s]+) ([^,]+),",m.group(1)):
        coords_for_poly.append((Decimal(c[0]),Decimal(c[1])))
    polys.append(Poly(r[11],r[12],r[13],coords_for_poly))
csv_file=open('csv/solar_production_with_community.csv','w+')
csv.writer(csv_file,quoting=csv.QUOTE_ALL).writerow(get_csv_header())
for s in sites:
    s.setCommunity(get_community_for_site(s))
    print("Site: "+str(s.name))
    print("Community: "+s.community)
    csv.writer(csv_file,quoting=csv.QUOTE_ALL).writerow(s.getCsv())
csv_file.close()
