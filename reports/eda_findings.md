# EDA Findings

Summarizes the exploratory analysis in `notebooks/03_eda.ipynb`. Every
number below is reproduced from that notebook's executed output, not
re-estimated here.

## Coverage

- Global average coverage across the 10 fetched antigens (2000–2025):
  DTP1 91.8%, BCG 89.7%, DTP3 86.8%, MCV1 85.9%, HEPB3 75.8%, HIB3 68.8%,
  IPV1 61.2%, MCV2 59.0% (mean across all country-years with data for
  that antigen).
- Regional average coverage (all antigens, all years) ranks: AMR 77.1%,
  EUR 76.7%, EMR 73.7%, WPR 71.5%, SEAR 65.9%, AFR 62.4%.
- In the latest year with DTP3 data (2025, 195 countries reporting), the
  10 lowest-coverage countries were Yemen (39%), Papua New Guinea (43%),
  Central African Republic (46%), Venezuela (50%), Azerbaijan (51%),
  Angola (52%), Lebanon (52%), Kazakhstan (54%), Haiti (58%), and Bolivia
  (59%).
- 132 of 195 countries with 2025 MCV1 data (67.7%) are below the WHO 95%
  measles target; the average shortfall among all 195 countries is 10.0
  percentage points.

## Dose completion

- The DTP1→DTP3 primary-series drop-off has held stable in the 5–6% range
  from 2000 through 2025.
- The MCV1→MCV2 gap fell from over 70% in 2000 to under 8% by 2025 — this
  reflects MCV2 maturing as a newer program over that period, not
  worsening dropout; by 2025 the two measures are comparable in size.

## Disease incidence and reported cases

- Global average incidence rate declined for every one of the 7 tracked
  diseases between their earliest and latest available years (see SQL
  query #14 / notebook Chart 6): polio −99.8% (1980→2018), rubella −98.0%
  (1997→2024), measles −97.1% (1980→2024), neonatal tetanus −93.4%,
  diphtheria −89.8%, total tetanus −84.4%, pertussis −72.2%.
- Over the most recent 10 reported years, measles accounted for the
  largest total case burden (3,587,498 cases) followed by pertussis
  (2,193,760); polio accounted for the fewest (242 cases).

## Coverage vs. incidence correlation

- MCV1 coverage vs. measles incidence rate, matched by country-year
  (n=4,487): Spearman r = −0.32 (p ≈ 2×10⁻¹⁰⁶), Pearson r = −0.10
  (p ≈ 2×10⁻¹²). The Spearman coefficient is the more appropriate read
  here since the relationship is monotonic rather than linear.
- **This is an association, not a causal finding** — see
  `docs/limitations.md` for the confounders this dataset cannot control
  for (surveillance capacity, healthcare access, outbreak dynamics).

## Antigen-to-antigen correlation

- Antigens delivered at the same routine visit (DTP3, HepB3, Hib3, PCV3 —
  all given around 6/10/14 weeks) show strong positive Spearman
  correlation in coverage across country-years, consistent with shared
  delivery infrastructure rather than a relationship between the vaccines
  themselves.

## Simulated-data observations (method demonstration only)

- Vaccine-introduction and vaccine-schedule charts (notebook Sections 8–9)
  are excluded from the findings above because the underlying data is
  simulated (see `data/README.md`); they demonstrate the analysis method
  a real WIISE-portal export would support, not real WHO figures.

## Not answerable with the provided data

Gender, education, urban/rural, seasonality, population-density, and
income/socioeconomic breakdowns — see `docs/limitations.md` for the full
list and what each would require.
