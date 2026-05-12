import pandas as pd
import geopandas as gpd
import plotly.graph_objs
import plotly.express as px
from shapely import wkt
from shapely.geometry.base import BaseGeometry
import networkx as nx

# Data Cleaning

def safe_wkt_load(geo_string) -> BaseGeometry | None:
    """
    Converts a string geometry to a geographic object (shape, point, line, etc.).
    Use on a list of string geometries with .apply()
    Provides easy handling for N/A and NaN values

    Parameters
    ----------
    geo_string : str
        String geometry to convert to an object

    Returns
    -------
    shapely.geometry.base.BaseGeometry
        Geometry object
    """

    if pd.isna(geo_string):
        return None
    return wkt.loads(geo_string)

def compute_osm_spacing(stations_gdf, G):
    """
    Computes approximate station spacings between consecutive stops using OpenStreetMap graph routing.

    For each unique (route_id, direction_id) pair, the function sorts stops in 
    order, computes the shortest-path distance between consecutive stop nodes, 
    and stores the distance in a new column

    Parameters
    ----------
    stations_gdf : geopandas.GeoDataFrame
        GeoDataFrame containing a list of transit stations, with CRS = EPSG:2227

    Returns
    -------
    pandas.DataFrame
        DataFrame containing all original stop data, with an added 'spacing_ft'
        While this technically works in other units and CRS as well, we assume 
        CRS = EPSG:2227
    """

    # Store processed route/direction groups
    results = []

    # Process each route + direction separately
    for (route_id, direction_id), stops in stations_gdf.groupby(
        ["route_id", "direction_id"]
    ):

        # order stops by stopping order along the route
        stops = stops.sort_values("stop_sequence").copy()

        # First stop has no previous stop, so spacing is None
        spacings = [None]

        # Compute spacing between consecutive stops after the first stop
        for i in range(1, len(stops)):

            # Previous stop node
            n1 = stops.iloc[i - 1]["node"]
            # Current stop node
            n2 = stops.iloc[i]["node"]

            try:
                # Shortest network distance along the street graph
                dist = nx.shortest_path_length(
                    G,
                    n1,
                    n2,
                    weight="length"
                )

            except:
                # Handle disconnected nodes or routing failures
                dist = None

            spacings.append(dist)

        stops["spacing_ft"] = spacings
        results.append(stops)

    return pd.concat(results, ignore_index=True)

# Visualization

def quick_px_scattermap(
    gdf: gpd.GeoDataFrame,
    **kwargs,
) -> plotly.graph_objs._figure.Figure:
    """
    Converts a GeoDataFrame to a geographic CRS (EPSG:4326) compatible with plotly.express, then plots a scatter map of that GDF.

    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        GeoDataFrame to plot.
    lat : str
        Column name containing point Latitudes (Y).
    lon : str
        Column name containing point Longitudes (X).
    **kwargs : 
        Add in any additional plotly.express.scatter_map map elements here, such as size, color, hover_data, etc.
        Refer to the documentation for plotly.express.scatter_map for additional arguments

    Returns
    -------
    plotly.graph_objs._figure.Figure
        Figure object
    """

    px_crs_adj_gdf = gdf.copy().to_crs("EPSG:4326")
    px_crs_adj_gdf["lat"] = px_crs_adj_gdf.geometry.y
    px_crs_adj_gdf["lon"] = px_crs_adj_gdf.geometry.x
    fig = px.scatter_map(
        px_crs_adj_gdf,
        lat="lat",
        lon="lon",
        **kwargs
    )

    fig.update_layout(map_style="carto-positron", margin={"r":0,"t":40,"l":0,"b":0})

    return fig