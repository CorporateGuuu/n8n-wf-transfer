"""Bounded synthetic PostgreSQL dump/restore rehearsal, never a production restore."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
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
        from app.db.models import Organization, Product, InventoryItem, AuditEvent
        with Session(source) as session:
            for suffix, qty in [("a", 3), ("b", 777)]:
                org = Organization(name=f"Synthetic Restore {suffix}", slug=f"restore-{suffix}")
                session.add(org); session.flush()
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
