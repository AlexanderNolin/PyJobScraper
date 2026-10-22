import geonamescache
import csv
from jobspy import scrape_jobs

gc = geonamescache.GeonamesCache()
cities = gc.get_cities()

us_cities = [
    {
        "name": city["name"],
        "state": city["admin1code"],
        "population": city.get("population", 0)
    }
    for city in cities.values()
    if city["countrycode"] == "US"
    and 1000000 <= city.get("population", 0)
]

for city in us_cities:
    print(f'{city["name"]}')