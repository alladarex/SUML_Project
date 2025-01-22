import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import mlflow
import mlflow.sklearn
import pickle
import streamlit as st

script_dir = os.path.dirname(__file__)
default_model_path = os.path.join(script_dir, "..", "models", "model.pkl")
default_vectorizer_path = os.path.join(script_dir, "..", "models", "vectorizer.pkl")

@st.cache_resource
def train_model(data, model_path=None, vectorizer_path=None, alpha=1.0):
    # Use the provided paths or fall back to the defaults
    model_path = model_path or default_model_path
    vectorizer_path = vectorizer_path or default_vectorizer_path

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
    train_acc = model.score(x_train, y_train)
    test_acc = model.score(x_test, y_test)

    # Save the vectorizer
    with open(vectorizer_path, "wb") as f:
        pickle.dump(vectorizer, f)

    # Save the model
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    # Log to MLflow
    with mlflow.start_run():
        mlflow.log_param("model_type", "MultinomialNB")
        mlflow.log_param("vectorizer", "CountVectorizer")
        mlflow.log_param("alpha", alpha)
        mlflow.log_metric("train_accuracy", train_acc)
        mlflow.log_metric("test_accuracy", test_acc)
        mlflow.log_artifact(vectorizer_path, artifact_path="preprocessing")
        mlflow.log_artifact(model_path, artifact_path="model")

    print(f"Train Accuracy: {train_acc}")
    print(f"Test Accuracy: {test_acc}")

    # Return model, vectorizer, and accuracy
    return model, vectorizer, accuracy

def predict(model, vectorizer, text):
    transformed_text = vectorizer.transform([text]).toarray()
    return model.predict(transformed_text)[0]

def evaluate_model(model, vectorizer, x_test, y_test, model_path=None, vectorizer_path=None):
    """
    Evaluates the model on test data and logs evaluation metrics to MLflow.
    """
    # Use the provided paths or fall back to the defaults
    model_path = model_path or default_model_path
    vectorizer_path = vectorizer_path or default_vectorizer_path

    # Predictions
    predictions = model.predict(x_test)

    # Calculate metrics
    acc = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True)
    confusion = confusion_matrix(y_test, predictions)

    # Save the vectorizer and model again after evaluation (if updated paths are provided)
    with open(vectorizer_path, "wb") as f:
        pickle.dump(vectorizer, f)

    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    # Log evaluation metrics to MLflow
    with mlflow.start_run():
        mlflow.log_metric("evaluation_accuracy", acc)
        mlflow.log_metric("precision_fake", report["FAKE"]["precision"])
        mlflow.log_metric("recall_fake", report["FAKE"]["recall"])
        mlflow.log_metric("precision_real", report["REAL"]["precision"])
        mlflow.log_metric("recall_real", report["REAL"]["recall"])

    print("Accuracy:", acc)
    print("Classification Report:\n", classification_report(y_test, predictions))
    print("Confusion Matrix:\n", confusion)

    return acc, report, confusion