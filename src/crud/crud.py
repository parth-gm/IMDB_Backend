from unicodedata import name
from sqlalchemy.orm import Session
from src import auth
from src.auth import auth_handler
from src.models import models
from sqlalchemy.sql import text


from uvicorn.logging import logging
logger = logging.getLogger("uvicorn.info")


async def _genre_check_and_add(db: Session, genre_list, movie_id, current_genre_dict):
    movies_genre = list()

    for genre in genre_list:
        genre = genre.strip(" ")
        if not current_genre_dict.get(genre):
            new_genre = models.Genre(name=genre)
            db.add(new_genre)
            db.commit()
            db.refresh(new_genre)
            current_genre_dict[genre] = new_genre.id
        print(current_genre_dict)
        movies_genre.append(
            {"genre_id": current_genre_dict[genre], "movie_id": movie_id})
    return movies_genre


async def add_movies(db: Session, movies: list):
    result_ls = []
    current_genre_dict = {
        gobj.name: gobj.id for gobj in db.query(models.Genre).all()}
    for movie in movies:
        new_movie = models.Movies(
            name=movie.get("name"),
            imdb_score=movie.get("imdb_score"),
            popularity99=movie.get("popularity99"),
            director=movie.get("director"),
        )
        db.add(new_movie)
        db.commit()
        db.refresh(new_movie)
        movie_id = new_movie.id

        movies_genre = await _genre_check_and_add(db, movie.get("genre", []), movie_id, current_genre_dict)
        db.bulk_insert_mappings(models.MoviesGenre, movies_genre)
        db.commit()
        result_ls.append(movie_id)
    return f'Added movies Ids: {result_ls}'


async def check_exist_movie(db: Session, movie_id: int):
    return db.query(models.Movies).get(movie_id)


async def update_movie(db: Session, movie_id, exist_movie_obj, new_movie_dict):

    # Get existing genre_ids for movie_id
    current_genres_list = db.query(models.MoviesGenre).filter(
        models.MoviesGenre.movie_id == movie_id).all()
    current_genres_ids_set = set(g.genre_id for g in current_genres_list)

    # Get new genre_ids from new movie dict
    new_genres_list = db.query(models.Genre).filter(
        models.Genre.name.in_(new_movie_dict.get("genre", []))).all()
    new_genres_ids_set = set(g.id for g in new_genres_list)

    genre_ids_tobe_add = new_genres_ids_set - current_genres_ids_set

    exist_movie_obj.name = new_movie_dict.get("name")
    exist_movie_obj.imdb_score = new_movie_dict.get("imdb_score")
    exist_movie_obj.popularity99 = new_movie_dict.get("popularity99")

    movies_genre = [{"genre_id": id, "movie_id": movie_id}
                    for id in genre_ids_tobe_add]
    db.bulk_insert_mappings(models.MoviesGenre, movies_genre)

    genre_tobe_delete = current_genres_ids_set - new_genres_ids_set

    await delete_genre_movies(db, movie_id, genre_tobe_delete)

    db.commit()
    return new_movie_dict


async def delete_genre_movies(db: Session, movie_id, genre_ids_ls):
    for mg in db.query(models.MoviesGenre).filter(
        (models.MoviesGenre.genre_id.in_(genre_ids_ls)),
            models.MoviesGenre.movie_id == movie_id).all():
        await delete_object(db, mg)


async def delete_object(db: Session, object):
    db.delete(object)
    db.commit()


async def get_movies(db: Session, filter_obj):
    results = db.query(models.Movies)
    if filter_obj.name_contains:
        results = results.filter(models.Movies.name.ilike(
            "%"+filter_obj.name_contains+"%"))

    if filter_obj.director_name_contains:
        results = results.filter(models.Movies.director.ilike(
            "%"+filter_obj.director_name_contains+"%"))

    if filter_obj.imdb_rat_gt_than_eq:
        results = results.filter(
            models.Movies.imdb_score >= filter_obj.imdb_rat_gt_than_eq)

    if filter_obj.pop_gt_than_eq:
        results = results.filter(
            models.Movies.popularity99 >= filter_obj.pop_gt_than_eq)

    if filter_obj.geners_filter:
        genre_obj_list = db.query(models.Genre).filter(
            models.Genre.name in set(filter_obj.geners_filter)).all()
        results = results.filter(models.Movies.id in set(
            gobj.movie_id for gobj in genre_obj_list))

    if filter_obj.ord_by_rating_desc:
        results = results.order_by(models.Movies.imdb_score)

    return results.all()


async def add_user(db: Session, user):
    new_user = models.Users(
        email=user.email,
        hashed_password=auth_handler.get_password_hash(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def get_user_by_email(db: Session, email):
    return db.query(models.Users).filter(models.Users.email == email).first()
