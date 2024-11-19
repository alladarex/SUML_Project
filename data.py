import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # Load dataset
    data = pd.read_csv("news.csv")
    # Ensure necessary columns are present
    required_columns = ['title', 'content', 'label']
    for col in required_columns:
        if col not in data.columns:
            raise ValueError(f"Missing column: {col}")
    return data[['title', 'content', 'label']]
