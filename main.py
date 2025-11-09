import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from sklearn.cluster import KMeans
import requests
import numpy as np
import os
import polyline
from geopy.geocoders import Nominatim
import time

# ---------- CONFIG ----------
DATA_FILE = "crime.csv"
ORS_API_KEY = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImQ2MDFlOWU1ZjhhMTRkYjFiZDA4ZjFiNmMwMmFkYWViIiwiaCI6Im11cm11cjY0In0="

# ---------- PAGE SETUP ----------
st.set_page_config(page_title="🚨 Chennai Crime Route Alert System", layout="wide")
st.title("🚨 Chennai Crime Prediction, Hotspot & Safe Route Mapping")

# ---------- LOAD DATA ----------
if not os.path.exists(DATA_FILE):
    st.error(f"❌ Dataset file '{DATA_FILE}' not found.")
    st.stop()

base_df = pd.read_csv(DATA_FILE)
base_df.columns = base_df.columns.str.strip().str.lower()
rename_map = {'lat': 'latitude', 'lon': 'longitude', 'long': 'longitude', 'crime': 'crime_type', 'type': 'crime_type'}
base_df.rename(columns=rename_map, inplace=True)
required_cols = {'latitude', 'longitude', 'crime_type'}
missing = required_cols - set(base_df.columns)
if missing:
    st.error(f"❌ Missing columns: {missing}")
    st.stop()
base_df.drop_duplicates(subset=['latitude', 'longitude', 'crime_type'], inplace=True)

if "crime_data" not in st.session_state:
    st.session_state["crime_data"] = base_df.copy()

def df():
    return st.session_state["crime_data"]

# ---------- CRIME MAP ----------
st.header("🗺️ Crime Map of Chennai")
gdf = gpd.GeoDataFrame(df(), geometry=gpd.points_from_xy(df().longitude, df().latitude))
crime_map = folium.Map(location=[13.0827, 80.2707], zoom_start=11)
for _, row in gdf.iterrows():
    folium.CircleMarker(
        [row["latitude"], row["longitude"]],
        radius=5, color="red", fill=True, fill_color="red",
        popup=f"{row.get('crime_type','Unknown')} at {row.get('location','')}"
    ).add_to(crime_map)
st_folium(crime_map, width=1200, height=700)

# ---------- REPORT CRIME ----------
st.header("📢 Report a Crime")
col1, col2 = st.columns(2)
with col1:
    date = st.date_input("Date")
    time_str = st.text_input("Time (e.g. 10:30 PM)")
    crime_type = st.selectbox("Crime Type", sorted(df()["crime_type"].dropna().unique()))
with col2:
    location = st.text_input("Area (e.g. Tambaram)")
    coords = st.text_input("Coordinates (lat, lon)")
    gender = st.text_input("Victim Gender")

if st.button("🚨 Submit Report"):
    if coords:
        try:
            lat, lon = map(float, coords.split(","))
            new = pd.DataFrame([{
                "date": str(date), "time_of_day": time_str, "crime_type": crime_type,
                "location": location, "latitude": lat, "longitude": lon, "victim_gender": gender
            }])
            st.session_state["crime_data"] = pd.concat([df(), new], ignore_index=True)
            st.session_state["crime_data"].to_csv(DATA_FILE, index=False)
            st.success("✅ Crime reported and saved.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Invalid coordinates: {e}")
    else:
        st.warning("⚠️ Enter coordinates to report a crime.")

# ---------- CLUSTERING ----------
st.header("📊 Crime Hotspot Clusters")
k = st.slider("Clusters", 2, 10, 4)
latlon = df()[["latitude", "longitude"]].astype(float).dropna()
work = df().copy()
if len(latlon) >= k:
    kmeans = KMeans(n_clusters=k, random_state=0, n_init="auto")
    work["cluster"] = kmeans.fit_predict(latlon)
else:
    work["cluster"] = 0
st.session_state["crime_data"] = work

cluster_map = folium.Map(location=[13.0827, 80.2707], zoom_start=11)
colors = ["red", "blue", "green", "purple", "orange", "gray"]
for i in range(work["cluster"].nunique()):
    for _, row in work[work["cluster"] == i].iterrows():
        folium.CircleMarker(
            [row["latitude"], row["longitude"]],
            radius=5, color=colors[i % len(colors)], fill=True,
            popup=f"Cluster {i}: {row['crime_type']} at {row['location']}"
        ).add_to(cluster_map)
