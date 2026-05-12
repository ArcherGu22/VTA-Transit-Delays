"""Build an enhanced interactive map combining the grid-summary speed layer
with a station overlay (colored by mean delay, sized by daily boardings).

Outputs:
  visualizations/map_grid_with_stations.html

Run from the repo root or scripts/ directory.
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
    stations = pd.read_csv(PROCESSED / "station_spacings.csv")
    stations["geometry"] = stations["geometry"].apply(safe_wkt_load)
    sgdf = gpd.GeoDataFrame(stations, geometry="geometry", crs="EPSG:2227").to_crs("EPSG:4326")
    sgdf["lat"] = sgdf.geometry.y
    sgdf["lon"] = sgdf.geometry.x

    # Marker size: daily boardings. Smaller base + tighter cap so stations
    # don't visually drown the underlying speed grid.
    sgdf["marker_size"] = (sgdf["boardings"].clip(lower=1)).pow(0.45).clip(upper=16) + 5

    # Build a hover label
    sgdf["hover"] = (
        "<b>" + sgdf["stop_name"].astype(str) + "</b><br>"
        "Route " + sgdf["route_id"].astype(str)
        + " (dir " + sgdf["direction_id"].astype(str) + ")<br>"
        "Mean delay: " + sgdf["mean_delay"].round(0).astype(int).astype(str) + " s<br>"
        "Daily boardings: " + sgdf["boardings"].round(1).astype(str) + "<br>"
        "Stop spacing: " + sgdf["spacing_ft"].round(0).astype(int).astype(str) + " ft"
    )
    return sgdf


def build_figure(grid_gdf, sgdf):
    fig = go.Figure()

    # ── Grid layer: continuous density heatmap of mean speed.
    # Weighted by mean_speed so brighter areas = faster bus operations,
    # darker areas = slow / stop-and-go segments. Acts as a soft
    # background canvas under the station overlay.
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
                x=1.0, y=0.78, len=0.40, thickness=14,
            ),
            hoverinfo="skip",
            name=f"Speed density ({GRID_FT}ft grid)",
        )
    )

    # ── Station layer: delay color, boardings size. Symmetric color
    # range around 0 so red/blue split is meaningful.
    delay_abs_max = sgdf["mean_delay"].abs().quantile(0.9)
    fig.add_trace(
        go.Scattermap(
            lat=sgdf["lat"],
            lon=sgdf["lon"],
            mode="markers",
            marker=dict(
                size=sgdf["marker_size"],
                color=sgdf["mean_delay"],
                colorscale="RdBu_r",
                cmin=-delay_abs_max,
                cmax=delay_abs_max,
                colorbar=dict(
                    title=dict(text="Mean delay (s)<br>red = late", side="right"),
                    x=1.0, y=0.22, len=0.40, thickness=14,
                ),
                opacity=0.92,
            ),
            text=sgdf["hover"],
            hovertemplate="%{text}<extra></extra>",
            name="Stations (size = boardings)",
        )
    )

    # NOTE on layer order: with style="carto-positron", plotly's vector
    # tiles render the white street layer ON TOP of data, occluding
    # markers. Workaround: use a blank style and inject carto positron
    # raster tiles as a `layers[]` entry with below="traces" so the
    # basemap is drawn underneath all data traces.
    fig.update_layout(
        map=dict(
            style="white-bg",
            layers=[
                dict(
                    below="traces",
                    sourcetype="raster",
                    sourceattribution=(
                        "© <a href='https://www.openstreetmap.org/copyright'>"
                        "OpenStreetMap</a> contributors © "
                        "<a href='https://carto.com/attributions'>CARTO</a>"
                    ),
                    source=[
                        "https://a.basemaps.cartocdn.com/light_all/"
                        "{z}/{x}/{y}@2x.png",
                        "https://b.basemaps.cartocdn.com/light_all/"
                        "{z}/{x}/{y}@2x.png",
                        "https://c.basemaps.cartocdn.com/light_all/"
                        "{z}/{x}/{y}@2x.png",
                    ],
                )
            ],
            center=dict(
                lat=float(sgdf["lat"].mean()),
                lon=float(sgdf["lon"].mean()),
            ),
            zoom=10,
        ),
        margin=dict(l=0, r=170, t=70, b=0),
        height=720,
        title=dict(
            text=(
                f"<b>VTA selected corridors</b> — speed grid ({GRID_FT} ft cells) "
                f"+ station overlay"
                "<br><sub>Grid color = mean vehicle speed (yellow = fast); "
                "stations = daily boardings (size) and mean arrival delay "
                "(red = late, blue = early). Hover for details.</sub>"
            ),
            x=0.01, y=0.97, xanchor="left",
        ),
        showlegend=False,
    )

    return fig


def main():
    print("Building grid layer from vehicle pings...", flush=True)
    grid_gdf = build_grid_layer()
    print(f"  grid cells: {len(grid_gdf)}", flush=True)

    print("Building station layer from station_spacings.csv...", flush=True)
    sgdf = build_station_layer()
    print(f"  stations: {len(sgdf)}", flush=True)

    print("Composing figure...", flush=True)
    fig = build_figure(grid_gdf, sgdf)

    out = VIZ / "map_grid_with_stations.html"
    fig.write_html(out, include_plotlyjs="cdn")
    print(f"Saved -> {out}", flush=True)


if __name__ == "__main__":
    main()
