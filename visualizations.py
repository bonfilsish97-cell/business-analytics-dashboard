"""Plotly chart builders. Each returns a figure or raises ValueError with a friendly message."""
import pandas as pd
import plotly.express as px
from utils.analysis import aggregate, numeric_columns

CHART_TYPES = ["Bar", "Line", "Pie", "Histogram", "Scatter", "Box", "Correlation heatmap"]
BLUE = ["#1F4E9E", "#4A90D9", "#8FBCE6", "#5B6B7F", "#B0B8C4", "#0B2A5B"]


def build_chart(df, chart, x=None, y=None, group=None, agg="Sum"):
    if df.empty:
        raise ValueError("No rows to plot. Try resetting your filters.")
    kw = dict(color_discrete_sequence=BLUE, template="plotly_white")

    if chart == "Correlation heatmap":
        nums = numeric_columns(df)
        if len(nums) < 2:
            raise ValueError("A correlation heatmap needs at least two numeric columns.")
        return px.imshow(df[nums].corr(), text_auto=".2f", color_continuous_scale="Blues", zmin=-1, zmax=1)

    if chart == "Histogram":
        if not x or not pd.api.types.is_numeric_dtype(df[x]):
            raise ValueError("Histogram needs a numeric X column.")
        return px.histogram(df, x=x, color=group, **kw)

    if chart == "Scatter":
        for col in (x, y):
            if not col or not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError("Scatter plots need numeric X and Y columns.")
        return px.scatter(df, x=x, y=y, color=group, **kw)

    if chart == "Box":
        if not y or not pd.api.types.is_numeric_dtype(df[y]):
            raise ValueError("Box plots need a numeric Y column.")
        return px.box(df, x=x, y=y, color=group, **kw)

    # Bar / Line / Pie: aggregate first
    if not x or not y:
        raise ValueError("Please choose both X and Y columns.")
    data = aggregate(df, x, y, agg, group)
    if data.empty:
        raise ValueError("Nothing to plot after removing missing values.")
    if chart == "Bar":
        return px.bar(data, x=x, y=y, color=group, barmode="group", **kw)
    if chart == "Line":
        return px.line(data, x=x, y=y, color=group, markers=True, **kw)
    if chart == "Pie":
        return px.pie(data, names=x, values=y, **kw)
    raise ValueError(f"Unknown chart type '{chart}'.")
