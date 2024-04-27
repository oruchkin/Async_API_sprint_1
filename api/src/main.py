import logging.config

import uvicorn
from api.v1 import films, genres, health, persons
from core.lifecycle import lifespan
from core.logger import LOGGING
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

load_dotenv()
logging.config.dictConfig(LOGGING)
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Read-only API для онлайн-кинотеатра",
    description="Информация о фильмах, жанрах и людях, участвовавших в создании произведения",
    version="1.0.0",
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    log_config=LOGGING,
    log_level=logging.DEBUG,
)

app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
