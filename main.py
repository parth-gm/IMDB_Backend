from imp import reload
import uvicorn
import uvicorn.config
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from routes.api import router as api_router

app = FastAPI(title="IMDB_Backend", description="Apis for Search/CRUD Operations on Movies")

app.include_router(api_router)


@app.get("/")
def index():
    return {"name": "First Data"}


log_config = uvicorn.config.LOGGING_CONFIG
log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
