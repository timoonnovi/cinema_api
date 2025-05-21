import pytest
from datetime import datetime, timedelta
from crud import (
    create_user,
    get_user_by_username,
    create_movie,
    get_movie,
    create_screening,
    create_rating,
    get_user_ratings
)
from database import get_db

@pytest.fixture
def sample_data():
    return {
        "user": {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass"
        },
        "movie": {
            "title": "Inception",
            "description": "Dream within a dream",
            "duration": 148,
            "genre": "Sci-Fi",
            "rating": 8.8
        },
        "screening": {
            "movie_id": 1,
            "hall_id": 1,
            "start_time": datetime.now() + timedelta(days=1),
            "price": 350.0
        },
        "rating": {
            "user_id": 1,
            "movie_id": 1,
            "rating": 5.0,
            "review": "Great movie!"
        }
    }

def test_user_crud(sample_data):
    with get_db() as db:
        # Create
        user = create_user(db, sample_data["user"])
        assert user["username"] == sample_data["user"]["username"]
        
        # Read
        fetched_user = get_user_by_username(db, sample_data["user"]["username"])
        assert fetched_user["email"] == sample_data["user"]["email"]

def test_movie_crud(sample_data):
    with get_db() as db:
        # Create
        movie = create_movie(db, sample_data["movie"])
        assert movie["title"] == sample_data["movie"]["title"]
        
        # Read
        fetched_movie = get_movie(db, movie["id"])
        assert fetched_movie["genre"] == sample_data["movie"]["genre"]

def test_screening_and_rating_crud(sample_data):
    with get_db() as db:
        # Создаем пользователя и фильм для теста
        create_user(db, sample_data["user"])
        create_movie(db, sample_data["movie"])

        # Screening
        screening = create_screening(db, sample_data["screening"])
        assert screening["price"] == sample_data["screening"]["price"]

        # Rating
        rating = create_rating(db, sample_data["rating"])
        assert rating["rating"] == sample_data["rating"]["rating"]

        # Get ratings
        ratings = get_user_ratings(db, sample_data["rating"]["user_id"])
        assert len(ratings) == 1
        assert ratings[0]["review"] == sample_data["rating"]["review"]