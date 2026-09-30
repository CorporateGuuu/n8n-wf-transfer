from __future__ import annotations

from decimal import Decimal

from sqlalchemy import select

from app.core.security import hash_password
from app.db.models import InventoryItem, Organization, Product, Role, User
from app.db.session import SessionLocal


def seed() -> None:
    with SessionLocal.begin() as db:
        if db.scalar(select(Organization.id).limit(1)):
            return
        roles = {name: Role(name=name) for name in ("admin", "manager", "operator", "analyst")}
        db.add_all(roles.values())
        north = Organization(name="Northstar Device Co.", slug="northstar")
        harbor = Organization(name="Harbor Electronics Lab", slug="harbor")
        db.add_all([north, harbor]); db.flush()
        admin = User(organization_id=north.id, email="admin@northstar.example", password_hash=hash_password("SyntheticPass123!"), roles=[roles["admin"]])
        analyst = User(organization_id=north.id, email="analyst@northstar.example", password_hash=hash_password("SyntheticPass123!"), roles=[roles["analyst"]])
        other = User(organization_id=harbor.id, email="admin@harbor.example", password_hash=hash_password("SyntheticPass123!"), roles=[roles["admin"]])
        db.add_all([admin, analyst, other])
        p1 = Product(organization_id=north.id, sku="DSP-16P-001", name="Nova 16 Pro Display", category="display", unit_cost=Decimal("82.50"), sale_price=Decimal("129.00"))
        p2 = Product(organization_id=harbor.id, sku="DSP-16P-001", name="Harbor 16 Pro Display", category="display", unit_cost=Decimal("75.00"), sale_price=Decimal("119.00"))
        db.add_all([p1, p2]); db.flush()
        db.add_all([
            InventoryItem(organization_id=north.id, product_id=p1.id, location="Warehouse East", condition="refurbished", quantity=18, reorder_point=6),
            InventoryItem(organization_id=harbor.id, product_id=p2.id, location="Warehouse West", condition="refurbished", quantity=999, reorder_point=10),
        ])


if __name__ == "__main__":
    seed()
