import streamlit as st
from data import load_data
from model import train_model
from components import list_articles, article_view

# Load data and model
data = load_data()
model, vectorizer = train_model(data)

# Define popular and recent articles
popular_articles = data.head(5)  # Select top 5 articles as "popular"
recent_articles = data.tail(5)   # Select bottom 5 articles as "recent"

# App layout
col1, col2 = st.columns([3, 2])

# Column 1: Fake News Validation
with col1:
    st.title("Fake News Detector")
    st.write("Enter a news article's title and content to check its validity.")
    title_input = st.text_input("News Headline", "")
    content_input = st.text_area("News Content", "")

    if st.button("Check Validity"):
        if title_input and content_input:
            combined_input = f"{title_input} {content_input}"
            prediction = predict(model, vectorizer, combined_input)
            if prediction == "FAKE":
                st.error("This news is likely FAKE.")
            else:
                st.success("This news is likely REAL.")
        else:
            st.warning("Please enter both a headline and content for the article.")

# Column 2: Popular and Recent Articles
with col2:
    st.write("Popular Articles")
    list_articles(popular_articles)  # Render popular articles

    st.write("Recent Articles")
    list_articles(recent_articles)  # Render recent articles
