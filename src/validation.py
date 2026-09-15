"""Post-cleaning validation checks.

Each function returns a list of human-readable problem strings (empty list
= passed). They are used both by pytest (tests/test_validation.py) and by
the data-quality report to give evidence-based, checkable claims instead
of narrative ones.
"""

from __future__ import annotations

import pandas as pd

REQUIRED_COVERAGE_COLUMNS = {
    "Group", "Code", "Name", "Year", "Antigen", "Antigen_description",
    "Coverage", "Coverage_category", "Coverage_category_description",
}
REQUIRED_CASES_COLUMNS = {
    "Group", "Code", "Name", "Year", "Disease", "Disease_description", "Cases",
}
REQUIRED_INCIDENCE_COLUMNS = {
    "Group", "Code", "Name", "Year", "Disease", "Disease_description",
    "Denominator", "Incidence_rate",
}
REQUIRED_INTRO_COLUMNS = {
    "ISO_3_Code", "Country_Name", "WHO_Region", "Year", "Description", "Intro",
}
REQUIRED_SCHEDULE_COLUMNS = {
    "ISO_3_Code", "Country_Name", "WHO_Region", "Year", "Vaccine_code",
    "Vaccine_description", "Schedule_rounds", "Target_pop",
    "Target_pop_description", "Geoarea", "Age_administered", "Source_comment",
}

VALID_WHO_REGIONS = {"AFR", "AMR", "SEAR", "EUR", "EMR", "WPR"}


def _check_schema(df: pd.DataFrame, required: set[str]) -> list[str]:
    missing = required - set(df.columns)
    return [f"missing required columns: {sorted(missing)}"] if missing else []


def validate_coverage(df: pd.DataFrame) -> list[str]:
    problems = _check_schema(df, REQUIRED_COVERAGE_COLUMNS)
    if problems:
        return problems
    if df.duplicated(subset=["Code", "Year", "Antigen", "Coverage_category"]).any():
        problems.append("duplicate Code/Year/Antigen/Coverage_category rows present")
    if not df["Coverage"].between(0, 100).all():
        problems.append("Coverage values outside [0, 100] present")
    if df["Code"].isna().any() or df["Year"].isna().any():
        problems.append("null Code or Year present")
    if not pd.api.types.is_integer_dtype(df["Year"]):
        problems.append("Year is not an integer dtype")
    return problems


def validate_reported_cases(df: pd.DataFrame) -> list[str]:
    problems = _check_schema(df, REQUIRED_CASES_COLUMNS)
    if problems:
        return problems
    if df.duplicated(subset=["Code", "Year", "Disease"]).any():
        problems.append("duplicate Code/Year/Disease rows present")
    if (df["Cases"].dropna() < 0).any():
        problems.append("negative Cases values present")
    return problems


def validate_incidence_rate(df: pd.DataFrame) -> list[str]:
    problems = _check_schema(df, REQUIRED_INCIDENCE_COLUMNS)
    if problems:
        return problems
    if (df["Incidence_rate"] < 0).any():
        problems.append("negative Incidence_rate values present")
    if (df["Denominator"] <= 0).any():
        problems.append("non-positive Denominator values present")
    if df["Incidence_rate"].isna().any():
        problems.append("null Incidence_rate values present")
    return problems


def validate_vaccine_introduction(df: pd.DataFrame) -> list[str]:
    problems = _check_schema(df, REQUIRED_INTRO_COLUMNS)
    if problems:
        return problems
    if not df["WHO_Region"].isin(VALID_WHO_REGIONS).all():
        problems.append("WHO_Region values outside the 6 recognized regions")
    bad = (df["Intro"] == "YES") & df["Year"].isna()
    if bad.any():
        problems.append("rows with Intro == YES but null Year")
    return problems


def validate_vaccine_schedule(df: pd.DataFrame) -> list[str]:
    problems = _check_schema(df, REQUIRED_SCHEDULE_COLUMNS)
    if problems:
        return problems
    if not df["WHO_Region"].isin(VALID_WHO_REGIONS).all():
        problems.append("WHO_Region values outside the 6 recognized regions")
    if (df["Schedule_rounds"] <= 0).any():
        problems.append("non-positive Schedule_rounds present")
    return problems


def validate_all(datasets: dict[str, pd.DataFrame]) -> dict[str, list[str]]:
    validators = {
        "coverage": validate_coverage,
        "reported_cases": validate_reported_cases,
        "incidence_rate": validate_incidence_rate,
        "vaccine_introduction": validate_vaccine_introduction,
        "vaccine_schedule": validate_vaccine_schedule,
    }
    return {name: fn(datasets[name]) for name, fn in validators.items() if name in datasets}
