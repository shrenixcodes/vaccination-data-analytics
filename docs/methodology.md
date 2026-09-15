# Methodology

## Data ingestion

Three of the five project datasets are fetched live from official public
APIs by `src/fetch_who_data.py`:

- **Coverage** and **reported cases**: WHO Global Health Observatory (GHO)
  OData API (`https://ghoapi.azureedge.net/api/`), querying specific
  indicator codes (e.g. `WHS4_100` for DTP3 coverage, `WHS3_62` for
  measles cases) filtered to `SpatialDimType eq 'COUNTRY'`.
- **Population** (used only as the incidence-rate denominator, not one of
  the 5 brief datasets itself): World Bank Open Data API, indicator
  `SP.POP.TOTL`.

The remaining two — **vaccine introduction** and **vaccine schedule** —
have no public bulk-download API (WHO exposes them only through the
interactive WIISE portal at immunizationdata.who.int). They are produced
by `src/generate_synthetic_supplementary_data.py` using real
country/ISO3/WHO-region/vaccine facts and a seeded random process
(seed=42) for the numeric content. This is disclosed throughout the repo,
not just here.

## Cleaning

`src/data_cleaning.py` applies one `clean_*` function per dataset. Every
decision (drop vs. retain-as-null vs. coerce) is documented in-line in
that file and summarized with exact row counts in
`reports/data_quality_report.md`. The general principles applied:

- A value outside its physically possible range (coverage > 100%, negative
  case count) is dropped, never clipped or corrected, since a corrected
  value would be invented.
- A *missing* value is kept as null, not imputed, when "missing" has a
  real-world meaning distinct from zero (a country not reporting a
  disease/year is not the same as zero cases).
- Deduplication uses each table's natural key (e.g. country + year +
  antigen + estimate type for coverage), not a full-row `drop_duplicates`,
  so two differing observations for the same real-world fact are not
  silently treated as one being a duplicate of the other.

## Validation

`src/validation.py` provides one `validate_*` function per cleaned
dataset, each returning a list of problem strings (empty = passed). These
are exercised both by `tests/test_validation.py` (pytest) and available
for ad hoc use against any future re-run of the pipeline.

## Transformation

`src/transformations.py` centralizes the statistical/analytical formulas
used by both the notebook and the reports (dose drop-off, year-over-year
change, coverage gap to target, Pearson/Spearman correlation, pre/post
comparison, regional averages, country ranking), so the same formula is
never re-implemented differently in two places.

## Exploratory data analysis

`notebooks/03_eda.ipynb` follows a fixed structure (dataset overview →
data quality → descriptive statistics → coverage analysis → incidence
analysis → reported-cases analysis → vaccine-introduction analysis →
vaccine-schedule analysis → time series → country/region comparison →
correlation → key findings → limitations), executed end-to-end with real
output captured in the committed notebook (no hand-edited outputs).

## SQL modeling

The database (`sql/`) uses a star-schema-style design: one dimension
table per real-world entity shared across multiple raw files
(`dim_country`, `dim_disease`, `dim_antigen`, `dim_vaccine`) and one fact
table per measurement type (`fact_coverage`, `fact_reported_cases`,
`fact_incidence_rate`, `fact_vaccine_introduction`,
`fact_vaccine_schedule`). This was chosen over a naive one-table-per-CSV
layout because four of the five raw files repeat the same country
name/region/description columns — normalizing those into `dim_country`
removes that repetition and gives every fact table a single, consistent
join key. See `docs/database_schema.md` for full detail.

## Analytical queries

`sql/06_analysis_queries.sql` contains 18 queries using CTEs, window
functions (`RANK`, `LAG`), conditional aggregation (`FILTER`, `CASE`), and
joins across the star schema. Query logic was validated by loading the
real cleaned CSVs into an equivalent SQLite schema and confirming each
query's output against the data before finalizing the PostgreSQL syntax
(PostgreSQL itself was not available in the build environment — see
`docs/limitations.md`).

## Power BI model

`powerbi/data_model.md` mirrors the SQL star schema exactly, so the two
representations of the data never diverge. `powerbi/dax_measures.md`
defines a small set of measures (11), each mapped to a specific brief
requirement rather than added for volume.

## Visualization strategy

Every chart in the notebook and every dashboard page in
`powerbi/dashboard_specification.md` is chosen to answer a specific brief
question, not for coverage of "chart types." Log scales are used only
where the underlying values span orders of magnitude (incidence rates
across diseases); correlation results are always reported with both
Pearson and Spearman coefficients since several relationships in this
domain are monotonic without being linear.

## Interpretation methodology

Every correlation or trend finding in `reports/` is phrased as
association ("X is negatively correlated with Y", "Y declined following
X"), never as causation, and each notes the specific confounders this
dataset cannot control for. See `docs/limitations.md` for the full
causal-inference discussion.
