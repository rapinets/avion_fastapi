from typing import Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.repositories.product_repository import JsonProductRepository
from app.services.product_service import ProductService

SettingsDependency = Annotated[Settings, Depends(get_settings)]


def get_product_service(settings: SettingsDependency) -> ProductService:
    """Construct the service from validated application settings."""
    return ProductService(JsonProductRepository(settings.data_file))
