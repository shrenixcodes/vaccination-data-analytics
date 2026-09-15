# DAX Measures

All measures reference the table names in `data_model.md`. Create these in
a dedicated "Measures" table rather than scattering them across the fact
tables.

## Coverage measures

```dax
Average Coverage =
AVERAGE ( FactCoverage[coverage_pct] )
```

```dax
Coverage Gap (95% target) =
[Average Coverage] - 95
```
Positive = above target, negative = shortfall. Used for the measles-target
pages; the 95 can be parameterized per-antigen if other targets are added.

```dax
Countries Below Target =
CALCULATE (
    DISTINCTCOUNT ( FactCoverage[iso3] ),
    FactCoverage[coverage_pct] < 95
)
```

```dax
YoY Coverage Change =
VAR CurrentAvg = [Average Coverage]
VAR PriorAvg =
    CALCULATE (
        [Average Coverage],
        DimYear[year] = SELECTEDVALUE ( DimYear[year] ) - 1
    )
RETURN
    DIVIDE ( CurrentAvg - PriorAvg, PriorAvg )
```
Requires `DimYear[year]` on the axis (e.g. a line chart X-axis), since it
reads `SELECTEDVALUE` in the current filter context.

## Case / incidence measures

```dax
Total Reported Cases =
SUM ( FactCases[cases] )
```

```dax
Average Incidence Rate =
AVERAGE ( FactIncidence[incidence_rate] )
```

```dax
Disease Case Change % =
VAR CurrentCases = [Total Reported Cases]
VAR PriorCases =
    CALCULATE (
        [Total Reported Cases],
        DimYear[year] = SELECTEDVALUE ( DimYear[year] ) - 1
    )
RETURN
    DIVIDE ( CurrentCases - PriorCases, PriorCases )
```

## Dose / series measures

```dax
DTP1 Coverage =
CALCULATE ( [Average Coverage], FactCoverage[antigen_code] = "DTP1" )
```

```dax
DTP3 Coverage =
CALCULATE ( [Average Coverage], FactCoverage[antigen_code] = "DTP3" )
```

```dax
Dose Drop-off Rate (DTP1->DTP3) =
DIVIDE ( [DTP1 Coverage] - [DTP3 Coverage], [DTP1 Coverage] )
```

```dax
MCV1 Coverage =
CALCULATE ( [Average Coverage], FactCoverage[antigen_code] = "MCV1" )
```

```dax
MCV2 Coverage =
CALCULATE ( [Average Coverage], FactCoverage[antigen_code] = "MCV2" )
```

```dax
Booster Uptake (MCV2) =
[MCV2 Coverage]
```
Named separately from `MCV2 Coverage` so a KPI card can be labeled
"Booster Uptake" without the underlying formula changing if the
second-dose antigen used for this KPI is revisited later.

## Target-achievement measures

```dax
Target Achievement % (95%, MCV1) =
VAR EligibleCountries =
    CALCULATE (
        DISTINCTCOUNT ( FactCoverage[iso3] ),
        FactCoverage[antigen_code] = "MCV1"
    )
VAR AtTarget =
    CALCULATE (
        DISTINCTCOUNT ( FactCoverage[iso3] ),
        FactCoverage[antigen_code] = "MCV1",
        FactCoverage[coverage_pct] >= 95
    )
RETURN
    DIVIDE ( AtTarget, EligibleCountries )
```

```dax
Measles 95% Target Gap =
CALCULATE ( [Coverage Gap (95% target)], FactCoverage[antigen_code] = "MCV1" )
```

## Notes

- Measures deliberately number under 15: every one maps to a specific
  brief requirement or a visual in `dashboard_specification.md`. No
  measure was added purely to pad the model.
- `FactCases[cases]` and `FactIncidence[incidence_rate]` contain genuine
  blanks (see `data_model.md`); `SUM`/`AVERAGE` skip blanks by default in
  DAX, so no `COALESCE`/`IFERROR` wrapping is needed or used.
