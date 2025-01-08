import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import streamlit as st

@st.cache_resource
def train_model(data):
    # Combine title and content
    data['combined'] = data['title'] + " " + data['content']
    x = np.array(data['combined'])
    y = np.array(data['label'])

    # Vectorize text
    vectorizer = CountVectorizer()
    x = vectorizer.fit_transform(x)

    # Train-test split
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # Train model
    model = MultinomialNB()
    model.fit(x_train, y_train)

    # Calculate accuracy on the test set
    y_pred = model.predict(x_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Return model, vectorizer, and accuracy
    return model, vectorizer, accuracy

def predict(model, vectorizer, text):
    transformed_text = vectorizer.transform([text]).toarray()
    return model.predict(transformed_text)[0]
