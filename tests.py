import pytest
from db import init_db, insert_article, fetch_all_reports, toggle_article_label, add_report, delete_report, fetch_popular_articles, register_user, authenticate_user, fetch_random_articles
from data import load_data
import sqlite3
import os

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
