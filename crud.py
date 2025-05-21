from auth import get_password_hash, verify_password
import schemas
from fastapi import HTTPException

# Users
# Получение объекта пользователя по имени
def get_user_by_username(db, username: str):
    return db.execute(
        "SELECT * FROM users WHERE username = ?", 
        (username,)
    ).fetchone()

# Получение объекта пользователя по почте
def get_user_by_email(db, email: str):
    return db.execute(
        "SELECT * FROM users WHERE email = ?", 
        (email,)
    ).fetchone()

# Регистрация нового пользователя
def create_user(db, user: schemas.UserBase):
    hashed_password = get_password_hash(user.password)
    db.execute(
        "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
        (user.username, user.email, hashed_password)
    )
    db.commit()
    usr = db.execute(
        "SELECT * FROM users WHERE username = ?",
        (user.username,)
    ).fetchone()
    return {"username": usr['username'],
            "email": usr['email'],
            "id": usr['id'],
            "is_active": usr['is_active'],
            "is_admin": usr['is_admin']}

# Удаление пользователя
def delete_user(db, user_id: int, password: str):
    # 1. Проверяем существование пользователя
    user = db.execute(
        "SELECT * FROM users WHERE id = ?", 
        (user_id,)
    ).fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Проверяем пароль
    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # 3. Удаляем связанные данные (каскадное удаление)
    db.execute("DELETE FROM movie_ratings WHERE user_id = ?", (user_id,))
    db.execute("DELETE FROM tickets WHERE user_id = ?", (user_id,))
    
    # 4. Удаляем самого пользователя
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    
    return {"message": "User deleted successfully"}

# Movies
# Получение фильма по ID
def get_movie(db, movie_id: int):
    movie = db.execute(
        "SELECT * FROM movies WHERE id = ?", 
        (movie_id,)
    ).fetchone()
    if movie is None:
        return None
    return {"id": movie['id'],
            "title": movie['title'],
            "description": movie['description'],
            "duration": movie['duration'],
            "genre": movie['genre'],
            "rating": movie['rating']}

# Регистрация нового фильма
def create_movie(db, movie: schemas.Movie):
    db.execute(
        """INSERT INTO movies (title, description, duration, genre, rating)
        VALUES (?, ?, ?, ?, ?)""",
        (movie.title, movie.description, movie.duration, movie.genre, movie.rating)
    )
    db.commit()
    movie = db.execute("SELECT * FROM movies WHERE id = last_insert_rowid()").fetchall()[0]
    return {"id": movie['id'],
            "title": movie['title'],
            "description": movie['description'],
            "duration": movie['duration'],
            "genre": movie['genre'],
            "rating": movie['rating']}

# Screenings
def create_screening(db, screening):
    db.execute(
        """INSERT INTO screenings (movie_id, hall_id, start_time, price)
        VALUES (?, ?, ?, ?)""",
        (screening.movie_id, screening.hall_id, screening.start_time, screening.price)
    )
    db.commit()
    return db.execute(
        "SELECT * FROM screenings WHERE id = last_insert_rowid()"
    ).fetchone()

# Ratings
# Создание новой оценки
def create_rating(db, user_id: int, rating_data: schemas.MovieRating):
    # Проверяем, существует ли фильм
    movie = db.execute(
        "SELECT id FROM movies WHERE id = ?", 
        (rating_data.movie_id,)
    ).fetchone()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Проверяем, не оценивал ли пользователь уже этот фильм
    existing_rating = db.execute(
        "SELECT id FROM movie_ratings WHERE user_id = ? AND movie_id = ?",
        (user_id, rating_data.movie_id)
    ).fetchone()

    if existing_rating:
        # Обновляем существующую оценку
        db.execute(
            """UPDATE movie_ratings 
            SET rating = ?, review = ? 
            WHERE id = ?""",
            (rating_data.rating, rating_data.review, existing_rating["id"])
        )
    else:
        # Создаем новую оценку
        db.execute(
            """INSERT INTO movie_ratings 
            (user_id, movie_id, rating, review) 
            VALUES (?, ?, ?, ?)""",
            (user_id, rating_data.movie_id, rating_data.rating, rating_data.review)
        )

    db.commit()

    # Возвращаем обновленную запись
    row = db.execute(
        """SELECT * FROM movie_ratings 
        WHERE user_id = ? AND movie_id = ?""",
        (user_id, rating_data.movie_id)
    ).fetchone()
    return {"id": row['id'],
            "user_id": row['user_id'],
            "movie_id": row['movie_id'],
            "rating": row['rating'],
            "review": row['review']}

# Получение оценки фильма пользователем
def get_user_rating_for_movie(db, user_id: int, movie_id: int):
    return db.execute(
        """SELECT * FROM movie_ratings 
        WHERE user_id = ? AND movie_id = ?""",
        (user_id, movie_id)
    ).fetchone()

# Получение всех оценок пользователя
def get_user_ratings(db, user_id: int):
    return db.execute(
        "SELECT * FROM movie_ratings WHERE user_id = ?",
        (user_id,)
    ).fetchall()
