from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.db.database import SessionLocal
from app.repositories.product_repository import JsonProductRepository
from app.services.product_service import ProductService

from sqlalchemy.orm import Session

SettingsDependency = Annotated[Settings, Depends(get_settings)]


def get_product_service(settings: SettingsDependency) -> ProductService:
    """Construct the service from validated application settings."""
    return ProductService(JsonProductRepository(settings.data_file))

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]
