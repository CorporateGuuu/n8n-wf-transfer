import pytest
from sqlalchemy import func, select
from app.db.models import AuditEvent, InventoryItem, Product
from conftest import login


@pytest.mark.parametrize("resource,field", [("products",field) for field in ("name","category","unit_cost","sale_price","active")]+[("inventory",field) for field in ("quantity","reorder_point","location")])
def test_explicit_null_patch_rejected_before_write_or_audit(client, db_session, resource, field):
    model=Product if resource=="products" else InventoryItem
    item=db_session.scalar(select(model).where(model.organization_id==db_session.scalar(select(InventoryItem).where(InventoryItem.quantity==3)).organization_id))
    original=getattr(item,field)
    audit_before=db_session.scalar(select(func.count()).select_from(AuditEvent))
    response=client.patch(f"/api/v1/{resource}/{item.id}",headers=login(client),json={field:None})
    assert response.status_code==422
    assert response.json()["error"]["code"]=="VALIDATION_ERROR"
    db_session.refresh(item)
    assert getattr(item,field)==original
    assert db_session.scalar(select(func.count()).select_from(AuditEvent))==audit_before


@pytest.mark.parametrize("resource,field,value",[("products","name","Updated Synthetic"),("inventory","quantity",5)])
def test_partial_patch_leaves_omitted_fields_unchanged(client,db_session,resource,field,value):
    model=Product if resource=="products" else InventoryItem
    org=db_session.scalar(select(InventoryItem).where(InventoryItem.quantity==3)).organization_id
    item=db_session.scalar(select(model).where(model.organization_id==org))
    untouched=item.category if resource=="products" else item.location
    response=client.patch(f"/api/v1/{resource}/{item.id}",headers=login(client),json={field:value})
    assert response.status_code==200
    db_session.refresh(item)
    assert getattr(item,field)==value
    assert (item.category if resource=="products" else item.location)==untouched


def test_validation_details_do_not_echo_password_input(client):
    response=client.post("/api/v1/auth/login",json={"organization_slug":"northstar","email":"synthetic@example.invalid","password":"Ab9!x"})
    assert response.status_code==422
    assert '"input"' not in response.text
    assert "Ab9!x" not in response.text


def test_patch_openapi_matches_nonnull_partial_contract(client):
    schemas=client.get("/openapi.json").json()["components"]["schemas"]
    for name in ("ProductPatch","InventoryPatch"):
        schema=schemas[name]
        assert not schema.get("required")
        for prop in schema["properties"].values():
            assert prop.get("type")!="null"
            assert all(option.get("type")!="null" for option in prop.get("anyOf",[]))
            assert prop.get("default","absent") is not None
