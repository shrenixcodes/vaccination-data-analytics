# Data

## Provenance

This project combines two kinds of source data. Every file's origin is
also recorded in `docs/data_dictionary.md` and `docs/limitations.md`.

### Real data (3 of 5 datasets)

Fetched live from official public APIs by `src/fetch_who_data.py`:

| File | Source | API |
|---|---|---|
| `coverage.csv` | WHO/UNICEF Estimates of National Immunization Coverage (WUENIC), 9 antigens | [WHO GHO OData API](https://ghoapi.azureedge.net/api/) |
| `reported-cases.csv` | WHO reported case counts, 7 vaccine-preventable diseases | [WHO GHO OData API](https://ghoapi.azureedge.net/api/) |
| `population.csv` | Total population by country and year | [World Bank Open Data API](https://api.worldbank.org/v2/) (indicator `SP.POP.TOTL`) |
| `who_country_reference.csv` | Country code, name, and WHO region lookup | WHO GHO `DIMENSION/COUNTRY` |

`population.csv` is used to derive an incidence-rate dataset
(cases per 100,000 population) during cleaning, since the WHO GHO
population indicator (`WHS9_86`) currently returns no country-level
records.

### Simulated data (2 of 5 datasets)

WHO publishes vaccine-introduction and vaccine-schedule data only through
the interactive WIISE portal (immunizationdata.who.int), which has no
public bulk-download API. `src/generate_synthetic_supplementary_data.py`
produces these two files using real country/ISO3/WHO-region facts and real
vaccine names, combined with a seeded random process (seed=42) for the
introduction years and schedule details:

| File | Status |
|---|---|
| `vaccine-introduction.csv` | **SIMULATED** — plausible introduction years, not WHO-reported figures |
| `vaccine-schedule-data.csv` | **SIMULATED** — plausible schedule structure, not WHO-reported figures |

Any finding in this project that touches these two files is labeled
"based on simulated data" in the relevant report/notebook section. See
`docs/limitations.md` for the full disclosure.

## Reproducing the raw data

Raw CSVs are gitignored (network-fetched / generated, and sizeable). To
regenerate them:

```bash
pip install -r requirements.txt
python src/fetch_who_data.py
python src/generate_synthetic_supplementary_data.py
```

## Processed data

`data/processed/` holds the cleaned, analysis-ready CSVs produced by
`src/data_cleaning.py`, documented in `docs/data_dictionary.md`.
