
import csv
import re
from pathlib import Path

import geonamescache
import pandas as pd
from jobspy import scrape_jobs

# Configuration
OUTPUT_DIR = Path("output")
SITES = ["indeed", "linkedin", "zip_recruiter", "glassdoor"]
SEARCH_TERMS = ["Assistant Manager"]

# Load cities
gc = geonamescache.GeonamesCache()
cities = gc.get_cities()

us_cities = [
    {
        "name": city["name"],
        "state": city["admin1code"],
        "population": city.get("population", 0),
    }
    for city in cities.values()
    if city["countrycode"] == "US"
    and city["admin1code"] == "AL"
    and city.get("population", 0) >= 100000
]

all_jobs = []

for city in us_cities:
    city_jobs = []

    print(f'\nSearching {city["name"]}, {city["state"]}...')

    for term in SEARCH_TERMS:
        try:
            jobs = scrape_jobs(
                site_name=SITES,
                search_term=term,
                location=f'{city["name"]}, {city["state"]}',
                distance=30,
                hours_old=24,
                results_wanted=25,
                country_indeed="USA",
            )

            if jobs.empty:
                print(f"  No results for: {term}")
                continue

            # Track where each result came from
            jobs["search_city"] = city["name"]
            jobs["search_state"] = city["state"]
            jobs["search_term"] = term

            city_jobs.append(jobs)
            print(f"  {term}: {len(jobs)} jobs")

        except Exception as exc:
            print(f"  Search failed for {term}: {exc}")

    if not city_jobs:
        continue

    # Combine terms for this city
    city_df = pd.concat(city_jobs, ignore_index=True)

    # Create output/jobs_by_city/AL/
    state_dir = OUTPUT_DIR / "jobs_by_city" / city["state"]
    state_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize city name for Windows filenames
    safe_name = re.sub(r'[<>:"/\\|?*]', "_", city["name"])
    output_file = state_dir / f"{safe_name}_jobs.csv"

    city_df.to_csv(
        output_file,
        index=False,
        quoting=csv.QUOTE_NONNUMERIC,
        escapechar="\\",
    )

    all_jobs.append(city_df)
    print(f"  Saved {len(city_df)} unique jobs to {output_file}")

# Export master dataset
if all_jobs:
    master_df = pd.concat(all_jobs, ignore_index=True)

    if "job_url" in master_df.columns:
        master_df = master_df.drop_duplicates(
            subset=["job_url"],
            keep="first",
        )

    master_file = OUTPUT_DIR / "all_jobs.csv"
    master_file.parent.mkdir(parents=True, exist_ok=True)

    master_df.to_csv(master_file, index=False)

    print(f"\nTotal unique jobs: {len(master_df)}")
    print(f"Master CSV: {master_file.resolve()}")
else:
    print("\nNo jobs were collected.")
