import sqlite3



def create_table():
    conn = sqlite3.connect("dosug.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            mood TEXT,
            free_time REAL,
            people INTEGER
        )
    """)
    conn.commit()
    conn.close()


def init_ratings_table():
    conn = sqlite3.connect("favorites.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            suggestion TEXT,
            rating INTEGER
        )
    """)
    conn.commit()
    conn.close()




def save_to_db(user_id, mood, free_time, people):
    conn = sqlite3.connect("dosug.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO activity_log (user_id, mood, free_time, people)
        VALUES (?, ?, ?, ?)
    """, (user_id, mood, free_time, people))
    conn.commit()
    conn.close()


def save_rating(user_id, suggestion, rating):
    conn = sqlite3.connect("favorites.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ratings (user_id, suggestion, rating)
        VALUES (?, ?, ?)
    """, (user_id, suggestion, rating))
    conn.commit()
    conn.close()
