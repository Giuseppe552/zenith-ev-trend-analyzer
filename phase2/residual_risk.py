#!/usr/bin/env python3
import sys, math, re
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def parse_year(s):
    try: return int(float(s))
    except: return None

def estimate_age_years(year, ref_year=2025):
    if year is None: return None
    return max(0.0, ref_year - year)

def clean_price(x):
    if x is None: return None
    s = re.sub(r"[£$,]", "", str(x)).strip()
    try:
        v = float(s)
        return v if v > 0 else None
    except: return None

def mileage_bucket(m):
    try: m = float(m)
    except: return "unknown"
    if m < 10000: return "0-10k"
    if m < 20000: return "10-20k"
    if m < 40000: return "20-40k"
    if m < 60000: return "40-60k"
    return "60k+"

def fit_curve(age, price):
    import numpy as np
    x = np.array(age, dtype=float); y = np.array(price, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y) & (y > 0)
    x, y = x[mask], y[mask]
    if len(x) < 8: return None
    X = np.column_stack([np.ones_like(x), x])
    beta, *_ = np.linalg.lstsq(X, np.log(y), rcond=None)
    ln_a, b = beta
    return float(np.exp(ln_a)), float(b)

def predict_price(a, b, age):
    return float(a * math.exp(b * age))

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 residual_risk.py data/ev_used_listings.csv"); sys.exit(1)
    src = Path(sys.argv[1])
    if not src.exists():
        print(f"File not found: {src}"); sys.exit(1)

    # always write outputs into this script's folder (phase2/)
    out_dir = Path(__file__).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(src)
    required = ["Make","Model","Year","Mileage","AskingPrice"]
    for col in required:
        if col not in df.columns: raise RuntimeError(f"Missing column: {col}")

    df["YearClean"]   = df["Year"].map(parse_year)
    df["AgeYears"]    = df["YearClean"].map(estimate_age_years)
    df["MileageBucket"]= df["Mileage"].map(mileage_bucket)
    df["Price"]       = df["AskingPrice"].map(clean_price)
    df = df.dropna(subset=["Make","Model","AgeYears","Price"]).copy()

    recs, curves = [], {}
    for (mk, md), g in df.groupby(["Make","Model"]):
        ab = fit_curve(g["AgeYears"], g["Price"])
        if ab is None: continue
        a, b = ab; curves[(mk,md)] = (a,b)
        preds = {f"RV_{h}y_base": predict_price(a,b,h) for h in [3,4,5]}
        scen = {}
        for h in [3,4,5]:
            base = preds[f"RV_{h}y_base"]
            scen[f"RV_{h}y_opt"]    = base * 1.05
            scen[f"RV_{h}y_cons"]   = base * 0.90
            scen[f"RV_{h}y_stress"] = base * 0.80
        recs.append({"Make":mk, "Model":md, "n_samples":len(g), **preds, **scen})

    rv_df = pd.DataFrame(recs).sort_values(["Make","Model","n_samples"], ascending=[True,True,False])
    rv_df.to_csv(out_dir / "rv_forecasts.csv", index=False)

    xs = np.linspace(0,8,81)
    import numpy as np
    plt.figure(figsize=(10,6))
    top = df.groupby(["Make","Model"]).size().sort_values(ascending=False).head(6).index.tolist()
    lines = 0
    for key in top:
        if key not in curves: continue
        a,b = curves[key]
        ys = [predict_price(a,b,x) for x in xs]
        mk, md = key
        plt.plot(xs, ys, label=f"{mk} {md}"); lines += 1
    if lines == 0:
        plt.text(0.5,0.5,"Insufficient data to plot curves.\nAdd rows to data/ev_used_listings.csv", ha="center")
    plt.title("Estimated EV Depreciation Curves (example models)")
    plt.xlabel("Age (years)"); plt.ylabel("Estimated Price (£)")
    plt.legend(); plt.tight_layout()
    plt.savefig(out_dir / "depreciation_curves.png", dpi=180); plt.close()

    lines = []
    lines.append("EV Residual Value Risk — Summary")
    lines.append("================================")
    lines.append(f"Input: {src.name}")
    lines.append(f"Models fitted: {len(curves)}")
    if not rv_df.empty:
        r = rv_df.iloc[0]
        lines.append(f"Example: {r['Make']} {r['Model']} (n={int(r['n_samples'])})")
        for h in [3,4,5]:
            lines.append(f"  RV @ {h}y (base/cons/stress): £{r[f'RV_{h}y_base']:.0f} / £{r[f'RV_{h}y_cons']:.0f} / £{r[f'RV_{h}y_stress']:.0f}")
    (out_dir / "rv_report.txt").write_text("\n".join(lines), encoding="utf-8")
    print("Done.\nWrote:", out_dir / "rv_forecasts.csv", "\n", out_dir / "depreciation_curves.png", "\n", out_dir / "rv_report.txt")

if __name__ == "__main__":
    main()
