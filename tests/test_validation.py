import pandas as pd

from src.validation import (
    validate_coverage,
    validate_incidence_rate,
    validate_reported_cases,
    validate_vaccine_introduction,
    validate_vaccine_schedule,
)


def test_validate_coverage_passes_on_clean_data():
    df = pd.DataFrame(
        [
            {
                "Group": "COUNTRIES", "Code": "AFG", "Name": "Afghanistan", "Year": 2020,
                "Antigen": "BCG", "Antigen_description": "BCG vaccine", "Coverage": 80.0,
                "Coverage_category": "WUENIC", "Coverage_category_description": "estimate",
            }
        ]
    )
    df["Year"] = df["Year"].astype("int64")
    assert validate_coverage(df) == []


def test_validate_coverage_flags_out_of_range_value():
    df = pd.DataFrame(
        [
            {
                "Group": "COUNTRIES", "Code": "AFG", "Name": "Afghanistan", "Year": 2020,
                "Antigen": "BCG", "Antigen_description": "BCG vaccine", "Coverage": 120.0,
                "Coverage_category": "WUENIC", "Coverage_category_description": "estimate",
            }
        ]
    )
    df["Year"] = df["Year"].astype("int64")
    problems = validate_coverage(df)
    assert any("Coverage values" in p for p in problems)


def test_validate_coverage_flags_missing_columns():
    df = pd.DataFrame([{"Code": "AFG"}])
    problems = validate_coverage(df)
    assert any("missing required columns" in p for p in problems)


def test_validate_reported_cases_flags_negative_cases():
    df = pd.DataFrame(
        [
            {
                "Group": "COUNTRIES", "Code": "AFG", "Name": "Afghanistan", "Year": 2020,
                "Disease": "MEASLES", "Disease_description": "Measles", "Cases": -1.0,
            }
        ]
    )
    problems = validate_reported_cases(df)
    assert any("negative Cases" in p for p in problems)


def test_validate_incidence_rate_flags_non_positive_denominator():
    df = pd.DataFrame(
        [
            {
                "Group": "COUNTRIES", "Code": "AFG", "Name": "Afghanistan", "Year": 2020,
                "Disease": "MEASLES", "Disease_description": "Measles",
                "Denominator": 0.0, "Incidence_rate": 10.0,
            }
        ]
    )
    problems = validate_incidence_rate(df)
    assert any("Denominator" in p for p in problems)


def test_validate_vaccine_introduction_flags_bad_region():
    df = pd.DataFrame(
        [
            {
                "ISO_3_Code": "AFG", "Country_Name": "Afghanistan", "WHO_Region": "ZZZ",
                "Year": 2015.0, "Description": "Rotavirus vaccine", "Intro": "YES",
            }
        ]
    )
    problems = validate_vaccine_introduction(df)
    assert any("WHO_Region" in p for p in problems)


def test_validate_vaccine_schedule_flags_non_positive_rounds():
    df = pd.DataFrame(
        [
            {
                "ISO_3_Code": "AFG", "Country_Name": "Afghanistan", "WHO_Region": "EMR",
                "Year": 2023, "Vaccine_code": "BCG", "Vaccine_description": "BCG vaccine",
                "Schedule_rounds": 0, "Target_pop": "INFANTS",
                "Target_pop_description": "Infants", "Geoarea": "NATIONWIDE",
                "Age_administered": "AT BIRTH", "Source_comment": "JRF",
            }
        ]
    )
    problems = validate_vaccine_schedule(df)
    assert any("Schedule_rounds" in p for p in problems)
