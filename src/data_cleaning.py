"""Clean the raw WHO/World Bank extracts into analysis-ready tables.

Each clean_* function documents, in-line, what was wrong with the raw
column and why the chosen handling (drop / retain-as-null / coerce) was
selected instead of some other option. Every function returns the cleaned
DataFrame plus a small dict of counts, so run_pipeline() can assemble an
evidence-based data-quality report rather than a narrative one.
"""

from __future__ import annotations

import pandas as pd

from src.config import (
    MAX_COVERAGE_PCT,
    MAX_VALID_YEAR,
    MIN_COVERAGE_PCT,
    MIN_VALID_YEAR,
    PROCESSED_FILES,
)
from src.utils import get_logger, standardize_text

logger = get_logger(__name__)


def clean_coverage(df: pd.DataFrame, valid_codes: set[str]) -> tuple[pd.DataFrame, dict]:
    report = {"rows_before": len(df)}

    df = df.copy()
    for col in ["Group", "Code", "Name", "Antigen", "Coverage_category"]:
        df[col] = standardize_text(df[col])

    dupes = df.duplicated(subset=["Code", "Year", "Antigen", "Coverage_category"]).sum()
    df = df.drop_duplicates(subset=["Code", "Year", "Antigen", "Coverage_category"])
    report["duplicate_rows_removed"] = int(dupes)

    bad_year = ~df["Year"].between(MIN_VALID_YEAR, MAX_VALID_YEAR)
    report["invalid_year_rows_removed"] = int(bad_year.sum())
    df = df[~bad_year]

    # A vaccination coverage percentage outside [0, 100] is not a plausible
    # value and cannot be safely corrected, so those rows are dropped rather
    # than clipped (clipping would silently invent a value).
    bad_coverage = ~df["Coverage"].between(MIN_COVERAGE_PCT, MAX_COVERAGE_PCT)
    report["invalid_coverage_rows_removed"] = int(bad_coverage.sum())
    df = df[~bad_coverage]

    unknown_code = ~df["Code"].isin(valid_codes)
    report["unknown_country_code_rows_removed"] = int(unknown_code.sum())
    df = df[~unknown_code]

    report["rows_after"] = len(df)
    logger.info("clean_coverage: %s", report)
    return df.reset_index(drop=True), report


def clean_reported_cases(df: pd.DataFrame, valid_codes: set[str]) -> tuple[pd.DataFrame, dict]:
    report = {"rows_before": len(df)}

    df = df.copy()
    for col in ["Group", "Code", "Name", "Disease"]:
        df[col] = standardize_text(df[col])

    dupes = df.duplicated(subset=["Code", "Year", "Disease"]).sum()
    df = df.drop_duplicates(subset=["Code", "Year", "Disease"])
    report["duplicate_rows_removed"] = int(dupes)

    bad_year = ~df["Year"].between(MIN_VALID_YEAR, MAX_VALID_YEAR)
    report["invalid_year_rows_removed"] = int(bad_year.sum())
    df = df[~bad_year]

    # A negative case count is impossible and is dropped. A *missing* case
    # count means the country did not report that disease/year to WHO that
    # cycle -- it is not the same as zero cases, so it is kept as NaN
    # rather than imputed with 0 (which would understate disease burden in
    # non-reporting countries and bias trend/correlation analysis).
    negative = df["Cases"].notna() & (df["Cases"] < 0)
    report["negative_case_rows_removed"] = int(negative.sum())
    df = df[~negative]
    report["missing_cases_retained_as_null"] = int(df["Cases"].isna().sum())

    unknown_code = ~df["Code"].isin(valid_codes)
    report["unknown_country_code_rows_removed"] = int(unknown_code.sum())
    df = df[~unknown_code]

    report["rows_after"] = len(df)
    logger.info("clean_reported_cases: %s", report)
    return df.reset_index(drop=True), report


def clean_population(df: pd.DataFrame, valid_codes: set[str]) -> tuple[pd.DataFrame, dict]:
    report = {"rows_before": len(df)}
    df = df.copy()
    df["Code"] = standardize_text(df["Code"])

    dupes = df.duplicated(subset=["Code", "Year"]).sum()
    df = df.drop_duplicates(subset=["Code", "Year"])
    report["duplicate_rows_removed"] = int(dupes)

    bad_pop = df["Population"] <= 0
    report["non_positive_population_rows_removed"] = int(bad_pop.sum())
    df = df[~bad_pop]

    unknown_code = ~df["Code"].isin(valid_codes)
    report["unknown_country_code_rows_removed"] = int(unknown_code.sum())
    df = df[~unknown_code]

    report["rows_after"] = len(df)
    logger.info("clean_population: %s", report)
    return df.reset_index(drop=True), report


