import sqlite3

# Initialize SQLite database connection
def init_db(csv_data):
    """Initialize the SQLite database, create tables, and populate with aggregated CSV data."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    # Recreate the articles table with the 'count' column
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            label TEXT NOT NULL,
            count INTEGER NOT NULL
        )
    ''')

    # Delete existing rows to recreate the database
    c.execute("DELETE FROM articles")

    # Aggregate duplicate rows in the CSV
    aggregated_data = (
        csv_data.groupby(['title', 'content', 'label'])
        .size()
        .reset_index(name='count')  # Add the 'count' column
    )

    # Insert the aggregated data into the database
    for _, row in aggregated_data.iterrows():
        c.execute("INSERT INTO articles (title, content, label, count) VALUES (?, ?, ?, ?)",
                  (row['title'], row['content'], row['label'], row['count']))

    conn.commit()
    conn.close()



def insert_article(title, content, label):
    """Insert a new article into the database."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()
    c.execute("INSERT INTO articles (title, content, label) VALUES (?, ?, ?)", (title, content, label))
    conn.commit()
    conn.close()

def fetch_articles(limit=10):
    """Fetch articles from the database."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()
    c.execute("SELECT id, title, content, label FROM articles ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def fetch_popular_articles(limit=5):
    """Fetch the most popular articles based on the count."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    # Fetch articles ordered by 'count' in descending order
    c.execute("SELECT id, title, content, label, count FROM articles ORDER BY count DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def fetch_recent_articles(limit=5):
    """Fetch the most recent articles based on the highest primary key (id)."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    # Fetch articles ordered by 'id' in descending order
    c.execute("SELECT id, title, content, label FROM articles ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def fetch_random_articles(limit=5):
    """Fetch random articles from the database."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    # Use SQL's RANDOM() to fetch random rows
    c.execute("SELECT id, title, content, label FROM articles ORDER BY RANDOM() LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
