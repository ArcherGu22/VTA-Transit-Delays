# VTA-Transit-Delays

CYPLAN 255 — VTA bus delay, stop spacing, and ridership (Spring 2026).

## Final deliverables (graphics)

Generated under `visualizations/`:

| Output | Description |
|--------|-------------|
| `fig_01_mean_delay_by_route.png/.svg` | Mean arrival delay by route with 95% CI (seconds) |
| `fig_02_top20_delay_hotspots.png/.svg` | Top 20 stops by mean arrival delay across selected routes |
| `fig_03_moving_speed_by_route.png/.svg` | Moving-speed distribution by route (speed > 1 m/s) |
| `fig_04_stop_idle_share_by_route.png/.svg` | Share of low-speed points by route (speed < 0.5 mph) |
| `fig_05a_map_stop_spacing_local.html` | Interactive map: stop spacing along local routes (22/23/25/60) |
| `fig_05b_map_stop_spacing_rapid.html` | Interactive map: stop spacing along rapid routes (522/523) |
| `fig_06_map_grid_stopshare_1200ft.html` | Interactive grid map (1200 ft): mean speed + low-speed share |
| `fig_07_scatter_spacing_vs_delay.png/.svg` | Stop spacing vs. mean arrival delay (per stop, by route; Pearson + Spearman) |
| `fig_08_scatter_boardings_vs_delay.png/.svg` | Stop-level boardings vs. mean arrival delay (log x, by route) |
| `fig_09_map_bubble_ridership_delay.html` | Interactive bubble map: stop locations sized by boardings, colored by delay |
| `fig_10_map_delay_hotspot_adt.html` | Interactive map: delay hotspot stops overlaid with San José ADT counters |

## Notebooks/scripts

- [`scripts/01_gtfs_route_location_speed_extractor.ipynb`] — pull 511 GTFS-Realtime vehicle positions (requires API key)
- [`scripts/02_preliminary_data_cleaning.ipynb`] — ridership, stops, routes, ADT, and vehicle buffer filter
- [`scripts/03_midterm_visuals.ipynb`] — figures 01–04 + grid map (fig_06)
- [`scripts/04_regression_models.ipynb`] — stop spacing computation (OSM), OLS, Spearman/Pearson robustness checks; produces figures 07–08
- [`scripts/build_scatter_plots.py`] — produces `data/processed/station_spacings*.csv` and figures 07–08
- [`scripts/build_grid_with_locations_map.py`] — produces `fig_06_map_grid_stopshare_1200ft.html`
- [`scripts/build_station_grid_map.py`] — produces `fig_09_map_bubble_ridership_delay.html`

## Environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Reproducing the pipeline

1. **Raw vehicle GTFS-RT sample** (already in repo):
   `data/raw/vehicle_route_location_speed_data_20260326_103149.csv`

2. **Corridor filter** (250 ft buffer around selected routes) — produces
   `data/processed/vehicle_points_filtered_buffer250ft.csv`:
```bash
   python scripts/run_vehicle_buffer_filter.py
```
   (Equivalent logic lives at the end of `scripts/02_preliminary_data_cleaning.ipynb`.)

3. **Figures and maps:**
```bash
   cd scripts
   jupyter nbconvert --to notebook --execute 03_midterm_visuals.ipynb --inplace
   jupyter nbconvert --to notebook --execute 04_regression_models.ipynb --inplace
   python build_scatter_plots.py
   python build_grid_with_locations_map.py
   python build_station_grid_map.py
```
   Or open each notebook in Jupyter and run all cells.
   Use `MPLBACKEND=Agg` for headless runs if needed.

## Team

See project docs for roles (content, slides, video).