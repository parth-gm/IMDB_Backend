from imp import reload
import uvicorn
import uvicorn.config
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from routes.api import router as api_router

app = FastAPI()

app.include_router(api_router)


@app.get("/")
def index():
    return {"name": "First Data"}


if __name__ == '__main__':
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
    uvicorn.run("main:app", host='0.0.0.0', port=8005,
                log_config=log_config, reload=True)
    print("Exited!")
