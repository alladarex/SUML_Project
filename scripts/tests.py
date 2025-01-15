import pytest
from db import init_db, insert_article, fetch_all_reports, toggle_article_label, add_report, delete_report, fetch_popular_articles, register_user, authenticate_user, fetch_random_articles
from data import load_data
from model import train_model, predict, evaluate_model
import sqlite3
import os
import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB

# Mock Data for Tests
@pytest.fixture
def mock_data():
    """Fixture to provide a mock dataset."""
    data = {
        "title": ["Title 1", "Title 2", "Title 3"],
        "content": ["Content 1", "Content 2", "Content 3"],
        "label": ["REAL", "FAKE", "REAL"]
    }
    return pd.DataFrame(data)

# Test Training
def test_train_model_with_temp_files(mock_data, tmp_path):
    """Test training the model and saving vectorizer.pkl and model.pkl to temporary paths."""
    # Create temporary paths
    model_path = tmp_path / "test_model.pkl"
    vectorizer_path = tmp_path / "test_vectorizer.pkl"

    # Train the model
    model, vectorizer = train_model(mock_data, model_path=str(model_path), vectorizer_path=str(vectorizer_path))

    # Verify that the model and vectorizer files were created
    assert os.path.exists(model_path)
    assert os.path.exists(vectorizer_path)

    # Load the saved model and vectorizer to ensure they are valid
    with open(model_path, "rb") as f:
        loaded_model = pickle.load(f)
    with open(vectorizer_path, "rb") as f:
        loaded_vectorizer = pickle.load(f)

    # Verify that the loaded objects are usable
    assert isinstance(loaded_model, MultinomialNB)
    assert isinstance(loaded_vectorizer, CountVectorizer)

# Test Prediction
def test_predict_with_temp_files(mock_data, tmp_path):
    """Test prediction functionality using a temporary model and vectorizer."""
    # Create temporary paths
    model_path = tmp_path / "test_model.pkl"
    vectorizer_path = tmp_path / "test_vectorizer.pkl"

    # Train the model and save files to temporary paths
    model, vectorizer = train_model(mock_data, model_path=str(model_path), vectorizer_path=str(vectorizer_path))

    # Load the saved model and vectorizer
    with open(model_path, "rb") as f:
        loaded_model = pickle.load(f)
    with open(vectorizer_path, "rb") as f:
        loaded_vectorizer = pickle.load(f)

    # Test prediction
    test_text = "Title 4 Content 4"
    transformed_text = loaded_vectorizer.transform([test_text])
    prediction = loaded_model.predict(transformed_text.toarray())

    # Verify that the prediction is valid
    assert prediction[0] in ["REAL", "FAKE"]

# Test Evaluation
def test_evaluate_model_with_temp_files(mock_data, tmp_path):
    """Test model evaluation and logging with temporary model and vectorizer files."""
    # Create temporary paths
    model_path = tmp_path / "test_model.pkl"
    vectorizer_path = tmp_path / "test_vectorizer.pkl"

    # Train the model and split data for evaluation
    model, vectorizer = train_model(mock_data, model_path=str(model_path), vectorizer_path=str(vectorizer_path))
    x = vectorizer.transform(mock_data["title"] + " " + mock_data["content"])
    y = mock_data["label"]
    _, x_test, _, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # Evaluate the model
    accuracy, report, confusion = evaluate_model(model, vectorizer, x_test, y_test, model_path=str(model_path), vectorizer_path=str(vectorizer_path))

    # Verify evaluation metrics
    assert accuracy >= 0  # Accuracy should be a valid number
    assert "REAL" in report  # Report should contain labels
    assert "FAKE" in report
    assert confusion is not None

    # Verify that the model and vectorizer were re-saved during evaluation
    assert os.path.exists(model_path)
    assert os.path.exists(vectorizer_path)

# Fixtures
@pytest.fixture
def test_db(tmp_path):
    """Fixture to create a temporary database for testing."""
    db_path = tmp_path / "test_articles.db"
    data = load_data()
    init_db(data, db_path=str(db_path))
    yield str(db_path)  # Provide the temporary DB path to tests

