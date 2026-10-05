"""Bounded synthetic PostgreSQL dump/restore rehearsal, never a production restore."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time
import uuid

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]


def run(args, env):
    result = subprocess.run(args, env=env, cwd=ROOT, capture_output=True, text=True)
    if result.returncode:
        # Do not expose connection strings, credentials or raw database errors.
        raise RuntimeError(f"{Path(args[0]).name} failed (exit {result.returncode})")


def snapshot(engine):
    values = {}
    with engine.connect() as connection:
        for table in sorted(inspect(engine).get_table_names()):
            rows = [dict(row._mapping) for row in connection.execute(text(f'SELECT * FROM "{table}"'))]
            values[table] = sorted(json.dumps(row, sort_keys=True, default=str) for row in rows)
    return values


def main():
    url = make_url(os.environ["TEST_POSTGRES_URL"])
    if url.get_backend_name() != "postgresql" or url.host not in {"localhost", "127.0.0.1"}:
        raise ValueError("Only an explicit loopback PostgreSQL fixture is accepted")
    # Two new uniquely named databases; never drop/overwrite the input database.
    stem = "restore_rehearsal_" + uuid.uuid4().hex
    names = [stem + "_source", stem + "_target"]
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    engines = []
    created = []
    env = dict(os.environ, PGHOST=url.host, PGPORT=str(url.port or 5432),
               PGUSER=url.username or "", PGPASSWORD=url.password or "")
    report = {"scope": "synthetic local PostgreSQL only; not RDS/PITR/RTO/RPO or disaster recovery proof",
              "procurement_or_deployment": False}
    try:
        with admin.connect() as connection:
            for name in names:
                connection.execute(text(f'CREATE DATABASE "{name}"'))
                created.append(name)
        source_url = url.set(database=names[0])
        migration_env = dict(env, DATABASE_URL=source_url.render_as_string(hide_password=False))
        run([str(Path(os.sys.executable).parent / "alembic"), "upgrade", "head"], migration_env)
        source = create_engine(source_url)
        target = create_engine(url.set(database=names[1]))
        engines.extend([source, target])
        from sqlalchemy.orm import Session
        from app.db.models import Organization, Product, InventoryItem, AuditEvent, Role, User
        from app.core.security import hash_password
        with Session(source) as session:
            role = Role(name="admin")
            session.add(role); session.flush()
            for suffix, qty in [("a", 3), ("b", 777)]:
                org = Organization(name=f"Synthetic Restore {suffix}", slug=f"restore-{suffix}")
                session.add(org); session.flush()
                session.add(User(organization_id=org.id, email=f"admin-{suffix}@restore.example", password_hash=hash_password("SyntheticRestoreOnly123!"), roles=[role]))
                product = Product(organization_id=org.id, sku="SAME-SKU", name=f"Fixture {suffix}", category="test", unit_cost=10, sale_price=20)
                session.add(product); session.flush()
                session.add(InventoryItem(organization_id=org.id, product_id=product.id, location=suffix, condition="new", quantity=qty))
                session.add(AuditEvent(organization_id=org.id, action="synthetic.restore.fixture", entity_type="product", entity_id=product.id, request_id=str(uuid.uuid4())))
            session.commit()
        before = snapshot(source)
        with tempfile.TemporaryDirectory(prefix="synthetic_restore_") as directory:
            dump = Path(directory) / "fixture.dump"
            start = time.monotonic()
            run(["pg_dump", "--format=custom", "--no-owner", "--no-acl", "--dbname", names[0], "--file", str(dump)], env)
            dump.chmod(0o600)
            backup_sha = hashlib.sha256(dump.read_bytes()).hexdigest()
            # Prove the restored target contains the saved point, not later source state.
            with source.begin() as connection:
                connection.execute(text("UPDATE inventory_items SET quantity=quantity+10"))
            assert snapshot(source) != before, "mutation control failed"
            run(["pg_restore", "--exit-on-error", "--single-transaction", "--no-owner", "--no-acl", "--dbname", names[1], str(dump)], env)
            restored = snapshot(target)
            assert restored == before, "restored rows differ from backed-up rows"
            assert snapshot(source) != restored, "target incorrectly matches post-backup changes"
            from sqlalchemy.exc import IntegrityError
            try:
                with target.begin() as connection:
                    connection.execute(text("UPDATE inventory_items SET quantity=-1"))
            except IntegrityError:
                constraint = True
            else:
                raise AssertionError("restored nonnegative quantity constraint missing")
            from fastapi.testclient import TestClient
            from sqlalchemy.orm import sessionmaker
            from app.api.deps import get_db
            import app.main as main_module
            restored_session = sessionmaker(bind=target)
            def get_restored_db():
                with restored_session() as session:
                    yield session
            original_session = main_module.SessionLocal
            main_module.SessionLocal = restored_session
            app = main_module.create_app()
            app.dependency_overrides[get_db] = get_restored_db
            checks = []
            try:
                with TestClient(app) as client:
                    assert client.get("/health").status_code == 200
                    checks.append("liveness")
                    assert client.get("/ready").status_code == 200
                    checks.append("restored_database_readiness")
                    assert client.get("/api/v1/inventory").status_code == 401
                    checks.append("unauthenticated_inventory_rejected")
                    identities = {}
                    for suffix, qty in [("a", 3), ("b", 777)]:
                        response = client.post("/api/v1/auth/login", json={"organization_slug":f"restore-{suffix}", "email":f"admin-{suffix}@restore.example", "password":"SyntheticRestoreOnly123!"})
                        assert response.status_code == 200
                        response_token = response.json()["refresh_token"]
                        headers = {"Authorization":"Bearer " + response.json()["access_token"]}
                        checks.append(f"restored_identity_{suffix}_login")
                        response = client.get("/api/v1/inventory", headers=headers)
                        assert response.status_code == 200
                        body = response.json()
                        assert body["total"] == 1 and len(body["items"]) == 1 and body["items"][0]["quantity"] == qty
                        identities[suffix] = (headers, body["items"][0]["id"], response_token)
                        checks.append(f"tenant_{suffix}_inventory_isolation")
                        response = client.get("/api/v1/products", headers=headers)
                        assert response.status_code == 200 and response.json()["total"] == 1 and response.json()["items"][0]["name"] == f"Fixture {suffix}"
                        checks.append(f"tenant_{suffix}_same_sku_product_isolation")
                    assert client.get("/api/v1/inventory/" + identities["b"][1], headers=identities["a"][0]).status_code == 404
                    checks.append("cross_tenant_object_hidden")
                    response = client.post("/api/v1/auth/login", json={"organization_slug":"restore-b", "email":"admin-a@restore.example", "password":"SyntheticRestoreOnly123!"})
                    assert response.status_code == 401
                    checks.append("wrong_organization_login_rejected")
                    original_refresh = identities["a"][2]
                    barrier = threading.Barrier(2)
                    def simultaneous_refresh():
                        with TestClient(app) as parallel_client:
                            barrier.wait(timeout=10)
                            response = parallel_client.post("/api/v1/auth/refresh", json={"refresh_token":original_refresh})
                            return response.status_code, response.json()
                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                        futures = [pool.submit(simultaneous_refresh) for _ in range(2)]
                        outcomes = [future.result(timeout=30) for future in futures]
                    assert sorted(status for status, _ in outcomes) == [200, 401]
                    checks.append("concurrent_refresh_single_winner")
                    assert client.post("/api/v1/auth/refresh", json={"refresh_token":original_refresh}).status_code == 401
                    checks.append("consumed_refresh_replay_rejected")
                    rotated_refresh = next(body["refresh_token"] for status,body in outcomes if status == 200)
                    assert client.post("/api/v1/auth/logout", json={"refresh_token":rotated_refresh}).status_code == 204
                    checks.append("rotated_session_logout")
                    assert client.post("/api/v1/auth/refresh", json={"refresh_token":rotated_refresh}).status_code == 401
                    checks.append("logged_out_refresh_rejected")
            finally:
                main_module.SessionLocal = original_session
            report["restored_api_checks"] = checks
            report["api_test_boundary"] = "in-process FastAPI TestClient with real restored PostgreSQL; not live network/IdP"
            report.update(tables=len(before), rows=sum(map(len, before.values())),
                          snapshot_match=True, source_mutation_excluded=True,
                          restored_nonnegative_constraint_enforced=constraint,
                          backup_sha256=backup_sha, elapsed_seconds=round(time.monotonic()-start, 3),
                          backup_deleted_after_check=True)
    finally:
        for engine in engines:
            engine.dispose()
        with admin.connect() as connection:
            for name in created:
                connection.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
            assert not connection.execute(text("SELECT datname FROM pg_database WHERE datname LIKE :prefix"), {"prefix": stem+"%"}).all()
        admin.dispose()
    report["temporary_databases_removed"] = True
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
