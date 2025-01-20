import sqlite3
import streamlit as st
import os

standard_db_path = "articles.db"

# Initialize SQLite database connection
@st.cache_resource
def init_db(csv_data, db_path=None):
    """Initialize the SQLite database without wiping existing user data."""
    db_path = db_path or os.getenv("DB_PATH", standard_db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create the articles table with the new 'confidence' column
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            label TEXT NOT NULL,
            confidence REAL DEFAULT 1.0  -- New column added
        )
    ''')

    # Create the users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            user_type TEXT NOT NULL CHECK(user_type IN ('normal', 'admin'))
        )
    ''')

    # Create the user_articles table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_articles (
            user_id INTEGER NOT NULL,
            article_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, article_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(article_id) REFERENCES articles(id)
        )
    ''')

    # Reports table
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            user_id INTEGER NOT NULL,
            article_id INTEGER NOT NULL,
            report_content TEXT NOT NULL,
            PRIMARY KEY (user_id, article_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (article_id) REFERENCES articles(id)
        )
    ''')

    # Insert articles into the database
    c.execute("DELETE FROM articles")  # Clear articles only
    for _, row in csv_data.iterrows():
        c.execute("INSERT INTO articles (title, content, label, confidence) VALUES (?, ?, ?, ?)",
                  (row['title'], row['content'], row['label'], row.get('confidence', 0.0)))

    # Ensure guest user exists
    c.execute("SELECT id FROM users WHERE username = 'guest'")
    guest_exists = c.fetchone()
    if not guest_exists:
        c.execute("INSERT INTO users (username, password, user_type) VALUES ('guest', 'guest', 'normal')")

    # Link guest user to all articles
    guest_user_id = c.execute("SELECT id FROM users WHERE username = 'guest'").fetchone()[0]
    c.execute("SELECT id FROM articles")
    article_ids = c.fetchall()
    for article_id in article_ids:
        c.execute("INSERT OR IGNORE INTO user_articles (user_id, article_id) VALUES (?, ?)", (guest_user_id, article_id[0]))

    conn.commit()
    conn.close()

# Other functions (examples):
def insert_article(title, content, label, confidence=1.0, db_path=None):
    db_path = db_path or os.getenv("DB_PATH", standard_db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO articles (title, content, label, confidence) VALUES (?, ?, ?, ?)", (title, content, label, float(confidence)))
    article_id = c.lastrowid
    conn.commit()
    conn.close()
    return article_id

def fetch_articles(limit=10, db_path=None):
    db_path = db_path or os.getenv("DB_PATH", standard_db_path)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id, title, content, label, confidence FROM articles ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def fetch_popular_articles(limit=5):
    """
    Fetch the most popular articles based on the number of users linked to each article.
    Include confidence for each article.
    """
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    # Query to fetch articles with user count and confidence
    c.execute('''
        SELECT a.id, a.title, a.content, a.label, a.confidence, COUNT(ua.user_id) as user_count
        FROM articles a
        LEFT JOIN user_articles ua ON a.id = ua.article_id
        GROUP BY a.id
        ORDER BY user_count DESC, a.id ASC
        LIMIT ?
    ''', (limit,))

    articles = c.fetchall()
    conn.close()
    return articles


def fetch_recent_articles(limit=5):
    """
    Fetch the most recent articles based on the highest primary key (id).
    Include confidence for each article.
    """
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    # Fetch articles ordered by 'id' in descending order with confidence
    c.execute("SELECT id, title, content, label, confidence FROM articles ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def fetch_random_articles(limit=5):
    """
    Fetch random articles from the database.
    Include confidence for each article.
    """
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    # Use SQL's RANDOM() to fetch random rows with confidence
    c.execute("SELECT id, title, content, label, confidence FROM articles ORDER BY RANDOM() LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def register_user(username, password, user_type='normal'):
    """Register a new user."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)", (username, password, user_type))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"IntegrityError: {e}")  # Log the error
        return False  # Username already exists
    except Exception as e:
        print(f"Error registering user: {e}")  # Log other errors
        return False
    finally:
        conn.close()


def authenticate_user(username, password):
    """Authenticate a user by username and password."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = c.fetchone()
    conn.close()

    return user  # Returns user row if found, otherwise None


# def add_user_article_relation(user_id, article_id):
#     """Add a relation between a user and an article."""
#     conn = sqlite3.connect("articles.db")
#     c = conn.cursor()

#     try:
#         c.execute("INSERT OR IGNORE INTO user_articles (user_id, article_id) VALUES (?, ?)", (user_id, article_id))
#         conn.commit()
#     finally:
#         conn.close()
def add_user_article_relation(user_id, article_id):
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO user_articles (user_id, article_id) VALUES (?, ?)", (user_id, article_id))
    conn.commit()
    conn.close()



def fetch_articles_for_user(user_id):
    """Fetch all articles linked to a specific user."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    c.execute('''
        SELECT a.id, a.title, a.content, a.label
        FROM articles a
        INNER JOIN user_articles ua ON a.id = ua.article_id
        WHERE ua.user_id = ?
    ''', (user_id,))
    
    articles = c.fetchall()
    conn.close()
    return articles


def add_report(user_id, article_id, report_content):
    """Add a report to the reports table."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    try:
        c.execute('''
            INSERT INTO reports (user_id, article_id, report_content)
            VALUES (?, ?, ?)
        ''', (user_id, article_id, report_content))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Report already exists for this user and article.")
    finally:
        conn.close()

def fetch_all_reports():
    """Fetch all reports from the database."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()
    c.execute('''
        SELECT r.article_id, a.title, r.report_content, r.user_id
        FROM reports r
        INNER JOIN articles a ON r.article_id = a.id
    ''')
    reports = c.fetchall()
    conn.close()
    return reports


def delete_report(user_id, article_id):
    """Delete a report from the database."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()
    c.execute("DELETE FROM reports WHERE user_id = ? AND article_id = ?", (user_id, article_id))
    conn.commit()
    conn.close()

def delete_article(article_id):
    """Delete an article from the database and its reports."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()
    c.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    c.execute("DELETE FROM reports WHERE article_id = ?", (article_id,))
    conn.commit()
    conn.close()

def toggle_article_label(article_id):
    """Toggle the label of an article between FAKE and REAL."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()
    c.execute("SELECT label FROM articles WHERE id = ?", (article_id,))
    current_label = c.fetchone()[0]

    new_label = "REAL" if current_label == "FAKE" else "FAKE"
    c.execute("UPDATE articles SET label = ? WHERE id = ?", (new_label, article_id))
    conn.commit()
    conn.close()
    return new_label  # Return the new label
