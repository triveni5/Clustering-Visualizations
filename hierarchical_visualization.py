
import geopandas as gpd
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
import pandas as pd
import matplotlib.pyplot as plt
from shapely.ops import unary_union
# Load county shapefile
counties_gdf = gpd.read_file("C:/Users/gurra/Downloads/IL_BNDY_County/IL_BNDY_County_Py.shp")
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
#total_population = merged_gdf["population"].sum()
#target_population = total_population // 4
# Create a distance matrix based on population differences
populations = merged_gdf["population"].values.reshape(-1, 1)
print(populations)
distances = np.abs(populations - populations.T)
print(distances)
# Calculate spatial weights based on shared boundaries (corrected calculation)
merged_gdf["neighbors"] = merged_gdf.geometry.apply(lambda g: g.touches)
# Ensure we have a NumPy array before conversion
neighbor_values = merged_gdf.neighbors.values
spatial_weights = merged_gdf.geometry.apply(lambda g: g.touches(merged_gdf.geometry.iloc[0])).values.astype(int) * 0.5
distances = distances.astype(float)
distances += spatial_weights

# Apply hierarchical clustering with spatial weights
linkage_matrix = linkage(distances, method='ward')  # Ward's method often promotes contiguity
cluster_labels = fcluster(linkage_matrix, 4, criterion='maxclust')    # Ensure 4 clusters
merged_gdf["region"] = cluster_labels

merged_regions_gdf = merged_gdf.dissolve(by="region")
# Assuming your population data is in a column named "population"
populations_per_cluster = merged_gdf.groupby("region")["population"].sum()
print(populations_per_cluster)

merged_regions_gdf["geometry"] = merged_regions_gdf.geometry.apply(lambda g: unary_union(g))
# Plot the GeoDataFrame
merged_regions_gdf.plot(cmap="Set2", legend=True, edgecolor="white")
plt.title("Illinois with 4 regions of equal population")
plt.show()

