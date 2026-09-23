from typing import Any, Annotated
from uuid import UUID

from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from pydantic import ValidationError

from app.dependencies import get_product_service
from app.models.product import Category, ProductCreate, ProductUpdate
from app.repositories.product_repository import StorageError
from app.services.product_service import DuplicateSkuError, ProductNotFoundError, ProductService
from app.api.templating import templates


router = APIRouter(prefix="/admin", tags=["admin"])

ProductServiceDependency = Annotated[ProductService, Depends(get_product_service)]


def parse_tags(value: str) -> list[str]:
    """Convert a comma-separated form value into a list of tags."""
    return [tag.strip() for tag in value.split(",") if tag.strip()]


def validation_messages(error: ValidationError) -> list[str]:
    """Create readable messages for validation errors shown in an HTML form."""
    return [
        f"{item['loc'][-1]}: {item['msg']}"
        for item in error.errors()
    ]


def product_form_response(
    *,
    request: Request,
    title: str,
    action_url: str,
    submit_label: str,
    values: dict[str, Any],
    errors: list[str] | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="admin/products/form.html",
        context={
            "page_title": title,
            "action_url": action_url,
            "submit_label": submit_label,
            "values": values,
            "categories": list(Category),
            "errors": errors or [],
        },
        status_code=status_code,
    )


def get_product_or_404(
    product_id: UUID,
    service: ProductServiceDependency,
) -> dict[str, Any]:
    try:
        return service.get_product(product_id)
    except ProductNotFoundError as error:
        raise HTTPException(status_code=404, detail="Товар не знайдено") from error
    except StorageError as error:
        raise HTTPException(
            status_code=500,
            detail="Не вдалося завантажити товар",
        ) from error


@router.get("", include_in_schema=False)
def admin_home() -> RedirectResponse:
    return RedirectResponse(url="/admin/products", status_code=303)


@router.get(
    "/products",
    response_class=HTMLResponse,
    name="admin_products",
)
def admin_products_page(
    request: Request,
    service: ProductServiceDependency,
) -> HTMLResponse:
    try:
        products = service.list_products()
    except StorageError as error:
        raise HTTPException(
            status_code=500,
            detail="Не вдалося завантажити товари",
        ) from error

    return templates.TemplateResponse(
        request=request,
        name="admin/products/list.html",
        context={
            "page_title": "Керування продуктами",
            "products": products,
        },
    )


@router.get(
    "/products/create",
    response_class=HTMLResponse,
    name="admin_create_product_form",
)
def create_product_form(request: Request) -> HTMLResponse:
    return product_form_response(
        request=request,
        title="Додати продукт",
        action_url=str(request.url_for("admin_create_product")),
        submit_label="Додати продукт",
        values={
            "name": "",
            "sku": "",
            "price": "",
            "category": Category.chairs.value,
            "tags": "",
        },
    )


@router.post("/products/create", name="admin_create_product")
def create_product(
    request: Request,
    service: ProductServiceDependency,
    name: str = Form(),
    sku: str = Form(),
    price: str = Form(),
    category: str = Form(),
    tags: str = Form(default=""),
) -> Response:
    values = {
        "name": name,
        "sku": sku,
        "price": price,
        "category": category,
        "tags": tags,
    }

    try:
        payload = ProductCreate(
            name=name,
            sku=sku,
            price=price,
            category=category,
            tags=parse_tags(tags),
        )
        service.create_product(payload)
    except ValidationError as error:
        return product_form_response(
            request=request,
            title="Додати продукт",
            action_url=str(request.url_for("admin_create_product")),
            submit_label="Додати продукт",
            values=values,
            errors=validation_messages(error),
            status_code=422,
        )
    except DuplicateSkuError as error:
        return product_form_response(
            request=request,
            title="Додати продукт",
            action_url=str(request.url_for("admin_create_product")),
            submit_label="Додати продукт",
            values=values,
            errors=[str(error)],
            status_code=409,
        )
    except StorageError as error:
        raise HTTPException(
            status_code=500,
            detail="Не вдалося зберегти товар",
        ) from error

    return RedirectResponse(
        url=str(request.url_for("admin_products")),
        status_code=303,
    )


@router.get(
    "/products/{product_id}/edit",
    response_class=HTMLResponse,
    name="admin_edit_product_form",
)
def edit_product_form(
    product_id: UUID,
    request: Request,
    service: ProductServiceDependency,
) -> HTMLResponse:
    product = get_product_or_404(product_id, service)
    values = {
        **product,
        "tags": ", ".join(product.get("tags", [])),
    }

    return product_form_response(
        request=request,
        title="Редагувати продукт",
        action_url=str(
            request.url_for("admin_update_product", product_id=product_id)
        ),
        submit_label="Зберегти зміни",
        values=values,
    )


@router.post("/products/{product_id}/edit", name="admin_update_product")
def update_product(
    product_id: UUID,
    request: Request,
    service: ProductServiceDependency,
    name: str = Form(),
    sku: str = Form(),
    price: str = Form(),
    category: str = Form(),
    tags: str = Form(default=""),
) -> Response:
    get_product_or_404(product_id, service)
    values = {
        "id": str(product_id),
        "name": name,
        "sku": sku,
        "price": price,
        "category": category,
        "tags": tags,
    }

    try:
        payload = ProductUpdate(
            name=name,
            sku=sku,
            price=price,
            category=category,
            tags=parse_tags(tags),
        )
        service.update_product(product_id, payload)
    except ValidationError as error:
        return product_form_response(
            request=request,
            title="Редагувати продукт",
            action_url=str(
                request.url_for("admin_update_product", product_id=product_id)
            ),
            submit_label="Зберегти зміни",
            values=values,
            errors=validation_messages(error),
            status_code=422,
        )
    except DuplicateSkuError as error:
        return product_form_response(
            request=request,
            title="Редагувати продукт",
            action_url=str(
                request.url_for("admin_update_product", product_id=product_id)
            ),
            submit_label="Зберегти зміни",
            values=values,
            errors=[str(error)],
            status_code=409,
        )
    except StorageError as error:
        raise HTTPException(
            status_code=500,
            detail="Не вдалося оновити товар",
        ) from error

    return RedirectResponse(
        url=str(request.url_for("admin_products")),
        status_code=303,
    )


@router.post("/products/{product_id}/delete", name="admin_delete_product")
def delete_product(
    product_id: UUID,
    request: Request,
    service: ProductServiceDependency,
) -> RedirectResponse:
    try:
        service.delete_product(product_id)
    except ProductNotFoundError as error:
        raise HTTPException(status_code=404, detail="Товар не знайдено") from error
    except StorageError as error:
        raise HTTPException(
            status_code=500,
            detail="Не вдалося видалити товар",
        ) from error

    return RedirectResponse(
        url=str(request.url_for("admin_products")),
        status_code=303,
    )
