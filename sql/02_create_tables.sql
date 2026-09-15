-- Normalized schema for vaccination_analytics.
--
-- Design: one dimension table per real-world entity shared across the raw
-- files (country, disease, antigen, vaccine), plus one fact table per
-- measurement type. This avoids the "one table per CSV" anti-pattern --
-- for example Name/Country_Name/WHO_Region appear in four of the five raw
-- files but are stored once, in dim_country.
--
-- Primary keys are declared here; foreign keys, uniqueness, and business-
-- rule CHECK constraints are added in 03_constraints.sql so referential
-- integrity is easy to review as its own unit.

-- ---------------------------------------------------------------- Dimensions

CREATE TABLE dim_country (
    iso3        CHAR(3)      PRIMARY KEY,
    country_name VARCHAR(150) NOT NULL,
    who_region  CHAR(4)      -- NULL for the handful of GHO entries that are
                              -- not assigned to one of the 6 WHO regions
                              -- (e.g. disputed territories); see docs/limitations.md
);

CREATE TABLE dim_disease (
    disease_code        VARCHAR(30)  PRIMARY KEY,
    disease_description VARCHAR(150) NOT NULL
);

CREATE TABLE dim_antigen (
    antigen_code        VARCHAR(20)  PRIMARY KEY,
    antigen_description VARCHAR(150) NOT NULL
);

CREATE TABLE dim_vaccine (
    vaccine_code        VARCHAR(20)  PRIMARY KEY,
    vaccine_description VARCHAR(150) NOT NULL
);

-- ---------------------------------------------------------------- Facts

-- Real data (WHO GHO API). One row per country/year/antigen/estimate type.
CREATE TABLE fact_coverage (
    coverage_id                    SERIAL PRIMARY KEY,
    iso3                           CHAR(3)     NOT NULL,
    year                           SMALLINT    NOT NULL,
    antigen_code                   VARCHAR(20) NOT NULL,
    coverage_category              VARCHAR(30) NOT NULL,
    coverage_category_description  VARCHAR(150),
    coverage_pct                   NUMERIC(5,2) NOT NULL
);

-- Real data (WHO GHO API). One row per country/year/disease.
CREATE TABLE fact_reported_cases (
    case_id      SERIAL PRIMARY KEY,
    iso3         CHAR(3)     NOT NULL,
    year         SMALLINT    NOT NULL,
    disease_code VARCHAR(30) NOT NULL,
    cases        NUMERIC(12,0)  -- nullable: country did not report that year
);

-- Real data, derived: cases (WHO) / population (World Bank) * 100,000.
CREATE TABLE fact_incidence_rate (
    incidence_id    SERIAL PRIMARY KEY,
    iso3            CHAR(3)     NOT NULL,
    year            SMALLINT    NOT NULL,
    disease_code    VARCHAR(30) NOT NULL,
    denominator     NUMERIC(15,0) NOT NULL,
    incidence_rate  NUMERIC(12,4) NOT NULL
);

-- SIMULATED data (see data/README.md). One row per country/vaccine.
CREATE TABLE fact_vaccine_introduction (
    introduction_id SERIAL PRIMARY KEY,
    iso3            CHAR(3)     NOT NULL,
    vaccine_code    VARCHAR(20) NOT NULL,
    year            SMALLINT,          -- NULL when intro = 'NO'
    intro           VARCHAR(3)  NOT NULL
);

-- SIMULATED data (see data/README.md). One row per country/vaccine.
CREATE TABLE fact_vaccine_schedule (
    schedule_id             SERIAL PRIMARY KEY,
    iso3                    CHAR(3)     NOT NULL,
    vaccine_code            VARCHAR(20) NOT NULL,
    year                    SMALLINT    NOT NULL,
    schedule_rounds         SMALLINT    NOT NULL,
    target_pop              VARCHAR(60) NOT NULL,
    target_pop_description  VARCHAR(150),
    geoarea                 VARCHAR(30),
    age_administered        VARCHAR(150),
    source_comment          VARCHAR(150)
);
