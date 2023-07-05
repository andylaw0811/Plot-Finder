import folium
import osmnx as ox
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium


place = 'Nottingham,  United Kingdom'

graph = ox.graph_from_place(place, network_type="drive")
nodes, streets = ox.graph_to_gdfs(graph)
brown_fields = ox.geometries_from_place(place, {'landuse': 'brownfield'})

# Use WGS 84 (epsg:4326) as the geographic coordinate system
brown_fields_polygon = brown_fields.to_crs(epsg=4326)
# brown_fields_polygon.plot(figsize=(6, 6))
# plt.show()


road_style = {'color': '#1A19AC', 'weight': '1'}


m = folium.Map(location=ox.geocode(place))
folium.GeoJson(streets, style_function=lambda x: road_style).add_to(m)

"""Add brownfield site boundary"""
for _, r in brown_fields_polygon.iterrows():
    # Without simplifying the representation of each borough,
    # the map might not be displayed
    sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
    geo_j = sim_geo.to_json()
    geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": "orange"})
    #folium.Popup(r["BoroName"]).add_to(geo_j)
    geo_j.add_to(m)

"""Add centroid markers"""
# Project to NAD83 projected crs
brown_fields_centroids = brown_fields_polygon.to_crs(epsg=2263)

# Access the centroid attribute of each polygon
brown_fields_centroids["centroid"] = brown_fields_centroids.centroid

# Project to WGS84 geographic crs
# geometry (active) column
brown_fields_centroids = brown_fields_centroids.to_crs(epsg=4326)

# Centroid column
brown_fields_centroids["centroid"] = brown_fields_centroids["centroid"].to_crs(epsg=4326)

brown_fields_centroids.head()

polygon_areas = brown_fields_polygon.to_crs({'init': 'epsg:32633'})['geometry'].area
print(polygon_areas)

for area, (_, r) in zip(polygon_areas, brown_fields_centroids.iterrows()):
    lat = r["centroid"].y
    lon = r["centroid"].x
    folium.Marker(
        location=[lat, lon],
        popup="Area: {:.2f}m²".format(float(area)),
    ).add_to(m)

# Save
#m.save("map.html")

st_data = st_folium(m, width=1200)