st_folium(cluster_map, width=1200, height=700)

# ---------- ROUTE CHECK ----------
st.header("🧭 Safe Route Finder")
col3, col4 = st.columns(2)
with col3:
    start_place = st.text_input("Start (e.g. Guindy)", key="start")
with col4:
    end_place = st.text_input("Destination (e.g. Avadi)", key="end")

known_coords = {
    "guindy": (13.0101, 80.2129),
    "avadi": (13.1143, 80.0958),
    "tambaram": (12.9249, 80.1275),
    "velachery": (12.9791, 80.2209),
    "chromepet": (12.9514, 80.1414),
    "tnagar": (13.0408, 80.2343),
    "adyar": (13.0067, 80.2577)
}

def get_coords(area):
    """Strong geocoding with fallback + known area map."""
    if not area:
        return None, None
    area_lower = area.strip().lower()
    if area_lower in known_coords:
        return known_coords[area_lower]
    try:
        geolocator = Nominatim(user_agent="crime_route_app")
        loc = geolocator.geocode(f"{area}, Chennai, Tamil Nadu, India", timeout=10)
        if loc:
            st.info(f"📍 Found {area}: ({loc.latitude:.4f}, {loc.longitude:.4f})")
            return loc.latitude, loc.longitude
    except:
        pass
    st.warning(f"⚠️ '{area}' not found, using Chennai center.")
    return 13.0827, 80.2707

def get_route_with_alternates(start, end):
    """Get main + alternate routes using ORS."""
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
    body = {
        "coordinates": [[start[1], start[0]], [end[1], end[0]]],
        "alternative_routes": {"share_factor": 0.7, "target_count": 2, "weight_factor": 2}
    }
    try:
        res = requests.post(url, json=body, headers=headers, timeout=20)
        data = res.json()
        routes = []
        if "routes" in data:
            for route in data["routes"]:
                summary = route.get("summary", {})
                decoded = polyline.decode(route["geometry"])
                coords = [[lat, lon] for lat, lon in decoded]
                routes.append((coords, summary))
        return routes
    except Exception as e:
        st.error(f"🚫 ORS Error: {e}")
        return []

def is_danger_near_route(route, threshold=0.02):
    """Check for crime points near route."""
    for _, crime in df().iterrows():
        for lat, lon in route:
            dist = np.sqrt((lat - crime["latitude"])**2 + (lon - crime["longitude"])**2)
            if dist < threshold:
                return True, (crime["latitude"], crime["longitude"], crime["location"])
    return False, None

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    route_btn = st.button("🚗 Find Route")
with col_btn2:
    clear_btn = st.button("🗑️ Clear")

if clear_btn:
    for k in ["routes", "crime_point"]:
        st.session_state[k] = None
    st.success("🧹 Cleared.")
    st.rerun()

if route_btn:
    start_latlon = get_coords(start_place)
    end_latlon = get_coords(end_place)
    routes = get_route_with_alternates(start_latlon, end_latlon)
    if not routes:
        st.error("No routes found.")
    else:
        st.session_state["routes"] = routes
        st.success(f"✅ Found {len(routes)} routes!")

# ---------- MAP DISPLAY ----------
if "routes" in st.session_state and st.session_state["routes"]:
    route_map = folium.Map(location=[13.0827, 80.2707], zoom_start=11)
    colors = ["blue", "green"]

    for idx, (coords, summary) in enumerate(st.session_state["routes"][:2]):
        folium.PolyLine(coords, color=colors[idx], weight=5, opacity=0.8,
                        tooltip=f"Route {idx+1}").add_to(route_map)
        if idx == 0:
            danger, point = is_danger_near_route(coords)
            if danger:
                folium.CircleMarker([point[0], point[1]], radius=10,
                                    color="red", fill=True, fill_opacity=0.7,
                                    popup=f"Crime near {point[2]}").add_to(route_map)

    st_folium(route_map, width=1200, height=700)

# ---------- DATA TABLE ----------
st.header("📋 Reported Crimes")
st.dataframe(df()[["date", "location", "latitude", "longitude", "crime_type"]])
