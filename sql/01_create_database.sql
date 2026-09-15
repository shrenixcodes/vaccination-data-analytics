-- Database: vaccination_analytics
-- Engine: PostgreSQL (chosen as a practical, widely used, free RDBMS with
-- strong window-function and CTE support, which the analysis queries in
-- 06_analysis_queries.sql rely on).
--
-- Run this file connected to the default "postgres" database, then
-- reconnect to vaccination_analytics before running 02-07.

CREATE DATABASE vaccination_analytics
    ENCODING 'UTF8'
    TEMPLATE template0;

-- \c vaccination_analytics
