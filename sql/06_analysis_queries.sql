-- Analytical queries against the schema in 02_create_tables.sql.
-- Logic validated against the real cleaned data (see docs/methodology.md);
-- written for PostgreSQL syntax.

-- 1. Average vaccination coverage, overall and by antigen.
SELECT antigen_code, ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct, COUNT(*) AS n_observations
FROM fact_coverage
GROUP BY antigen_code
ORDER BY avg_coverage_pct DESC;

-- 2. Average coverage by country (DTP3, all years), ranked.
SELECT c.country_name, c.who_region, ROUND(AVG(f.coverage_pct), 2) AS avg_dtp3_coverage,
       RANK() OVER (ORDER BY AVG(f.coverage_pct) DESC) AS coverage_rank
FROM fact_coverage f
JOIN dim_country c ON c.iso3 = f.iso3
WHERE f.antigen_code = 'DTP3'
GROUP BY c.country_name, c.who_region
ORDER BY avg_dtp3_coverage DESC;

-- 3. Coverage trend by year (all antigens combined).
SELECT year, ROUND(AVG(coverage_pct), 2) AS avg_coverage_pct
FROM fact_coverage
GROUP BY year
ORDER BY year;

-- 4. Coverage by WHO region and antigen.
SELECT c.who_region, f.antigen_code, ROUND(AVG(f.coverage_pct), 2) AS avg_coverage_pct
FROM fact_coverage f
JOIN dim_country c ON c.iso3 = f.iso3
WHERE c.who_region IS NOT NULL
GROUP BY c.who_region, f.antigen_code
ORDER BY c.who_region, f.antigen_code;

-- 5. Disease incidence trend, year over year, with % change.
WITH yearly AS (
    SELECT disease_code, year, AVG(incidence_rate) AS avg_incidence_rate
    FROM fact_incidence_rate
    GROUP BY disease_code, year
)
SELECT disease_code, year, ROUND(avg_incidence_rate, 3) AS avg_incidence_rate,
       ROUND(
           (avg_incidence_rate - LAG(avg_incidence_rate) OVER (PARTITION BY disease_code ORDER BY year))
           / NULLIF(LAG(avg_incidence_rate) OVER (PARTITION BY disease_code ORDER BY year), 0) * 100, 2
       ) AS yoy_pct_change
FROM yearly
ORDER BY disease_code, year;

-- 6. Reported cases trend (global total per year, per disease).
SELECT disease_code, year, SUM(cases) AS total_cases
FROM fact_reported_cases
WHERE cases IS NOT NULL
GROUP BY disease_code, year
ORDER BY disease_code, year;

-- 7. Vaccine introduction timeline (SIMULATED data) -- introductions per year per region.
SELECT c.who_region, i.year, COUNT(*) AS vaccines_introduced
FROM fact_vaccine_introduction i
JOIN dim_country c ON c.iso3 = i.iso3
WHERE i.intro = 'YES'
GROUP BY c.who_region, i.year
ORDER BY c.who_region, i.year;

-- 8. Regional disparities in introduction timelines (SIMULATED data):
--    average introduction year per vaccine per region.
SELECT v.vaccine_code, c.who_region, ROUND(AVG(i.year), 1) AS avg_introduction_year,
       COUNT(*) FILTER (WHERE i.intro = 'YES') AS countries_introduced,
       COUNT(*) AS countries_eligible
FROM fact_vaccine_introduction i
JOIN dim_country c ON c.iso3 = i.iso3
JOIN dim_vaccine v ON v.vaccine_code = i.vaccine_code
WHERE c.who_region IS NOT NULL
GROUP BY v.vaccine_code, c.who_region
ORDER BY v.vaccine_code, c.who_region;

-- 9. Dose comparison: DTP1 vs DTP3 coverage and the completion drop-off, by country-year.
SELECT d1.iso3, d1.year,
       d1.coverage_pct AS dtp1_coverage,
       d3.coverage_pct AS dtp3_coverage,
       ROUND((d1.coverage_pct - d3.coverage_pct) / NULLIF(d1.coverage_pct, 0) * 100, 2) AS dropoff_pct
FROM fact_coverage d1
JOIN fact_coverage d3
  ON d3.iso3 = d1.iso3 AND d3.year = d1.year AND d3.antigen_code = 'DTP3'
WHERE d1.antigen_code = 'DTP1'
ORDER BY d1.iso3, d1.year;

-- 10. Countries below the WHO 95% measles (MCV1) coverage target, latest year.
WITH latest_year AS (SELECT MAX(year) AS yr FROM fact_coverage WHERE antigen_code = 'MCV1')
SELECT c.country_name, c.who_region, f.coverage_pct,
       ROUND(f.coverage_pct - 95.0, 2) AS gap_to_target
FROM fact_coverage f
JOIN dim_country c ON c.iso3 = f.iso3
JOIN latest_year ly ON f.year = ly.yr
WHERE f.antigen_code = 'MCV1' AND f.coverage_pct < 95.0
ORDER BY gap_to_target ASC;

-- 11. High-incidence despite high-coverage countries (measles, latest matched year):
--     coverage >= 90% but incidence rate above the global median that year.
WITH latest AS (
    SELECT MAX(year) AS yr FROM fact_incidence_rate WHERE disease_code = 'MEASLES'
),
median_incidence AS (
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY incidence_rate) AS median_rate
    FROM fact_incidence_rate i, latest l
    WHERE i.disease_code = 'MEASLES' AND i.year = l.yr
)
SELECT c.country_name, c.who_region, cov.coverage_pct AS mcv1_coverage, inc.incidence_rate
FROM fact_incidence_rate inc
JOIN latest l ON inc.year = l.yr AND inc.disease_code = 'MEASLES'
JOIN fact_coverage cov ON cov.iso3 = inc.iso3 AND cov.year = inc.year AND cov.antigen_code = 'MCV1'
JOIN dim_country c ON c.iso3 = inc.iso3
CROSS JOIN median_incidence m
WHERE cov.coverage_pct >= 90.0 AND inc.incidence_rate > m.median_rate
ORDER BY inc.incidence_rate DESC;

