import pandas as pd
import geopandas as gpd
import googlemaps
import folium
from streamlit_folium import folium_static
import requests
import os
import streamlit as st
import random
import polyline
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import io
import json
import openai
from bs4 import BeautifulSoup
from streamlit_extras.switch_page_button import switch_page
from config import open_ai_key
from config import google_api_key

google_key = google_api_key
gmaps = googlemaps.Client(key=google_key)

if 'df2' not in st.session_state:
    st.session_state.df2 = pd.DataFrame()
    
school_id = st.session_state.school_id
school_data = st.session_state.df2
student_race = st.session_state.race
user_lat = st.session_state.lat
user_lon = st.session_state.lon
selected_school = school_data[school_data['school_id'] == school_id].copy()
school_name = selected_school['SCHOOL_NAME'].iloc[0]
school_lat = selected_school['Latitude'].iloc[0]
school_lon = selected_school['Longitude'].iloc[0]
phone = str(selected_school['PHONE'].iloc[0])
mailing_address = selected_school['MAILING_ADDRESS'].iloc[0]
school_type = selected_school['SCHOOL_TYPE'].iloc[0]
neighborhood = selected_school['nbhd_name'].iloc[0]
fake_data_avgs = 'https://storage.googleapis.com/school_finder_bucket/fake_data_avgs.csv'
df_avgs = pd.read_csv(fake_data_avgs)
df_avgs_selected = df_avgs[df_avgs['school_id'] == school_id].copy()
fake_data_all = 'https://storage.googleapis.com/school-finder-models/fake_data.csv'
df_fake = pd.read_csv(fake_data_all)
df_fake_selected = df_fake[df_fake['school_id'] == school_id].copy()

def dems():
    st.write('School Demographics')
    dems = df_avgs_selected[['pct_asian', 'pct_black', 'pct_hispanic', 'pct_white', 'pct_other']].iloc[0]
    colors = ['lightgrey'] * len(dems)

    if student_race == 'Asian':
        highlighted_bar_index = 0
    elif student_race == 'Black or African American':
        highlighted_bar_index = 1
    elif student_race == 'Hispanic or Latino':
        highlighted_bar_index = 2
    elif student_race == 'White':
        highlighted_bar_index = 3
    else:
        highlighted_bar_index = 4

    colors[highlighted_bar_index] = 'blue'
    # Create a figure and axes
    fig, ax = plt.subplots()

    # Create your barplot
    sns.barplot(x=dems.values, y=dems.index, palette=colors, orient='h', ax=ax)

    # Here's how you can change the labels
    ax.set_xlabel('% of Students') 
    ax.set_ylabel('Race') 

    # Remove the chart border
    sns.despine(bottom=True, left=True)

    # Eliminate tick marks
    ax.tick_params(bottom=False, left=False)

    # Eliminate axis values
    ax.xaxis.set_major_formatter(plt.NullFormatter())
    ax.yaxis.set_major_formatter(plt.NullFormatter())

    # Add data labels
    for p in ax.patches:
        width = p.get_width()
        ax.text(width + 0.1,  
                p.get_y() + p.get_height() / 2, 
                '{:1.2f}%'.format(width), 
                ha = 'left', 
                va = 'center')

    return st.pyplot(fig)

def school_picture():
    x = random.randint(70, 80)
    image_url = f'https://s3-us-west-2.amazonaws.com/schoolmint-chooser-media/denver/{x}.jpg'
    response = requests.get(image_url, stream=True)
    img = Image.open(io.BytesIO(response.content))
    desired_size = (400, 400)
    img.thumbnail(desired_size)
    return st.image(img, caption=f"Phone: {phone[0:3]}-{phone[3:6]}-{phone[6:10]}", use_column_width=True)

def create_map(user_lat, user_lon, school_lat, school_lon, school_name):
    # Create a map centered around user's location
    map_center = [(school_lat + user_lat)/2, (user_lon + school_lon)/2]
    m = folium.Map(location=map_center, zoom_start=12)
    
    # Add marker for user's location
    folium.Marker(location=[user_lat, user_lon], 
                  popup="Home", 
                  icon=folium.Icon(icon='home', color='red')).add_to(m)
    
    # Add marker for the school
    folium.Marker(location=[school_lat, school_lon], 
                  popup=school_name, 
                  icon=folium.Icon(icon='school', prefix='fa', color='blue')).add_to(m)
    
    return m

def create_route(user_lon, user_lat, school_lon, school_lat):
    url = f"http://router.project-osrm.org/route/v1/driving/{user_lon},{user_lat};{school_lon},{school_lat}?overview=full&geometries=geojson"
    response = requests.get(url)
    data = response.json()
    coordinates = data['routes'][0]['geometry']['coordinates']

    # Convert coordinates format from [lon, lat] to (lat, lon)
    coordinates = [(coord[1], coord[0]) for coord in coordinates]
    return coordinates

def school_description(prompt):
    url = "https://api.openai.com/v1/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {open_ai_key}",
    }
    data = {
        "model": "text-davinci-003",
        "prompt": prompt,
        "max_tokens": 150
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    try:
        response.raise_for_status()  # Check for any HTTP errors
        response_json = response.json()
        
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json['choices'][0]['text'].strip()
        else:
            return None  # Handle the case when no choices are available
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"An error occurred: {e}")
        return None  # Return None or handle the error appropriately

def main():
    col1, col2, col3 = st.columns((3, 1, 3))
    with col1:
        st.title(school_name)
        school_info = school_description(f"Provide me with a one-paragraph description of {school_name} in Denver, Colorado")
        st.write(school_info)
        school_picture()
        dems()
        
    with col3:
        st.title('Driving Directions')
        m = create_map(user_lat, user_lon, school_lat, school_lon, school_name)   
        # Get the route coordinates
        route_coordinates = create_route(user_lon, user_lat, school_lon, school_lat)
        # Add the route polyline to the map
        folium.PolyLine(locations=route_coordinates, color='blue').add_to(m)     
        folium_static(m)
        
if __name__ == "__main__":
    main()
    