# Database Initialization Tests
def test_database_initialization(test_db):
    """Test if the database initializes correctly."""
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    expected_tables = {"articles", "users", "user_articles", "reports"}
    assert expected_tables.issubset(tables)

# User Authentication Tests
def test_user_registration(test_db):
    """Test user registration functionality."""
    assert register_user("testuser", "password123", "normal", db_path=test_db) is True
    assert register_user("testuser", "password123", "normal", db_path=test_db) is False  # Duplicate user

def test_user_login(test_db):
    """Test user login functionality."""
    register_user("testuser", "password123", "normal", db_path=test_db)
    user = authenticate_user("testuser", "password123", db_path=test_db)
    assert user is not None
    assert user[1] == "testuser"

    invalid_user = authenticate_user("wronguser", "wrongpassword", db_path=test_db)
    assert invalid_user is None

# Article Management Tests
def test_article_insertion(test_db):
    """Test inserting articles into the database."""
    article_id = insert_article("Test Title", "Test Content", "REAL", db_path=test_db)
    assert article_id is not None

    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
    article = cursor.fetchone()
    conn.close()

    assert article[1] == "Test Title"
    assert article[2] == "Test Content"
    assert article[3] == "REAL"

def test_toggle_article_label(test_db):
    """Test toggling an article's label between FAKE and REAL."""
    article_id = insert_article("Toggle Title", "Toggle Content", "FAKE", db_path=test_db)
    new_label = toggle_article_label(article_id, db_path=test_db)
    assert new_label == "REAL"

    new_label = toggle_article_label(article_id, db_path=test_db)
    assert new_label == "FAKE"

# Report Management Tests
def test_report_creation(test_db):
    """Test creating a report for an article."""
    article_id = insert_article("Report Title", "Report Content", "REAL", db_path=test_db)
    add_report(1, article_id, "This article is inaccurate.", db_path=test_db)

    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE article_id = ?", (article_id,))
    report = cursor.fetchone()
    conn.close()

    assert report is not None
    assert report[2] == "This article is inaccurate."

def test_report_deletion(test_db):
    """Test deleting a report from the database."""
    article_id = insert_article("Delete Test", "Delete Content", "REAL", db_path=test_db)
    add_report(1, article_id, "This report should be deleted.", db_path=test_db)

    delete_report(1, article_id, db_path=test_db)

    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE article_id = ?", (article_id,))
    report = cursor.fetchone()
    conn.close()

    assert report is None

def test_fetch_random_articles(test_db):
    """Test fetching random articles."""
    insert_article("Random Title 1", "Random Content 1", "REAL", db_path=test_db)
    insert_article("Random Title 2", "Random Content 2", "FAKE", db_path=test_db)

    articles = fetch_random_articles(limit=2, db_path=test_db)
    assert len(articles) == 2

def test_fetch_all_reports(test_db):
    """Test fetching all reports from the database."""
    article_id1 = insert_article("Report Title 1", "Report Content 1", "REAL", db_path=test_db)
    article_id2 = insert_article("Report Title 2", "Report Content 2", "FAKE", db_path=test_db)

    add_report(1, article_id1, "First report content.", db_path=test_db)
    add_report(2, article_id2, "Second report content.", db_path=test_db)

    reports = fetch_all_reports(db_path=test_db)

    assert len(reports) == 2

    report1 = reports[0]
    assert report1[0] == article_id1
    assert report1[1] == "Report Title 1"
    assert report1[2] == "First report content."

    report2 = reports[1]
    assert report2[0] == article_id2
    assert report2[1] == "Report Title 2"
    assert report2[2] == "Second report content."

# Error Handling Tests
def test_invalid_article_insertion(test_db):
    """Test inserting an article with invalid data."""
    with pytest.raises(sqlite3.IntegrityError):
        insert_article(None, None, None, db_path=test_db)
