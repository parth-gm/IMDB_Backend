from fastapi import APIRouter
from src.endpoints import movies, users

router = APIRouter()
router.include_router(movies.router)
router.include_router(users.router)
