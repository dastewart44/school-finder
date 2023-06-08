import pandas as pd
import geopandas as gpd
import googlemaps
import folium
import requests
import tempfile
import os
import streamlit as st
from geopy.geocoders import Nominatim
from streamlit_extras.switch_page_button import switch_page
from config import google_api_key

# Use the full page instead of a narrow central column
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    
b1, b2 = st.columns((1, 4))
with b1:
    previous_page = st.button("Previous Page")
    if previous_page:
        switch_page("app")
        
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame() 
    
# Setup Google Maps Client
api_key = google_api_key
gmaps = googlemaps.Client(key=api_key)

def parse_address(address):
    address_parts = address.split(",")
    street = address_parts[0].strip()
    city = "Denver"
    state = "Colorado"
    return street, city, state

def geocode_place(street, city, state):
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(f"{street}, {city}, {state}")
    if location is not None:
        return location.latitude, location.longitude
    else:
        print(f"Geocoding Error: Unable to locate {street}, {city}, {state}")
        return None, None
    
def calculate_distance_and_time(origin, destination):
    result = gmaps.directions(origin, destination)
    if result:
        distance = result[0]['legs'][0]['distance']['text']
        duration = result[0]['legs'][0]['duration']['text']
        return distance, duration
    return None, None

def create_school_finder_map(number_of_schools, df):
    df_filtered = df.iloc[:number_of_schools]
    base_url = "https://storage.googleapis.com/schools-de-shape-file/"
    shapefile_files = [
        "geo_export_ac6e6a66-9556-4943-b31c-b66e9d27fbad.shp",
        "geo_export_ac6e6a66-9556-4943-b31c-b66e9d27fbad.shx",
        "geo_export_ac6e6a66-9556-4943-b31c-b66e9d27fbad.dbf",
    ]

    temp_dir = tempfile.mkdtemp()

    # Download shapefile and associated files
    file_paths = []
    for file in shapefile_files:
        file_url = base_url + file
        file_response = requests.get(file_url)
        file_path = os.path.join(temp_dir, file)
        with open(file_path, 'wb') as f:
            f.write(file_response.content)
        file_paths.append(file_path)

    # Read the shapefile with neighborhood boundaries
    shapefile_options = {'options': '-oo SHAPE_RESTORE_SHX=YES'}
    neighborhoods_df = gpd.read_file(file_paths[0], **shapefile_options)

    # Set the CRS of the GeoDataFrame
    neighborhoods_df = neighborhoods_df.set_crs("EPSG:4326")

    # Create a map centered on Denver
    map_center = [39.7392, -104.9903]
    m = folium.Map(location=map_center, zoom_start=11)

    # Add neighborhood boundaries to the map
    folium.GeoJson(neighborhoods_df).add_to(m)

    for index, row in df_filtered.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"{row['SCHOOL_NAME']}<br>Distance: {row['Distance']}<br>Duration: {row['Duration']}",
            icon=folium.Icon(icon='school', prefix='fa')
        ).add_to(m)

    return m

def main():
    csv_url = "https://storage.googleapis.com/school-finder-den/geocoded_schools.csv"
    schools_df = pd.read_csv(csv_url)
    predictions = st.session_state.df
    df = pd.merge(schools_df, predictions, on='school_id', how='inner')
    df_school_type = df[df['SCHOOL_TYPE'] == df['school_type_keep']].copy().reset_index()
    # Calculate distance and time
    st.title("Let's see which schools are likely to maximize your child's GPA.")
    address_input = st.text_input('Enter your home address:')
    number_of_schools = st.slider('Select number of schools:', 1, 20, 10)
    
    if 'school_id' not in st.session_state:
        st.session_state.school_id = df_school_type['school_id'].iloc[0]
    
    if address_input:
        street, city, state = parse_address(address_input)
        user_lat, user_lng = geocode_place(street, city, state)
        df_school_type["Distance"], df_school_type["Duration"] = zip(*df_school_type.apply(lambda row: calculate_distance_and_time(f"{user_lat},{user_lng}", f"{row['Latitude']},{row['Longitude']}"), axis=1))
        df_school_type = df_school_type.sort_values('prediction', ascending=False)
        map = create_school_finder_map(number_of_schools, df_school_type)
        if 'lat' not in st.session_state :
            st.session_state.lat = user_lat
        if 'lon' not in st.session_state :
            st.session_state.lon = user_lng
        
        # Define the columns before the map is created
        c1, c2 = st.columns((2, 1))
        with c1:
            folium.Marker([user_lat, user_lng], popup=address_input, icon=folium.Icon(color='red')).add_to(map)
            map.save("map.html")
            with open("map.html", "r") as f:
                html = f.read()
                # Use column 1 (c1) for the map
                st.components.v1.html(html, width=800, height=600)
        with c2:
            st.title('School Recommendations')
            for i in range(number_of_schools):
                next_page = st.button(f"{df_school_type['SCHOOL_NAME'].iloc[i]} | Predicted GPA: {round(df_school_type['prediction'].iloc[i], 2)} | Distance: {df_school_type['Distance'].iloc[i]} | Duration: {df_school_type['Duration'].iloc[i]}")
                if next_page:
                    st.write(f"School ID just changed to {df_school_type['school_id'].iloc[i]}")
                    st.session_state.school_id = df_school_type['school_id'].iloc[i]
                    switch_page("page_02")
    if 'df2' not in st.session_state :
        st.session_state.df2 = df_school_type

if __name__ == "__main__":
    main()