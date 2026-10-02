from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import OperationalError

import app.main as main_module
from app.core.security import hash_refresh_token
from app.db.models import AuditEvent, InventoryItem, RefreshSession
from conftest import login, login_tokens


def test_health(client):
    response = client.get("/health")
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]


def test_readiness_returns_503_when_database_is_unavailable(client, monkeypatch):
    def unavailable_session():
        raise OperationalError("SELECT 1", {}, Exception("synthetic database outage"))

    monkeypatch.setattr(main_module, "SessionLocal", unavailable_session)
    response = client.get("/ready")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "SERVICE_UNAVAILABLE"
    assert response.json()["error"]["message"] == "Database dependency unavailable"
    assert response.json()["error"]["request_id"] == response.headers["X-Request-ID"]


def test_metrics_exposes_bounded_http_series(client):
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "ops_http_requests_total" in response.text
    assert 'route="/health"' in response.text
    assert "ops_http_request_duration_seconds" in response.text


def test_login_and_me(client):
    headers = login(client)
    r = client.get("/api/v1/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["roles"] == ["admin"]


def test_login_is_organization_aware(client):
    r = client.post(
        "/api/v1/auth/login",
        json={"organization_slug": "harbor", "email": "admin@northstar.example", "password": "SyntheticPass123!"},
    )
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "UNAUTHORIZED"


def test_refresh_rotates_and_old_token_cannot_replay(client):
    tokens = login_tokens(client)
    rotated = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert rotated.status_code == 200
    rotated_tokens = rotated.json()
    assert rotated_tokens["refresh_token"] != tokens["refresh_token"]
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401
    me = client.get("/api/v1/me", headers={"Authorization": f"Bearer {rotated_tokens['access_token']}"})
    assert me.status_code == 200


def test_logout_revokes_refresh_session(client):
    tokens = login_tokens(client)
    assert client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]}).status_code == 204
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401


def test_expired_refresh_session_is_rejected(client, db_session):
    tokens = login_tokens(client)
    session = db_session.scalar(select(RefreshSession).where(RefreshSession.token_hash == hash_refresh_token(tokens["refresh_token"])))
    session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401


def test_tenant_list_isolation_and_page_envelope(client):
    headers = login(client)
    body = client.get("/api/v1/inventory?page=1&page_size=10", headers=headers).json()
    assert body["total"] == 1
    assert body["page"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 3


def test_product_pagination(client):
    headers = login(client)
    create = client.post(
        "/api/v1/products",
        headers=headers,
        json={"sku": "SKU-B", "name": "Synthetic Display B2", "category": "display", "unit_cost": "12.00", "sale_price": "25.00"},
    )
    assert create.status_code == 201
    first = client.get("/api/v1/products?page=1&page_size=1&sort=sku&order=asc", headers=headers).json()
    second = client.get("/api/v1/products?page=2&page_size=1&sort=sku&order=asc", headers=headers).json()
    assert first["total"] == 2
    assert len(first["items"]) == 1
    assert len(second["items"]) == 1
    assert first["items"][0]["sku"] != second["items"][0]["sku"]


def test_cross_tenant_object_returns_404(client, db_session):
    other = db_session.scalar(select(InventoryItem).where(InventoryItem.quantity == 777))
    r = client.get(f"/api/v1/inventory/{other.id}", headers=login(client))
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_FOUND"


def test_inventory_mutation_is_audited_with_normalized_request_id(client, db_session):
    headers = login(client)
    item = db_session.scalar(select(InventoryItem).where(InventoryItem.quantity == 3))
    request_id = "11111111-1111-1111-1111-111111111111"
    r = client.patch(f"/api/v1/inventory/{item.id}", headers={**headers, "X-Request-ID": request_id}, json={"quantity": 5})
    assert r.status_code == 200
    assert r.json()["quantity"] == 5
    assert r.headers["X-Request-ID"] == request_id
    events = list(db_session.scalars(select(AuditEvent).where(AuditEvent.entity_id == item.id)))
    assert len(events) == 1
    assert events[0].request_id == request_id


def test_invalid_request_id_is_replaced(client):
    r = client.get("/api/v1/me", headers={**login(client), "X-Request-ID": "not-a-uuid"})
    assert r.status_code == 200
    assert r.headers["X-Request-ID"] != "not-a-uuid"
    assert len(r.headers["X-Request-ID"]) == 36


def test_analyst_cannot_write(client):
    headers = login(client, "analyst@northstar.example")
    inventory = client.get("/api/v1/inventory", headers=headers).json()["items"][0]
    r = client.patch(f"/api/v1/inventory/{inventory['id']}", headers=headers, json={"quantity": 99})
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "FORBIDDEN"


def test_validation_error_uses_error_envelope(client):
    headers = login(client)
    r = client.get("/api/v1/inventory?page_size=101", headers=headers)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"
    assert r.json()["error"]["request_id"] == r.headers["X-Request-ID"]


def test_duplicate_sku_is_conflict_envelope(client):
    headers = login(client)
    r = client.post(
        "/api/v1/products",
        headers=headers,
        json={"sku": "SKU-A", "name": "Duplicate", "category": "display", "unit_cost": "1.00", "sale_price": "2.00"},
    )
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "CONFLICT"


def test_kpi_excludes_other_tenant(client):
    r = client.get("/api/v1/analytics/kpis", headers=login(client))
    assert r.status_code == 200
    assert Decimal(r.json()["inventory_value"]) == Decimal("30.00")
