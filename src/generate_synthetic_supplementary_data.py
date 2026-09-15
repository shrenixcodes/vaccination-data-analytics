"""Generate the vaccine-introduction and vaccine-schedule datasets.

WHO publishes these two datasets only through the interactive WIISE portal
(immunizationdata.who.int), which has no public bulk-download API. Unlike
coverage.csv, reported-cases.csv, and population.csv (all fetched from the
real WHO GHO / World Bank APIs by fetch_who_data.py), these two files are
SIMULATED: real country lists, real WHO region assignments, and real
vaccine names are combined with a seeded random process to produce
plausible introduction years and schedule details.

This is disclosed throughout the repository (README, data dictionary,
limitations). Do not treat vaccine-introduction.csv or
vaccine-schedule-data.csv as authoritative WHO figures.

Run:
    python src/generate_synthetic_supplementary_data.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
SEED = 42

# (vaccine_code, full description, WHO regions where it is part of typical
# programming; None = offered everywhere)
VACCINES = [
    ("ROTA", "Rotavirus vaccine", None),
    ("PCV", "Pneumococcal conjugate vaccine", None),
    ("HPV", "Human papillomavirus vaccine", None),
    ("HEPB_BD", "Hepatitis B birth dose", None),
    ("IPV", "Inactivated polio vaccine", None),
    ("MENA", "Meningococcal A conjugate vaccine", {"AFR"}),
    ("JE", "Japanese encephalitis vaccine", {"SEAR", "WPR"}),
    ("YF", "Yellow fever vaccine", {"AFR", "AMR"}),
    ("RCV1", "Rubella-containing vaccine, 1st dose", None),
]

# vaccine_code, description, typical rounds, target population, ages administered
SCHEDULE_VACCINES = [
    ("BCG", "Bacille Calmette-Guerin vaccine", 1, "INFANTS", "AT BIRTH"),
    ("DTP", "Diphtheria-tetanus-pertussis vaccine", 3, "INFANTS", "6 WEEKS;10 WEEKS;14 WEEKS"),
    ("OPV", "Oral polio vaccine", 4, "INFANTS", "AT BIRTH;6 WEEKS;10 WEEKS;14 WEEKS"),
    ("MCV", "Measles-containing vaccine", 2, "INFANTS;CHILDREN", "9 MONTHS;18 MONTHS"),
    ("HEPB", "Hepatitis B vaccine", 3, "INFANTS", "6 WEEKS;10 WEEKS;14 WEEKS"),
    ("HIB", "Haemophilus influenzae type b vaccine", 3, "INFANTS", "6 WEEKS;10 WEEKS;14 WEEKS"),
    ("PCV", "Pneumococcal conjugate vaccine", 3, "INFANTS", "6 WEEKS;10 WEEKS;14 WEEKS"),
    ("ROTA", "Rotavirus vaccine", 2, "INFANTS", "6 WEEKS;10 WEEKS"),
]

INTRO_YEAR_MIN, INTRO_YEAR_MAX = 2000, 2023


def load_country_reference() -> pd.DataFrame:
    ref = pd.read_csv(RAW_DIR / "who_country_reference.csv")
    return ref.dropna(subset=["WHO_Region"]).reset_index(drop=True)


def build_vaccine_introduction(country_ref: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for _, country in country_ref.iterrows():
        for code, description, eligible_regions in VACCINES:
            if eligible_regions is not None and country["WHO_Region"] not in eligible_regions:
                continue
            introduced = rng.random() < 0.72
            year = int(rng.integers(INTRO_YEAR_MIN, INTRO_YEAR_MAX + 1)) if introduced else np.nan
            rows.append(
                {
                    "ISO_3_Code": country["ISO3"],
                    "Country_Name": country["Country_Name"],
                    "WHO_Region": country["WHO_Region"],
                    "Year": year,
                    "Vaccine_code": code,
                    "Description": description,
                    "Intro": "Yes" if introduced else "No",
                }
            )
    return pd.DataFrame(rows)


def build_vaccine_schedule(country_ref: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for _, country in country_ref.iterrows():
        for code, description, base_rounds, target_pop, base_ages in SCHEDULE_VACCINES:
            # Most countries follow the WHO-recommended schedule; a minority
            # run a reduced-dose schedule (rounds - 1).
            rounds = base_rounds if rng.random() < 0.85 else max(1, base_rounds - 1)
            ages = ";".join(base_ages.split(";")[:rounds]) if rounds <= base_rounds else base_ages
            rows.append(
                {
                    "ISO_3_Code": country["ISO3"],
                    "Country_Name": country["Country_Name"],
                    "WHO_Region": country["WHO_Region"],
                    "Year": 2023,
                    "Vaccine_code": code,
                    "Vaccine_description": description,
                    "Schedule_rounds": rounds,
                    "Target_pop": target_pop,
                    "Target_pop_description": target_pop.replace(";", " and ").title(),
                    "Geoarea": "NATIONWIDE",
                    "Age_administered": ages,
                    "Source_comment": "WHO/UNICEF Joint Reporting Form on Immunization",
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    rng = np.random.default_rng(SEED)
    country_ref = load_country_reference()

    intro = build_vaccine_introduction(country_ref, rng)
    intro_path = RAW_DIR / "vaccine-introduction.csv"
    intro.to_csv(intro_path, index=False)
    print(f"wrote {intro_path} ({len(intro)} rows) [SIMULATED]")

    schedule = build_vaccine_schedule(country_ref, rng)
    schedule_path = RAW_DIR / "vaccine-schedule-data.csv"
    schedule.to_csv(schedule_path, index=False)
    print(f"wrote {schedule_path} ({len(schedule)} rows) [SIMULATED]")


if __name__ == "__main__":
    main()
