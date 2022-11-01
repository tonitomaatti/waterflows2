import streamlit as st
import datetime
from streamlit_folium import st_folium
import folium
import pandas as pd
import coordinates
import json

# Reading data
preds_df = pd.read_csv("Data/year_predictions.csv", sep=",")
waterflow_df = pd.read_csv("Data/Waterflow Data.csv")

# Route Data
routes = []
for i in range(0, 6):
    with open("Data/Routepoints/routepoints_" + str(i) + ".geojson") as f:
        route = json.load(f)
    all_coordinates = []
        
    for feature in route["features"]:
        coords = [(coord[1], coord[0]) for coord in feature["geometry"]["coordinates"]]
        all_coordinates = all_coordinates + coords
    
    routes.append(all_coordinates)

# Building the side bar
with st.sidebar:
    st.title('WaterFlows')
    st.write(
        "A Dashboard to check the status of canoeing routes. Start by picking a date.")

    date_picker = st.date_input(
        "Select Date",
        min_value=datetime.date.today(),
        max_value=datetime.date.today()+datetime.timedelta(days=365))

    toggle_map = st.radio(
        "Map Type",
        ('Color', 'Grey'),
        index=1,
        horizontal=True
    )

    st.write("")
    st.write("Green = Easy")
    st.write("Yellow = Doable")
    st.write("Red = Impossible")


# Building the map
if toggle_map == "Color":
    map_tiles = "OpenStreetMap"
else:
    map_tiles = "CartoDB Positron"
    
m = folium.Map([60.30246404560092, 24.85931396484375],
               zoom_start=9, tiles=map_tiles)

# Draw plugin for map
folium.plugins.Draw(export=True).add_to(m)


# Drawing routes and coloring with predictions
day_prediction = preds_df[preds_df["date"] ==str(date_picker)]["predicted_mean"].values[0]

for i in range(0, 6):
    if i > 4:
        color = "grey"
    elif day_prediction >= waterflow_df.at[i, "Treshold Easy"]:
        color = "green"
    elif day_prediction >= waterflow_df.at[i, "Treshold Doable"]:
        color = "yellow"
    else:
        color = "red"

    folium.vector_layers.PolyLine(
        locations = routes[i],
        color=color,
        weight=5
    ).add_to(m)


# Add route markers
start_coords = waterflow_df[["Route Start GPS N", "Route Start GPS E", "Route Start"]].rename(
    columns={"Route Start GPS N": "N",
             "Route Start GPS E": "E",
             "Route Start": "Name"}
).to_dict("records")

end_coords = waterflow_df[["Route End GPS N", "Route End GPS E", "Route End"]].rename(
    columns={"Route End GPS N": "N",
             "Route End GPS E": "E", "Route End": "Name"}
).to_dict("records")

coords = start_coords + end_coords

for coord in coords:
    route_name = coord.pop("Name", None)
    coords_wgs84 = coordinates.ETRSTM35FINxy_to_WGS84lalo(coord)
    folium.vector_layers.Circle(
        location=(coords_wgs84["La"], coords_wgs84["Lo"]),
        radius=1,
        popup=None,
        tooltip=route_name,
        weight=5,
        color="black",
        fill_color="purple",
        fill_opacity=1.0
    ).add_to(m)

# Call to render Folium map in Streamlit
st_data = st_folium(m, width=1000, height=800)
