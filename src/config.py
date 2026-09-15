"""Paths and constants shared across the pipeline."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RAW_FILES = {
    "coverage": RAW_DIR / "coverage.csv",
    "reported_cases": RAW_DIR / "reported-cases.csv",
    "population": RAW_DIR / "population.csv",
    "vaccine_introduction": RAW_DIR / "vaccine-introduction.csv",
    "vaccine_schedule": RAW_DIR / "vaccine-schedule-data.csv",
    "country_reference": RAW_DIR / "who_country_reference.csv",
}

PROCESSED_FILES = {
    "coverage": PROCESSED_DIR / "clean_coverage.csv",
    "reported_cases": PROCESSED_DIR / "clean_reported_cases.csv",
    "incidence_rate": PROCESSED_DIR / "clean_incidence_rate.csv",
    "vaccine_introduction": PROCESSED_DIR / "clean_vaccine_introduction.csv",
    "vaccine_schedule": PROCESSED_DIR / "clean_vaccine_schedule.csv",
}

# Datasets produced by generate_synthetic_supplementary_data.py rather than
# fetched from a live WHO/World Bank API. Surfaced in reports and the
# notebook so findings drawn from them are labeled accordingly.
SIMULATED_DATASETS = {"vaccine_introduction", "vaccine_schedule"}

MIN_VALID_YEAR = 1974
MAX_VALID_YEAR = 2026
MIN_COVERAGE_PCT = 0.0
MAX_COVERAGE_PCT = 100.0
