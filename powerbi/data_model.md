# Power BI Data Model

Star schema, built directly from the SQL views in `sql/07_views.sql` (or
the equivalent `data/processed/` CSVs). One dimension per real-world
entity, one fact table per measurement type — mirrors the SQL schema in
`docs/database_schema.md` so the two stay consistent.

## Tables

### Dimensions

| Table | Source | Key | Columns |
|---|---|---|---|
| `DimCountry` | `who_country_reference.csv` | `iso3` | country_name, who_region |
| `DimYear` | generated range 1974–2026 | `year` | year (no sub-year granularity exists in any source file) |
| `DimAntigen` | distinct from `clean_coverage.csv` | `antigen_code` | antigen_description |
| `DimDisease` | distinct from `clean_reported_cases.csv` | `disease_code` | disease_description |
| `DimVaccine` | distinct from `clean_vaccine_introduction.csv` + `clean_vaccine_schedule.csv` | `vaccine_code` | vaccine_description |

### Facts

| Table | Source | Status | Grain |
|---|---|---|---|
| `FactCoverage` | `clean_coverage.csv` | Real | country × year × antigen × coverage_category |
| `FactCases` | `clean_reported_cases.csv` | Real | country × year × disease |
| `FactIncidence` | `clean_incidence_rate.csv` | Real, derived | country × year × disease |
| `FactIntroduction` | `clean_vaccine_introduction.csv` | **Simulated** | country × vaccine |
| `FactSchedule` | `clean_vaccine_schedule.csv` | **Simulated** | country × vaccine × year |

## Relationships

All relationships are **one-to-many, single filter direction** (dimension
filters fact), the standard star-schema pattern — no bidirectional
filtering is needed because no fact table needs to filter another fact
table through a shared dimension in this model.

| From (1) | To (*) | Key |
|---|---|---|
| DimCountry | FactCoverage, FactCases, FactIncidence, FactIntroduction, FactSchedule | iso3 |
| DimYear | FactCoverage, FactCases, FactIncidence, FactSchedule | year |
| DimYear | FactIntroduction | year *(inactive by default — `year` is null for ~28% of rows where a vaccine was never introduced; activate with `USERELATIONSHIP` in measures that need it)* |
| DimAntigen | FactCoverage | antigen_code |
| DimDisease | FactCases, FactIncidence | disease_code |
| DimVaccine | FactIntroduction, FactSchedule | vaccine_code |

## Notes on cardinality and nulls

- `DimCountry.who_region` is null for 6 GHO entries that are not assigned
  to one of the 6 standard WHO regions (disputed territories / historical
  aggregates). Region-level visuals implicitly exclude these — documented
  in `docs/limitations.md`, not hidden.
- `FactCases.cases` and `FactIncidence` rows are null/absent respectively
  wherever a country did not report a disease/year to WHO (15.6% of case
  rows). Power BI's default `SUM`/`AVERAGE` already skip blanks correctly;
  no special handling is required, but any KPI card built on these should
  note the denominator is "reporting country-years," not "all country-years."
