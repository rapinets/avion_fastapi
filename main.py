from contextlib import asynccontextmanager

from fastapi import FastAPI
# from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from app.api.routers.admin import router as admin_router
from app.api.routers.public import router as public_router
from app.core.config import get_settings
from app.db.database import engine
from app.db.models import Base

from app.api.routers.films import router as films_router

@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.mount(
    "/static",
    StaticFiles(directory= "app/static"),
    name="static",
)

app.include_router(public_router)
app.include_router(admin_router)
app.include_router(films_router)

@app.get("/health", tags=["service"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
