import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Use the full page instead of a narrow central column
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.set_option('deprecation.showPyplotGlobalUse', False)

def scatter_chart():
    url = 'https://storage.googleapis.com/school-finder-models/avg_gpas_by_group.csv'
    df = pd.read_csv(url)
    df2 = df[df['group'].isin(['Asian', 'Black or African American', 'Hispanic or Latino', 'White', 'Special Education', 'English Language Learner', 'Free or Reduced Lunch'])]  
    
    # Create a Streamlit app
    st.title("Average GPAs by School and Group")

    # Get the unique group values from the dataset
    groups = df2['group'].unique()

    # Add a multiselect widget to select groups with a unique key
    selected_groups = st.multiselect("Select Groups", groups, default=groups, key="group_selector_" + str(len(groups)))

    # Filter the dataframe based on selected groups
    filtered_df = df2[df2['group'].isin(selected_groups)]

    # Set the style of the plot
    sns.set_style('whitegrid')

    # Create the scatterplot
    plt.figure(figsize=(12, 8))
    sns.scatterplot(data=filtered_df, x='avg_starting_gpa', y='avg_ending_gpa', hue='group', palette='Set1')

    # Remove the grid lines
    sns.despine()

    # Move the legend below the chart
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=len(selected_groups))

    # Set plot labels and title
    plt.xlabel('Starting GPA')
    plt.ylabel('Ending GPA')
    plt.title('Scatterplot of GPA')

    # Display the plot
    st.pyplot()