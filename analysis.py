"""Aggregation helpers used by the chart builder."""
import pandas as pd

AGGREGATIONS = {"Sum": "sum", "Average": "mean", "Count": "count", "Median": "median", "Min": "min", "Max": "max"}


def numeric_columns(df): return df.select_dtypes(include="number").columns.tolist()
def date_columns(df): return df.select_dtypes(include="datetime").columns.tolist()
def category_columns(df):
    return [c for c in df.columns if c not in numeric_columns(df) and c not in date_columns(df)]


def aggregate(df: pd.DataFrame, x: str, y: str, agg_label: str, group=None) -> pd.DataFrame:
    """Group by x (and optionally group) and aggregate y. Raises ValueError for bad selections."""
    if agg_label not in AGGREGATIONS:
        raise ValueError(f"Unknown aggregation '{agg_label}'.")
    func = AGGREGATIONS[agg_label]
    if func != "count" and not pd.api.types.is_numeric_dtype(df[y]):
        raise ValueError(f"'{agg_label}' needs a numeric column, but '{y}' is not numeric.")
    keys = [x] + ([group] if group and group != x else [])
    if y in keys:  # grouping a column by itself would make a duplicate-column error
        raise ValueError("X/group and Y must be different columns for this chart.")
    return df.groupby(keys, dropna=True, as_index=False)[y].agg(func).sort_values(keys)
