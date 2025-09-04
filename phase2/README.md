
# 📉 Phase 2 — EV Residual Value Risk Simulator

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.x-yellow.svg)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.x-green.svg)
![Status](https://img.shields.io/badge/Stage-Prototyping-orange.svg)

---

## 📌 Overview
This phase models **depreciation curves** for popular EV models and simulates residual value (RV) exposure at **36 / 48 / 60 months**.  
It addresses the most important risk in leasing portfolios: **what vehicles will be worth at contract end**.

---

## 🔧 How It Works
**Inputs:** used EV listings (`Make, Model, Year, Mileage, AskingPrice`)  
**Outputs:**
- `rv_forecasts.csv` — expected RVs at 3/4/5 years under multiple scenarios  
- `depreciation_curves.png` — fitted model-level depreciation chart  
- `rv_report.txt` — executive summary of exposure  

---

## 📊 Example Output
<p align="center">
  <img src="./depreciation_curves.png" alt="EV Depreciation Curves" width="75%">
</p>

---

## 💡 Key Insight (Example: BMW i3)

The simulator fitted **8 models**. For the BMW i3 (n=140 listings):

- **3 years:** £20,220 (base) → £16,176 (stress)  
- **4 years:** £16,697 (base) → £13,358 (stress)  
- **5 years:** £13,788 (base) → £11,030 (stress)  

📉 A 5-year contract could see values swing by **>£2,700 per unit** between base vs. stress scenarios —  
enough to erase leasing margins if not priced correctly.


---

## 🧪 Data Generation Notes (Synthetic but Realistic)
We include a generator [`gen_synthetic_ev_listings.py`](./gen_synthetic_ev_listings.py) so the pipeline runs out-of-the-box.

**Assumptions applied:**
- Models = common UK EVs in fleet portfolios  
- New price anchors per model, exponential depreciation by year  
- Annual mileage ~ N(11k, 3k), truncated to [5k – 25k]  
- Mileage penalty ~ £1.5 per 1k miles  
- ±5% noise for market variation  
- Floor of £2.5k to prevent unrealistic tails  

**Reproduce locally:**
```bash
python3 gen_synthetic_ev_listings.py
python3 residual_risk.py data/ev_used_listings.csv
````

**Swap in real data** by replacing `data/ev_used_listings.csv` with actual used EV listings (same columns).

---

## 💡 Why This Matters

Residual value is the **profit lever** in leasing.
A 10–20% swing in RVs can erase margins.

This simulator shows how finance teams can:

* Automate depreciation modelling,
* Run base/optimistic/conservative/stress scenarios,
* Deliver **finance-ready insights** to guide pricing and risk strategy.

````


