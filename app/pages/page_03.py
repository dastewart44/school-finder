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
from bs4 import BeautifulSoup
from geopy.distance import geodesic
from streamlit_extras.switch_page_button import switch_page
import plotly.graph_objects as go
import numpy as np
import matplotlib.patches as mpatches

st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

google_key = google_api_key
gmaps = googlemaps.Client(key=google_key)

if 'df2' not in st.session_state:
    st.session_state.df2 = pd.DataFrame()

if 'race' not in st.session_state:
    st.session_state.race = 'Asian'

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
avg_gpas_by_group = 'https://storage.googleapis.com/school-finder-models/avg_gpas_by_group.csv'
df_gpas = pd.read_csv(avg_gpas_by_group)
df_gpas_selected = df_gpas[df_gpas['school_id'] == school_id].copy()

def scatter_chart():
    df = pd.read_csv(fake_data_all)
    groups =['sped_flag', 'frl_flag', 'ell_flag', 'asian_flag', 'black_flag', 'hispanic_flag', 'white_flag']
    group_name = ['Special Education', 'Free and Reduced Lunch', 'English Language Learner',
              'Asian', 'Black or African American', 'Hispanic or Latino', 'White']
    df1 = df[df['school_id'] == school_id].copy()
    df2 = pd.DataFrame()
    for i in range(len(groups)):
        df_group = df1[df1[groups[i]] == 1].copy()
        df_group['group'] = group_name[i]
        df_group2 = df_group[['student_id', 'school_id', 'group', 'starting_gpa', 'gpa']].copy()
        df2 = pd.concat([df2, df_group2])

    # Create a Streamlit app
    st.markdown(f"### GPAs by Student Group at {school_name}")

    # Get the unique group values from the dataset
    groups = group_name

    # Add a multiselect widget to select groups with a unique key
    selected_groups = st.multiselect("Select Groups", groups, default=groups, key="group_selector_" + str(len(groups)))

    # Filter the dataframe based on selected groups
    filtered_df = df2[df2['group'].isin(selected_groups)]

    # Set the style of the plot
    sns.set_style('white')

    # Create the scatterplot
    sns.scatterplot(data=filtered_df, x='starting_gpa', y='gpa', hue='group', palette='Set1')

    # Remove the grid lines
    sns.despine()

    # Move the legend below the chart
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False)

    # Set plot labels and title
    plt.xlabel('Starting GPA')
    plt.ylabel('Ending GPA')

    # Display the plot
    st.pyplot()

def circle_plot():
    st.markdown("### School Demographics")
    dems = df_avgs_selected[['pct_asian', 'pct_black', 'pct_hispanic', 'pct_white', 'pct_other']].iloc[0] * 100
    dems_rounded = dems.round(1)
    labels = ['% Asian', '% Black or African American', '% Hispanic or Latino', '% White', '% Other']
    # Determine the index of the student_race within labels
    race_index = labels.index('% ' + student_race)

    # Create a list of 'pull' values that offsets the slice at the race_index
    pull_values = [0.1 if i == race_index else 0 for i in range(len(labels))]

    fig = go.Figure(data=[go.Pie(labels=labels, values=dems_rounded, hole=0.5,
                                  marker=dict(colors=['#2F3C4F', '#506E86', '#FCB040', '#DE703B', '#B31312']),
                                  pull=pull_values)])

    fig.update_layout(
        width=600,
        height=600,
        legend=dict(
            font=dict(
                size=14  # Change this value to your desired font size
            )
        )
    )
    return st.plotly_chart(fig)

def dems():
    st.markdown("### School Demographics")
    st.write(student_race)
    dems = df_avgs_selected[['pct_asian', 'pct_black', 'pct_hispanic', 'pct_white', 'pct_other']].iloc[0] * 100
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

    # Specify the new race categories
    race_categories = ['Asian', 'Black or African American', 'Hhispanic or Latino', 'White', 'Other']

    # Create your barplot with race categories
    sns.barplot(x=dems.values, y=race_categories, palette=colors, orient='h', ax=ax)

    # Here's how you can change the labels
    ax.set_xlabel('% of Students')
    ax.set_ylabel('Race')

    # Remove the chart borders
    sns.despine(ax=ax, left=True, bottom=True)

    # Set thicker lines
    #for spine in ax.spines.values():
    #    spine.set_linewidth(2)

    # Remove the chart border on the right
    ax.spines['right'].set_visible(False)

    # Adjust the bar width
    bar_width = 0.5
    for i, bar in enumerate(ax.patches):
        bar.set_height(bar_width)
        bar.set_y(i - bar_width / 2)

    # Add data labels
    for i, value in enumerate(dems.values):
        ax.text(value + 0.1,
                i,
                ' {:.2f}%'.format(value),  # Use {:.2f}% to format the value as a percentage with two decimal places
                ha='left',
                va='center')

    # Eliminate tick marks and axis values
    ax.tick_params(left=False, bottom=False)
    ax.xaxis.set_major_formatter(plt.NullFormatter())

    return st.pyplot(fig)

def add_line_breaks(string, n):
    if len(string) <= n:
        return string
    else:
        space_index = string.rfind(' ', 0, n)
        if space_index == -1:  # If no spaces found, don't add a line break
            return string
        else:
            return string[:space_index] + '\n' + add_line_breaks(string[space_index+1:], n)

