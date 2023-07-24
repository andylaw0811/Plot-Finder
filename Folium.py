import folium
import osmnx as ox
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium
from folium.plugins import Draw

st.title("Land Uses in Nottingham")

input = st.text_input("Search", value="Nottingham, United Kingdom")

place = input
m = folium.Map(location=ox.geocode(place), zoom_start=12)
Draw(export=True).add_to(m)

colours = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
              'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']

def add_site_boundary(uses, colour):
    try:
        site = ox.geometries_from_place(place, {'landuse': uses})
        polygon = site.to_crs(epsg=4326)
        for _, r in polygon.iterrows():
            # Without simplifying the representation of each borough,
            # the map might not be displayed
            sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
            geo_j = sim_geo.to_json()
            geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": colour,'color': colour})
            folium.Popup(uses).add_to(geo_j)
            geo_j.add_to(m)
    except Exception as e:
        print(e)


# Sidebar
st.sidebar.subheader("Add landuses to map")
landuses = ['brownfield', 'residential', 'grass', 'industrial','cemetery', 'commercial', 'retail', 'construction', 'recreation_ground', 'religious', 'garages', 'greenfield', 'railway', 'education', 'greenery', 'school', 'institutional', 'healthcare']

default = 'brownfield'

i=0
colours = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen',
              'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']
for x in landuses:
    if x == default:
        checkbox = st.sidebar.checkbox(x, True)
        add_site_boundary(x, '#964B00')
        # Add centroid markers
        # Project to NAD83 projected crs
        # Use WGS 84 (epsg:4326) as the geographic coordinate system
        brown_fields = ox.geometries_from_place(place, {'landuse': 'brownfield'})
        brown_fields_polygon = brown_fields.to_crs(epsg=4326)
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

        for area, (_, r) in zip(polygon_areas, brown_fields_centroids.iterrows()):
            lat = r["centroid"].y
            lon = r["centroid"].x
            folium.Marker(
                location=[lat, lon],
                popup="Area: {:.2f}m²".format(float(area)),
                icon=folium.Icon(color="red")
            ).add_to(m)
        continue
    else:
        checkbox = st.sidebar.checkbox(x, False)
    if checkbox:
        add_site_boundary(x, colours[i])
        i+=1



st_data = st_folium(m, width=1200, height=500,  returned_objects=[])

