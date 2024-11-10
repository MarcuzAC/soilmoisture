import os
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Define paths for the images
MAP_IMAGE_PATH = "data/map_image/Screenshot_2-11-2024_73055_browser.dataspace.copernicus.eu.jpeg"
CLASSIFICATION_IMAGE_PATH = "data/map_image/2024-07-03-00_00_2024-07-03-23_59_Sentinel-2_L2A_Scene_classification_map_.png"
MASK_OUTPUT_FOLDER = "output_results"

# Define coordinates of area of interest
COORDINATES = [
    [[35.632233, -15.492857], [35.376801, -15.492857], 
     [35.376801, -15.352397], [35.632233, -15.352397], 
     [35.632233, -15.492857]]
]

# Function to fetch and process data
def fetch_data():
    # Sample data (Replace with your actual data)
    data = {
        "image_name": ["2024-01-01_image", "2024-02-01_image", "2024-03-01_image"],
        "dry_percentage": [10, 15, 20],
        "normal_percentage": [70, 65, 60],
        "wet_percentage": [20, 20, 20],
        "condition_summary": ["Normal", "Dry", "Wet"]
    }
    df = pd.DataFrame(data)
    
    # Extract and process date information
    df['date'] = pd.to_datetime(df['image_name'].apply(lambda x: x.split('_')[0]), errors='coerce')
    df = df.dropna(subset=['date'])
    df = df.sort_values(by='date')
    df.set_index('date', inplace=True)

    # Resample monthly data
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    monthly_df = numeric_df.resample('M').mean()
    return monthly_df, df

# Streamlit layout and rendering
def main():
    # Set up the page title and layout
    st.title("Moisture Analysis")
    
    # Display images if available
    if os.path.exists(MAP_IMAGE_PATH):
        st.image(MAP_IMAGE_PATH, caption="Map Image", use_column_width=True)

    if os.path.exists(CLASSIFICATION_IMAGE_PATH):
        st.image(CLASSIFICATION_IMAGE_PATH, caption="Classification Map", use_column_width=True)

    # Fetch and process data
    monthly_df, df = fetch_data()

    # Show raw data and resampled monthly data
    st.subheader("Monthly Moisture Data")
    st.write(monthly_df)

    st.subheader("Raw Moisture Data")
    st.write(df)

    # Plotting the monthly data using Plotly
    st.subheader("Moisture Trends Over Time")
    fig = px.line(monthly_df, x=monthly_df.index, y=['dry_percentage', 'normal_percentage', 'wet_percentage'],
                  title="Moisture Trends Over Time")
    st.plotly_chart(fig)

    # Display condition summary
    st.subheader("Condition Summary")
    condition_summary = df['condition_summary'].value_counts()
    st.write(condition_summary)

if __name__ == "__main__":
    main()
