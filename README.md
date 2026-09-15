# Vaccination Data Analysis and Visualization

## Overview

An end-to-end public-health analytics project on WHO immunization data:
Python data ingestion and cleaning, exploratory analysis, a normalized
PostgreSQL database, SQL analytics, and a fully specified Power BI
dashboard. Three of the five datasets are fetched live from official WHO
and World Bank APIs; the other two (vaccine introduction and vaccine
schedule) are clearly-labeled simulated data, because WHO does not expose
them through any public bulk API. See [`data/README.md`](data/README.md)
for the full provenance breakdown.

## Problem Statement

Vaccination coverage and vaccine-preventable disease burden vary widely
across countries and over time. This project asks: where is coverage
lowest, how does it relate to disease incidence, how complete are
multi-dose vaccination series, and which countries are furthest from
WHO's immunization targets — using only what the available data can
actually support.

## Objectives

- Build a reproducible pipeline from raw WHO/World Bank data to
  analysis-ready tables.
- Answer the project's easy/medium analytical questions with real,
  computed figures wherever the underlying variables exist, and say so
  explicitly wherever they don't.
- Provide a normalized SQL database and a fully specified Power BI
  dashboard suitable as a portfolio piece.

## Public Health Use Cases

Supported by this project's real data (see
[`reports/public_health_insights.md`](reports/public_health_insights.md)
for the full scenario-by-scenario breakdown):
resource allocation toward low-coverage countries, tracking progress
toward the WHO 95% measles-coverage target, and comparing dose-series
completion rates. Explicitly **not** supported: demand forecasting,
gender/education/socioeconomic disparity analysis, seasonal-pattern
analysis, and age-targeted allocation beyond the infant/1-year-old cohort
— none of the required variables exist in the source data.

## Dataset

| Dataset | Status | Source |
|---|---|---|
| Vaccination coverage | Real | WHO GHO API (WUENIC estimates, 10 antigens) |
| Reported cases | Real | WHO GHO API (7 diseases) |
| Incidence rate | Real, derived | Cases (WHO) ÷ population (World Bank) × 100,000 |
| Vaccine introduction | **Simulated** | Real countries/regions/vaccines, seeded random introduction data |
| Vaccine schedule | **Simulated** | Real countries/regions/vaccines, seeded random schedule data |

Full detail: [`data/README.md`](data/README.md) ·
[`docs/data_dictionary.md`](docs/data_dictionary.md).

## Data Pipeline

```
WHO GHO API + World Bank API  ─┐
                                ├─► data/raw/*.csv ─► src/data_cleaning.py ─► data/processed/*.csv
generate_synthetic_supplementary_data.py ─┘                                        │
                                                                                     ├─► SQL database (sql/)
                                                                                     ├─► notebooks/03_eda.ipynb
                                                                                     └─► Power BI (powerbi/)
```

Full diagram and component list: [`docs/architecture.md`](docs/architecture.md).

## Data Cleaning

Documented decision-by-decision, with exact row counts, in
[`reports/data_quality_report.md`](reports/data_quality_report.md).
Headline decisions: out-of-range values are dropped (never clipped or
invented); a missing case count is kept as null, not imputed to zero,
because "not reported" and "zero cases" are not the same thing.

## Exploratory Data Analysis

[`notebooks/03_eda.ipynb`](notebooks/03_eda.ipynb) — 15 charts across
coverage, incidence, reported cases, vaccine introduction/schedule, time
series, regional comparison, and correlation analysis, with every chart
tied to a specific finding. Findings summary:
[`reports/eda_findings.md`](reports/eda_findings.md).

## SQL Database

PostgreSQL (see [`docs/database_schema.md`](docs/database_schema.md) for
why). Star-schema design: `dim_country`, `dim_disease`, `dim_antigen`,
`dim_vaccine` plus one fact table per measurement type — not a
one-table-per-CSV layout. Scripts run in order:

```bash
psql -f sql/01_create_database.sql
psql -d vaccination_analytics -f sql/02_create_tables.sql
psql -d vaccination_analytics -f sql/03_constraints.sql
psql -d vaccination_analytics -f sql/04_indexes.sql
psql -d vaccination_analytics -f sql/05_load_data.sql
```

18 analytical queries (window functions, CTEs, conditional aggregation)
in [`sql/06_analysis_queries.sql`](sql/06_analysis_queries.sql); 6
BI-facing views in [`sql/07_views.sql`](sql/07_views.sql). Query logic was
validated against the real cleaned data via an equivalent SQLite database
before being finalized in PostgreSQL syntax — see
[`docs/methodology.md`](docs/methodology.md) for why (PostgreSQL was not
available in the build environment).

## Database Architecture

Full ER diagram, grain, and constraint list:
[`docs/database_schema.md`](docs/database_schema.md).

## Power BI Dashboard

