from collections.abc import Iterable
from typing import Any
from uuid import UUID, uuid4

from app.models.product import ProductCreate, ProductUpdate
from app.repositories.product_repository import JsonProductRepository


class ProductNotFoundError(LookupError):
    pass


class DuplicateSkuError(ValueError):
    pass


class ProductService:
    def __init__(self, repository: JsonProductRepository) -> None:
        self.repository = repository

    def list_products(self, category: str | None = None) -> list[dict[str, Any]]:
        products = self.repository.load_all()
        if category is not None:
            products = [
                product for product in products if product["category"] == category
            ]
        return sorted(products, key=lambda product: product["id"])

    def get_product(self, product_id: UUID) -> dict[str, Any]:
        for product in self.repository.load_all():
            if product["id"] == str(product_id):
                return product
        raise ProductNotFoundError(product_id)

    def create_product(self, payload: ProductCreate) -> dict[str, Any]:
        products = self.repository.load_all()
        self._ensure_unique_sku(products, payload.sku)
        product = {"id": str(uuid4()), **payload.model_dump(mode="json")}
        products.append(product)
        self.repository.save_all(products)
        return product

    def update_product(
        self, product_id: UUID, payload: ProductUpdate
    ) -> dict[str, Any]:
        products = self.repository.load_all()
        for product in products:
            if product["id"] == str(product_id):
                product.update(payload.model_dump(exclude_unset=True, mode="json"))
                self.repository.save_all(products)
                return product
        raise ProductNotFoundError(product_id)

    def delete_product(self, product_id: UUID) -> None:
        products = self.repository.load_all()
        remaining = [
            product for product in products if product["id"] != str(product_id)
        ]
        if len(remaining) == len(products):
            raise ProductNotFoundError(product_id)
        self.repository.save_all(remaining)

    @staticmethod
    def _ensure_unique_sku(products: Iterable[dict[str, Any]], sku: str) -> None:
        if any(product["sku"] == sku for product in products):
            raise DuplicateSkuError("Товар з таким SKU вже існує")
