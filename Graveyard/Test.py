import csv
from jobspy import scrape_jobs

jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor","google"],
    search_term="Data Center",
    google_search_term= "Data Center",
    location="Madison, AL",
    distance =40,
    hours_old=72,
    country_indeed='USA'

    # fetch_description=True # for boards whose search results don't include the description (slower)
    # proxies=["208.195.175.46:65095", "208.195.175.45:65095", "localhost"],
)
print(f"Found {len(jobs)} jobs")
print(jobs.head())
jobs.to_csv("jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)  # to_excel