def avg_gpa_by_group():
    # Add title
    st.markdown('### Average GPAs by Student Race/Ethnicity')

    # Define the set of text string values for the group column
    specific_groups = {'Asian', 'Black or African American', 'Hispanic or Latino', 'White'}

    # Subset the DataFrame based on the specified conditions
    subset_df = df_gpas_selected[df_gpas_selected['group'].isin(specific_groups)]

    # Extract the necessary columns
    groups = subset_df['group']
    avg_pre_test_scores = subset_df['avg_starting_gpa']
    avg_post_test_scores = subset_df['avg_ending_gpa']

    # Set the width of the bars
    bar_width = 0.35

    # Create a new figure and axes with adjusted width
    fig, ax = plt.subplots(figsize=(4, 3))  # Adjust the width as desired

    # Calculate the bar positions
    bar_positions1 = np.arange(len(groups))
    bar_positions2 = bar_positions1 + bar_width

    # Set color scheme
    color_all_1 = '#FCB040'
    color_specific_1 = '#506E86'
    colors1 = [color_specific_1 if group == student_race else color_all_1 for group in groups]

    color_all_2 = '#DE703B'
    color_specific_2 = '#2F3C4F'
    colors2 = [color_specific_2 if group == student_race else color_all_2 for group in groups]

    # Plotting the data with custom colors
    rects1 = ax.bar(bar_positions1, avg_pre_test_scores, bar_width, color=colors1)
    rects2 = ax.bar(bar_positions2, avg_post_test_scores, bar_width, color=colors2)

    # Add data labels
    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.annotate(f'{height:.2f}', xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

    # Remove borders and axis labels
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)
    # ax.set_yticks([])

    # Adjust spacing between bars
    ax.set_xlim(bar_positions1[0] - bar_width, bar_positions2[-1] + bar_width)

    # Split group names at most every 'n' characters
    n = 10  # Change this number to your preference
    groups = [add_line_breaks(group, n) for group in groups]

    # Change orientation of group labels
    ax.set_xticks(bar_positions1 + bar_width / 2)
    ax.set_xticklabels(groups, rotation=0, ha='center', fontsize=7)

    # Create custom legend handles
    legend_labels = ['Starting GPA', 'Ending GPA']
    legend_colors = [color_all_1, color_all_2]
    legend_handles = [mpatches.Patch(color=color, label=label) for color, label in zip(legend_colors, legend_labels)]

    # Add custom legend outside of the plot
    ax.legend(handles=legend_handles, loc='upper right', frameon=False, fontsize=8)

    # Remove y-axis values
    ax.set_yticks([])

    return st.pyplot(plt.gcf())

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

    # Calculate the map width based on the column width
    map_width = 100  # Adjust this value as needed

    # Create a map figure with the desired width and height
    fig = folium.Figure(width=map_width, height=map_width)
    m = folium.Map(location=map_center, zoom_start=11).add_to(fig)

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

    total_distance = 0.0
    for i in range(len(coordinates) - 1):
        start_coord = coordinates[i]
        end_coord = coordinates[i + 1]
        distance = geodesic(start_coord, end_coord).miles
        total_distance += distance

    return coordinates, total_distance

def generate_driving_directions(start_lat, start_lon, end_lat, end_lon):
    url = "https://api.openai.com/v1/completions"
    prompt = f"What are the best driving directions from {start_lat}, {start_lon} to {end_lat}, {end_lon}? Please don't include the coordinates in your response."
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
    response_json = response.json()

    if "choices" in response_json and len(response_json["choices"]) > 0:
        directions = response_json["choices"][0]["text"].strip()
        return directions.split("\n")
    else:
        return None

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
            completion_text = response_json['choices'][0]['text'].strip()

            # Trim the output to start with the first word
            #first_word_index = completion_text.find(' ')
            #if first_word_index != -1:
            #    trimmed_text = completion_text[first_word_index:].strip()
            #else:
            #    trimmed_text = completion_text

            return completion_text
        else:
            return None  # Handle the case when no choices are available
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"An error occurred: {e}")
        return None  # Return None or handle the error appropriately

def main():
    st.title(f'School Profile')
    # Add custom CSS style
    st.markdown(
        """
        <style>
        .custom-bar {
            background-color: lightgrey;
            height: 4px;
            width: 100%;
            margin-top: 10px;
            margin-bottom: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Insert the custom bar
    st.markdown('<div class="custom-bar"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns((4, 1, 5))

    with col1:
        st.markdown(f"### {school_name}")
        school_picture()
        school_info = school_description(f"Provide me with a one-paragraph description of {school_name} in Denver, Colorado")
        st.write(school_info)
        st.markdown("### Driving Route")
        m = create_map(user_lat, user_lon, school_lat, school_lon, school_name)
        # Get the route coordinates
        route_coordinates, total_distance = create_route(user_lon, user_lat, school_lon, school_lat)
        # Add the route polyline to the map
        folium.PolyLine(locations=route_coordinates, color='blue').add_to(m)

        # Render the map using folium_static
        folium_static(m, width=450)

        directions = generate_driving_directions(user_lat, user_lon, school_lat, school_lon)
        for line in directions:
            st.markdown(line)
        st.write(f"Total driving distance from your house to {school_name} is {total_distance:.1f} miles.")

    with col3:
        circle_plot()
        avg_gpa_by_group()

if __name__ == "__main__":
    main()
