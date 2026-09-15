-- Analytical views intended for BI consumption (Power BI connects to
-- these directly rather than to the raw fact/dimension tables -- see
-- powerbi/data_model.md).

CREATE VIEW vw_coverage_overview AS
SELECT f.iso3, c.country_name, c.who_region, f.year, f.antigen_code,
       a.antigen_description, f.coverage_category, f.coverage_pct
FROM fact_coverage f
JOIN dim_country c ON c.iso3 = f.iso3
JOIN dim_antigen a ON a.antigen_code = f.antigen_code;

CREATE VIEW vw_disease_impact_overview AS
SELECT rc.iso3, c.country_name, c.who_region, rc.year, rc.disease_code,
       d.disease_description, rc.cases, ir.incidence_rate, ir.denominator AS population
FROM fact_reported_cases rc
JOIN dim_country c ON c.iso3 = rc.iso3
JOIN dim_disease d ON d.disease_code = rc.disease_code
LEFT JOIN fact_incidence_rate ir
    ON ir.iso3 = rc.iso3 AND ir.year = rc.year AND ir.disease_code = rc.disease_code;

CREATE VIEW vw_country_year_summary AS
SELECT c.iso3, c.country_name, c.who_region, cov.year,
       AVG(cov.coverage_pct) AS avg_coverage_pct,
       AVG(ir.incidence_rate) AS avg_incidence_rate
FROM fact_coverage cov
JOIN dim_country c ON c.iso3 = cov.iso3
LEFT JOIN fact_incidence_rate ir ON ir.iso3 = cov.iso3 AND ir.year = cov.year
GROUP BY c.iso3, c.country_name, c.who_region, cov.year;

-- SIMULATED data (see data/README.md).
CREATE VIEW vw_vaccine_introduction_summary AS
SELECT i.iso3, c.country_name, c.who_region, v.vaccine_code, v.vaccine_description,
       i.year AS introduction_year, i.intro
FROM fact_vaccine_introduction i
JOIN dim_country c ON c.iso3 = i.iso3
JOIN dim_vaccine v ON v.vaccine_code = i.vaccine_code;

-- SIMULATED data (see data/README.md).
CREATE VIEW vw_schedule_summary AS
SELECT s.iso3, c.country_name, c.who_region, v.vaccine_code, v.vaccine_description,
       s.schedule_rounds, s.target_pop, s.age_administered
FROM fact_vaccine_schedule s
JOIN dim_country c ON c.iso3 = s.iso3
JOIN dim_vaccine v ON v.vaccine_code = s.vaccine_code;

-- Target-achievement summary: MCV1 vs. the WHO 95% measles target, latest year.
CREATE VIEW vw_target_achievement_summary AS
SELECT c.iso3, c.country_name, c.who_region, f.year, f.coverage_pct AS mcv1_coverage,
       (f.coverage_pct >= 95.0) AS meets_measles_target,
       ROUND(f.coverage_pct - 95.0, 2) AS gap_to_target
FROM fact_coverage f
JOIN dim_country c ON c.iso3 = f.iso3
WHERE f.antigen_code = 'MCV1' AND f.year = (SELECT MAX(year) FROM fact_coverage WHERE antigen_code = 'MCV1');
