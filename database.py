import sqlite3
from contextlib import contextmanager

DATABASE = "cinema.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            is_admin BOOLEAN DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            duration INTEGER,
            genre TEXT,
            rating REAL
        );
        
        CREATE TABLE IF NOT EXISTS halls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            capacity INTEGER NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS screenings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            hall_id INTEGER NOT NULL,
            start_time DATETIME NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            FOREIGN KEY (hall_id) REFERENCES halls(id)
        );
        
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            screening_id INTEGER NOT NULL,
            seat_number INTEGER NOT NULL,
            purchase_time DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (screening_id) REFERENCES screenings(id)
        );
        
        CREATE TABLE IF NOT EXISTS movie_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            rating REAL NOT NULL,
            review TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (movie_id) REFERENCES movies(id),
            UNIQUE(user_id, movie_id)
        );
        """)
