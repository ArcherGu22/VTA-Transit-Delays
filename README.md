# VTA-Transit-Delays

CYPLAN 255 — VTA bus delay, stop spacing, and ridership (Spring 2026).

## Midterm deliverables (graphics)

Generated under [`03-output-graphics/`](03-output-graphics/):

| Output | Description |
|--------|-------------|
| `chart1b_moving_speed_boxplot_gt1.0.png` | Moving-speed distribution by route (speed > 1 m/s) |
| `chart2_speed_timeseries_5min.png` | Mean speed by route, 5-minute bins |
| `chart3_stop_share_th0.5.png` | Share of GPS points with speed < 0.5 m/s (idle / stop proxy) |
| `chart4_hotspots_overlay_grid1200ft.png` | Low-speed share hotspots (top 10% of grid cells), 1200 ft grid |
| `map_grid_stopshare_1200ft.html` | Interactive map: grid mean speed, hover includes low-speed share |

Notebook: [`01-scripts/midterm_visuals.ipynb`](01-scripts/midterm_visuals.ipynb).

## Environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Reproducing the midterm pipeline

1. **Raw vehicle GTFS-RT sample** (already in repo):  
   `02-data/cleaned_data/vehicle_route_location_speed_data_20260326_103149.csv`

2. **Corridor filter (250 ft buffer around selected routes)** — produces  
   `02-data/cleaned_data/vehicle_points_filtered_buffer250ft.csv`:

   ```bash
   python 01-scripts/run_vehicle_buffer_filter.py
   ```

   (Equivalent logic lives at the end of [`01-scripts/preliminary_data_cleaning.ipynb`](01-scripts/preliminary_data_cleaning.ipynb).)

3. **Figures and map:**

   ```bash
   cd 01-scripts
   jupyter nbconvert --to notebook --execute midterm_visuals.ipynb --inplace
   ```

   Or open `midterm_visuals.ipynb` in Jupyter and run all cells. Use `MPLBACKEND=Agg` for headless runs if needed.

## Other scripts

- [`01-scripts/gtfs_route_location_speed_extractor.ipynb`](01-scripts/gtfs_route_location_speed_extractor.ipynb) — pull 511 GTFS-Realtime vehicle positions (requires API key in notebook).
- [`01-scripts/preliminary_data_cleaning.ipynb`](01-scripts/preliminary_data_cleaning.ipynb) — ridership, stops, routes, ADT, and vehicle buffer filter.

## Course correction (TA feedback)

Research questions, tolerances/tradeoffs, and the statistical plan (OLS + Spearman, etc.) are drafted in [`04-final-report/methodology_midterm_revision.md`](04-final-report/methodology_midterm_revision.md). **Align this with the annotated PDF from instructors** and use **office hours or email** if anything needs clarification before the final proposal.

## Team

See project docs for roles (content, slides, video).
