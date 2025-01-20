import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

st.set_page_config(layout="wide")
# Load and prepare the data with st.cache_data to cache the dataset
@st.cache_data
def load_data():
    # Load dataset (ensure "news.csv" is in the same directory or provide the full path)
    data = pd.read_csv("news.csv")
    data = data[['title', 'content', 'label']]  # Assuming 'title' is the column with news titles, 'content' with article text, and 'label' with FAKE/REAL
    return data

# Train the model with st.cache_resource to cache the trained model and vectorizer
@st.cache_resource
def train_model(data):
    # Combine title and content for feature extraction
    data['combined'] = data['title'] + " " + data['content']
    x = np.array(data["combined"])
    y = np.array(data["label"])

    # Vectorize the combined title and content text
    cv = CountVectorizer()
    x = cv.fit_transform(x)

    # Split data into training and test sets
    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.2, random_state=42)

    # Train the model using Multinomial Naive Bayes
    model = MultinomialNB()
    model.fit(xtrain, ytrain)
    
    # Return model and vectorizer
    return model, cv



# Load data and train model
data = load_data()
model, cv = train_model(data)

@st.dialog("Article details", width="large")
def article(data):
    st.title(data['title'])
    st.write(data['content'])
    if data['label'] == "FAKE":
        st.error("This news is likely FAKE.")
    else:
        st.success("This news is likely REAL.")

# Streamlit app layout
col1, col2 = st.columns([3,2])

# Column 1 contains the validation function
with col1:
    st.title("Fake News Detector")
    st.write("Enter a news article's title and content to check its validity.")

    # User input fields
    title_input = st.text_input("News Headline", "")
    content_input = st.text_area("News Content", "")

    # Predict button
    if st.button("Check Validity"):
        if title_input and content_input:
            # Combine the title and content inputs
            combined_input = title_input + " " + content_input

            # Transform the combined input using the trained vectorizer
            transformed_input = cv.transform([combined_input]).toarray()

            # Get prediction from the model
            prediction = model.predict(transformed_input)

            # Display the result
            if prediction[0] == "FAKE":
                st.error("This news is likely FAKE.")
            else:
                st.success("This news is likely REAL.")
        else:
            st.warning("Please enter both a headline and content for the article.")


# Column 2 contains collections of popular/recent articles
with col2:
    #TODO: Select popular and recent articles
    popular_articles = data.head(5)  # dummy data
    recent_articles = data.tail(5)  # dummy data

    # Display Popular Articles
    st.write("Popular articles")
    for idx, row in popular_articles.iterrows():
        if st.button(row['title'], key=f"popular_{idx}",use_container_width=True):
            # Trigger the article function
            article(row)

    # Display Recent Articles
    st.write("Recent articles")
    for idx, row in recent_articles.iterrows():
        if st.button(row['title'], key=f"recent_{idx}",use_container_width=True):
            # Trigger the article function
            article(row)

