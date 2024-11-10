import os
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from pymongo import MongoClient
import re
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection configuration
MONGO_URI = os.getenv("MONGO_URI")  # Store MongoDB URI in .env file
client = MongoClient(MONGO_URI)
db = client['moisture_results']  # Replace with your database name
moisture_collection = db['moisture_results']  # Replace with your collection name

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
    # Fetch data from MongoDB
    cursor = moisture_collection.find({}, {"_id": 0, "image_name": 1, "dry_percentage": 1, "normal_percentage": 1, "wet_percentage": 1, "condition_summary": 1})
    df = pd.DataFrame(list(cursor))
    
    # Extract and process date information
    df['date'] = df['image_name'].apply(lambda x: re.search(r"\d{4}-\d{2}-\d{2}", x).group() if re.search(r"\d{4}-\d{2}-\d{2}", x) else None)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
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
