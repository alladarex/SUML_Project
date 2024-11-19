import sqlite3

# Initialize SQLite database connection
def init_db(csv_data):
    """Initialize the SQLite database, create tables, and populate from CSV if empty."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    # Create the articles table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            label TEXT NOT NULL
        )
    ''')

    # Check if the table is empty
    c.execute("SELECT COUNT(*) FROM articles")
    if c.fetchone()[0] == 0:  # If the table is empty
        # Insert rows from CSV
        for _, row in csv_data.iterrows():
            c.execute("INSERT INTO articles (title, content, label) VALUES (?, ?, ?)",
                      (row['title'], row['content'], row['label']))
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



def fetch_random_articles(limit=5):
    """Fetch random articles from the database."""
    conn = sqlite3.connect("articles.db")
    c = conn.cursor()

    # Use SQL's RANDOM() to fetch random rows
    c.execute("SELECT id, title, content, label FROM articles ORDER BY RANDOM() LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
