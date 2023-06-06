import streamlit as st
import googlemaps
import streamlit_folium
import folium
import requests

def parse_address(address):
    address_parts = address.split(",")
    street = address_parts[0].strip()
    city = "Denver"
    state = "Colorado"
    return street, city, state

def geocode_place(street, city, state):
    address = f"{street}, {city}, {state}"
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": "AIzaSyCDxLFiHPVpF3iiE--ZDfRznVIvCAKQIl8"
    }
    response = requests.get(geocode_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'OK':
            latitude = data['results'][0]['geometry']['location']['lat']
            longitude = data['results'][0]['geometry']['location']['lng']
            return latitude, longitude
        else:
            print(f"Geocoding API Error: {data['status']}")
    else:
        print(f"Error: {response.status_code}, {response.text}")
    return None, None

def main():
    st.title('Welcome to the (Fake) Denver School Finder')

    st.write('The goal of this school finder is to help you find the best school for your child.'
             'Answering the questions below will help us determine which school will help your child grow the most.')

    address_input = st.text_input('What is your address?')
            
    if address_input:
        street, city, state = parse_address(address_input)
        st.write(street, city, state)
        latitude, longitude = geocode_place(street, city, state)
        st.write(latitude, longitude)
        
        # Create a folium map centered on the latitude and longitude
        map = folium.Map(location=[latitude, longitude], zoom_start=12)

        # Add a marker to the map at the latitude and longitude
        folium.Marker([latitude, longitude], popup=address_input, icon=folium.Icon(color='blue')).add_to(map)
        
        # Display the map using streamlit-folium
        streamlit_folium.folium_static(map)
        
    options = ['Special Education', 'Free/Reduced Lunch', 'English Language Learner']
    selected_options = st.multiselect('Please select the services your child receives:', options)
    race_ethnicity = st.radio("Please click on your child's race/ethnicity:", ('Asian', 'Black or African American', 'Hispanic or Latino', 'White', 'Other'))
    starting_gpa = st.slider("Enter your child's current GPA [0-1]", 0.0, 1.0, .5)

    race_vals = []
    if race_ethnicity == 'Asian':
        race_vals = [1, 0, 0, 0]
    elif race_ethnicity == 'Black or African American':
        race_vals = [0, 1, 0, 0]
    elif race_ethnicity == 'Hispanic or Latino':
        race_vals = [0, 0, 1, 0]
    elif race_ethnicity == 'White':
        race_vals = [0, 0, 0, 1]
    else :
        race_vals = [0, 0, 0, 0]

    sped, frl, ell = 0, 0, 0

    if 'Special Education' in selected_options :
        sped = 1
    if 'Free/Reduced Lunch' in selected_options :
        frl = 1
    if 'English Language Learner' in selected_options :
        ell = 1

    characteristics = [sped, frl, ell, race_vals[0], race_vals[1], race_vals[2], race_vals[3], starting_gpa]

    st.write(characteristics)
    
    if address_input:
        return map
    else :
        pass

if __name__ == "__main__":
    main()


