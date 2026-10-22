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
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor","google"],
        search_term="IT",
        google_search_term= "IT",
        location=f'{city["name"]}, {city["state"]}',
        distance =30,
        hours_old=24,
        country_indeed='USA'

        # fetch_description=True # for boards whose search results don't include the description (slower)
        # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
    )
    jobs = jobs[jobs["is_remote"] == True]
    print(f"Found {len(jobs)} jobs")
    print(jobs.head())
    jobs.to_csv("" + city["name"]+ " "+ " remote jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)  # to_excel