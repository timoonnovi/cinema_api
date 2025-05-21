import pytest
from auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user
)
from database import get_db

@pytest.fixture
def test_user():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "hashed_password": get_password_hash("testpass"),
        "is_active": True,
        "is_admin": False
    }

def test_password_hashing():
    password = "securepassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_authenticate_user(test_user):
    with get_db() as db:
        # Создаем тестового пользователя
        db.execute(
            "INSERT INTO users (username, email, hashed_password, is_active) VALUES (?, ?, ?, ?)",
            (test_user["username"], test_user["email"], test_user["hashed_password"], test_user["is_active"])
        )
        db.commit()

        # Проверяем успешную аутентификацию
        user = authenticate_user("testuser", "testpass")
        assert user["username"] == "testuser"

        # Проверяем неверный пароль
        assert not authenticate_user("testuser", "wrongpass")

        # Проверяем несуществующего пользователя
        assert not authenticate_user("nonexistent", "testpass")

def test_jwt_token_creation(test_user):
    token = create_access_token(data={"sub": test_user["username"]})
    assert isinstance(token, str)
    assert len(token.split(".")) == 3  # Проверяем структуру JWT

def test_get_current_user_valid_token(test_user):
    with get_db() as db:
        db.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
            (test_user["username"], test_user["email"], test_user["hashed_password"])
        )
        db.commit()

        token = create_access_token(data={"sub": test_user["username"]})
        user = get_current_user(token)
        assert user["username"] == test_user["username"]

def test_get_current_user_invalid_token():
    with pytest.raises(Exception):
        get_current_user("invalid.token.here")