# Power BI

## Status

**`pbip/VaccinationAnalytics.pbip` is a real Power BI Project** — a
hand-authored TMDL semantic model (all 10 tables, 15 relationships, 11
DAX measures, reading directly from `data/raw/`/`data/processed/`) plus a
minimal 7-page report shell, openable directly in Power BI Desktop.

Two honest caveats:

1. **Not verified by opening it myself.** This environment has no Windows
   desktop UI automation available (only a shell and a web browser), so
   I could not click through Desktop to confirm the project loads
   without error. The M/TMDL was written carefully and checked for valid
   JSON, consistent tab indentation, and correct (non-doubled) file-path
   escaping, but the *first real test* is you opening it. If Desktop
   reports an error on open, it's almost certainly a small, fixable
   syntax issue — please report it back if you hit one.
2. **No `.pbix` file is included.** `.pbix` is a compiled binary format;
   the standard way to produce one is to open the `.pbip` project in
   Desktop and use **File → Save As → Power BI file (.pbix)**. There is
   no way to produce a `.pbix` directly without Desktop.

## Opening the project

1. Open `powerbi/pbip/VaccinationAnalytics.pbip` in Power BI Desktop
   (double-click it, or File → Open in Desktop).
2. Desktop will prompt for the `RepoRootPath` parameter on first load (or:
   Transform Data → Manage Parameters). Set it to the absolute path of
   your local clone of this repository, e.g.
   `C:\Users\you\vaccination-data-analytics` — **no trailing backslash**.
3. Click **Refresh** to load all 10 tables from the CSVs in `data/raw/`
   and `data/processed/`.
4. The 7 report pages already exist (named per
   `dashboard_specification.md`) but are empty canvases — add the visuals
   listed in that spec via the GUI. The data model and all 11 measures are
   already there, so this is materially faster than starting from zero.
5. **File → Save As → Power BI file (.pbix)** once you're happy with it.

## What's in `pbip/`

| Path | Contents |
|---|---|
| `VaccinationAnalytics.SemanticModel/definition/tables/*.tmdl` | 5 dimension + 5 fact tables + a hidden `_Measures` table, matching `data_model.md` exactly |
| `VaccinationAnalytics.SemanticModel/definition/relationships.tmdl` | All 15 relationships (dimension → fact, single-direction), including the inactive `FactIntroduction.year → DimYear.year` link noted in `data_model.md` |
| `VaccinationAnalytics.SemanticModel/definition/tables/_Measures.tmdl` | All 11 DAX measures from `dax_measures.md`, verbatim |
| `VaccinationAnalytics.SemanticModel/definition/expressions.tmdl` | The `RepoRootPath` text parameter every table's Power Query source reads from |
| `VaccinationAnalytics.Report/` | 7 empty, named, correctly-ordered pages — no visuals (see caveat above) |

## Other documentation (still the source of truth for *what* to build)

- [`data_model.md`](data_model.md) — the star-schema design the TMDL
  implements.
- [`dax_measures.md`](dax_measures.md) — the same 11 measures, with
  prose explanation of each.
- [`dashboard_specification.md`](dashboard_specification.md) —
  page-by-page visual specification for the empty pages above.

## Screenshots

`screenshots/` is still empty — producing one requires actually opening
and populating the report, which is the one step this project could not
complete without Desktop UI automation.
