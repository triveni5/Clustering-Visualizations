import pandas as pd
import geopandas as gpd
from sklearn.cluster import KMeans
import geopandas as gpd
import matplotlib.pyplot as plt

# Load the shapefile of the contiguous US states
illinois = gpd.read_file("C:/Users/gurra/Downloads/IL_BNDY_County/IL_BNDY_County_Py_Changed.shp")
population_df = pd.read_excel("C:/Users/gurra/Downloads/DECENNIALPL2020.P1-2023-12-25T043449.xlsx", sheet_name="Data")
population_df["County"] = population_df["Label"].str.replace(" County, Illinois", "").str.upper()
county_names = population_df.columns[1:].str.replace(" County, Illinois", "").str.upper()
population_data = dict(zip(county_names, population_df.iloc[0, 1:]))
merged_gdf = illinois.copy()
merged_gdf["population"] = merged_gdf["COUNTY_NAM"].map(population_data)
merged_gdf["population"] = merged_gdf["population"].str.replace(",", "")
merged_gdf["population"] = merged_gdf["population"].apply(int)
#usa['population'] =  merged_gdf["population"]

# Divide the states into equal population clusters using the KMeans algorithm
kmeans = KMeans(n_clusters=4)
illinois['cluster'] = kmeans.fit_predict(merged_gdf[['population']])

# Plot the map
fig, ax = plt.subplots(figsize=(10, 10))
illinois.plot(column='cluster',cmap='Set2', ax=ax, legend=False)
plt.show()