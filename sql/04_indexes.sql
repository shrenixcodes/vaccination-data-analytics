-- Indexes beyond what the UNIQUE constraints in 03_constraints.sql already
-- provide. Every fact table is queried heavily by year and by country in
-- the analysis queries and Power BI model, so both get a dedicated index;
-- the UNIQUE constraints already cover the (iso3, year, ...) composite
-- case, so these add the reverse access paths.

CREATE INDEX idx_coverage_year ON fact_coverage (year);
CREATE INDEX idx_coverage_antigen ON fact_coverage (antigen_code);

CREATE INDEX idx_cases_year ON fact_reported_cases (year);
CREATE INDEX idx_cases_disease ON fact_reported_cases (disease_code);

CREATE INDEX idx_incidence_year ON fact_incidence_rate (year);
CREATE INDEX idx_incidence_disease ON fact_incidence_rate (disease_code);

CREATE INDEX idx_intro_vaccine ON fact_vaccine_introduction (vaccine_code);

CREATE INDEX idx_schedule_vaccine ON fact_vaccine_schedule (vaccine_code);

CREATE INDEX idx_country_region ON dim_country (who_region);
