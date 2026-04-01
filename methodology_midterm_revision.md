# Midterm revision: research questions, interpretation, and statistical plan

This document responds to instructor feedback (refine measurable outcomes; three sub-questions; tolerances/tradeoffs; explicit OLS variables; named correlation methods). Final variable choices should be confirmed with course staff (office hours / email) against your marked PDF.

## 1. Three targeted sub-questions (quantities)

**Q1 — Stop spacing vs. passenger demand (descriptive / correlational)**  
*Quantity:* For each **stop segment** (pair of consecutive stops) on selected routes, compute **distance along the route (m or ft)** between stops and **average daily boardings** (or alightings) at the downstream stop from October 2025 ridership.  
*Outcome:* Identify segments where **spacing is below a stated threshold** (e.g. &lt; 400 m) **and** ridership is below a **lower tertile or fixed boardings/day cutoff**—candidate “redundant stop” segments. No causal claim: pattern description only.

**Q2 — “Dead time” from slow / stop-like driving (GTFS-reported speed)**  
*Quantity:* Using filtered vehicle GPS in the **route corridor buffer** (250 ft), define **idle share** as the share of observations with speed &lt; 0.5 m/s (or agency-chosen threshold) and **low-speed share** as share with speed &lt; ~5 mph (2.24 m/s), aggregated by **route** and by **space–time grid cell** (e.g. 1200 ft).  
*Outcome:* Map **where** corridor segments show high low-speed share (hotspots) and **how** that varies by time of day (5-min mean speed series). Interpret as **operational delay proxies**, not causal attribution to stops vs. traffic.

**Q3 — Relating stop-level demand to delay proxies (exploratory regression)**  
*Quantity:* At **stop or segment level**, merge ridership with **nearby grid aggregates** of mean speed / low-speed share (e.g. average within distance *d* of the stop).  
*Outcome:* A **pre-specified OLS** (below) and **Spearman rank correlation** as a robustness check for skewed counts—reporting **association**, not causal effect of consolidation.

## 2. Interpretation: tolerances and tradeoffs

- **Tolerances (thresholds):**  
  - **Stop spacing:** Flag segments below **400 m** (or FTA-informed range cited in the paper) *and* ridership below a **data-driven cutoff** (e.g. bottom third of boardings on the corridor).  
  - **Speed / idle:** Flag grid cells in the **top decile** of `low_share` (already used in midterm charts) as “priority for review.”  
  These cutoffs are **transparent** and can be sensitivity-tested (e.g. 80th vs. 90th percentile).

- **Tradeoffs (non-causal):**  
  - Removing a low-ridership stop may **reduce door time and acceleration cycles** but **increase walking distance** for riders using that stop; report **who is affected** using equity-relevant geographies if data allow.  
  - **Do not** claim that consolidation “causes” faster trips; phrase as **consistent with** reduced stop time under simplifying assumptions (seconds per stop × stops removed).

## 3. Statistical analysis plan

### 3.1 OLS (primary pre-specified model)

Example specification (units must match merged data):

- **Dependent variable (Y):**  
  `mean_low_speed_share` or `mean_idle_share` in buffer around stop *i*, or segment-level average speed during peak window.

- **Independent variables (X):**  
  - `log(1 + daily_boardings)` at stop *i* (skewed demand).  
  - `stop_spacing_m` (distance to next/previous stop).  
  - **Controls:** route fixed effects (dummy per route), optional **peak vs. off-peak** indicator, optional **day-of-week** if multiple days are pooled.

- **Interpretation:** Coefficients are **associations** conditional on controls; discuss **heterogeneity** (e.g. interaction spacing × demand) only if pre-specified.

### 3.2 Other methods (named)

- **Spearman correlation** between `stop_spacing_m` and `daily_boardings` (segment level) and between `boardings` and grid `mean_speed`—robust to outliers.  
- **Pearson correlation** on **log-transformed** positive variables where appropriate.  
- **Descriptive stratification:** Compare speed distributions by route (boxplots) and over time (5-min series)—already in midterm outputs.

### 3.3 What we will not claim

- No **causal** interpretation of consolidation without experimental or quasi-experimental design.  
- **511 speed** reflects reported values; validate units (m/s) in appendix.

## 4. Office hours / email

If any part of **Y/X definitions** or **thresholds** conflicts with the annotated PDF, **confirm with course staff before final submission.**
