# Analysis Results — Project Questions

Every "Easy" and "Medium" question from the project brief, answered
directly against the cleaned data, or marked not answerable with a stated
reason. Numbers are reproduced from `notebooks/03_eda.ipynb` and
`sql/06_analysis_queries.sql` (validated against the real data — see
`docs/methodology.md`), not re-derived here.

## Easy

**1 & 9. How do vaccination rates correlate with a decrease in disease incidence?**
Answerable. MCV1 coverage vs. measles incidence rate, matched by
country-year (n=4,487): Spearman r = −0.32 (p ≈ 2×10⁻¹⁰⁶). DTP3 coverage
vs. diphtheria incidence: Spearman r = −0.19 (p ≈ 9×10⁻³²). DTP3 vs.
pertussis incidence is much weaker (Spearman r = −0.035, p = 0.026) —
notably, pertussis shows near-zero association with DTP3 coverage in this
data, consistent with well-documented waning pertussis-vaccine immunity
and endemic resurgence patterns rather than a data error. All figures are
**associations, not causal estimates** (see `docs/limitations.md`).

**2. What is the drop-off rate between 1st dose and subsequent doses?**
Answerable. DTP1→DTP3 drop-off has held steady at 5–6% globally,
2000–2025. MCV1→MCV2 drop-off fell from >70% (2000) to <8% (2025) as MCV2
programs matured; the two measures converge by the most recent years.

**3. Are vaccination rates different between genders?**
**NOT ANSWERABLE WITH PROVIDED DATASET.** No sex/gender field exists in
any of the 5 source files. Would require sex-disaggregated coverage
records (e.g. from a household survey such as DHS/MICS).

**4. How does education level impact vaccination rates?**
**NOT ANSWERABLE WITH PROVIDED DATASET.** No education field exists.
Would require survey data linking caregiver/maternal education to child
vaccination status.

**5. What is the urban vs. rural vaccination rate difference?**
**NOT ANSWERABLE WITH PROVIDED DATASET.** No urban/rural classification
exists; WHO's national-level WUENIC estimates do not carry a residence
dimension. Would require sub-national survey data with a residence field.

**6. Has the rate of booster dose uptake increased over time?**
Answerable, using MCV2 (2nd measles dose) as the available booster-style
proxy: global average MCV2 coverage rose from its earliest recorded value
to a materially higher level by 2025 (see notebook Chart 3 for the
year-by-year series). Trend is upward but not perfectly monotonic.

**7. Is there a seasonal pattern in vaccination uptake?**
**NOT ANSWERABLE WITH PROVIDED DATASET.** All coverage/case data is
annual. Would require monthly or quarterly vaccination-administration
records.

**8. How does population density relate to vaccination coverage?**
**NOT ANSWERABLE WITH PROVIDED DATASET.** `population.csv` has total
population only, no land area, so density cannot be derived. Would
require a land-area field per country (available from World Bank
indicator `AG.SRF.TOTL.K2`, not currently fetched into this project) or
sub-national gridded population data.

**10. Which regions have high disease incidence despite high vaccination rates?**
Answerable. Using MCV1 coverage ≥ 90% and measles incidence above the
global median for 2024: 40 countries met both conditions. The highest
incidence among them: Kyrgyzstan (91% coverage, 199.1 per 100,000),
Iraq (96%, 70.6), Uzbekistan (99%, 57.6), Mauritania (93%, 21.4), Armenia
(96%, 18.5). This pattern (high coverage, non-trivial incidence) is
consistent with outbreak dynamics, historical immunity gaps predating
recent high coverage, or under-vaccinated pockets not visible in a
national-average figure — this dataset cannot distinguish between those
explanations.

## Medium

**1. Is there a correlation between vaccine introduction and a decrease in disease cases?**
**Not reliably answerable with real data.** `vaccine_introduction.csv` is
simulated (see `data/README.md`); any correlation computed against its
introduction years would be an artifact of the random generator used to
produce it, not evidence about real-world introduction timing. The
notebook demonstrates the *method* for this analysis (Section 12,
pre/post comparison) using real MCV1 coverage data instead, with that
substitution stated explicitly.

