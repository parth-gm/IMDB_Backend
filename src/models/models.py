from email.policy import default
from enum import unique
from operator import index
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime, Enum
from src.db.database import Base
from src.schemas import schemas
from sqlalchemy.orm import backref
import datetime


class Movies(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    popularity99 = Column(Float, index=True)
    imdb_score = Column(Float, index=True)
    director = Column(String)
    name = Column(String, index=True)


class Genre(Base):
    __tablename__ = "genre"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)


class MoviesGenre(Base):
    __tablename__ = "movies_genre"

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"), index=True)
    genre_id = Column(Integer, ForeignKey("genre.id"), index=True, )
    parent_genre = relationship(
        "Genre", backref=backref("children", cascade="all,delete"))
    parent_movies = relationship(
        "Movies", backref=backref("children", cascade="all,delete"))


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    role = Column(Enum(schemas.Roles), default="user")
