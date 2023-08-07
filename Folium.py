import folium
import osmnx as ox
import geopandas as gpd
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_folium import st_folium
from folium.plugins import Draw

# Set page to wide
st.set_page_config(layout="wide")

# Create Login Authenticator

authenticator = stauth.Authenticate(
    dict(st.secrets['credentials']),
    st.secrets['cookie']['name'],
    st.secrets['cookie']['key'],
    st.secrets['cookie']['expiry_days'],
    st.secrets['preauthorized']
)

st.title("Plot Finder")

name, authentication_status, username = authenticator.login('Login', 'main')



if authentication_status:
    authenticator.logout('Logout', 'main')
    # Streamlit Website
    input = st.text_input("Search", value="Nottingham, United Kingdom")

    place = input
    m = folium.Map(location=ox.geocode(place), zoom_start=12)
    folium.plugins.Fullscreen().add_to(m)
    # Add measurement tools
    # Draw(export=True).add_to(m)
    measure_control = folium.plugins.MeasureControl(position='topleft',
                                                    active_color='red',
                                                    completed_color='red',
                                                    primary_length_unit='kilometers',
                                                    font_color='black'
                                                    )

    m.add_child(measure_control)

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
                geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {"fillColor": colour, 'color': colour})
                folium.Popup(uses).add_to(geo_j)
                geo_j.add_to(m)
        except Exception as e:
            print(e)


    # Sidebar
    st.sidebar.subheader("Add landuses to map")
    landuses = ['brownfield', 'residential', 'grass', 'industrial', 'cemetery', 'commercial', 'retail', 'construction',
                'recreation_ground', 'religious', 'garages', 'greenfield', 'railway', 'education', 'greenery', 'school',
                'institutional', 'healthcare']

    default = 'brownfield'

    i = 0
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

            brown_fields_columns = [
                "name",
                "disused:amenity",
                "landuse",
                "proposed:landuse",
                "addr:city",
                "addr:housenumber",
                "addr:postcode",
                "addr:street"
            ]

            for area, (_, r), name in zip(polygon_areas, brown_fields_centroids.iterrows(),
                                          brown_fields['name'].values):
                lat = r["centroid"].y
                lon = r["centroid"].x
                folium.Marker(
                    location=[lat, lon],
                    popup="<b>Name: </b>{} <br><b>Area: </b>{:.2f}m²".format(name, float(area)),
                    icon=folium.Icon(color="red")
                ).add_to(m)

            continue
        else:
            checkbox = st.sidebar.checkbox(x, False)
        if checkbox:
            add_site_boundary(x, colours[i])
            i += 1

    st_data = st_folium(m, width=1200, height=600, returned_objects=[])
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')

# if st.session_state["authentication_status"]:
#     authenticator.logout('Logout', 'main')
#     st.write(f'Welcome *{st.session_state["name"]}*')
#     st.title('Some content')
# elif st.session_state["authentication_status"] == False:
#     st.error('Username/password is incorrect')
# elif st.session_state["authentication_status"] == None:
#     st.warning('Please enter your username and password')




