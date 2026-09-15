# Public Health Insights

Scenario-oriented read of `reports/analysis_results.md` and
`reports/eda_findings.md`, for the brief's scenario list. Only scenarios
the real data actually supports are covered; the rest are marked
accordingly rather than answered speculatively.

## 1. Government agency identifying low-coverage regions for resource allocation

**Supported.** SEAR and AFR have the lowest average coverage across
antigens (65.9% and 62.4% respectively, vs. 77.1% in AMR). At the country
level, the 2025 DTP3 data flags Yemen (39%), Papua New Guinea (43%),
Central African Republic (46%), Venezuela (50%), and Azerbaijan (51%) as
the lowest-coverage countries — concrete candidates for a resource-
allocation review, though country-level program constraints (conflict,
access, health-system capacity) are not captured in this data and should
inform any real allocation decision alongside these figures.

## 2. Public health organization evaluating a measles vaccination campaign

**Partially supported.** Real MCV1 coverage and real measles incidence
are both available and negatively correlated (Spearman r = −0.32). A
true campaign evaluation needs the campaign's actual date and target
population, which this project's vaccine-introduction data does not
provide (it is simulated). The notebook's pre/post-comparison method
(Section 12) is ready to apply the moment real campaign-date data is
available.

## 3. Vaccine manufacturer estimating future vaccine demand

**Not supported.** Demand forecasting needs population-at-risk by birth
cohort, planned campaign calendars, and current stock/pipeline data —
none of which exist in this project's 5 datasets. Coverage trend data
alone (Chart 1) could inform a very rough directional view but should not
be used for actual demand planning.

## 4. Researchers exploring polio incidence among populations with no vaccination coverage

**Partially supported.** Real polio incidence data exists and shows a
99.8% decline from 1980 to 2018 with very low residual case counts (242
reported cases globally in the most recent 10-year window). However, this
project has no coverage=0% subgroup to isolate — coverage data is
national averages, not individual-level, so "populations with no
coverage" cannot be isolated from a national aggregate. This would need
sub-national or individual-level vaccination records.

## 5. WHO tracking progress toward 95% measles coverage by 2030

**Fully supported with real data.** In the latest year available (2025),
67.7% of the 195 countries with MCV1 data (132 countries) remain below
the 95% target, with an average shortfall of 10.0 percentage points
across all 195 countries. This is a directly usable, real baseline for
tracking progress toward the 2030 target.

## 6. Health agency allocating vaccines to high-risk populations (children under five, elderly)

**Not supported.** Age-group breakdown does not exist beyond "1-year-olds"
(the implicit WUENIC coverage denominator) — there is no separate
under-five or elderly vaccination series in any of the 5 datasets (this
project's antigens are all childhood/routine-infant vaccines; no
elderly-specific vaccine such as influenza or pneumococcal-adult is
tracked here).

## 7. Non-profit identifying disparities across socioeconomic groups

**Not supported.** No income, wealth-quintile, or socioeconomic field
exists in any source file. Would require household survey data (e.g.
DHS/MICS wealth quintiles) linked to vaccination status.

## 8. Authorities analyzing vaccination patterns throughout the year

**Not supported.** All coverage and case data in this project is annual;
no month/quarter granularity exists to analyze intra-year patterns.

## 9. Comparing different vaccination strategies

**Partially supported.** Dose-schedule structure (number of rounds,
target population) exists but only in the simulated vaccine-schedule
dataset, so a real strategy comparison is not possible from this project
as built. The DTP1→DTP3 vs. MCV1→MCV2 drop-off comparison (Easy #2) is a
real, if narrower, example of comparing completion outcomes across two
different dosing structures.

## Priority recommendations (evidence-based, from the findings above)

1. **Prioritize SEAR and AFR for coverage-gap interventions** — both
   regions sit below the other four WHO regions on average coverage
   across all tracked antigens, and SEAR alone falls below a 90% target
   for both BCG and HepB3 in the latest year.
2. **Treat the 132 countries below the 95% MCV1 target as the near-term
   measles-elimination focus list** — this is a real, current baseline,
   not a projection.
3. **Investigate the pertussis/DTP3 relationship further before assuming
   vaccination directly explains observed pertussis trends** — the
   near-zero correlation found here (Spearman r = −0.035) is a genuine
   result worth a dedicated study, not treated as vaccine failure without
   further investigation (waning immunity and case-definition changes are
   documented alternative explanations in the epidemiological
   literature, outside the scope of what this dataset can confirm).
4. **Do not use this project's vaccine-introduction or vaccine-schedule
   data for any operational decision** — both are simulated placeholders
   for datasets WHO does not expose through a public bulk API (see
   `data/README.md`); replace them with a real WIISE-portal export before
   using Page 4/5 of the dashboard for anything beyond a design preview.

## Limitations recap

See `docs/limitations.md` for the complete list. In short: this project
answers coverage/incidence/case-count questions well with real WHO and
World Bank data, and cannot answer any question requiring demographic,
socioeconomic, sub-national, sub-annual, or vaccine-supply data, because
none of that exists in the five project datasets.