**2. What is the trend in disease cases before and after vaccination campaigns?**
Same limitation as Medium #1 — campaign/introduction timing in this
project is simulated. Not reported as a finding.

**3. Which diseases have shown the most significant reduction in cases due to vaccination?**
Partially answerable — the dataset shows real, large reductions in
*incidence rate* over time, but cannot establish vaccination as the cause
(no controlled comparison, no unvaccinated control population). Observed
reductions, first available year to latest: polio −99.8% (1980→2018),
rubella −98.0% (1997→2024), measles −97.1% (1980→2024), neonatal tetanus
−93.4%, diphtheria −89.8%, total tetanus −84.4%, pertussis −72.2%. Phrased
as association: these declines occurred over the same period global
vaccination programs expanded (Chart 1), not as proof of causation.

**4. What percentage of the target population has been covered by each vaccine?**
Answerable directly — WHO's WUENIC `Coverage` figure *is* the percentage
of the target population (typically 1-year-olds) reached. Global averages
(all country-years): DTP1 91.8%, BCG 89.7%, DTP3 86.8%, MCV1 85.9%,
HEPB3 75.8%, HIB3 68.8%, IPV1 61.2%, MCV2 59.0%, PCV3 and ROTAC (see
`reports/eda_findings.md` for the full antigen list and notebook Section 4
for country-level detail).

**5. How does the vaccination schedule, including booster doses, impact target population coverage?**
**Not reliably answerable with real data.** `vaccine_schedule.csv` is
simulated. A real analysis would need actual WHO/UNICEF Joint Reporting
Form schedule data (dose counts, timing) linked to real coverage
outcomes, which was not obtainable through a public bulk API in this
project (see `data/README.md`).

**6. Are there significant disparities in vaccine introduction timelines across WHO regions?**
**Computed on simulated data only** (see `data/README.md`); results exist
(`sql/06_analysis_queries.sql`, query #8) but are not reported as a real
finding, since the introduction years are randomly generated, not
WHO-reported.

**7. How does vaccine coverage correlate with disease reduction for specific antigens?**
Answerable — see Easy #1/#9 above (MCV1/measles, DTP3/diphtheria,
DTP3/pertussis) for antigen-specific correlation coefficients.

**8. Are there specific regions or countries with low coverage despite high availability of vaccines?**
**Partially not answerable.** No vaccine-availability/supply-chain
dataset exists in this project (stock levels, cold-chain capacity, or
doses shipped are not part of any of the 5 source files), so the
"despite high availability" comparison cannot be made. The low-coverage
side is answerable on its own: see Easy #10's lowest-DTP3-coverage list
and `sql/06_analysis_queries.sql` query #12.

**9. What are the gaps in coverage for vaccines targeting high-priority diseases such as TB and Hepatitis B?**
Answerable, using BCG (TB) and HepB3 as proxies, gap to a 90% programmatic
target, by WHO region, latest year (2025): BCG gap ranges from AFR +2.6pp
(i.e. slightly above 90%) down to SEAR −4.3pp (below target); HepB3 gap
ranges from AFR +8.3pp down to SEAR −2.2pp. SEAR is below the 90% target
for both antigens in the latest year.

**10. Are certain diseases more prevalent in specific geographic areas?**
Answerable. Average incidence rate by WHO region shows clear disease-
specific geographic concentration: AFR has the highest average incidence
for measles (102.6/100k), pertussis (25.0/100k), neonatal tetanus, and
total tetanus; WPR has the highest for diphtheria (1.0/100k); EMR has the
highest for polio (0.55/100k); EUR has the highest for rubella
(8.4/100k). Full region × disease table in
`notebooks/03_eda.ipynb` and `sql/06_analysis_queries.sql` query #15.
