# Power BI

## Status

Power BI Desktop is not available in the environment this project was
built in, and there is no way to programmatically assemble a `.pbix` file
without it (the format has no public write API; the Power BI REST API can
only push data into an already-authored report, not author one). **No
`.pbix` file is included in this repository.**

What *is* included is everything needed to build the report in Power BI
Desktop in under an hour:

- [`data_model.md`](data_model.md) — the star-schema data model, table
  relationships, and cardinality/filter-direction settings.
- [`dax_measures.md`](dax_measures.md) — every DAX measure used, with its
  full expression.
- [`dashboard_specification.md`](dashboard_specification.md) — page-by-page
  visual specification (what chart, what fields, what filters).

## Reproduction steps

1. Load the SQL database (`sql/01`–`05`), or import the CSVs directly from
   `data/processed/` and `data/raw/who_country_reference.csv` if you don't
   want to stand up PostgreSQL.
2. In Power BI Desktop: **Get Data → PostgreSQL database** (or **Text/CSV**
   for the file-based route), and load the 6 views from `sql/07_views.sql`
   (or the equivalent processed CSVs).
3. Build the relationships described in `data_model.md`.
4. Create the measures in `dax_measures.md` in a dedicated measures table.
5. Build each page following `dashboard_specification.md`.

## Screenshots

`screenshots/` is empty for the same reason: it would require an actually
rendered report, which requires the Desktop app. Do not interpret an empty
folder as missing effort — it is disclosed here rather than filled with
placeholder images.
