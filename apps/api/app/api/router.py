from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import current_user, get_db, get_request_id, require_roles
from app.api.schemas import (
    AuditResponse,
    InventoryCreate,
    InventoryPatch,
    InventoryResponse,
    KPIResponse,
    LoginRequest,
    LogoutRequest,
    Page,
    ProductCreate,
    ProductPatch,
    ProductResponse,
    RefreshRequest,
    TokenResponse,
    UserResponse,
)
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_credential,
    hash_refresh_token,
    verify_password,
)
from app.db.models import AuditEvent, InventoryItem, Order, Organization, Product, RefreshSession, User

router = APIRouter(prefix="/api/v1")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def _issue_token_pair(db: Session, user: User) -> TokenResponse:
    credential = create_refresh_credential()
    db.add(
        RefreshSession(
            user_id=user.id,
            token_hash=credential.token_hash,
            expires_at=_utcnow() + timedelta(seconds=settings.refresh_token_ttl_seconds),
        )
    )
    db.flush()
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=credential.raw,
        expires_in=settings.access_token_ttl_seconds,
    )


def _audit(
    db: Session,
    *,
    user: User,
    request_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    metadata: dict,
) -> None:
    db.add(
        AuditEvent(
            organization_id=user.organization_id,
            actor_user_id=user.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            request_id=request_id,
            metadata_json=json.dumps(metadata, default=str),
        )
    )


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(
        select(User)
        .join(Organization, Organization.id == User.organization_id)
        .where(
            Organization.slug == payload.organization_slug,
            User.email == payload.email,
            User.status == "active",
        )
    )
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    result = _issue_token_pair(db, user)
    db.commit()
    return result


@router.post("/auth/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token_hash = hash_refresh_token(payload.refresh_token)
    session = db.scalar(
        select(RefreshSession)
        .where(RefreshSession.token_hash == token_hash)
        .with_for_update()
    )
    now = _utcnow()
    if (
        not session
        or session.revoked_at is not None
        or _as_utc(session.expires_at) <= now
        or session.user.status != "active"
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    session.revoked_at = now
    result = _issue_token_pair(db, session.user)
    db.commit()
    return result


@router.post("/auth/logout", status_code=204)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)) -> Response:
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_hash == hash_refresh_token(payload.refresh_token)))
    if session and session.revoked_at is None:
        session.revoked_at = _utcnow()
        db.commit()
    return Response(status_code=204)


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)) -> UserResponse:
    return UserResponse(id=user.id, organization_id=user.organization_id, email=user.email, roles=[r.name for r in user.roles])


@router.post("/products", response_model=ProductResponse, status_code=201)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "manager")),
    request_id: str = Depends(get_request_id),
):
    product = Product(organization_id=user.organization_id, **payload.model_dump())
    db.add(product)
    try:
        db.flush()
        _audit(
            db,
            user=user,
            request_id=request_id,
            action="product.created",
            entity_type="product",
            entity_id=product.id,
            metadata={"sku": product.sku},
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="SKU already exists")
    db.refresh(product)
    return product


