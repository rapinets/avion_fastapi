from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Depends, Query
from fastapi.responses import HTMLResponse

from app.dependencies import get_product_service
from app.models.product import Category
from app.repositories.product_repository import StorageError
from app.services.product_service import (ProductNotFoundError, ProductService)
from app.api.templating import templates


router = APIRouter(tags=["pages"])

ProductServiceDependency = Annotated[ProductService, Depends(get_product_service)]

CategoryFilter = Annotated[
    Category | None,
    Query(description="Фільтр товарів за категорією"),
]


@router.get("/", response_class=HTMLResponse, name="home")
def home_page(
    request: Request,
    service: ProductServiceDependency,
) -> HTMLResponse:
    try:
        featured_products = service.list_products()[:3]
    except StorageError as error:
        raise HTTPException(
            status_code=500,
            detail="Не вдалося завантажити товари",
        ) from error

    return templates.TemplateResponse(
        request=request,
        name="pages/home.html",
        context={
            "page_title": "Avion — сучасні меблі для вашого дому",
            "featured_products": featured_products,
        },
    )


@router.get("/contacts", response_class=HTMLResponse, name="contacts")
def contacts_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="pages/contacts.html",
        context={"page_title": "Контакти"},
    )


@router.get("/catalog", response_class=HTMLResponse, name="catalog")
def catalog_page(
    request: Request,
    service: ProductServiceDependency, category: CategoryFilter = None
) -> HTMLResponse:
    try:
        products = service.list_products(category.value if category else None)
    except StorageError as error:
        raise HTTPException(
            status_code=500,
            detail="Не вдалося завантажити товари",
        ) from error

    return templates.TemplateResponse(
        request=request,
        name="products/list.html",
        context={
            "page_title": "Усі продукти",
            "products": products,
            "categories": list(Category),
            "selected_category": category,
        },
    )


@router.get(
    "/catalog/{product_id}",
    response_class=HTMLResponse,
    name="product_detail",
)
def product_detail_page(
    product_id: UUID,
    request: Request,
    service: ProductServiceDependency,
) -> HTMLResponse:
    try:
        product = service.get_product(product_id)
    except ProductNotFoundError as error:
        raise HTTPException(status_code=404, detail="Товар не знайдено") from error
    except StorageError as error:
        raise HTTPException(
            status_code=500,
            detail="Не вдалося завантажити товар",
        ) from error

    return templates.TemplateResponse(
        request=request,
        name="products/detail.html",
        context={
            "page_title": product["name"],
            "product": product,
        },
    )
