from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from database import get_db, init_db
import schemas
import crud
import auth
from auth import get_current_user, authenticate_user, create_access_token
from algorithms.recommend import MovieRecommender
from typing import List

# Инициализация базы данных
init_db()

app = FastAPI()

# Эндпоинты аутентификации
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate):
    with get_db() as db:
        db_user = crud.get_user_by_username(db, username=user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        db_user = crud.get_user_by_email(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        return crud.create_user(db=db, user=user)

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with get_db() as db:
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user['username']}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

@app.delete("/users/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(
    user_data: schemas.UserDelete,
    current_user: schemas.User = Depends(get_current_user),
):
    with get_db() as db:
        crud.delete_user(db, current_user['id'], user_data.password)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

# Защищенные эндпоинты
@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return {"username": current_user['username'],
            "email": current_user['email'],
            "id": current_user['id'],
            "is_active": current_user['is_active'],
            "is_admin": current_user['is_admin']}

# Эндпоинты для фильмов
@app.post("/movies/", response_model=schemas.Movie)
def create_movie(
    movie: schemas.MovieCreate, 
    current_user: schemas.User = Depends(get_current_user)
):
    user = {"username": current_user['username'],
            "email": current_user['email'],
            "id": current_user['id'],
            "is_active": current_user['is_active'],
            "is_admin": current_user['is_admin']}
    if not user['is_admin']:
        raise HTTPException(status_code=403, detail="Only admins can add movies")
    with get_db() as db:
        return crud.create_movie(db=db, movie=movie)

@app.get("/movies/{movie_id}", response_model=schemas.Movie)
def read_movie(movie_id: int):
    with get_db() as db:
        db_movie = crud.get_movie(db, movie_id=movie_id)
        if db_movie is None:
            raise HTTPException(status_code=404, detail="Movie not found")
        return db_movie

@app.post("/movies/{movie_id}/rate", response_model=schemas.MovieRating)
def rate_movie(
    movie_id: int,
    rating_data: schemas.MovieRatingBase,
    current_user: schemas.User = Depends(get_current_user)
):
    with get_db() as db:
        # Проверяем, что movie_id в пути совпадает с movie_id в теле запроса
        if movie_id != rating_data.movie_id:
            raise HTTPException(
                status_code=400,
                detail="Movie ID in path does not match Movie ID in body"
            )
        
        return crud.create_rating(db, current_user['id'], rating_data)

# Эндпоинты для рекомендаций
@app.get("/movies/{movie_id}/recommendations", response_model=List[schemas.MovieRecommendation])
def get_movie_recommendations(movie_id: int):
    with get_db() as db:
        db_movie = crud.get_movie(db, movie_id=movie_id)
        if db_movie is None:
            raise HTTPException(status_code=404, detail="Movie not found")
        recommender = MovieRecommender(db)
        recommender.prepare_data()
        return recommender.recommend(movie_id)

@app.get("/users/me/recommendations", response_model=List[schemas.MovieRecommendation])
def get_user_recommendations(current_user: schemas.User = Depends(get_current_user)):
    with get_db() as db:
        recommender = MovieRecommender(db)
        recommender.prepare_data()
        return recommender.recommend_for_user(current_user['id'])
