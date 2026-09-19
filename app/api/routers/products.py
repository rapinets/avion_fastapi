from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.dependencies import get_product_service
from app.models.product import Category, ProductCreate, ProductOut, ProductUpdate
from app.repositories.product_repository import StorageError
from app.services.product_service import (
    DuplicateSkuError,
    ProductNotFoundError,
    ProductService,
)

router = APIRouter(prefix="/products", tags=["products"])

ProductServiceDependency = Annotated[ProductService, Depends(get_product_service)]

CategoryFilter = Annotated[
    Category | None,
    Query(description="Фільтр товарів за категорією"),
]


def raise_storage_error(error: StorageError) -> None:
    raise HTTPException(status_code=500, detail="Помилка локального сховища") from error


@router.get("", response_model=list[ProductOut])
def list_products(
    service: ProductServiceDependency, category: CategoryFilter = None
) -> list[dict[str, Any]] | None:
    try:
        return service.list_products(category.value if category else None)
    except StorageError as error:
        raise_storage_error(error)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: UUID, service: ProductServiceDependency) -> dict[str, Any] | None:
    try:
        return service.get_product(product_id)
    except ProductNotFoundError as error:
        raise HTTPException(status_code=404, detail="Товар не знайдено") from error
    except StorageError as error:
        raise_storage_error(error)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, service: ProductServiceDependency) -> dict[str, Any] | None:
    try:
        return service.create_product(payload)
    except DuplicateSkuError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except StorageError as error:
        raise_storage_error(error)


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: UUID, payload: ProductUpdate, service: ProductServiceDependency
) -> dict[str, Any] | None:
    try:
        return service.update_product(product_id, payload)
    except ProductNotFoundError as error:
        raise HTTPException(status_code=404, detail="Товар не знайдено") from error
    except StorageError as error:
        raise_storage_error(error)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, service: ProductServiceDependency) -> Response:
    try:
        service.delete_product(product_id)
    except ProductNotFoundError as error:
        raise HTTPException(status_code=404, detail="Товар не знайдено") from error
    except StorageError as error:
        raise_storage_error(error)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
