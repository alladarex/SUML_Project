import pandas as pd
import streamlit as st
import os

script_dir = os.path.dirname(__file__)
data_path = os.path.join(script_dir, "..", "data", "news.csv")

@st.cache_data
def load_data():
    # Load dataset
    data = pd.read_csv(data_path)
    # Ensure necessary columns are present
    required_columns = ['title', 'content', 'label']
    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"Missing column: {col}")
    return data[['title', 'content', 'label']]
