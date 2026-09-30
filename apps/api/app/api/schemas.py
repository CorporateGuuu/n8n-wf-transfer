from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int


class LoginRequest(BaseModel):
    organization_slug: str = Field(min_length=1, max_length=120)
    email: str
    password: str = Field(min_length=8)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=32)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    organization_id: str
    email: str
    roles: list[str]


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=160)
    category: str = Field(min_length=1, max_length=80)
    unit_cost: Decimal = Field(ge=0)
    sale_price: Decimal = Field(ge=0)


class ProductPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    unit_cost: Decimal | None = Field(default=None, ge=0)
    sale_price: Decimal | None = Field(default=None, ge=0)
    active: bool | None = None


class ProductResponse(ORMModel):
    id: str
    organization_id: str
    sku: str
    name: str
    category: str
    unit_cost: Decimal
    sale_price: Decimal
    active: bool
    updated_at: datetime


class InventoryCreate(BaseModel):
    product_id: str
    location: str = Field(min_length=1, max_length=120)
    condition: str = Field(min_length=1, max_length=40)
    quantity: int = Field(ge=0)
    reorder_point: int = Field(ge=0)


class InventoryPatch(BaseModel):
    quantity: int | None = Field(default=None, ge=0)
    reorder_point: int | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, min_length=1, max_length=120)


class InventoryResponse(ORMModel):
    id: str
    organization_id: str
    product_id: str
    location: str
    condition: str
    quantity: int
    reorder_point: int
    updated_at: datetime


class KPIResponse(BaseModel):
    inventory_value: Decimal
    revenue: Decimal
    cogs: Decimal
    gross_profit: Decimal
    gross_margin_pct: Decimal | None


class AuditResponse(ORMModel):
    id: str
    organization_id: str
    actor_user_id: str | None
    action: str
    entity_type: str
    entity_id: str
    request_id: str
    created_at: datetime


class ErrorBody(BaseModel):
    code: str
    message: str
    details: object | None = None
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorBody
