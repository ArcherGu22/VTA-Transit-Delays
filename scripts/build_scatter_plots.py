"""Build chart_05 (spacing vs delay) and chart_06 (boardings vs delay) scatter plots.

Reproduces the station-level merged dataset used in 04_regression_models.ipynb,
saves the intermediate data to processed CSVs, and writes two PNGs to visualizations/.

Run from repo root or scripts/ directory.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
from shapely import wkt
from sklearn.cluster import DBSCAN

REPO_ROOT = Path(__file__).resolve().parent.parent
PROCESSED = REPO_ROOT / "data" / "processed"
VIZ = REPO_ROOT / "visualizations"
VIZ.mkdir(exist_ok=True)

SELECTED_ROUTES = ["22", "Rapid 522", "23", "Rapid 523", "25", "60"]

ROUTE_COLORS = {
    22: "#8c2d04",
    522: "#cc4c02",
    23: "#ec7014",
    523: "#fe9929",
    25: "#fec44f",
    60: "#a6611a",
}

ROUTE_LABELS = {
    22: "22",
    522: "Rapid 522",
    23: "23",
    523: "Rapid 523",
    25: "25",
    60: "60",
}


def safe_wkt_load(geo_string):
    if pd.isna(geo_string):
        return None
    return wkt.loads(geo_string)


def build_station_table() -> gpd.GeoDataFrame:
    delay = pd.read_csv(PROCESSED / "cleaned_delay_data.csv")
    ridership = pd.read_csv(PROCESSED / "selected_station_ridership.csv")

    delay = delay[delay["route_id"].isin(SELECTED_ROUTES)]
    delay = (
        delay.groupby(["route_id", "direction_id", "stop_id", "stop_sequence"])
        .agg(mean_delay=("computed_delay_sec", "mean"),
             n_obs=("computed_delay_sec", "size"))
        .reset_index()
        .sort_values(["route_id", "direction_id", "stop_sequence"])
    )
    delay["route_id"] = (
        delay["route_id"].str.replace(r"^Rapid\s+", "", regex=True).astype(int)
    )

    ridership["direction_id"] = ridership["direction_id"] % 10
    ridership = ridership.sort_values(["route_id", "direction_id", "stop_id"])

    merged = pd.merge(
        delay,
        ridership,
        on=["route_id", "direction_id", "stop_id"],
        how="inner",
    )
    merged["geometry"] = merged["geometry"].apply(safe_wkt_load)
    gdf = gpd.GeoDataFrame(merged, geometry="geometry", crs="EPSG:2227")
    return gdf.sort_values(["route_id", "direction_id", "stop_sequence"])


def compute_spacings(stations_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    print("Loading OSMnx network for Santa Clara County (cached if available)...",
          flush=True)
    G = ox.graph_from_place("Santa Clara County, California, USA",
                            network_type="drive")
    G = ox.project_graph(G, to_crs="EPSG:2227")

    stations_gdf = stations_gdf.to_crs(G.graph["crs"]).copy()
    stations_gdf["node"] = ox.distance.nearest_nodes(
        G, X=stations_gdf.geometry.x, Y=stations_gdf.geometry.y
    )

    out = []
    for (route_id, direction_id), stops in stations_gdf.groupby(["route_id", "direction_id"]):
        stops = stops.sort_values("stop_sequence").copy()
        spacings = [None]
        for i in range(1, len(stops)):
            n1 = stops.iloc[i - 1]["node"]
            n2 = stops.iloc[i]["node"]
            try:
                d = nx.shortest_path_length(G, n1, n2, weight="length")
            except Exception:
                d = None
            spacings.append(d)
        stops["spacing_ft"] = spacings
        out.append(stops)

    return pd.concat(out, ignore_index=True).dropna(subset=["spacing_ft"])


def attach_adt(spacings_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    sj_adt = pd.read_csv(PROCESSED / "selected_sj_adt.csv")
    sj_adt["geometry"] = sj_adt["geometry"].apply(safe_wkt_load)
    sj_adt_gdf = gpd.GeoDataFrame(sj_adt, geometry="geometry", crs="EPSG:2227")

    coords = np.array(list(zip(sj_adt_gdf.geometry.x, sj_adt_gdf.geometry.y)))
    sj_adt_gdf["cluster"] = DBSCAN(eps=350, min_samples=1).fit(coords).labels_
    adt_clustered = sj_adt_gdf.dissolve(by="cluster", aggfunc={"adt": "mean"})
    adt_clustered["geometry"] = adt_clustered.geometry.centroid
    adt_clustered = adt_clustered.reset_index()

    return gpd.sjoin_nearest(
        spacings_gdf.copy(),
        adt_clustered,
        how="left",
        max_distance=350,
        distance_col="dist_to_adt",
    ).dropna(subset=["adt"])


def scatter(df, x, y, xlabel, ylabel, title, out_path,
            log_x=False, x_cap=None, drop_zero_x=True):
    """Scatter colored by route with OLS fit and Pearson/Spearman in title."""
    from scipy import stats

    full_df = df.copy()
    if drop_zero_x:
        full_df = full_df[full_df[x] > 0]
    n_full = len(full_df)

    # Stats over full data (after dropping invalid x<=0 rows only)
    pearson_r, pearson_p = stats.pearsonr(full_df[x], full_df[y])
    spearman_r, spearman_p = stats.spearmanr(full_df[x], full_df[y])

    # For visualization, optionally cap x to reveal the bulk distribution
    plot_df = full_df.copy()
    if x_cap is not None:
        n_capped = (plot_df[x] > x_cap).sum()
        plot_df = plot_df[plot_df[x] <= x_cap]
    else:
        n_capped = 0

    fig, ax = plt.subplots(figsize=(10, 6.5))
    for rid in sorted(plot_df["route_id"].unique()):
        sub = plot_df[plot_df["route_id"] == rid]
        ax.scatter(
            sub[x], sub[y],
            s=26, alpha=0.6, edgecolor="white", linewidth=0.3,
            color=ROUTE_COLORS.get(int(rid), "#333"),
            label=ROUTE_LABELS.get(int(rid), str(rid)),
        )

    ax.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.6)
    if log_x:
        ax.set_xscale("log")

    xv = np.log10(plot_df[x]) if log_x else plot_df[x]
    yv = plot_df[y]
    slope, intercept = np.polyfit(xv, yv, 1)
    xs_vals = np.linspace(xv.min(), xv.max(), 100)
    ys_vals = slope * xs_vals + intercept
    ax.plot(10 ** xs_vals if log_x else xs_vals, ys_vals,
            color="black", linewidth=1.6, alpha=0.75, label="Linear fit")

    subtitle = (f"Pearson r = {pearson_r:+.3f} (p={pearson_p:.2g})   "
                f"Spearman ρ = {spearman_r:+.3f} (p={spearman_p:.2g})   "
                f"n = {n_full}  (full sample)")

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=13, weight="bold", pad=24)
    ax.text(0.5, 1.02, subtitle, transform=ax.transAxes,
            fontsize=10, ha="center", va="bottom", color="#444")
    if n_capped:
        ax.text(0.99, -0.13,
                f"{n_capped} stops with {x} > {x_cap:g} omitted from plot only "
                f"(stats above use full sample of {n_full})",
                transform=ax.transAxes, fontsize=8, ha="right",
                va="top", style="italic", color="#666")
    ax.legend(title="Route", loc="best", fontsize=9, ncol=2, framealpha=0.85)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(alpha=0.25, linestyle=":")

    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved -> {out_path} (plot n={len(plot_df)}, full n={n_full}, "
          f"r={pearson_r:+.3f}, ρ={spearman_r:+.3f})", flush=True)


def main():
    print("Building station-level merged dataset...", flush=True)
    stations = build_station_table()
    print(f"  rows: {len(stations)}", flush=True)

    print("Computing OSMnx-based stop spacings...", flush=True)
    spacings = compute_spacings(stations)
    print(f"  rows with spacing: {len(spacings)}", flush=True)

    spacings_out = PROCESSED / "station_spacings.csv"
    spacings.drop(columns=["node"], errors="ignore").to_csv(spacings_out, index=False)
    print(f"  Saved -> {spacings_out}", flush=True)

    print("Attaching ADT (San Jose stops only)...", flush=True)
    sj_adt = attach_adt(spacings)
    sj_out = PROCESSED / "station_spacings_with_adt.csv"
    sj_adt.drop(columns=["node", "index_right"], errors="ignore").to_csv(sj_out, index=False)
    print(f"  rows with ADT: {len(sj_adt)} -> {sj_out}", flush=True)

    print("Drawing scatter plots...", flush=True)
    scatter(
        spacings,
        x="spacing_ft", y="mean_delay",
        xlabel="Stop spacing (ft, OSM road distance)",
        ylabel="Mean arrival delay (s)",
        title="Stop spacing vs. mean delay by route",
        out_path=VIZ / "chart_05_scatter_spacing_vs_delay.png",
        log_x=False,
        x_cap=3500,
        drop_zero_x=True,
    )
    scatter(
        spacings,
        x="boardings", y="mean_delay",
        xlabel="Average daily boardings per stop (log scale)",
        ylabel="Mean arrival delay (s)",
        title="Stop-level boardings vs. mean delay by route",
        out_path=VIZ / "chart_06_scatter_boardings_vs_delay.png",
        log_x=True,
        x_cap=None,
        drop_zero_x=True,
    )
    print("Done.")


if __name__ == "__main__":
    main()
