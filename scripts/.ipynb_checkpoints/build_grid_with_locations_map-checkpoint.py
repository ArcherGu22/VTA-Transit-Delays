"""Strict-task version of Ashley's map deliverable #3:
"Refine the existing grid speed map, add stop locations layer."

Differences from `build_station_grid_map.py`:
  - Stations are plain uniform location markers (one shape, one color, fixed size).
    No size/color encoding of ridership or delay — that belongs to Yidan's
    bubble map deliverable.
  - The grid layer is upgraded from chunky scatter dots to a continuous
    density color band (the "refine" part).

Output: visualizations/map_grid_with_stop_locations.html
"""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
from shapely import wkt

REPO_ROOT = Path(__file__).resolve().parent.parent
PROCESSED = REPO_ROOT / "data" / "processed"
VIZ = REPO_ROOT / "visualizations"
VIZ.mkdir(exist_ok=True)

GRID_FT = 1200
STOP_TH = 0.5
MIN_PINGS_PER_CELL = 20

CARTO_TILE_LAYER = dict(
    below="traces",
    sourcetype="raster",
    sourceattribution=(
        "© <a href='https://www.openstreetmap.org/copyright'>"
        "OpenStreetMap</a> contributors © "
        "<a href='https://carto.com/attributions'>CARTO</a>"
    ),
    source=[
        "https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
        "https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
        "https://c.basemaps.cartocdn.com/light_all/{z}/{x}/{y}@2x.png",
    ],
)


def safe_wkt_load(g):
    if pd.isna(g):
        return None
    return wkt.loads(g)


def build_grid_layer():
    df = pd.read_csv(PROCESSED / "vehicle_points_filtered_buffer250ft.csv")
    df["route_id"] = df["route_id"].astype(str)
    df["speed"] = pd.to_numeric(df["speed"], errors="coerce")
    df = df.dropna(subset=["lat", "lon", "speed"])
    df = df[df["speed"] >= 0]

    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["lon"], df["lat"]),
        crs="EPSG:4326",
    ).to_crs("EPSG:2227")

    gdf["gx"] = (gdf.geometry.x // GRID_FT) * GRID_FT
    gdf["gy"] = (gdf.geometry.y // GRID_FT) * GRID_FT
    gdf["is_stop"] = gdf["speed"] < STOP_TH

    grid = (
        gdf.groupby(["gx", "gy"])
        .agg(
            mean_speed=("speed", "mean"),
            stop_share=("is_stop", "mean"),
            n=("speed", "size"),
        )
        .reset_index()
    )
    grid = grid[grid["n"] >= MIN_PINGS_PER_CELL].copy()

    grid_gdf = gpd.GeoDataFrame(
        grid,
        geometry=gpd.points_from_xy(grid["gx"], grid["gy"]),
        crs="EPSG:2227",
    ).to_crs("EPSG:4326")
    grid_gdf["lat"] = grid_gdf.geometry.y
    grid_gdf["lon"] = grid_gdf.geometry.x
    return grid_gdf


def build_station_layer():
    """Plain location markers — NO bubble encoding."""
    s = pd.read_csv(PROCESSED / "station_spacings.csv")
    s["geometry"] = s["geometry"].apply(safe_wkt_load)
    sgdf = gpd.GeoDataFrame(s, geometry="geometry", crs="EPSG:2227").to_crs("EPSG:4326")
    sgdf["lat"] = sgdf.geometry.y
    sgdf["lon"] = sgdf.geometry.x

    # Hover label: identify the stop only (no ridership/delay encoding,
    # since this map's purpose is location reference).
    sgdf["hover"] = (
        "<b>" + sgdf["stop_name"].astype(str) + "</b><br>"
        "Route " + sgdf["route_id"].astype(str)
        + " (dir " + sgdf["direction_id"].astype(str) + ")"
    )
    return sgdf


def build_figure(grid_gdf, sgdf):
    fig = go.Figure()

    # ── Grid layer: continuous density heatmap of mean speed (refined
    # representation of the chunky scatter grid in the original midterm map).
    fig.add_trace(
        go.Densitymap(
            lat=grid_gdf["lat"],
            lon=grid_gdf["lon"],
            z=grid_gdf["mean_speed"],
            radius=42,
            colorscale="Viridis",
            zmin=0,
            zmax=float(grid_gdf["mean_speed"].quantile(0.95)),
            opacity=0.55,
            colorbar=dict(
                title=dict(text="Mean speed<br>(m/s)", side="right"),
                x=1.0, y=0.5, len=0.55, thickness=14,
            ),
            hoverinfo="skip",
            name=f"Speed density ({GRID_FT}ft grid)",
        )
    )

    # ── Stations: uniform markers showing location only
    fig.add_trace(
        go.Scattermap(
            lat=sgdf["lat"],
            lon=sgdf["lon"],
            mode="markers",
            marker=dict(
                size=6,
                color="#222222",
                opacity=0.85,
            ),
            text=sgdf["hover"],
            hovertemplate="%{text}<extra></extra>",
            name="VTA stops (selected routes)",
        )
    )

    fig.update_layout(
        # Inject carto positron tiles as raster basemap below traces so
        # streets/labels don't occlude markers.
        map=dict(
            style="white-bg",
            layers=[CARTO_TILE_LAYER],
            center=dict(
                lat=float(sgdf["lat"].mean()),
                lon=float(sgdf["lon"].mean()),
            ),
            zoom=10,
        ),
        margin=dict(l=0, r=130, t=70, b=0),
        height=720,
        title=dict(
            text=(
                f"<b>VTA selected corridors</b> — refined speed grid "
                f"({GRID_FT} ft) + stop locations"
                "<br><sub>Continuous density band = mean vehicle speed; "
                "black points = VTA stop locations on selected routes. "
                "Hover a stop for name and route.</sub>"
            ),
            x=0.01, y=0.97, xanchor="left",
        ),
        showlegend=False,
    )
    return fig


def main():
    print("Building grid layer...", flush=True)
    g = build_grid_layer()
    print(f"  grid cells: {len(g)}", flush=True)

    print("Building stop locations layer...", flush=True)
    s = build_station_layer()
    print(f"  stops: {len(s)}", flush=True)

    fig = build_figure(g, s)
    out = VIZ / "map_grid_with_stop_locations.html"
    fig.write_html(out, include_plotlyjs="cdn")
    print(f"Saved -> {out}", flush=True)


if __name__ == "__main__":
    main()
