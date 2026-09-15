-- Referential integrity and business-rule constraints.

-- ---------------------------------------------------------------- Foreign keys

ALTER TABLE fact_coverage
    ADD CONSTRAINT fk_coverage_country FOREIGN KEY (iso3) REFERENCES dim_country (iso3),
    ADD CONSTRAINT fk_coverage_antigen FOREIGN KEY (antigen_code) REFERENCES dim_antigen (antigen_code);

ALTER TABLE fact_reported_cases
    ADD CONSTRAINT fk_cases_country FOREIGN KEY (iso3) REFERENCES dim_country (iso3),
    ADD CONSTRAINT fk_cases_disease FOREIGN KEY (disease_code) REFERENCES dim_disease (disease_code);

ALTER TABLE fact_incidence_rate
    ADD CONSTRAINT fk_incidence_country FOREIGN KEY (iso3) REFERENCES dim_country (iso3),
    ADD CONSTRAINT fk_incidence_disease FOREIGN KEY (disease_code) REFERENCES dim_disease (disease_code);

ALTER TABLE fact_vaccine_introduction
    ADD CONSTRAINT fk_intro_country FOREIGN KEY (iso3) REFERENCES dim_country (iso3),
    ADD CONSTRAINT fk_intro_vaccine FOREIGN KEY (vaccine_code) REFERENCES dim_vaccine (vaccine_code);

ALTER TABLE fact_vaccine_schedule
    ADD CONSTRAINT fk_schedule_country FOREIGN KEY (iso3) REFERENCES dim_country (iso3),
    ADD CONSTRAINT fk_schedule_vaccine FOREIGN KEY (vaccine_code) REFERENCES dim_vaccine (vaccine_code);

-- ---------------------------------------------------------------- Uniqueness
-- Matches the deduplication keys used in src/data_cleaning.py, so the
-- database enforces the same grain the Python pipeline already validated.

ALTER TABLE fact_coverage
    ADD CONSTRAINT uq_coverage UNIQUE (iso3, year, antigen_code, coverage_category);

ALTER TABLE fact_reported_cases
    ADD CONSTRAINT uq_reported_cases UNIQUE (iso3, year, disease_code);

ALTER TABLE fact_incidence_rate
    ADD CONSTRAINT uq_incidence_rate UNIQUE (iso3, year, disease_code);

ALTER TABLE fact_vaccine_introduction
    ADD CONSTRAINT uq_vaccine_introduction UNIQUE (iso3, vaccine_code);

ALTER TABLE fact_vaccine_schedule
    ADD CONSTRAINT uq_vaccine_schedule UNIQUE (iso3, vaccine_code, year);

-- ---------------------------------------------------------------- Business-rule checks

ALTER TABLE dim_country
    ADD CONSTRAINT ck_country_region CHECK (who_region IN ('AFR','AMR','SEAR','EUR','EMR','WPR') OR who_region IS NULL);

ALTER TABLE fact_coverage
    ADD CONSTRAINT ck_coverage_pct CHECK (coverage_pct BETWEEN 0 AND 100),
    ADD CONSTRAINT ck_coverage_year CHECK (year BETWEEN 1974 AND 2026);

ALTER TABLE fact_reported_cases
    ADD CONSTRAINT ck_cases_nonneg CHECK (cases IS NULL OR cases >= 0),
    ADD CONSTRAINT ck_cases_year CHECK (year BETWEEN 1974 AND 2026);

ALTER TABLE fact_incidence_rate
    ADD CONSTRAINT ck_incidence_nonneg CHECK (incidence_rate >= 0),
    ADD CONSTRAINT ck_incidence_denominator CHECK (denominator > 0);

ALTER TABLE fact_vaccine_introduction
    ADD CONSTRAINT ck_intro_value CHECK (intro IN ('YES', 'NO')),
    ADD CONSTRAINT ck_intro_year_consistency CHECK (intro = 'NO' OR year IS NOT NULL);

ALTER TABLE fact_vaccine_schedule
    ADD CONSTRAINT ck_schedule_rounds CHECK (schedule_rounds > 0);
