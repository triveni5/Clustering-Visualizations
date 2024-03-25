import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering

counties_gdf = gpd.read_file("C:/Users/gurra/Downloads/IL_BNDY_County/IL_BNDY_County_Py_Changed.shp")
population_df = pd.read_excel("C:/Users/gurra/Downloads/DECENNIALPL2020.P1-2023-12-25T043449.xlsx", sheet_name="Data")
population_df["County"] = population_df["Label"].str.replace(" County, Illinois", "").str.upper()
county_names = population_df.columns[1:].str.replace(" County, Illinois", "").str.upper()
population_data = dict(zip(county_names, population_df.iloc[0, 1:]))
merged_gdf = counties_gdf.copy()
merged_gdf["population"] = merged_gdf["COUNTY_NAM"].map(population_data)
merged_gdf["population"] = merged_gdf["population"].str.replace(",", "")
merged_gdf["population"] = merged_gdf["population"].apply(int)

# Calculate the target population
total_population = merged_gdf["population"].sum()
target_population = total_population // 4

# Create a new GeoDataFrame with the centroids of the counties
centroids_gdf = merged_gdf.copy()
centroids_gdf["geometry"] = centroids_gdf.geometry.centroid
centroids_gdf["x"] = centroids_gdf.geometry.centroid.x
centroids_gdf["y"] = centroids_gdf.geometry.centroid.y

# Cluster the counties based on their spatial proximity and population
agg_clustering = AgglomerativeClustering(n_clusters=4, linkage="ward")
agg_clustering.fit(centroids_gdf[["population", "x", "y"]])

# Assign the cluster labels to the counties
merged_gdf["region"] = agg_clustering.labels_ + 1
# Create the choropleth map
merged_gdf.plot(column="region", cmap="Set2", legend=False)
plt.title("Illinois with 4 contiguous regions of equal population")
plt.show()