#!/usr/bin/env python3
"""
Generates a synthetic-but-realistic used EV listings file for RV modelling.

Design choices:
- Models reflect UK fleet mix seen commonly in leasing portfolios.
- Price decays exponentially with age (industry-standard shape), plus a mileage penalty and noise.
- Annual mileage ~ N(11k, 3k), truncated at [5k, 25k], to mimic fleet/private spread.
- Noise term (~±5%) captures market dispersion, options, condition.
- Prices are clamped to a floor so old EVs don't go absurdly low.

Output: phase2/data/ev_used_listings.csv
Columns: Make,Model,Year,Mileage,AskingPrice
"""
from pathlib import Path
import numpy as np
import pandas as pd
rng = np.random.default_rng(42)

models = [
    # (Make, Model, base_new_price, decay_rate_per_year)
    ("Tesla",   "Model 3",        42000, 0.18),
    ("Tesla",   "Model Y",        47000, 0.17),
    ("Nissan",  "Leaf",           30000, 0.20),
    ("BMW",     "i3",             36000, 0.19),
    ("Hyundai", "Kona Electric",  34000, 0.18),
    ("Kia",     "e-Niro",         36000, 0.18),
    ("VW",      "ID.3",           36000, 0.18),
    ("Renault", "Zoe",            26000, 0.21),
]

def annual_miles_sample(n):
    # Truncated normal ~ N(11k, 3k), clamp to [5k, 25k]
    miles = rng.normal(11000, 3000, size=n)
    return np.clip(miles, 5000, 25000)

def price_from_age_miles(p0, k, age_years, miles_total):
    # Base exponential depreciation
    base = p0 * np.exp(-k * age_years)
    # Mileage penalty ~ £1.5 per 1k miles beyond 5k/year baseline
    # Convert to per-1k miles penalty
    penalty_per_k = 1.5
    penalty = penalty_per_k * (miles_total / 1000.0)
    # Noise ±5%
    noise = rng.normal(0, 0.05) * base
    price = base - penalty + noise
    return max(price, 2500.0)  # floor

def make_rows(n_per_model=120):
    rows = []
    # We simulate listings from 2016–2024 model years
    years = np.arange(2016, 2025)
    for (mk, md, p0, k) in models:
        for _ in range(n_per_model):
            year = int(rng.choice(years))
            age = 2025 - year
            # annual mileage draws by vehicle, then multiply by age
            ann_miles = float(annual_miles_sample(1)[0])
            mileage = int(ann_miles * max(age, 0.5))
            price = price_from_age_miles(p0, k, age, mileage)
            rows.append({
                "Make": mk,
                "Model": md,
                "Year": year,
                "Mileage": mileage,
                "AskingPrice": round(price, 0)
            })
    return rows

def main():
    out = Path("phase2/data/ev_used_listings.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(make_rows(n_per_model=140))
    # Shuffle for realism
    df = df.sample(frac=1.0, random_state=7).reset_index(drop=True)
    df.to_csv(out, index=False)
    print(f"Wrote {out} with {len(df)} rows")

if __name__ == "__main__":
    main()