-- 12. Low-coverage countries (DTP3 < 70%, latest year).
WITH latest_year AS (SELECT MAX(year) AS yr FROM fact_coverage WHERE antigen_code = 'DTP3')
SELECT c.country_name, c.who_region, f.coverage_pct
FROM fact_coverage f
JOIN dim_country c ON c.iso3 = f.iso3
JOIN latest_year ly ON f.year = ly.yr
WHERE f.antigen_code = 'DTP3' AND f.coverage_pct < 70.0
ORDER BY f.coverage_pct ASC;

-- 13. Coverage gap to the 90% programmatic target, by antigen (latest year, region average).
WITH latest_year AS (SELECT antigen_code, MAX(year) AS yr FROM fact_coverage GROUP BY antigen_code)
SELECT c.who_region, f.antigen_code, ROUND(AVG(f.coverage_pct), 2) AS avg_coverage,
       ROUND(AVG(f.coverage_pct) - 90.0, 2) AS avg_gap_to_90pct_target
FROM fact_coverage f
JOIN latest_year ly ON f.antigen_code = ly.antigen_code AND f.year = ly.yr
JOIN dim_country c ON c.iso3 = f.iso3
WHERE c.who_region IS NOT NULL
GROUP BY c.who_region, f.antigen_code
ORDER BY f.antigen_code, avg_gap_to_90pct_target;

-- 14. Disease reduction trend: first vs. last available year, by disease.
WITH bounds AS (
    SELECT disease_code, MIN(year) AS first_year, MAX(year) AS last_year
    FROM fact_incidence_rate
    GROUP BY disease_code
),
first_val AS (
    SELECT i.disease_code, AVG(i.incidence_rate) AS first_rate
    FROM fact_incidence_rate i JOIN bounds b ON i.disease_code = b.disease_code AND i.year = b.first_year
    GROUP BY i.disease_code
),
last_val AS (
    SELECT i.disease_code, AVG(i.incidence_rate) AS last_rate
    FROM fact_incidence_rate i JOIN bounds b ON i.disease_code = b.disease_code AND i.year = b.last_year
    GROUP BY i.disease_code
)
SELECT f.disease_code, b.first_year, ROUND(f.first_rate, 3) AS first_year_rate,
       b.last_year, ROUND(l.last_rate, 3) AS last_year_rate,
       ROUND((l.last_rate - f.first_rate) / NULLIF(f.first_rate, 0) * 100, 1) AS pct_change
FROM first_val f
JOIN last_val l ON f.disease_code = l.disease_code
JOIN bounds b ON b.disease_code = f.disease_code
ORDER BY pct_change ASC;

-- 15. Regional comparison: average coverage vs. average incidence, most recent shared year.
SELECT c.who_region,
       ROUND(AVG(cov.coverage_pct), 2) AS avg_mcv1_coverage,
       ROUND(AVG(inc.incidence_rate), 3) AS avg_measles_incidence
FROM fact_coverage cov
JOIN fact_incidence_rate inc
  ON inc.iso3 = cov.iso3 AND inc.year = cov.year AND inc.disease_code = 'MEASLES'
JOIN dim_country c ON c.iso3 = cov.iso3
WHERE cov.antigen_code = 'MCV1' AND c.who_region IS NOT NULL
GROUP BY c.who_region
ORDER BY avg_measles_incidence DESC;

-- 16. Booster-style second-dose uptake trend (MCV2) with a rolling classification.
SELECT year, ROUND(AVG(coverage_pct), 2) AS avg_mcv2_coverage,
       CASE
           WHEN AVG(coverage_pct) >= 80 THEN 'HIGH'
           WHEN AVG(coverage_pct) >= 50 THEN 'MODERATE'
           ELSE 'LOW'
       END AS coverage_tier
FROM fact_coverage
WHERE antigen_code = 'MCV2'
GROUP BY year
ORDER BY year;

-- 17. Coverage gaps for high-priority antigens (BCG = TB, HEPB3 = Hepatitis B), by region.
SELECT c.who_region, f.antigen_code, ROUND(AVG(f.coverage_pct), 2) AS avg_coverage,
       ROUND(90.0 - AVG(f.coverage_pct), 2) AS gap_to_90pct
FROM fact_coverage f
JOIN dim_country c ON c.iso3 = f.iso3
WHERE f.antigen_code IN ('BCG', 'HEPB3') AND c.who_region IS NOT NULL
  AND f.year = (SELECT MAX(year) FROM fact_coverage)
GROUP BY c.who_region, f.antigen_code
ORDER BY f.antigen_code, gap_to_90pct DESC;

-- 18. Vaccine schedule summary: rounds and target population by vaccine (SIMULATED data).
SELECT v.vaccine_code, v.vaccine_description,
       ROUND(AVG(s.schedule_rounds), 1) AS avg_rounds,
       MODE() WITHIN GROUP (ORDER BY s.target_pop) AS most_common_target_pop,
       COUNT(DISTINCT s.iso3) AS countries_covered
FROM fact_vaccine_schedule s
JOIN dim_vaccine v ON v.vaccine_code = s.vaccine_code
GROUP BY v.vaccine_code, v.vaccine_description
ORDER BY v.vaccine_code;
