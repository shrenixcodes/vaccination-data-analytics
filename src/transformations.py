"""Reusable analytical transformations used by the EDA notebook and reports.

Kept as plain functions over DataFrames/Series so the same logic can be
unit tested (tests/test_transformations.py) and reused in the notebook
without duplicating formulas.
"""

from __future__ import annotations

import pandas as pd
from scipy import stats


def dose_dropoff_rate(first_dose_coverage: float, later_dose_coverage: float) -> float:
    """Percentage of children who received the first dose but not the
    later dose, relative to the first-dose total. Returns NaN when the
    first-dose coverage is 0 (division is undefined)."""
    if first_dose_coverage in (0, None) or pd.isna(first_dose_coverage):
        return float("nan")
    return (first_dose_coverage - later_dose_coverage) / first_dose_coverage * 100


def year_over_year_change(series_by_year: pd.Series) -> pd.Series:
    """Percentage change vs. the prior year, for a Series indexed by year."""
    return series_by_year.sort_index().pct_change() * 100


def coverage_gap(coverage_pct: pd.Series, target_pct: float) -> pd.Series:
    """Positive value = coverage above target; negative = shortfall."""
    return coverage_pct - target_pct


def pearson_and_spearman(x: pd.Series, y: pd.Series) -> dict:
    """Paired-drop NaNs, then compute both correlation coefficients.
    Returns None values when fewer than 3 paired observations remain."""
    paired = pd.DataFrame({"x": x, "y": y}).dropna()
    if len(paired) < 3:
        return {"n": len(paired), "pearson_r": None, "pearson_p": None, "spearman_r": None, "spearman_p": None}
    pearson_r, pearson_p = stats.pearsonr(paired["x"], paired["y"])
    spearman_r, spearman_p = stats.spearmanr(paired["x"], paired["y"])
    return {
        "n": len(paired),
        "pearson_r": pearson_r,
        "pearson_p": pearson_p,
        "spearman_r": spearman_r,
        "spearman_p": spearman_p,
    }


def pre_post_comparison(df: pd.DataFrame, year_col: str, value_col: str, pivot_year: int) -> dict:
    """Mean of value_col strictly before vs. at-or-after pivot_year."""
    before = df.loc[df[year_col] < pivot_year, value_col].dropna()
    after = df.loc[df[year_col] >= pivot_year, value_col].dropna()
    return {
        "pivot_year": pivot_year,
        "mean_before": before.mean() if len(before) else None,
        "mean_after": after.mean() if len(after) else None,
        "n_before": len(before),
        "n_after": len(after),
    }


def regional_average(df: pd.DataFrame, region_col: str, value_col: str) -> pd.Series:
    return df.groupby(region_col)[value_col].mean().sort_values(ascending=False)


def country_ranking(df: pd.DataFrame, country_col: str, value_col: str, ascending: bool = False) -> pd.DataFrame:
    ranked = df.groupby(country_col)[value_col].mean().sort_values(ascending=ascending)
    return ranked.reset_index()
