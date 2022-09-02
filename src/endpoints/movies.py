from fastapi import APIRouter, HTTPException, status, Path, Body, Request
from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session
from src.models import models
from src.crud import crud
from src.db.database import SessionLocal, engine
from fastapi_pagination import paginate, Params
from uvicorn.logging import logging
from src.schemas import schemas
from src.auth import auth_handler
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/movies",
    tags=["Movies"],
    responses={404: {"Error": "Not found"}},
)

logger = logging.getLogger("uvicorn.info")
models.Base.metadata.create_all(bind=engine)

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('/add', dependencies=[Depends(auth_handler.check_admin)])
async def add_movies(
    movies: List[schemas.Movies],
    db: Session = Depends(get_db),
):
    json_compatible_dict = jsonable_encoder(movies)
    print(json_compatible_dict)
    return await crud.add_movies(db, json_compatible_dict)


@router.put("/update/{movie_id}", dependencies=[Depends(auth_handler.check_admin)])
async def update_movie(movie_obj: schemas.Movies,
                       movie_id: int = Path(title="The ID of the movie to get"), db: Session = Depends(get_db)):
    update_movie_dict = jsonable_encoder(movie_obj)
    exist_movie_obj = await crud.check_exist_movie(db, movie_id=movie_id)
    if exist_movie_obj:
        return await crud.update_movie(db, movie_id, exist_movie_obj, update_movie_dict)
    raise HTTPException(
        status_code=404, detail=f"Movie with Id:{movie_id} not found")


@router.delete("/delete/{movie_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(auth_handler.check_admin)])
async def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie_obj = await crud.check_exist_movie(db, movie_id=movie_id)
    if movie_obj:
        return await crud.delete_object(db=db, object=movie_obj)
    raise HTTPException(
        status_code=404, detail=f"todo item with id {id} not found")


@router.get('/searchMovies')
async def search_movies(params: Params = Depends(), filter_obj: schemas.MovieFilter = Depends(), db: Session = Depends(get_db)):
    movies = await crud.get_movies(db, filter_obj)
    return paginate(movies, params)
