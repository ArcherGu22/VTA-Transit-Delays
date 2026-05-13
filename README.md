# VTA-Transit-Delays

CYPLAN 255 — VTA bus delay, stop spacing, and ridership (Spring 2026).  
Group 5: Yidan Tang, Archer Gu, Ashley Li

This project is presented as an ArcGIS StoryMap:  
👉 [VTA Transit Delays — StoryMap]([https://storymaps.arcgis.com/stories/61af1aa47b94452aad8ae69a7cc74dbc])

## Project Structure
VTA-Transit-Delays/
├── data/
│   ├── raw/
│   └── processed/
├── visualizations/
├── scripts/
│   ├── 01_gtfs_live_feed_extractors.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_regression_models.ipynb
│   ├── 04_visualizations.ipynb
│   └── 05_helper_functions.py
├── report.pdf
└── requirements.txt

## Scripts

| Script | Description |
|--------|-------------|
| `01_gtfs_live_feed_extractors.ipynb` | Pulls 511 GTFS-Realtime vehicle positions (requires API key) |
| `02_data_cleaning.ipynb` | Cleans and processes ridership, stops, routes, ADT, and vehicle position data |
| `03_regression_models.ipynb` | Computes stop spacing (OSM), runs OLS and Spearman/Pearson correlation analysis |
| `04_visualizations.ipynb` | Generates all figures and interactive maps |
| `05_helper_functions.py` | Shared utility functions used across notebooks |

## Figures

Generated under `visualizations/`:

| Output | Description |
|--------|-------------|
| `fig_01_mean_delay_by_route.png/.svg` | Mean arrival delay by route with 95% CI (seconds) |
| `fig_02_top20_delay_hotspots.png/.svg` | Top 20 stops by mean arrival delay |
| `fig_03_moving_speed_by_route.png/.svg` | Moving-speed distribution by route (speed > 1 m/s) |
| `fig_04_stop_idle_share_by_route.png/.svg` | Share of low-speed points by route (speed < 0.5 mph) |
| `fig_05a_map_stop_spacing_local.html` | Interactive map: stop spacing, local routes (22/23/25/60) |
| `fig_05b_map_stop_spacing_rapid.html` | Interactive map: stop spacing, rapid routes (522/523) |
| `fig_06_map_grid_stopshare_1200ft.html` | Interactive grid map (1200 ft): mean speed + low-speed share |
| `fig_07_scatter_spacing_vs_delay.png/.svg` | Stop spacing vs. mean arrival delay (Pearson + Spearman) |
| `fig_08_scatter_boardings_vs_delay.png/.svg` | Stop-level boardings vs. mean arrival delay (log x, by route) |
| `fig_09_map_bubble_ridership_delay.html` | Bubble map: stops sized by boardings, colored by delay |
| `fig_10_map_delay_hotspot_adt.html` | Delay hotspot stops overlaid with San José ADT counters |

## Environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Reproducing the Pipeline

Run notebooks in order:

```bash
cd scripts
jupyter nbconvert --to notebook --execute 02_data_cleaning.ipynb --inplace
jupyter nbconvert --to notebook --execute 03_regression_models.ipynb --inplace
jupyter nbconvert --to notebook --execute 04_visualizations.ipynb --inplace
```

Or open each notebook in Jupyter and run all cells (`Restart & Run All`).  
Use `MPLBACKEND=Agg` for headless runs if needed.

> Note: `01_gtfs_live_feed_extractors.ipynb` requires a 511 API key and live feed access.
> Raw vehicle position data is already included in `data/raw/`.

## Data Sources

- VTA Open Data Portal: route shapes, stop locations, ridership by stop
- 511 Open Transit Data: GTFS-Realtime vehicle positions and trip updates
- City of San José GIS Open Data: Average Daily Traffic (ADT) counters
