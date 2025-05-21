from fastapi.testclient import TestClient
from main import app
import sqlite3
import pytest

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    # Создаем временную базу данных для тестов
    test_db = "test_cinema.db"
    conn = sqlite3.connect(test_db)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        is_admin BOOLEAN DEFAULT 0
    );
    
    INSERT INTO users (username, email, hashed_password, is_admin)
    VALUES ('admin', 'admin@example.com', 'hashedpass', 1);
    
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        duration INTEGER,
        genre TEXT,
        rating REAL
    );
    
    INSERT INTO movies (title, description, duration, genre, rating)
    VALUES ('Inception', 'Dream within a dream', 148, 'Sci-Fi', 8.8),
           ('The Shawshank Redemption', 'Prison drama', 142, 'Drama', 9.3);
    """)
    conn.commit()
    yield conn
    conn.close()
    # Можно удалить тестовую базу после тестов
    import os
    os.remove(test_db)

def test_register():
    response = client.post(
        "/register",
        json={"username": "testuser", "email": "test@example.com", "password": "testpass"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_login():
    response = client.post(
        "/token",
        data={"username": "admin", "password": "hashedpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_endpoint():
    login_response = client.post(
        "/token",
        data={"username": "admin", "password": "hashedpass"}
    )
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/users/me/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "admin"

def test_movie_recommendations():
    response = client.get("/movies/1/recommendations")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_user_recommendations():
    login_response = client.post(
        "/token",
        data={"username": "admin", "password": "hashedpass"}
    )
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/users/me/recommendations",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200