No `.pbix` file is included — Power BI Desktop was not available in the
build environment and the format has no programmatic write path (see
[`powerbi/README.md`](powerbi/README.md) for the full explanation). What
is included is everything needed to build it in under an hour:
[`powerbi/data_model.md`](powerbi/data_model.md) (star schema, matches the
SQL model), [`powerbi/dax_measures.md`](powerbi/dax_measures.md) (11
measures, each mapped to a specific requirement), and
[`powerbi/dashboard_specification.md`](powerbi/dashboard_specification.md)
(7 pages, scoped to what the data supports).

## Key Questions

Every "Easy" and "Medium" question from the project brief, answered with
real figures or marked **NOT ANSWERABLE WITH PROVIDED DATASET** with a
stated reason: [`reports/analysis_results.md`](reports/analysis_results.md).

## Key Findings

- 132 of 195 countries with 2025 MCV1 data (67.7%) are below the WHO 95%
  measles-coverage target; average shortfall 10.0 percentage points.
- MCV1 coverage and measles incidence are negatively correlated across
  country-years (Spearman r = −0.32) — an association, not proof of
  causation.
- The DTP1→DTP3 primary-series drop-off has held steady at 5–6% for 25
  years; the MCV1→MCV2 gap fell from >70% (2000) to <8% (2025) as MCV2
  programs matured globally.
- SEAR and AFR have the lowest average coverage of the 6 WHO regions
  (65.9% and 62.4% vs. 77.1% in AMR).
- DTP3 coverage shows almost no correlation with pertussis incidence
  (Spearman r = −0.035) — a genuine, reported finding worth further
  investigation, not an error.

Full list: [`reports/eda_findings.md`](reports/eda_findings.md).

## Public Health Insights

Scenario-by-scenario read (resource allocation, measles-target tracking,
polio/no-coverage research, etc.), each marked supported / partially
supported / not supported by the actual data:
[`reports/public_health_insights.md`](reports/public_health_insights.md).

## Limitations

Full discussion of what's observed vs. correlated vs. causal, every
"not answerable" question with what data would be needed, and every data
quality / geographic / temporal / methodological limitation:
[`docs/limitations.md`](docs/limitations.md).

## Tech Stack

Python (pandas, NumPy, SciPy, matplotlib, seaborn), Jupyter, pytest,
PostgreSQL, Power BI (specification only — see above).

## Project Structure

```
vaccination-data-analytics/
├── data/
│   ├── raw/          Fetched/generated raw extracts (gitignored CSVs; README documents provenance)
│   └── processed/    Cleaned, analysis-ready CSVs
├── notebooks/         01_data_audit, 02_data_cleaning, 03_eda
├── src/                Pipeline modules (fetch, generate, load, clean, validate, transform)
├── tests/              pytest coverage for cleaning/validation/transformations
├── sql/                01-07: database, schema, constraints, indexes, load, queries, views
├── powerbi/            Data model, DAX measures, dashboard spec (no .pbix — see powerbi/README.md)
├── reports/            Data quality, EDA findings, analysis results, public health insights
└── docs/                Architecture, methodology, data dictionary, database schema, limitations
```

## Installation

```bash
git clone <this-repository>
cd vaccination-data-analytics
pip install -r requirements.txt
```

## Running the Python Pipeline

```bash
python src/fetch_who_data.py                          # real data from WHO/World Bank APIs
python src/generate_synthetic_supplementary_data.py    # simulated introduction/schedule data
python -m src.data_cleaning                            # cleans + writes data/processed/
pytest                                                  # run the test suite
jupyter nbconvert --to notebook --execute notebooks/03_eda.ipynb  # re-run the EDA
```

## Running the SQL Database

```bash
psql -f sql/01_create_database.sql
psql -d vaccination_analytics -f sql/02_create_tables.sql -f sql/03_constraints.sql -f sql/04_indexes.sql
psql -d vaccination_analytics -f sql/05_load_data.sql
psql -d vaccination_analytics -f sql/06_analysis_queries.sql
psql -d vaccination_analytics -f sql/07_views.sql
```

## Power BI Setup

See [`powerbi/README.md`](powerbi/README.md) for the full reproduction
steps (connect to the 6 views in `sql/07_views.sql`, build the
relationships in `data_model.md`, add the measures in `dax_measures.md`,
build the pages in `dashboard_specification.md`).

## Reproducibility

All paths are relative to the repository root (`src/config.py`); nothing
is hard-coded to a specific machine or username. `data/raw/*.csv` is
gitignored and regenerated by the two fetch/generate scripts above, so a
fresh clone plus `pip install -r requirements.txt` is enough to rebuild
everything from scratch.

## Future Improvements

- Fetch a real vaccine-introduction and vaccine-schedule export if/when
  WHO exposes one through a bulk API, replacing the simulated versions.
- Add a land-area field to enable population-density analysis.
- Execute `sql/01`–`07` against a live PostgreSQL instance as a final
  check (validated so far via an equivalent SQLite database — see
  `docs/methodology.md`).
- Build the actual `.pbix` file in Power BI Desktop from the specification
  in `powerbi/`.

## License

[MIT](LICENSE)
