# VTA-Transit-Delays

CYPLAN 255 — VTA bus delay, stop spacing, and ridership (Spring 2026).

## Midterm deliverables (graphics)

Generated under [`visualizations/`](visualizations/):

| Output | Description |
|--------|-------------|
| `chart 01_average_delay_by_route.png` | Average delay by route (seconds) |
| `chart 02_top20_delay_hotspots.png` | Top 20 stations for greatest average delays on selected routes |
| `chart 03_Moving-speed_distribution_by_route.png` | Moving-speed distribution by route (speed > 1 m/s) |
| `chart 04_proxy_for_stop-and-go_delay` | Percentage of low-speed points by route |
| `map_grid_stopshare_1200ft.html` | Interactive map: grid mean speed, hover includes low-speed share |

Notebook: [`scripts/03_midterm_visuals.ipynb`](scripts/03_midterm_visuals.ipynb).

## Environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Reproducing the midterm pipeline

1. **Raw vehicle GTFS-RT sample** (already in repo):  
   `data/raw/vehicle_route_location_speed_data_20260326_103149.csv`

2. **Corridor filter (250 ft buffer around selected routes)** — produces  
   `data/processed/vehicle_points_filtered_buffer250ft.csv`:

   ```bash
   python scripts/run_vehicle_buffer_filter.py
   ```

   (Equivalent logic lives at the end of [`scripts/02_data_cleaning.ipynb`](scripts/02_data_cleaning.ipynb).)

3. **Figures and map:**

   ```bash
   cd scripts
   jupyter nbconvert --to notebook --execute 03_midterm_visuals.ipynb --inplace
   ```

   Or open `03_midterm_visuals.ipynb` in Jupyter and run all cells. Use `MPLBACKEND=Agg` for headless runs if needed.

## Other scripts

- [`scripts/01_gtfs_route_location_speed_extractor.ipynb`](scripts/01_gtfs_route_location_speed_extractor.ipynb) — pull 511 GTFS-Realtime vehicle positions (requires API key in notebook).
- [`scripts/02_preliminary_data_cleaning.ipynb`](scripts/02_data_cleaning.ipynb) — ridership, stops, routes, ADT, and vehicle buffer filter.

## Course correction (TA feedback)

Research questions, tolerances/tradeoffs, and the statistical plan (OLS + Spearman, etc.) are drafted in [`methodology_midterm_revision.md`](methodology_midterm_revision.md). **Align this with the annotated PDF from instructors** and use **office hours or email** if anything needs clarification before the final proposal.

## Team

See project docs for roles (content, slides, video).
