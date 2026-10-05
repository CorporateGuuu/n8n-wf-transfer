from decimal import Decimal
import pytest
from pydantic import ValidationError
from app.api.schemas import InventoryCreate, InventoryPatch, ProductCreate, ProductPatch


@pytest.mark.parametrize("model,field,value",[(ProductPatch,"unit_cost","1000000000000"),(ProductPatch,"sale_price","10.001"),(ProductPatch,"unit_cost","1e1000"),(InventoryPatch,"quantity",2147483648),(InventoryPatch,"reorder_point",2147483648)])
def test_storage_overflow_or_unrepresentable_money_is_rejected(model,field,value):
    with pytest.raises(ValidationError):model(**{field:value})


def test_exact_storage_boundary_and_normal_values_remain_accepted():
    assert ProductPatch(unit_cost="999999999999.99").unit_cost==Decimal("999999999999.99")
    assert ProductPatch(sale_price="10.00").sale_price==Decimal("10")
    assert InventoryPatch(quantity=2147483647).quantity==2147483647
    assert InventoryPatch(quantity=0,reorder_point=0).quantity==0


def test_create_and_patch_share_storage_constraints():
    with pytest.raises(ValidationError):ProductCreate(sku="S",name="Synthetic",category="test",unit_cost="10.001",sale_price="20")
    with pytest.raises(ValidationError):InventoryCreate(product_id="synthetic",location="test",condition="new",quantity=2147483648,reorder_point=0)


@pytest.mark.parametrize("resource,field,value",[("products","sale_price","10.001"),("inventory","quantity",2147483648)])
def test_api_storage_validation_returns_422_without_mutation(client,db_session,resource,field,value):
    from sqlalchemy import func,select
    from app.db.models import Product,InventoryItem,AuditEvent
    from conftest import login
    item=db_session.scalar(select(InventoryItem).where(InventoryItem.quantity==3))
    if resource=="products":item=db_session.scalar(select(Product).where(Product.id==item.product_id))
    before=getattr(item,field)
    audit_before=db_session.scalar(select(func.count()).select_from(AuditEvent))
    response=client.patch(f"/api/v1/{resource}/{item.id}",headers=login(client),json={field:value})
    assert response.status_code==422
    assert response.json()["error"]["code"]=="VALIDATION_ERROR"
    db_session.refresh(item)
    assert getattr(item,field)==before
    assert db_session.scalar(select(func.count()).select_from(AuditEvent))==audit_before