@router.get("/products", response_model=Page[ProductResponse])
def list_products(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort: Literal["sku", "name", "updated_at"] = "sku",
    order: Literal["asc", "desc"] = "asc",
):
    columns = {"sku": Product.sku, "name": Product.name, "updated_at": Product.updated_at}
    order_by = desc(columns[sort]) if order == "desc" else asc(columns[sort])
    base = select(Product).where(Product.organization_id == user.organization_id)
    items = list(db.scalars(base.order_by(order_by).offset((page - 1) * page_size).limit(page_size)))
    total = db.scalar(select(func.count()).select_from(Product).where(Product.organization_id == user.organization_id)) or 0
    return Page(items=items, page=page, page_size=page_size, total=total)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    product = db.scalar(select(Product).where(Product.id == product_id, Product.organization_id == user.organization_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/products/{product_id}", response_model=ProductResponse)
def patch_product(
    product_id: str,
    payload: ProductPatch,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "manager")),
    request_id: str = Depends(get_request_id),
):
    product = db.scalar(select(Product).where(Product.id == product_id, Product.organization_id == user.organization_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    changes = payload.model_dump(exclude_unset=True)
    before = {key: getattr(product, key) for key in changes}
    for key, value in changes.items():
        setattr(product, key, value)
    _audit(
        db,
        user=user,
        request_id=request_id,
        action="product.updated",
        entity_type="product",
        entity_id=product.id,
        metadata={"before": before, "after": changes},
    )
    db.commit()
    db.refresh(product)
    return product


@router.post("/inventory", response_model=InventoryResponse, status_code=201)
def create_inventory(
    payload: InventoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "manager", "operator")),
    request_id: str = Depends(get_request_id),
):
    product = db.scalar(select(Product).where(Product.id == payload.product_id, Product.organization_id == user.organization_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    item = InventoryItem(organization_id=user.organization_id, **payload.model_dump())
    db.add(item)
    db.flush()
    _audit(
        db,
        user=user,
        request_id=request_id,
        action="inventory.created",
        entity_type="inventory_item",
        entity_id=item.id,
        metadata={"quantity": item.quantity},
    )
    db.commit()
    db.refresh(item)
    return item


@router.get("/inventory", response_model=Page[InventoryResponse])
def list_inventory(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort: Literal["updated_at", "quantity", "location"] = "updated_at",
    order: Literal["asc", "desc"] = "desc",
):
    columns = {"updated_at": InventoryItem.updated_at, "quantity": InventoryItem.quantity, "location": InventoryItem.location}
    order_by = desc(columns[sort]) if order == "desc" else asc(columns[sort])
    base = select(InventoryItem).where(InventoryItem.organization_id == user.organization_id)
    items = list(db.scalars(base.order_by(order_by).offset((page - 1) * page_size).limit(page_size)))
    total = db.scalar(select(func.count()).select_from(InventoryItem).where(InventoryItem.organization_id == user.organization_id)) or 0
    return Page(items=items, page=page, page_size=page_size, total=total)


@router.get("/inventory/{item_id}", response_model=InventoryResponse)
def get_inventory(item_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.scalar(select(InventoryItem).where(InventoryItem.id == item_id, InventoryItem.organization_id == user.organization_id))
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@router.patch("/inventory/{item_id}", response_model=InventoryResponse)
def patch_inventory(
    item_id: str,
    payload: InventoryPatch,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "manager", "operator")),
    request_id: str = Depends(get_request_id),
):
    item = db.scalar(select(InventoryItem).where(InventoryItem.id == item_id, InventoryItem.organization_id == user.organization_id))
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    changes = payload.model_dump(exclude_unset=True)
    before = {"quantity": item.quantity, "reorder_point": item.reorder_point, "location": item.location}
    for key, value in changes.items():
        setattr(item, key, value)
    _audit(
        db,
        user=user,
        request_id=request_id,
        action="inventory.updated",
        entity_type="inventory_item",
        entity_id=item.id,
        metadata={"before": before, "after": changes},
    )
    db.commit()
    db.refresh(item)
    return item


@router.get("/analytics/kpis", response_model=KPIResponse)
def kpis(db: Session = Depends(get_db), user: User = Depends(current_user)):
    inventory_value = db.scalar(
        select(func.coalesce(func.sum(InventoryItem.quantity * Product.unit_cost), 0))
        .join(Product, Product.id == InventoryItem.product_id)
        .where(InventoryItem.organization_id == user.organization_id, Product.organization_id == user.organization_id)
    ) or Decimal("0")
    revenue, cogs = db.execute(
        select(func.coalesce(func.sum(Order.total), 0), func.coalesce(func.sum(Order.cost_total), 0))
        .where(Order.organization_id == user.organization_id, Order.status.in_(["completed", "fulfilled"]))
    ).one()
    revenue = Decimal(str(revenue or 0))
    cogs = Decimal(str(cogs or 0))
    gp = revenue - cogs
    margin = None if revenue == 0 else (gp / revenue * Decimal("100")).quantize(Decimal("0.01"))
    return KPIResponse(inventory_value=Decimal(str(inventory_value)), revenue=revenue, cogs=cogs, gross_profit=gp, gross_margin_pct=margin)


@router.get("/audit-events", response_model=Page[AuditResponse])
def audit_events(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles("admin", "manager", "analyst")),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    base = select(AuditEvent).where(AuditEvent.organization_id == user.organization_id)
    items = list(db.scalars(base.order_by(AuditEvent.created_at.desc()).offset((page - 1) * page_size).limit(page_size)))
    total = db.scalar(select(func.count()).select_from(AuditEvent).where(AuditEvent.organization_id == user.organization_id)) or 0
    return Page(items=items, page=page, page_size=page_size, total=total)
