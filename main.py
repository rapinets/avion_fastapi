from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.exception_handlers import request_validation_exception_handler
from app.api.routers.products import router as products_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_exception_handler(
    RequestValidationError,
    request_validation_exception_handler,
)

app.include_router(products_router)


@app.get("/health", tags=["service"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
