# Data Quality Report

Generated from `data/processed/cleaning_report.json`, produced by
`src/data_cleaning.py`. Row counts below are exact outputs of that run, not
estimates.

## Source summary

| Dataset | Status | Rows (raw) | Rows (cleaned) | Years | Countries |
|---|---|---:|---:|---|---:|
| Coverage | Real (WHO GHO API) | 42,800 | 42,800 | 2000–2025 | 195 |
| Reported cases | Real (WHO GHO API) | 64,860 | 64,860 | 1974–2025 | 214 |
| Incidence rate | Real, derived (cases ÷ World Bank population × 100,000) | — | 48,652 | 1980–2024 | see below |
| Vaccine introduction | **Simulated** (see `data/README.md`) | 1,565 | 1,565 | 2000–2023 | 228 |
| Vaccine schedule | **Simulated** (see `data/README.md`) | 1,824 | 1,824 | 2023 | 228 |

## Per-dataset cleaning actions and counts

### Coverage (`coverage.csv` → `clean_coverage.csv`)

- Duplicate rows on (Code, Year, Antigen, Coverage_category): **0 removed**
- Rows with Year outside [1974, 2026]: **0 removed**
- Rows with Coverage outside [0, 100]%: **0 removed**
- Rows with a country Code not in the WHO country reference: **0 removed**
- Result: all 42,800 raw rows retained — WHO's WUENIC estimates were already
  schema-consistent and range-valid at the point of extraction (source is
  the same GHO API used by the portal itself, not a manually-exported
  file with transcription risk).
- Antigens present: BCG, DTP1, DTP3, HEPB3, HIB3, IPV1, MCV1, MCV2, PCV3, ROTAC.

### Reported cases (`reported-cases.csv` → `clean_reported_cases.csv`)

- Duplicate rows on (Code, Year, Disease): **0 removed**
- Rows with Year outside [1974, 2026]: **0 removed**
- Rows with a negative Cases value: **0 removed**
- Rows with Cases missing: **10,135 of 64,860 (15.6%) retained as null**,
  not imputed. A missing value means the country did not submit that
  disease/year to WHO's Joint Reporting Form that cycle; treating it as
  zero would understate disease burden in non-reporting countries and bias
  every trend and correlation computed from this table. Any aggregate in
  the EDA/reports built from `Cases` is computed only over non-null rows,
  which is stated wherever it matters.
- Diseases present: Diphtheria, Measles, Pertussis, Polio, Rubella, Total
  tetanus, Neonatal tetanus.

### Incidence rate (derived, not a raw WHO file)

- Formula: `Incidence_rate = Cases / Population * 100,000`, the standard
  epidemiological convention (cases per 100,000 population).
- Of 64,860 candidate case-count rows: **8,612 dropped** for no matching
  World Bank population record for that country-year, and **7,596 dropped**
  because Cases was null (see above) — a rate cannot be computed without
  both a case count and a population. **48,652 rows** produced.

### Population (`population.csv`, auxiliary — not one of the 5 brief datasets)

- Duplicate rows on (Code, Year): **0 removed**
- Rows with non-positive population: **0 removed**
- Rows for World Bank regional/income-group aggregates (e.g. `WLD`, `AFE`)
  that are not real countries: excluded during fetch (see
  `src/fetch_who_data.py`), not counted as a cleaning removal.

### Vaccine introduction (`vaccine-introduction.csv` → `clean_vaccine_introduction.csv`)

*This dataset is simulated — see `data/README.md` for why and how.*

- Duplicate rows on (ISO_3_Code, Description): **0 removed**
- Rows with a WHO_Region outside the 6 recognized codes: **0 removed**
- Rows with Intro == "Yes" but a null Year (an internally inconsistent
  record): **0 removed**
- 1,128 vaccine-country combinations marked introduced, 437 not introduced
  (Year is legitimately null for the latter — retained, not an error).

### Vaccine schedule (`vaccine-schedule-data.csv` → `clean_vaccine_schedule.csv`)

*This dataset is simulated — see `data/README.md` for why and how.*

- Duplicate rows on (ISO_3_Code, Vaccine_code, Year): **0 removed**
- Rows with a WHO_Region outside the 6 recognized codes: **0 removed**
- Rows with non-positive Schedule_rounds: **0 removed**

## Remaining limitations

- **Coverage and reported-cases country sets differ** (195 vs. 214
  countries) because not every country reports every indicator to WHO.
  Any analysis joining the two datasets is implicitly limited to their
  intersection; this is not an error to fix, it reflects real reporting
  gaps.
- **15.6% of reported-cases rows have no case count.** Time-series and
  correlation analyses using `Cases` or the derived `Incidence_rate`
  necessarily exclude those country-years; this can understate disease
  burden trends for countries with weak surveillance reporting rather than
  low actual incidence — the two are not distinguishable from this data
  alone.
- **Vaccine introduction and vaccine schedule are simulated**, not WHO-
  reported figures (see `data/README.md`). Findings that depend on them
  are explicitly labeled in `reports/analysis_results.md` and
  `reports/public_health_insights.md`.
- No sub-national (state/province), demographic (age, sex, urban/rural,
  education, income), or seasonal (sub-annual) breakdown exists in any of
  the 5 datasets. Several brief questions cannot be answered as a result;
  see `docs/limitations.md` for the full list.
