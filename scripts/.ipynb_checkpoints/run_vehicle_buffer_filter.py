"""
Generate vehicle_points_filtered_buffer250ft.csv from raw vehicle CSV + selected routes.
Same logic as the tail of preliminary_data_cleaning.ipynb (buffer join in EPSG:2227).
Run from repo root: python 01-scripts/run_vehicle_buffer_filter.py
"""
from __future__ import annotations

import os

import geopandas as gpd
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VEHICLE_CSV = os.path.join(BASE, "02-data/cleaned_data/vehicle_route_location_speed_data_20260326_103149.csv")
ROUTES_CSV = os.path.join(BASE, "02-data/cleaned_data/selected_routes.csv")
OUT_CSV = os.path.join(BASE, "02-data/cleaned_data/vehicle_points_filtered_buffer250ft.csv")
BUFFER_FT = 250


def main() -> None:
    routes_df = pd.read_csv(ROUTES_CSV)
    selected_routes_gdf = gpd.GeoDataFrame(
        routes_df,
        geometry=gpd.GeoSeries.from_wkt(routes_df["geometry"]),
        crs="EPSG:2227",
    )
    if selected_routes_gdf.crs.to_string() != "EPSG:2227":
        selected_routes_gdf = selected_routes_gdf.to_crs("EPSG:2227")

    route_buffers = selected_routes_gdf.copy()
    route_buffers["geometry"] = route_buffers.geometry.buffer(BUFFER_FT)

    veh = pd.read_csv(VEHICLE_CSV)
    veh = veh.dropna(subset=["lat", "lon", "route_id", "time"])
    veh["route_id"] = veh["route_id"].astype(str).str.strip()

    veh_gdf = gpd.GeoDataFrame(
        veh,
        geometry=gpd.points_from_xy(veh["lon"], veh["lat"]),
        crs="EPSG:4326",
    ).to_crs("EPSG:2227")

    veh_in = gpd.sjoin(
        veh_gdf,
        route_buffers[["route_name", "geometry"]],
        how="inner",
        predicate="within",
    )
    veh_in = veh_in.drop_duplicates(subset=["bus_id", "trip_id", "time", "route_id"])

    veh_in_out = veh_in.drop(columns=[c for c in ["index_right"] if c in veh_in.columns])
    veh_in_out.to_csv(OUT_CSV, index=False)
    print("Saved:", OUT_CSV, "rows:", len(veh_in_out))


if __name__ == "__main__":
    main()
