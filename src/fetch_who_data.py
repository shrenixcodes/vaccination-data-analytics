"""Download real immunization coverage, reported-case, and population data
from the WHO Global Health Observatory (GHO) OData API and write them to
data/raw/ in the long format described in the project brief.

The GHO API (https://ghoapi.azureedge.net/api/) is WHO's official
programmatic data source. It does not expose vaccine introduction or
vaccine schedule data as queryable indicators (those live only in the
interactive WIISE portal), so those two datasets are produced separately
by generate_synthetic_supplementary_data.py and are clearly labeled as
simulated.

Run:
    python src/fetch_who_data.py
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import requests

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
GHO_BASE = "https://ghoapi.azureedge.net/api"

# WHO/UNICEF Estimates of National Immunization Coverage (WUENIC) indicators.
COVERAGE_INDICATORS = {
    "WHS4_543": ("BCG", "Bacille Calmette-Guerin vaccine (tuberculosis)"),
    "VACCINECOVERAGE_DTP1": ("DTP1", "Diphtheria tetanus toxoid and pertussis, 1st dose"),
    "WHS4_100": ("DTP3", "Diphtheria tetanus toxoid and pertussis, 3rd dose"),
    "WHS4_117": ("HEPB3", "Hepatitis B vaccine, 3rd dose"),
    "WHS4_129": ("HIB3", "Haemophilus influenzae type B vaccine, 3rd dose"),
    "WHS4_544": ("IPV1", "Inactivated polio vaccine, 1st dose"),
    "WHS8_110": ("MCV1", "Measles-containing vaccine, 1st dose"),
    "MCV2": ("MCV2", "Measles-containing vaccine, 2nd dose"),
    "PCV3": ("PCV3", "Pneumococcal conjugate vaccine, 3rd dose"),
    "ROTAC": ("ROTAC", "Rotavirus vaccine, completed series"),
}

# WHO reported-case counts for vaccine-preventable diseases.
REPORTED_CASES_INDICATORS = {
    "WHS3_41": ("DIPHTHERIA", "Diphtheria"),
    "WHS3_43": ("PERTUSSIS", "Pertussis"),
    "WHS3_46": ("TETANUS_TOTAL", "Total tetanus"),
    "WHS3_56": ("TETANUS_NEONATAL", "Neonatal tetanus"),
    "WHS3_49": ("POLIO", "Poliomyelitis"),
    "WHS3_57": ("RUBELLA", "Rubella"),
    "WHS3_62": ("MEASLES", "Measles"),
}

WORLD_BANK_POP_URL = (
    "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL"
    "?format=json&per_page=20000&date=1980:2024"
)


def _fetch_indicator(code: str) -> pd.DataFrame:
    """Fetch every country-level, year-level record for one GHO indicator."""
    url = f"{GHO_BASE}/{code}?$filter=SpatialDimType eq 'COUNTRY'"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    records = resp.json()["value"]
    return pd.DataFrame.from_records(records)


def _fetch_dimension_values(dimension: str) -> pd.DataFrame:
    url = f"{GHO_BASE}/DIMENSION/{dimension}/DimensionValues"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return pd.DataFrame.from_records(resp.json()["value"])


def fetch_country_reference() -> pd.DataFrame:
    """Country code -> country name -> parent WHO region, from GHO dimensions."""
    countries = _fetch_dimension_values("COUNTRY")[["Code", "Title", "ParentCode"]]
    countries = countries.rename(
        columns={"Code": "ISO3", "Title": "Country_Name", "ParentCode": "WHO_Region"}
    )
    return countries


def build_coverage_csv(country_ref: pd.DataFrame) -> None:
    frames = []
    for indicator_code, (antigen, description) in COVERAGE_INDICATORS.items():
        print(f"  fetching coverage indicator {indicator_code} ({antigen})")
        df = _fetch_indicator(indicator_code)
        if df.empty:
            continue
        df = df[["SpatialDim", "TimeDim", "NumericValue"]].copy()
        df["Antigen"] = antigen
        df["Antigen_description"] = description
        frames.append(df)
        time.sleep(0.2)

    coverage = pd.concat(frames, ignore_index=True)
    coverage = coverage.rename(
        columns={"SpatialDim": "Code", "TimeDim": "Year", "NumericValue": "Coverage"}
    )
    coverage["Group"] = "COUNTRIES"
    coverage = coverage.merge(
        country_ref[["ISO3", "Country_Name"]],
        left_on="Code",
        right_on="ISO3",
        how="left",
    ).rename(columns={"Country_Name": "Name"})
    coverage = coverage[
        ["Group", "Code", "Name", "Year", "Antigen", "Antigen_description", "Coverage"]
    ]
    coverage["Coverage_category"] = "WUENIC"
    coverage["Coverage_category_description"] = (
        "WHO/UNICEF Estimates of National Immunization Coverage"
    )
    out_path = RAW_DIR / "coverage.csv"
    coverage.to_csv(out_path, index=False)
    print(f"  wrote {out_path} ({len(coverage)} rows)")


def build_reported_cases_csv(country_ref: pd.DataFrame) -> None:
    frames = []
    for indicator_code, (disease, description) in REPORTED_CASES_INDICATORS.items():
        print(f"  fetching reported-cases indicator {indicator_code} ({disease})")
        df = _fetch_indicator(indicator_code)
        if df.empty:
            continue
        df = df[["SpatialDim", "TimeDim", "NumericValue"]].copy()
        df["Disease"] = disease
        df["Disease_description"] = description
        frames.append(df)
        time.sleep(0.2)

    cases = pd.concat(frames, ignore_index=True)
    cases = cases.rename(
        columns={"SpatialDim": "Code", "TimeDim": "Year", "NumericValue": "Cases"}
    )
    cases["Group"] = "COUNTRIES"
    cases = cases.merge(
        country_ref[["ISO3", "Country_Name"]],
        left_on="Code",
        right_on="ISO3",
        how="left",
    ).rename(columns={"Country_Name": "Name"})
    cases = cases[["Group", "Code", "Name", "Year", "Disease", "Disease_description", "Cases"]]
    out_path = RAW_DIR / "reported-cases.csv"
    cases.to_csv(out_path, index=False)
    print(f"  wrote {out_path} ({len(cases)} rows)")


def build_population_csv(country_ref: pd.DataFrame) -> None:
    """World Bank total-population series, used as the incidence-rate
    denominator (the GHO population indicator WHS9_86 is unpopulated at
    country level as of 2026)."""
    print("  fetching World Bank population indicator SP.POP.TOTL")
    records: list[dict] = []
    page = 1
    while True:
        resp = requests.get(f"{WORLD_BANK_POP_URL}&page={page}", timeout=60)
        resp.raise_for_status()
        meta, data = resp.json()
        if not data:
            break
        records.extend(data)
        if page >= meta["pages"]:
            break
        page += 1

    df = pd.DataFrame.from_records(records)
    df = df[["countryiso3code", "date", "value"]].rename(
        columns={"countryiso3code": "Code", "date": "Year", "value": "Population"}
    )
    # World Bank includes region/income-group aggregates (e.g. AFE, WLD, EAS)
    # alongside real countries; keep only codes WHO also recognizes as countries.
    df = df[df["Code"].isin(country_ref["ISO3"])]
    df["Year"] = df["Year"].astype(int)
    df = df.dropna(subset=["Population"])
    out_path = RAW_DIR / "population.csv"
    df.to_csv(out_path, index=False)
    print(f"  wrote {out_path} ({len(df)} rows)")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print("Fetching country reference dimensions...")
    country_ref = fetch_country_reference()
    country_ref.to_csv(RAW_DIR / "who_country_reference.csv", index=False)

    print("Building coverage.csv...")
    build_coverage_csv(country_ref)

    print("Building reported-cases.csv...")
    build_reported_cases_csv(country_ref)

    print("Building population.csv (used to derive incidence rate)...")
    build_population_csv(country_ref)

    print("Done.")


if __name__ == "__main__":
    main()
