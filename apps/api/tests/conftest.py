from __future__ import annotations

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.security import hash_password
from app.db.base import Base
from app.db.models import InventoryItem, Organization, Product, Role, User
from app.main import create_app


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as db:
        roles = {name: Role(name=name) for name in ("admin", "manager", "operator", "analyst")}
        db.add_all(roles.values())
        org_a = Organization(name="Northstar Device Co.", slug="northstar")
        org_b = Organization(name="Harbor Electronics Lab", slug="harbor")
        db.add_all([org_a, org_b])
        db.flush()
        admin = User(organization_id=org_a.id, email="admin@northstar.example", password_hash=hash_password("SyntheticPass123!"), roles=[roles["admin"]])
        analyst = User(organization_id=org_a.id, email="analyst@northstar.example", password_hash=hash_password("SyntheticPass123!"), roles=[roles["analyst"]])
        other = User(organization_id=org_b.id, email="admin@harbor.example", password_hash=hash_password("SyntheticPass123!"), roles=[roles["admin"]])
        db.add_all([admin, analyst, other])
        p_a = Product(organization_id=org_a.id, sku="SKU-A", name="Synthetic Display A", category="display", unit_cost=Decimal("10"), sale_price=Decimal("20"))
        p_b = Product(organization_id=org_b.id, sku="SKU-A", name="Synthetic Display B", category="display", unit_cost=Decimal("100"), sale_price=Decimal("200"))
        db.add_all([p_a, p_b])
        db.flush()
        inv_a = InventoryItem(organization_id=org_a.id, product_id=p_a.id, location="A", condition="new", quantity=3, reorder_point=1)
        inv_b = InventoryItem(organization_id=org_b.id, product_id=p_b.id, location="B", condition="new", quantity=777, reorder_point=1)
        db.add_all([inv_a, inv_b])
        db.commit()
        yield db


@pytest.fixture()
def client(db_session):
    app = create_app()

    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c


def login_tokens(client, email="admin@northstar.example", organization_slug="northstar"):
    r = client.post(
        "/api/v1/auth/login",
        json={"organization_slug": organization_slug, "email": email, "password": "SyntheticPass123!"},
    )
    assert r.status_code == 200, r.text
    return r.json()


def login(client, email="admin@northstar.example", organization_slug="northstar"):
    tokens = login_tokens(client, email=email, organization_slug=organization_slug)
    return {"Authorization": f"Bearer {tokens['access_token']}"}
