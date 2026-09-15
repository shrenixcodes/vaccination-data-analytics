# Data Dictionary

Documents every field in `data/processed/`. "Source" names the raw file it
was read from (see `data/README.md` for provenance); "Transformation"
names the cleaning step, if any, applied in `src/data_cleaning.py`.

## clean_coverage.csv (real data)

| Field | Type | Nullable | Example | Source | Transformation | Meaning |
|---|---|---|---|---|---|---|
| Group | text | No | `COUNTRIES` | coverage.csv | upper-cased | Aggregation level; always COUNTRIES in this extract |
| Code | text(3) | No | `PAK` | coverage.csv | upper-cased, validated against country reference | ISO3 country code |
| Name | text | No | `PAKISTAN` | coverage.csv | upper-cased | Country name |
| Year | integer | No | `2015` | coverage.csv | range-validated [1974, 2026] | Reporting year |
| Antigen | text | No | `BCG` | coverage.csv | upper-cased | Antigen code (BCG, DTP1, DTP3, HEPB3, HIB3, IPV1, MCV1, MCV2, PCV3, ROTAC) |
| Antigen_description | text | No | `Bacille Calmette-Guerin vaccine (tuberculosis)` | coverage.csv | none | Human-readable antigen name |
| Coverage | float | No | `86.0` | coverage.csv | range-validated [0, 100] | % of the target population (typically 1-year-olds) vaccinated — WHO/UNICEF WUENIC estimate |
| Coverage_category | text | No | `WUENIC` | coverage.csv | upper-cased | Estimate methodology; constant (WUENIC) in this extract |
| Coverage_category_description | text | No | `WHO/UNICEF Estimates of National Immunization Coverage` | coverage.csv | none | Full name of the estimate methodology |

## clean_reported_cases.csv (real data)

| Field | Type | Nullable | Example | Source | Transformation | Meaning |
|---|---|---|---|---|---|---|
| Group | text | No | `COUNTRIES` | reported-cases.csv | upper-cased | Aggregation level |
| Code | text(3) | No | `TGO` | reported-cases.csv | upper-cased, validated | ISO3 country code |
| Name | text | No | `TOGO` | reported-cases.csv | upper-cased | Country name |
| Year | integer | No | `1978` | reported-cases.csv | range-validated | Reporting year |
| Disease | text | No | `DIPHTHERIA` | reported-cases.csv | upper-cased | Disease code (DIPHTHERIA, PERTUSSIS, TETANUS_TOTAL, TETANUS_NEONATAL, POLIO, RUBELLA, MEASLES) |
| Disease_description | text | No | `Diphtheria` | reported-cases.csv | none | Human-readable disease name |
| Cases | float | **Yes (15.6%)** | `0.0` | reported-cases.csv | negative values dropped; missing retained as null, not imputed | Reported case count for that country/year/disease. Null = not reported to WHO that cycle, not zero |

## clean_incidence_rate.csv (real data, derived — not a raw WHO file)

| Field | Type | Nullable | Example | Source | Transformation | Meaning |
|---|---|---|---|---|---|---|
| Group | text | No | `COUNTRIES` | derived | copied from reported_cases | Aggregation level |
| Code | text(3) | No | `PYF` | derived | — | ISO3 country code |
| Name | text | No | `FRENCH POLYNESIA` | derived | — | Country name |
| Year | integer | No | `1999` | derived | — | Reporting year |
| Disease | text | No | `DIPHTHERIA` | derived | — | Disease code |
| Disease_description | text | No | `Diphtheria` | derived | — | Human-readable disease name |
| Denominator | float | No | `236595.0` | World Bank `SP.POP.TOTL` | matched by (Code, Year) | Total population used as the incidence-rate denominator |
| Incidence_rate | float | No | `0.0` | derived | `Cases / Denominator * 100,000` | Reported cases per 100,000 population |

## clean_vaccine_introduction.csv (SIMULATED — see data/README.md)

| Field | Type | Nullable | Example | Source | Transformation | Meaning |
|---|---|---|---|---|---|---|
| ISO_3_Code | text(3) | No | `ABW` | real country reference | upper-cased | ISO3 country code |
| Country_Name | text | No | `Aruba` | real country reference | none | Country name |
| WHO_Region | text(4) | No | `AMR` | real country reference | validated against 6 known regions | WHO region code |
| Year | float | **Yes (28%)** | `NaN` | simulated | consistency-checked against Intro | Simulated introduction year; null when Intro = NO |
| Vaccine_code | text | No | `ROTA` | simulated | upper-cased | Vaccine code, matches dim_vaccine |
| Description | text | No | `Rotavirus vaccine` | simulated | none | Human-readable vaccine name |
| Intro | text | No | `NO` | simulated | upper-cased | Whether the vaccine is simulated as introduced (YES/NO) |

## clean_vaccine_schedule.csv (SIMULATED — see data/README.md)

| Field | Type | Nullable | Example | Source | Transformation | Meaning |
|---|---|---|---|---|---|---|
| ISO_3_Code | text(3) | No | `ABW` | real country reference | upper-cased | ISO3 country code |
| Country_Name | text | No | `Aruba` | real country reference | none | Country name |
| WHO_Region | text(4) | No | `AMR` | real country reference | validated | WHO region code |
| Year | integer | No | `2023` | simulated | fixed at 2023 (snapshot, not a time series) | Schedule reference year |
| Vaccine_code | text | No | `BCG` | simulated | upper-cased | Vaccine code |
| Vaccine_description | text | No | `Bacille Calmette-Guerin vaccine` | simulated | none | Human-readable vaccine name |
| Schedule_rounds | integer | No | `1` | simulated | validated > 0 | Number of doses in the routine schedule |
| Target_pop | text | No | `INFANTS` | simulated | none | Target population category |
| Target_pop_description | text | No | `Infants` | simulated | none | Human-readable target population |
| Geoarea | text | No | `NATIONWIDE` | simulated | none | Geographic scope of the schedule (always NATIONWIDE in this extract) |
| Age_administered | text | No | `AT BIRTH` | simulated | none | Semicolon-separated ages/timing for each round |
| Source_comment | text | No | `WHO/UNICEF Joint Reporting Form on Immunization` | simulated | none | Attribution string (constant placeholder text) |
