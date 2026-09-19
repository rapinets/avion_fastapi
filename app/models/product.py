from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Category(str, Enum):
    chairs = "chairs"
    vases = "vases"
    sofas = "sofas"

class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120, examples=["The Dandy chair"])
    sku: str = Field(pattern=r"^[A-Z0-9-]{4,20}$", examples=["CHAIR-001"])
    price: float = Field(gt=0, le=1_000_000, examples=[99.99])
    category: Category
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Назва не може бути порожньою")
        return normalized

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, values: list[str]) -> list[str]:
        normalized = [tag.strip().lower() for tag in values if tag.strip()]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Теги не повинні повторюватися")
        return normalized


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    price: float | None = Field(default=None, gt=0, le=1_000_000)
    category: Category | None = None
    tags: list[str] | None = Field(default=None, max_length=10)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("Назва не може бути порожньою")
        return normalized

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return None
        normalized = [tag.strip().lower() for tag in values if tag.strip()]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Теги не повинні повторюватися")
        return normalized


class ProductOut(ProductCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
