import math

import pandas as pd

from src.transformations import (
    coverage_gap,
    dose_dropoff_rate,
    pearson_and_spearman,
    pre_post_comparison,
    regional_average,
    year_over_year_change,
)


def test_dose_dropoff_rate_basic():
    assert dose_dropoff_rate(100.0, 80.0) == 20.0


def test_dose_dropoff_rate_zero_first_dose_is_nan():
    assert math.isnan(dose_dropoff_rate(0.0, 50.0))


def test_year_over_year_change():
    series = pd.Series([50.0, 100.0, 150.0], index=[2018, 2019, 2020])
    result = year_over_year_change(series)
    assert result.loc[2019] == 100.0
    assert result.loc[2020] == 50.0


def test_coverage_gap_positive_and_negative():
    result = coverage_gap(pd.Series([98.0, 80.0]), target_pct=95.0)
    assert result.iloc[0] == 3.0
    assert result.iloc[1] == -15.0


def test_pearson_and_spearman_perfect_positive_correlation():
    x = pd.Series([1, 2, 3, 4, 5])
    y = pd.Series([2, 4, 6, 8, 10])
    result = pearson_and_spearman(x, y)
    assert result["n"] == 5
    assert round(result["pearson_r"], 4) == 1.0
    assert round(result["spearman_r"], 4) == 1.0


def test_pearson_and_spearman_insufficient_data():
    result = pearson_and_spearman(pd.Series([1, None]), pd.Series([1, 2]))
    assert result["pearson_r"] is None


def test_pre_post_comparison():
    df = pd.DataFrame({"year": [2015, 2016, 2019, 2020], "value": [10.0, 20.0, 40.0, 60.0]})
    result = pre_post_comparison(df, "year", "value", pivot_year=2018)
    assert result["mean_before"] == 15.0
    assert result["mean_after"] == 50.0
    assert result["n_before"] == 2
    assert result["n_after"] == 2


def test_regional_average():
    df = pd.DataFrame({"region": ["AFR", "AFR", "EUR"], "value": [50.0, 70.0, 90.0]})
    result = regional_average(df, "region", "value")
    assert result.loc["EUR"] == 90.0
    assert result.loc["AFR"] == 60.0
