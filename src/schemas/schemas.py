from datetime import datetime
from pydantic import BaseModel, EmailStr
from enum import Enum
from pydantic import BaseModel


class Roles(Enum):
    user = "user"
    admin = "admin"


class Movies(BaseModel):
    name: str
    director: str
    popularity99: float
    imdb_score: float
    genre: list


class MovieFilter(BaseModel):
    name_contains: str = None
    director_name_contains: str = None
    imdb_rat_gt_than_eq: int = 5
    pop_gt_than_eq: int = 0
    geners_filter: list = []
    ord_by_rating_desc: bool = True


class UserLoginSchema(BaseModel):
    email: str
    password: str


class UserSchema(BaseModel):
    email: EmailStr
    password: str
    role: Roles = "user"

    class Config:
        orm_mode = True
