# Limitations

## What this project's data directly shows

- National-level annual vaccination coverage (% of target population,
  typically 1-year-olds) for 10 antigens, 2000–2025, for up to 195
  countries, from WHO's WUENIC methodology.
- National-level annual reported case counts for 7 vaccine-preventable
  diseases, 1974–2025, for up to 214 countries, as submitted to WHO.
- A derived incidence rate (cases per 100,000 population) computed from
  the above case counts and World Bank population totals.

## What is correlated / observed (not causal)

- Higher MCV1 coverage is associated with lower measles incidence across
  country-years (Spearman r = −0.32). This is consistent with, but does
  not prove, vaccination's protective effect — surveillance capacity,
  healthcare access, and outbreak dynamics are confounders present in the
  real world but absent from this dataset, so they cannot be statistically
  controlled for here.
- Incidence rates for all 7 tracked diseases declined substantially over
  their observed history, the same period vaccination programs expanded.
  This is a temporal co-occurrence, not a controlled before/after study.
- DTP3 coverage shows only a very weak association with pertussis
  incidence (Spearman r = −0.035). This is a genuine, reported finding,
  not an error — but this dataset cannot explain *why* (candidate
  real-world explanations include waning vaccine-induced immunity and
  changes in case surveillance/definition over time; testing either
  requires data this project does not have).

## What cannot be concluded

- **Causation.** No dataset here includes a control group, a randomized
  or quasi-experimental design, or individual-level records, so no
  finding in this project should be read as "vaccination caused X."
- **Sub-national patterns.** Every figure is a national aggregate; a
  country's national coverage can mask large within-country disparities
  this data cannot reveal.
- **Individual risk.** National-average coverage says nothing about
  whether any specific unvaccinated individual or subgroup is
  responsible for a specific outbreak.

## Questions not answerable with the provided data

| Question | Missing variable | What would be needed |
|---|---|---|
| Gender differences in vaccination rates | Sex/gender field | Sex-disaggregated coverage records (e.g. DHS/MICS survey) |
| Education-level impact on vaccination | Education field | Survey linking caregiver education to child vaccination status |
| Urban vs. rural vaccination difference | Residence classification | Sub-national survey data with an urban/rural field |
| Seasonal vaccination patterns | Sub-annual date granularity | Monthly/quarterly vaccination-administration records |
| Population-density relationship | Land area | A land-area field (e.g. World Bank `AG.SRF.TOTL.K2`, not fetched into this project) to compute density from the population data already present |
| Socioeconomic/income disparities | Income or wealth-quintile field | Household survey with wealth-quintile data |
| Vaccine availability/supply-driven low coverage | Stock/supply-chain data | Doses shipped, cold-chain capacity, or stockout records |
| Vaccine-introduction correlation with case decline | Real introduction-timing data | A real WIISE-portal export of vaccine-introduction.csv (this project's copy is simulated) |
| Schedule/booster impact on coverage | Real schedule data | A real WIISE-portal export of vaccine-schedule-data.csv (this project's copy is simulated) |

## Data quality limitations

- 15.6% of reported-cases rows have no case count (retained as null, not
  imputed) — see `reports/data_quality_report.md` for the reasoning.
  Any total/average computed from `Cases` implicitly excludes
  non-reporting country-years, which can understate burden in countries
  with weaker surveillance rather than genuinely lower incidence; this
  dataset cannot distinguish the two.
- Coverage (195 countries) and reported cases (214 countries) do not
  cover identical country sets, since not every country reports every
  indicator to WHO. Any cross-dataset join implicitly restricts to the
  intersection.
- 6 GHO spatial entities have no assigned WHO region (disputed
  territories / historical aggregates) and are excluded from every
  region-level aggregate in this project.

## Geographic limitations

- Country-level (national) only — no sub-national (state/province)
  breakdown exists anywhere in the 5 datasets.
- 195–228 countries/territories depending on dataset, not a fixed
  universal set — see the country-count differences noted above.

## Temporal limitations

- Coverage: 2000–2025. Reported cases: 1974–2025 (longer history, since
  disease surveillance predates the WUENIC coverage methodology).
  Comparisons across the two are implicitly restricted to their
  overlapping years.
- Annual granularity only. No month/quarter/week data exists, ruling out
  any seasonality analysis.
- The most recent 1–2 years in any WHO dataset are typically provisional
  and subject to revision in WHO's own future updates; this project used
  a live snapshot fetched at build time.

## Methodological limitations

- **Vaccine introduction and vaccine schedule datasets are simulated**
  (see `data/README.md`, `docs/data_dictionary.md`). Every report and
  the notebook labels findings drawn from them accordingly; they are
  excluded from `reports/eda_findings.md`'s numbered key findings for
  exactly this reason.
- **The SQL schema and queries were validated against real data via an
  equivalent SQLite database, not executed against a live PostgreSQL
  server** (PostgreSQL was not available in the build environment) — see
  `docs/database_schema.md`.
- **No `.pbix` file exists, and the PBIP project has not been opened in
  Power BI Desktop.** `powerbi/pbip/VaccinationAnalytics.pbip` is a
  real, hand-authored TMDL semantic model (tables, relationships, all 11
  measures) plus an empty 7-page report shell. It was checked for valid
  JSON, consistent TMDL tab-indentation, and correct file-path escaping,
  but this environment has no Windows desktop UI automation, so it could
  not be opened in Desktop to confirm it loads without error. Treat the
  first real open as a validation step, not a guarantee. See
  `powerbi/README.md`.
- Correlation coefficients (Pearson and Spearman) are reported together
  because several relationships in this domain are monotonic without
  being linear; neither coefficient implies causation.
