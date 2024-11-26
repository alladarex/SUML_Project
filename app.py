import streamlit as st
from data import load_data
from model import train_model, predict
from components import article_view
from db import init_db, insert_article, fetch_popular_articles, fetch_recent_articles

# Initialize session state for articles and selected article
if "popular_articles" not in st.session_state:
    st.session_state["popular_articles"] = None
if "recent_articles" not in st.session_state:
    st.session_state["recent_articles"] = None
if "selected_article" not in st.session_state:
    st.session_state["selected_article"] = None

# Load data from CSV
data = load_data()

# Initialize the SQLite database with CSV data
init_db(data)

# Train model
@st.cache_resource
def get_trained_model(data):
    return train_model(data)

model, vectorizer = get_trained_model(data)

# Fetch articles only if they are not already in session state
if st.session_state["popular_articles"] is None:
    st.session_state["popular_articles"] = fetch_popular_articles(limit=5)
if st.session_state["recent_articles"] is None:
    st.session_state["recent_articles"] = fetch_recent_articles(limit=5)

# Use session state to access articles
popular_articles = st.session_state["popular_articles"]
recent_articles = st.session_state["recent_articles"]

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

            # Save to database
            label = "FAKE" if prediction == "FAKE" else "REAL"
            insert_article(title_input, content_input, label)

            # Display result
            if label == "FAKE":
                st.error("This news is likely FAKE.")
            else:
                st.success("This news is likely REAL.")
        else:
            st.warning("Please enter both a headline and content for the article.")

# Column 2: Popular and Recent Articles
with col2:
    st.write("Popular Articles")
    for article in popular_articles:
        id, title, content, label, count = article
        if st.button(f"{title} ({count})", key=f"popular_{id}"):
            st.session_state["selected_article"] = {"title": title, "content": content, "label": label}

    st.write("Recent Articles")
    for article in recent_articles:
        id, title, content, label = article
        if st.button(title, key=f"recent_{id}"):
            st.session_state["selected_article"] = {"title": title, "content": content, "label": label}

# Display selected article in a dialog
if st.session_state["selected_article"]:
    article_view(st.session_state["selected_article"])