def derive_incidence_rate(cases_df: pd.DataFrame, population_df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Incidence rate per 100,000 population, following the standard
    epidemiological convention: cases / population * 100,000. Rows where
    Cases is missing (not reported) or population is unavailable for that
    country-year cannot yield a rate and are excluded, rather than
    treating a missing rate as zero."""
    report = {"rows_before": len(cases_df)}

    merged = cases_df.merge(population_df, on=["Code", "Year"], how="left")
    no_population = merged["Population"].isna()
    report["rows_dropped_no_population_match"] = int(no_population.sum())
    merged = merged[~no_population]

    no_cases = merged["Cases"].isna()
    report["rows_dropped_no_case_count"] = int(no_cases.sum())
    merged = merged[~no_cases]

    merged["Denominator"] = merged["Population"]
    merged["Incidence_rate"] = merged["Cases"] / merged["Population"] * 100_000

    result = merged[
        ["Group", "Code", "Name", "Year", "Disease", "Disease_description", "Denominator", "Incidence_rate"]
    ].reset_index(drop=True)
    report["rows_after"] = len(result)
    logger.info("derive_incidence_rate: %s", report)
    return result, report


def clean_vaccine_introduction(df: pd.DataFrame, valid_regions: set[str]) -> tuple[pd.DataFrame, dict]:
    report = {"rows_before": len(df)}
    df = df.copy()
    df["ISO_3_Code"] = standardize_text(df["ISO_3_Code"])
    df["WHO_Region"] = standardize_text(df["WHO_Region"])
    df["Intro"] = standardize_text(df["Intro"])

    dupes = df.duplicated(subset=["ISO_3_Code", "Vaccine_code"]).sum()
    df = df.drop_duplicates(subset=["ISO_3_Code", "Vaccine_code"])
    report["duplicate_rows_removed"] = int(dupes)

    bad_region = ~df["WHO_Region"].isin(valid_regions)
    report["invalid_who_region_rows_removed"] = int(bad_region.sum())
    df = df[~bad_region]

    # Year is legitimately missing when Intro == "No" (never introduced);
    # that is retained. A missing Year alongside Intro == "Yes" would be a
    # genuine data error and is dropped.
    inconsistent = (df["Intro"] == "YES") & df["Year"].isna()
    report["inconsistent_intro_yes_no_year_removed"] = int(inconsistent.sum())
    df = df[~inconsistent]

    report["rows_after"] = len(df)
    logger.info("clean_vaccine_introduction: %s", report)
    return df.reset_index(drop=True), report


def clean_vaccine_schedule(df: pd.DataFrame, valid_regions: set[str]) -> tuple[pd.DataFrame, dict]:
    report = {"rows_before": len(df)}
    df = df.copy()
    df["ISO_3_Code"] = standardize_text(df["ISO_3_Code"])
    df["WHO_Region"] = standardize_text(df["WHO_Region"])
    df["Vaccine_code"] = standardize_text(df["Vaccine_code"])

    dupes = df.duplicated(subset=["ISO_3_Code", "Vaccine_code", "Year"]).sum()
    df = df.drop_duplicates(subset=["ISO_3_Code", "Vaccine_code", "Year"])
    report["duplicate_rows_removed"] = int(dupes)

    bad_region = ~df["WHO_Region"].isin(valid_regions)
    report["invalid_who_region_rows_removed"] = int(bad_region.sum())
    df = df[~bad_region]

    bad_rounds = df["Schedule_rounds"] <= 0
    report["non_positive_rounds_removed"] = int(bad_rounds.sum())
    df = df[~bad_rounds]

    report["rows_after"] = len(df)
    logger.info("clean_vaccine_schedule: %s", report)
    return df.reset_index(drop=True), report


def run_pipeline() -> dict[str, dict]:
    """Load every raw file, clean it, derive incidence rate, and write the
    processed CSVs. Returns the per-dataset cleaning reports."""
    from src import data_loader

    country_ref = data_loader.load_country_reference()
    valid_codes = set(country_ref["ISO3"])
    valid_regions = {"AFR", "AMR", "SEAR", "EUR", "EMR", "WPR"}

    PROCESSED_FILES["coverage"].parent.mkdir(parents=True, exist_ok=True)

    reports = {}

    coverage, reports["coverage"] = clean_coverage(data_loader.load_coverage(), valid_codes)
    coverage.to_csv(PROCESSED_FILES["coverage"], index=False)

    cases, reports["reported_cases"] = clean_reported_cases(data_loader.load_reported_cases(), valid_codes)
    cases.to_csv(PROCESSED_FILES["reported_cases"], index=False)

    population, reports["population"] = clean_population(data_loader.load_population(), valid_codes)

    incidence, reports["incidence_rate"] = derive_incidence_rate(cases, population)
    incidence.to_csv(PROCESSED_FILES["incidence_rate"], index=False)

    intro, reports["vaccine_introduction"] = clean_vaccine_introduction(
        data_loader.load_vaccine_introduction(), valid_regions
    )
    intro.to_csv(PROCESSED_FILES["vaccine_introduction"], index=False)

    schedule, reports["vaccine_schedule"] = clean_vaccine_schedule(
        data_loader.load_vaccine_schedule(), valid_regions
    )
    schedule.to_csv(PROCESSED_FILES["vaccine_schedule"], index=False)

    return reports


if __name__ == "__main__":
    import json

    print(json.dumps(run_pipeline(), indent=2))
