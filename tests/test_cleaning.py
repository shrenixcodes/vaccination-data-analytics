import pandas as pd

from src.data_cleaning import (
    clean_coverage,
    clean_reported_cases,
    clean_vaccine_introduction,
    derive_incidence_rate,
)

VALID_CODES = {"AFG", "IND"}
VALID_REGIONS = {"AFR", "AMR", "SEAR", "EUR", "EMR", "WPR"}


def _coverage_row(**overrides):
    row = {
        "Group": "COUNTRIES",
        "Code": "AFG",
        "Name": "Afghanistan",
        "Year": 2020,
        "Antigen": "BCG",
        "Antigen_description": "BCG vaccine",
        "Coverage": 80.0,
        "Coverage_category": "WUENIC",
        "Coverage_category_description": "estimate",
    }
    row.update(overrides)
    return row


def test_clean_coverage_drops_out_of_range_percentage():
    df = pd.DataFrame([_coverage_row(), _coverage_row(Antigen="DTP3", Coverage=150.0)])
    cleaned, report = clean_coverage(df, VALID_CODES)
    assert len(cleaned) == 1
    assert report["invalid_coverage_rows_removed"] == 1


def test_clean_coverage_drops_unknown_country_code():
    df = pd.DataFrame([_coverage_row(), _coverage_row(Code="ZZZ")])
    cleaned, report = clean_coverage(df, VALID_CODES)
    assert len(cleaned) == 1
    assert report["unknown_country_code_rows_removed"] == 1


def test_clean_coverage_drops_exact_duplicates():
    df = pd.DataFrame([_coverage_row(), _coverage_row()])
    cleaned, report = clean_coverage(df, VALID_CODES)
    assert len(cleaned) == 1
    assert report["duplicate_rows_removed"] == 1


def test_clean_reported_cases_retains_missing_as_null_not_zero():
    df = pd.DataFrame(
        [
            {
                "Group": "COUNTRIES", "Code": "AFG", "Name": "Afghanistan",
                "Year": 2020, "Disease": "MEASLES", "Disease_description": "Measles",
                "Cases": None,
            }
        ]
    )
    cleaned, report = clean_reported_cases(df, VALID_CODES)
    assert len(cleaned) == 1
    assert pd.isna(cleaned.loc[0, "Cases"])
    assert report["missing_cases_retained_as_null"] == 1


def test_clean_reported_cases_drops_negative_counts():
    df = pd.DataFrame(
        [
            {
                "Group": "COUNTRIES", "Code": "AFG", "Name": "Afghanistan",
                "Year": 2020, "Disease": "MEASLES", "Disease_description": "Measles",
                "Cases": -5,
            }
        ]
    )
    cleaned, report = clean_reported_cases(df, VALID_CODES)
    assert len(cleaned) == 0
    assert report["negative_case_rows_removed"] == 1


def test_derive_incidence_rate_formula():
    cases = pd.DataFrame(
        [
            {
                "Group": "COUNTRIES", "Code": "AFG", "Name": "Afghanistan",
                "Year": 2020, "Disease": "MEASLES", "Disease_description": "Measles",
                "Cases": 100.0,
            }
        ]
    )
    population = pd.DataFrame([{"Code": "AFG", "Year": 2020, "Population": 1_000_000.0}])
    result, report = derive_incidence_rate(cases, population)
    assert len(result) == 1
    assert result.loc[0, "Incidence_rate"] == 10.0  # 100 / 1,000,000 * 100,000
    assert report["rows_dropped_no_population_match"] == 0


def test_clean_vaccine_introduction_drops_inconsistent_yes_with_no_year():
    df = pd.DataFrame(
        [
            {
                "ISO_3_Code": "AFG", "Country_Name": "Afghanistan", "WHO_Region": "EMR",
                "Year": None, "Description": "Rotavirus vaccine", "Intro": "Yes",
            }
        ]
    )
    cleaned, report = clean_vaccine_introduction(df, VALID_REGIONS)
    assert len(cleaned) == 0
    assert report["inconsistent_intro_yes_no_year_removed"] == 1
