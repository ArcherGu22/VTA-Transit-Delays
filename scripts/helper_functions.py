import pandas as pd
import geopandas as gpd
import plotly.graph_objs
import plotly.express as px
from shapely import wkt
from shapely.geometry.base import BaseGeometry

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