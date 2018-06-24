import csv,json

c = open('csv/Solar_Energy_Production.csv', 'r')
j = open('json/Solar_Energy_Production.json', 'w+')

fieldnames = ("name","id","address","date",'kWh')
reader = csv.DictReader(c, fieldnames)
for row in reader:
    json.dump(row, j)
    j.write('\n')
