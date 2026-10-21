"""Creates synthetic sample data (no real company data). Run once: python make_sample_data.py"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 500
dates = pd.date_range("2024-01-01", "2025-12-31", periods=n).normalize()
regions = rng.choice(["North", "South", "East", "West"], n)
categories = rng.choice(["Electronics", "Furniture", "Office Supplies", "Clothing"], n, p=[.3, .2, .3, .2])
channels = rng.choice(["Online", "Retail", "Wholesale"], n, p=[.5, .35, .15])
units = rng.integers(1, 30, n)
unit_price = np.round(rng.uniform(5, 400, n), 2)
revenue = np.round(units * unit_price * rng.uniform(0.85, 1.0, n), 2)
cost = np.round(revenue * rng.uniform(0.5, 0.85, n), 2)

df = pd.DataFrame({
    "order_id": range(1001, 1001 + n),
    "order_date": dates,
    "region": regions,
    "category": categories,
    "sales_channel": channels,
    "units_sold": units,
    "unit_price": unit_price,
    "revenue": revenue,
    "cost": cost,
    "customer_rating": np.round(rng.uniform(1, 5, n), 1),
})
# Add a few realistic problems so the cleaning features have something to find
df.loc[rng.choice(n, 15, replace=False), "customer_rating"] = np.nan
df.loc[rng.choice(n, 8, replace=False), "region"] = np.nan
df = pd.concat([df, df.sample(5, random_state=1)], ignore_index=True)  # 5 duplicate rows
df.to_csv("data/sample_business_data.csv", index=False)
print("Wrote data/sample_business_data.csv", df.shape)
