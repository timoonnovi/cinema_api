from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True

class UserDelete(BaseModel):
    password: str  # Для подтверждения удаления

class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration: int
    genre: str
    rating: float

class Movie(MovieBase):
    id: int

    class Config:
        orm_mode = True

class MovieCreate(MovieBase):
    pass

class ScreeningBase(BaseModel):
    movie_id: int
    hall_id: int
    start_time: datetime
    price: float

class Screening(ScreeningBase):
    id: int

    class Config:
        orm_mode = True

class MovieRatingBase(BaseModel):
    movie_id: int
    rating: float = Field(..., ge=1, le=10)
    review: Optional[str] = None

class MovieRating(MovieRatingBase):
    id: int
    user_id: int
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class MovieRecommendation(BaseModel):
    movie_id: int
    title: str
    genre: str
    similarity_score: float