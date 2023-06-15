import streamlit as st
import requests
import pickle
import io
import zipfile
import pandas as pd
import tempfile
import os
from PIL import Image
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_icon=None, layout="centered", initial_sidebar_state="collapsed", menu_items=None)

def best_schools(user_vals):
    # Create a temporary directory
    temp_dir = tempfile.gettempdir()
    model_dir = os.path.join(temp_dir, 'models')

    # Check if models have already been downloaded
    if not os.path.exists(model_dir) or len(os.listdir(model_dir)) < 176:
        # URL for the zip file
        url = 'https://storage.googleapis.com/school-finder-models/models.zip'

        # Download the zip file
        response = requests.get(url)
        response.raise_for_status()  # Ensure we got a successful response

        # Save the zip file to disk
        with open(f'{temp_dir}/models.zip', 'wb') as f:
            f.write(response.content)

        # Extract the models
        with zipfile.ZipFile(f'{temp_dir}/models.zip', 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

    # Now that the models are extracted, you can load each one and generate predictions
    predictions = {}

    for i in range(1, 177):
        with open(f'{model_dir}/{i}_model.pkl', 'rb') as file:
            pickle_model = pickle.load(file)

            # Make predictions
            predict_val = pickle_model.predict(user_vals)
            predictions[i] = predict_val[0]

    predictions_df = pd.DataFrame.from_dict(predictions, orient='index', columns=['prediction'])

    # Reset the index and name it 'school_id'
    predictions_df = predictions_df.reset_index().rename(columns={'index': 'school_id'})
    predictions_df = predictions_df.sort_values('prediction', ascending=False)

    return predictions_df

def main():
    st.title('Welcome to the (Fake) Denver School Finder')
    st.markdown(
        """
        <style>
        .stButton {
            margin-top: 100px;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 200px;
            height: 50px;
            font-size: 18px;
        }
        .stApp {
            background-image: url("https://imgur.com/prYJXix.jpg");
            background-attachment: fixed;
            background-size: cover;
        }
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
    
    # Add custom CSS style
    st.markdown('<div class="custom-bar"></div>', unsafe_allow_html=True)

    st.write('The goal of this school finder is to help you find the best school for your child.'
             'Answering the questions below will help us determine which school will help your child grow the most.')

    school_type = st.radio('What type of school are you looking for?', ('Elementary School', 'Middle School', 'High School'))
    options = ['Special Education', 'Free/Reduced Lunch', 'English Language Learner']
    selected_options = st.multiselect('Please select the services your child receives:', options)
    race_ethnicity = st.radio("Please click on your child's race/ethnicity:", ('Asian', 'Black or African American', 'Hispanic or Latino', 'White', 'Other'))
    starting_gpa = st.slider("Enter your child's current GPA [0-1]", 0.0, 1.0, .5)
        
    # Sync the race_ethnicity selection with st.session_state.race
    if 'race' not in st.session_state:
        st.session_state.race = 'Asian'

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

    characteristics = [[sped, frl, ell, race_vals[0], race_vals[1], race_vals[2], race_vals[3], starting_gpa]]
    vals = pd.DataFrame(characteristics, columns=['sped_flag', 'frl_flag', 'ell_flag', 'asian_flag', 'black_flag', 'hispanic_flag', 'white_flag', 'starting_gpa'])
    
    with st.spinner('Calculating best schools for your child...'):
        top_schools = best_schools(vals)
        top_schools['school_type_keep'] = school_type
        # Check if you've already initialized the data
        if 'df' not in st.session_state:
            # Save the data to session state
            st.session_state.df = pd.DataFrame()
        st.session_state.df = top_schools
        st.session_state.race = race_ethnicity
        next_page = st.button("Click to See Schools")
        if next_page:
            switch_page("page_02")   

if __name__ == "__main__":
    main()
