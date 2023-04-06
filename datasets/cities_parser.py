import csv
import math
from tqdm import tqdm
import random

def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d


data_selected = []

lines = []
with open("cities_1m.csv") as datafile:
    reader = csv.DictReader(datafile, delimiter=";")
    headers = reader.fieldnames
    lines = list(line for line in reader)

lines = list(filter(lambda _ : int(_["Population"]) > 50000, lines))

coord_extracter = lambda _ : list(float(c) for c in _["Coordinates"].split(","))
city_parser = lambda _ : [_["ASCII Name"],_["Country name EN"], _["Coordinates"]]
parsed = []
#  rnd_cities = random.sample(lines, 1000)
rnd_cities = lines
for city_1 in tqdm(rnd_cities):

    lines.sort(key = lambda _ : distance(coord_extracter(_), coord_extracter(city_1)))
    parsed.append(list(city_parser(_) for _ in [lines[0],lines[1],lines[2]]))
    
#
#  ascii_name = line["ASCII Name"]
#  country_name = line["Country name EN"]
#  population = int(line["Population"])
#  coordinates = line(["coordinates"])
        #  if population < 50000:
        #      continue
        #
        # 50 - 100 k for 1
        # 100 - 200 k for 3
        # 200 - 500 k for 4
        # 500k - 1m for 5
        # 1m to 2.5m for 6
        # 2.5m + > for 10
        #  data_selected.append([ascii_name, country_name, population])

with open("closest_cities.csv", "w") as datafile:
    writer = csv.writer(datafile)
    writer.writerows(parsed)
