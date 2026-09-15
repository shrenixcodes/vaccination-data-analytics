# Dashboard Specification

7 pages, following the brief's structure but trimmed to visuals the data
actually supports — no gender, education, urban/rural, or population-
density breakdowns, since none of those variables exist in the source
data (see `docs/limitations.md`).

## Page 1 — Executive Overview

**KPI cards** (top row): Total Countries (`DISTINCTCOUNT(DimCountry[iso3])`),
Average Coverage, Total Reported Cases, Average Incidence Rate, Countries
Below Target, Target Achievement % (95%, MCV1).

**Visuals:**
- Line chart: Average Coverage by DimYear[year], one line per antigen (top
  4 antigens by data volume: BCG, DTP3, MCV1, HEPB3).
- Line chart: Average Incidence Rate by year, one line per disease.
- Filled/choropleth map: Average Coverage by DimCountry (requires ISO3
  codes recognized by Power BI's built-in map — `iso3` matches directly).
- Bar chart: top 10 / bottom 10 countries by Average Coverage.
- Text box: 3–4 key findings pulled verbatim from
  `reports/eda_findings.md`.

**Filters (page-level):** DimYear[year] range slicer.

## Page 2 — Vaccination Coverage

**Visuals:**
- Map or bar: Average Coverage by country.
- Bar: Average Coverage by DimAntigen.
- Line: Average Coverage by year (antigen-filterable).
- Bar: Average Coverage by DimCountry[who_region].
- Clustered bar: DTP1 Coverage vs. DTP3 Coverage by region (dose
  comparison — uses the two dedicated measures in `dax_measures.md`).
- Table: Coverage Gap (95% target) by country, sorted ascending (worst
  gaps first).

**Filters:** year, country, WHO region, antigen, coverage_category.

## Page 3 — Disease Impact

**Visuals:**
- Line: Average Incidence Rate by year, by disease.
- Line/area: Total Reported Cases by year, by disease.
- Bar: Total Reported Cases by disease (selected year).
- Scatter: MCV1 Coverage (X) vs. Measles Average Incidence Rate (Y), one
  point per country-year — the Power BI equivalent of notebook Chart 13.
  Add a trend line (Power BI's built-in analytics pane) rather than a
  hard-coded regression, and label the correlation is observational, not
  causal, in the visual's subtitle.
- Table: countries with MCV1 coverage ≥ 90% AND incidence rate above the
  period median (mirrors SQL query #11 in `sql/06_analysis_queries.sql`).

**Filters:** year, disease, WHO region.

## Page 4 — Vaccine Introduction *(SIMULATED DATA — labeled on the page)*

**Visuals:**
- Line: count of introductions per year, by WHO region.
- Bar: countries introduced (Intro = Yes) by vaccine.
- Bar: average introduction year by vaccine, by region (regional
  disparity view — mirrors SQL query #8).

**Filters:** vaccine, WHO region.

**Not included:** a pre/post case-count comparison around the
introduction year. The introduction years in this dataset are simulated
and not tied to the real case-count trajectories, so a before/after chart
here would visually imply a causal story the data cannot support. The
notebook's pre/post section (Section 12) instead demonstrates the
*method* using real MCV1 coverage against a fixed reference year, with
that caveat stated explicitly.

## Page 5 — Vaccine Schedule *(SIMULATED DATA — labeled on the page)*

**Visuals:**
- Box plot or clustered bar: Schedule_rounds by DimVaccine.
- Bar: count of countries by Target_pop category.
- Table: Vaccine_code, typical Age_administered, Schedule_rounds.

**Filters:** vaccine, WHO region.

## Page 6 — Geographic / Regional Analysis

**Visuals:**
- Map: Average Coverage by WHO region.
- Table: country ranking by Average Coverage (sortable, all antigens or
  antigen-filtered).
- Bar: lowest 10 countries by DTP3 coverage (disease-hotspot proxy —
  low coverage, not case counts, since case-count "hotspot" mapping needs
  the Page 3 scatter/table instead).
- Bar: Average Coverage by region, split by antigen (small multiples).

**Filters:** WHO region, antigen, year.

## Page 7 — Public Health Insights

**Format:** text-and-card layout, not chart-heavy — this page reads more
like a briefing than a dashboard.

**Content (each pulled from `reports/public_health_insights.md`, not
authored ad hoc on the page):**
- Priority regions/countries for resource allocation (lowest coverage).
- Coverage gap summary (Coverage Gap measure, worst 10 countries).
- Measles 95%-by-2030 target progress (Target Achievement % KPI +
  short narrative).
- 3–5 evidence-based recommendations, each citing the specific query or
  chart that supports it.
- A visible "Limitations" callout box linking the two simulated datasets
  and the demographic data gaps, so a viewer landing on this page first
  still sees the caveats.
