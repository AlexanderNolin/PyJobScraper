import random
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from jobspy import scrape_jobs

# Configuration
OUTPUT_DIR = Path("output")
SITES = ["indeed", "linkedin", "zip_recruiter", "glassdoor"]
SEARCH_TERMS = [
    "Systems Administrator",
    "Network Engineer",
    "Network Administrator",
    "Network Analyst",
    "IT",
    "Helpdesk",
    "Security Engineer",
    "SOC",
    "NOC",
]
HOURS_OLD = 24
RESULTS_WANTED = 50       # per site, per term
DELAY_RANGE = (2, 5)      # seconds to pause between searches


def search_term_remote(term: str) -> pd.DataFrame:
    """Run one nationwide remote search and return only confirmed-remote jobs."""
    jobs = scrape_jobs(
        site_name=SITES,
        search_term=term,
        location="USA",
        is_remote=True,
        hours_old=HOURS_OLD,
        results_wanted=RESULTS_WANTED,
        country_indeed="USA",
    )

    if jobs is None or jobs.empty:
        return pd.DataFrame()

    # Some sites ignore the remote flag, so filter afterwards
    if "is_remote" in jobs.columns:
        jobs = jobs[jobs["is_remote"].fillna(False).astype(bool)]

    if not jobs.empty:
        jobs = jobs.copy()
        jobs["search_term"] = term

    return jobs


def main() -> None:
    all_jobs = []

    for i, term in enumerate(SEARCH_TERMS):
        print(f"Searching remote: {term}...")

        try:
            jobs = search_term_remote(term)
        except Exception as exc:
            print(f"  Search failed for {term}: {exc}")
            continue

        if jobs.empty:
            print("  No results")
        else:
            all_jobs.append(jobs)
            print(f"  {len(jobs)} jobs")

        # Pause between searches (skip after the last one)
        if i < len(SEARCH_TERMS) - 1:
            time.sleep(random.uniform(*DELAY_RANGE))

    if not all_jobs:
        print("\nNo jobs were collected.")
        return

    master_df = pd.concat(all_jobs, ignore_index=True)

    # Same posting can match several search terms
    if "job_url" in master_df.columns:
        master_df = master_df.drop_duplicates(subset=["job_url"], keep="first")

    # Same job posted on multiple sites has different URLs, so dedupe on content too
    dedupe_cols = [c for c in ("title", "company") if c in master_df.columns]
    if len(dedupe_cols) == 2:
        key = master_df[dedupe_cols].apply(
            lambda col: col.astype(str).str.lower().str.strip()
        )
        master_df = master_df[~key.duplicated(keep="first")]

    master_df["date_scraped"] = datetime.now().strftime("%Y-%m-%d")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    master_file = OUTPUT_DIR / "all_remote_jobs.csv"
    master_df.to_csv(master_file, index=False)

    print(f"\nTotal unique remote jobs: {len(master_df)}")
    print(f"Master CSV: {master_file.resolve()}")


if __name__ == "__main__":
    main()