#!/usr/bin/env python3
import sys, re
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt

def detect_quarter_cols(cols):
    pat = re.compile(r"^\s*(20\d{2})\s*Q([1-4])\s*$")
    out = []
    for c in cols:
        if isinstance(c, str) and pat.match(c):
            out.append(c)
    return out

def normalize_fuel(s):
    if not isinstance(s, str): return None
    t = s.strip().lower()
    if "battery" in t or "bev" in t: return "Battery Electric"
    if "plug-in" in t or "plugin" in t or "phev" in t: return "Plug-in Hybrid"
    return None

def normalize_keepership(s):
    if not isinstance(s, str): return None
    t = s.strip().lower()
    if "company" in t: return "Company"
    if "private" in t: return "Private"
    return None

def quarter_to_period(qstr):
    y, q = re.match(r"^\s*(20\d{2})\s*Q([1-4])\s*$", qstr).groups()
    return pd.Period(freq="Q", year=int(y), quarter=int(q))

def pct_change(first, last):
    if first in (None, 0) or last is None: return None
    return (last - first) / first * 100.0

def safe_div(num, den):
    try:
        if den == 0: return None
        return num / den
    except Exception:
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 ev_trends.py /path/to/df_VEH0145.csv")
        sys.exit(1)
    src = Path(sys.argv[1])
    if not src.exists():
        print(f"File not found: {src}")
        sys.exit(1)

    print("Loading CSV (this can take a minute)...")
    df = pd.read_csv(src, low_memory=False, dtype=str)

    quarter_cols = detect_quarter_cols(df.columns)
    if not quarter_cols:
        # fallback: pick columns that contain “YYYY Q#”
        quarter_cols = [c for c in df.columns if isinstance(c, str) and re.search(r"20\d{2}\s*Q[1-4]", c)]
    if not quarter_cols:
        raise RuntimeError("Couldn't find quarter columns like '2015 Q1' in header.")

    colmap = {c.lower(): c for c in df.columns}
    fuel_col = colmap.get("fuel")
    keep_col = colmap.get("keepership")
    if fuel_col is None or keep_col is None:
        raise RuntimeError("Missing expected columns 'Fuel' and/or 'Keepership'.")

    base_cols = [fuel_col, keep_col] + quarter_cols
    df_small = df[base_cols].copy()

    df_small["FuelNorm"] = df_small[fuel_col].map(normalize_fuel)
    df_small["KeeperNorm"] = df_small[keep_col].map(normalize_keepership)
    df_small = df_small.dropna(subset=["FuelNorm", "KeeperNorm"])

    long = df_small.melt(
        id_vars=["FuelNorm", "KeeperNorm"],
        value_vars=quarter_cols,
        var_name="Quarter",
        value_name="Vehicles"
    )

    def to_num(x):
        if x is None: return 0.0
        if isinstance(x, (int, float)): return float(x)
        x = str(x).strip()
        if x in ("[c]", "[x]", "[z]", ""): return 0.0
        try: return float(x)
        except: return 0.0

    long["Vehicles"] = long["Vehicles"].map(to_num)
    long["Period"] = long["Quarter"].map(quarter_to_period)
    long["Year"] = long["Period"].dt.year
    long = long[(long["Year"] >= 2015) & (long["Year"] <= 2025)].copy()

    agg = (
        long.groupby(["FuelNorm", "KeeperNorm", "Period"], as_index=False)["Vehicles"]
            .sum()
            .sort_values(["FuelNorm", "KeeperNorm", "Period"])
    )

    latest_period = agg["Period"].max()
    first_period = agg["Period"].min()

    growth_rows = []
    for (fuel, keep), g in agg.groupby(["FuelNorm", "KeeperNorm"]):
        g = g.set_index("Period").sort_index()
        first = g.loc[first_period, "Vehicles"] if first_period in g.index else None
        last = g.loc[latest_period, "Vehicles"] if latest_period in g.index else None
        change_pct = pct_change(first, last)
        growth_rows.append({
            "Fuel": fuel,
            "Keeper": keep,
            "FirstPeriod": str(first_period),
            "LatestPeriod": str(latest_period),
            "FirstVehicles": 0 if first is None else int(round(first)),
            "LatestVehicles": 0 if last is None else int(round(last)),
            "PctChange": None if change_pct is None else round(change_pct, 2),
        })
    growth_df = pd.DataFrame(growth_rows)

    latest_slice = agg[agg["Period"] == latest_period]
    latest_totals = latest_slice.groupby("KeeperNorm")["Vehicles"].sum()
    latest_all = latest_totals.sum()
    company_share = safe_div(latest_totals.get("Company", 0.0), latest_all)
    company_share_pct = None if company_share is None else round(company_share * 100, 2)

    out_timeseries = Path("cleaned_ev_timeseries.csv")
    agg.to_csv(out_timeseries, index=False)

    plt.figure(figsize=(10, 6))
    for fuel in ["Battery Electric", "Plug-in Hybrid"]:
        for keep in ["Company", "Private"]:
            sub = agg[(agg["FuelNorm"] == fuel) & (agg["KeeperNorm"] == keep)]
            if sub.empty: 
                continue
            x = sub["Period"].dt.to_timestamp(how="end")
            y = sub["Vehicles"]
            plt.plot(x, y, label=f"{fuel} – {keep}")
    plt.title("UK Plug-in Vehicles by Fuel & Keepership (2015–2025)")
    plt.xlabel("Quarter"); plt.ylabel("Licensed Vehicles")
    plt.legend(); plt.tight_layout()
    plt.savefig("EV_growth.png", dpi=180)
    plt.close()

    lines = []
    lines.append("Fleet EV Trend Analyzer — Summary")
    lines.append("================================")
    lines.append("Source: DfT df_VEH0145 (Licensed plug-in vehicles), aggregated across UK LSOAs.")
    lines.append(f"Period covered: {first_period} to {latest_period}\n")
    lines.append("Growth by Fuel & Keepership:")
    for _, r in growth_df.sort_values(["Fuel", "Keeper"]).iterrows():
        pct = "n/a" if r["PctChange"] is None else f"{r['PctChange']}%"
        lines.append(f"- {r['Fuel']} ({r['Keeper']}): {r['FirstVehicles']} → {r['LatestVehicles']} vehicles ({pct})")
    share_txt = "n/a" if company_share_pct is None else f"{company_share_pct}%"
    lines.append(f"\nCompany-kept share of all plug-in vehicles (latest quarter): {share_txt}\n")
    lines.append("Implications for fleet & finance:")
    lines.append("- BEV growth increases exposure to EV residual value dynamics.")
    lines.append("- Higher company-kept share signals accelerating fleet electrification → impacts leasing mix & pricing.")
    lines.append("- Quarterly trends enable remarketing timeline planning and maintenance provisioning.\n")
    Path("report.txt").write_text("\n".join(lines), encoding="utf-8")

    print(f"Done.\nWrote: {out_timeseries}\nWrote: EV_growth.png\nWrote: report.txt")

if __name__ == "__main__":
    main()
