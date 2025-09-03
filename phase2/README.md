# 📉 Phase 2 — EV Residual Value Risk Simulator

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.x-yellow.svg)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.x-green.svg)
![Status](https://img.shields.io/badge/Stage-Prototyping-orange.svg)

Goal: model depreciation curves for popular EV models and simulate residual value (RV) exposure at 36/48/60 months.

**Inputs:** used EV listings (`Make, Model, Year, Mileage, AskingPrice`).  
**Outputs:**
- `rv_forecasts.csv` — expected RVs per model at 3/4/5y under scenarios  
- `depreciation_curves.png` — model-level depreciation chart  
- `rv_report.txt` — executive summary with exposure scenarios

---

## Example Output
<p align="center"><img src="./depreciation_curves.png" alt="EV Depreciation Curves" width="70%"></p>

---

## Data Generation Notes (Synthetic but Realistic)
We include a generator [`gen_synthetic_ev_listings.py`](./gen_synthetic_ev_listings.py) so the pipeline runs out-of-the-box.

**Assumptions**
- Common UK EV models (fleet-relevant); new-price anchors per model  
- Exponential depreciation per year; model-specific rates  
- Annual mileage ~ N(11k, 3k), truncated [5k–25k]  
- Mileage penalty ~ £1.5 per 1k miles  
- ±5% noise for market dispersion; price floor at £2.5k

**Reproduce**

cat > phase2/README.md << 'EOF'
# 📉 Phase 2 — EV Residual Value Risk Simulator

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-2.x-yellow.svg)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.x-green.svg)
![Status](https://img.shields.io/badge/Stage-Prototyping-orange.svg)

Goal: model depreciation curves for popular EV models and simulate residual value (RV) exposure at 36/48/60 months.

**Inputs:** used EV listings (`Make, Model, Year, Mileage, AskingPrice`).  
**Outputs:**
- `rv_forecasts.csv` — expected RVs per model at 3/4/5y under scenarios  
- `depreciation_curves.png` — model-level depreciation chart  
- `rv_report.txt` — executive summary with exposure scenarios

---

## Example Output
<p align="center"><img src="./depreciation_curves.png" alt="EV Depreciation Curves" width="70%"></p>

---

## Data Generation Notes (Synthetic but Realistic)
We include a generator [`gen_synthetic_ev_listings.py`](./gen_synthetic_ev_listings.py) so the pipeline runs out-of-the-box.

**Assumptions**
- Common UK EV models (fleet-relevant); new-price anchors per model  
- Exponential depreciation per year; model-specific rates  
- Annual mileage ~ N(11k, 3k), truncated [5k–25k]  
- Mileage penalty ~ £1.5 per 1k miles  
- ±5% noise for market dispersion; price floor at £2.5k

**Reproduce**


**Swap in real data** by replacing `data/ev_used_listings.csv` with real listings (same columns).

---

## Why This Matters
Residual value is the **profit lever** in leasing. This simulator automates depreciation modelling and stress testing so finance teams can quantify downside risk quickly.
