# Shared helper functions for the urban analytics project.

import pandas as pd
import geopandas as gpd
import plotly.graph_objs
import plotly.express as px

# Visualization

def quick_px_scattermap(
    gdf: gpd.GeoDataFrame,
    **kwargs,
) -> plotly.graph_objs._figure.Figure:
    """
    Converts a GeoDataFrame to a geographic CRS (EPSG:4326) compatible with plotly.express, then plot a scatter map of that GDF.

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