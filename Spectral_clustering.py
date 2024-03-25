import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.cluster import SpectralClustering
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
from shapely.ops import unary_union
# Load county shapefile
counties_gdf = gpd.read_file("C:/Users/gurra/Downloads/IL_BNDY_County/IL_BNDY_County_Py_Changed.shp")
population_df = pd.read_excel("C:/Users/gurra/Downloads/DECENNIALPL2020.P1-2023-12-25T043449.xlsx", sheet_name="Data")
# Clean county names by removing "County, Illinois" suffix and converting to lowercase
population_df["County"] = population_df["Label"].str.replace(" County, Illinois", "").str.upper()
county_names = population_df.columns[1:].str.replace(" County, Illinois", "").str.upper()
population_data = dict(zip(county_names, population_df.iloc[0, 1:]))
merged_gdf=counties_gdf.copy()
merged_gdf["population"] = merged_gdf["COUNTY_NAM"].map(population_data)
# Calculate total population and target population per region
merged_gdf["population"] = merged_gdf["population"].str.replace(",", "")
merged_gdf["population"] = merged_gdf["population"].apply(int)
total_population = merged_gdf["population"].sum()
target_population = total_population // 4
# Create a graph where nodes represent counties and edges connect intersecting/touching counties
G = nx.Graph()
for idx, row in merged_gdf.iterrows():
    G.add_node(idx, population=row["population"])
    poly1 = row["geometry"]
    for idx2, row2 in merged_gdf.iterrows():
        if idx != idx2:
            poly2 = row2["geometry"]
            if poly1.intersects(poly2) or poly1.touches(poly2):
                G.add_edge(idx, idx2)

# Apply Spectral Clustering
sc = SpectralClustering(n_clusters=4, affinity="precomputed", random_state=42)
labels = sc.fit_predict(nx.adjacency_matrix(G))
merged_gdf["region"] = labels + 1  # Add 1 to make region labels start from 1

# Plot the GeoDataFrame
merged_gdf.plot(column="region",cmap="Set2", legend=True)
plt.title("Illinois with 4 regions of equal population")
plt.show()
