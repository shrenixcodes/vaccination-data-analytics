-- Loads the cleaned CSVs (data/processed/) and the country reference
-- (data/raw/who_country_reference.csv) into the schema created by
-- 02-04. Uses staging tables so dimension rows can be derived with
-- SELECT DISTINCT before the fact tables are loaded (dimensions must
-- exist first to satisfy the foreign keys added in 03_constraints.sql).
--
-- Run with psql from the repository root so the relative \copy paths
-- resolve correctly:
--   psql -d vaccination_analytics -f sql/05_load_data.sql

-- ---------------------------------------------------------------- Staging

CREATE TEMP TABLE stg_country (
    iso3 CHAR(3), country_name VARCHAR(150), who_region CHAR(4)
);
\copy stg_country FROM 'data/raw/who_country_reference.csv' WITH (FORMAT csv, HEADER true)

CREATE TEMP TABLE stg_coverage (
    grp TEXT, code CHAR(3), name TEXT, year SMALLINT, antigen_code VARCHAR(20),
    antigen_description TEXT, coverage_pct NUMERIC, coverage_category VARCHAR(30),
    coverage_category_description TEXT
);
\copy stg_coverage FROM 'data/processed/clean_coverage.csv' WITH (FORMAT csv, HEADER true)

CREATE TEMP TABLE stg_cases (
    grp TEXT, code CHAR(3), name TEXT, year SMALLINT, disease_code VARCHAR(30),
    disease_description TEXT, cases NUMERIC
);
\copy stg_cases FROM 'data/processed/clean_reported_cases.csv' WITH (FORMAT csv, HEADER true)

CREATE TEMP TABLE stg_incidence (
    grp TEXT, code CHAR(3), name TEXT, year SMALLINT, disease_code VARCHAR(30),
    disease_description TEXT, denominator NUMERIC, incidence_rate NUMERIC
);
\copy stg_incidence FROM 'data/processed/clean_incidence_rate.csv' WITH (FORMAT csv, HEADER true)

CREATE TEMP TABLE stg_introduction (
    iso3 CHAR(3), country_name TEXT, who_region CHAR(4), year SMALLINT,
    vaccine_code VARCHAR(20), description TEXT, intro VARCHAR(3)
);
\copy stg_introduction FROM 'data/processed/clean_vaccine_introduction.csv' WITH (FORMAT csv, HEADER true)

CREATE TEMP TABLE stg_schedule (
    iso3 CHAR(3), country_name TEXT, who_region CHAR(4), year SMALLINT,
    vaccine_code VARCHAR(20), vaccine_description TEXT, schedule_rounds SMALLINT,
    target_pop VARCHAR(60), target_pop_description TEXT, geoarea VARCHAR(30),
    age_administered TEXT, source_comment TEXT
);
\copy stg_schedule FROM 'data/processed/clean_vaccine_schedule.csv' WITH (FORMAT csv, HEADER true)

-- ---------------------------------------------------------------- Dimensions

INSERT INTO dim_country (iso3, country_name, who_region)
SELECT DISTINCT iso3, country_name, who_region FROM stg_country
ON CONFLICT (iso3) DO NOTHING;

INSERT INTO dim_antigen (antigen_code, antigen_description)
SELECT DISTINCT antigen_code, antigen_description FROM stg_coverage
ON CONFLICT (antigen_code) DO NOTHING;

INSERT INTO dim_disease (disease_code, disease_description)
SELECT DISTINCT disease_code, disease_description FROM stg_cases
ON CONFLICT (disease_code) DO NOTHING;

INSERT INTO dim_vaccine (vaccine_code, vaccine_description)
SELECT DISTINCT vaccine_code, description FROM stg_introduction
ON CONFLICT (vaccine_code) DO NOTHING;

INSERT INTO dim_vaccine (vaccine_code, vaccine_description)
SELECT DISTINCT vaccine_code, vaccine_description FROM stg_schedule
ON CONFLICT (vaccine_code) DO NOTHING;

-- ---------------------------------------------------------------- Facts

INSERT INTO fact_coverage (iso3, year, antigen_code, coverage_category, coverage_category_description, coverage_pct)
SELECT code, year, antigen_code, coverage_category, coverage_category_description, coverage_pct
FROM stg_coverage;

INSERT INTO fact_reported_cases (iso3, year, disease_code, cases)
SELECT code, year, disease_code, cases
FROM stg_cases;

INSERT INTO fact_incidence_rate (iso3, year, disease_code, denominator, incidence_rate)
SELECT code, year, disease_code, denominator, incidence_rate
FROM stg_incidence;

INSERT INTO fact_vaccine_introduction (iso3, vaccine_code, year, intro)
SELECT iso3, vaccine_code, year, intro
FROM stg_introduction;

INSERT INTO fact_vaccine_schedule (
    iso3, vaccine_code, year, schedule_rounds, target_pop,
    target_pop_description, geoarea, age_administered, source_comment
)
SELECT
    iso3, vaccine_code, year, schedule_rounds, target_pop,
    target_pop_description, geoarea, age_administered, source_comment
FROM stg_schedule;
