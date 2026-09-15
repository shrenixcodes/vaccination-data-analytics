"""Load raw CSV files into pandas DataFrames."""

import pandas as pd

from src.config import RAW_FILES


def load_coverage() -> pd.DataFrame:
    return pd.read_csv(RAW_FILES["coverage"])


def load_reported_cases() -> pd.DataFrame:
    return pd.read_csv(RAW_FILES["reported_cases"])


def load_population() -> pd.DataFrame:
    return pd.read_csv(RAW_FILES["population"])


def load_vaccine_introduction() -> pd.DataFrame:
    return pd.read_csv(RAW_FILES["vaccine_introduction"])


def load_vaccine_schedule() -> pd.DataFrame:
    return pd.read_csv(RAW_FILES["vaccine_schedule"])


def load_country_reference() -> pd.DataFrame:
    return pd.read_csv(RAW_FILES["country_reference"])


def load_all() -> dict[str, pd.DataFrame]:
    return {
        "coverage": load_coverage(),
        "reported_cases": load_reported_cases(),
        "population": load_population(),
        "vaccine_introduction": load_vaccine_introduction(),
        "vaccine_schedule": load_vaccine_schedule(),
        "country_reference": load_country_reference(),
    }
