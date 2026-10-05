"""Run the browser suite against disposable synthetic data and owned local servers."""
from __future__ import annotations

import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


def main() -> int:
    report_dir = Path(os.environ.get("E2E_REPORT_DIR", ROOT / ".e2e-results"))
    report_dir.mkdir(parents=True, exist_ok=True)
    api_port, web_port = free_port(), free_port()
    while web_port == api_port:
        web_port = free_port()
    processes: list[subprocess.Popen] = []
    summary: dict = {"scope": "local synthetic SQLite browser integration", "productionProof": False}
    with tempfile.TemporaryDirectory(prefix="ops-browser-test-") as temporary:
        env = os.environ.copy()
        env.update(
            APP_ENV="test",
            DATABASE_URL=f"sqlite+pysqlite:///{temporary}/fixture.db",
            PYTHONPATH=str(ROOT / "apps/api"),
            OPS_API_BASE_URL=f"http://127.0.0.1:{api_port}",
            PLAYWRIGHT_BASE_URL=f"http://127.0.0.1:{web_port}",
        )
        try:
            subprocess.run(
                [sys.executable, "-c", "from app.db.base import Base; from app.db.session import engine; "
                 "import app.db.models; Base.metadata.create_all(engine); from scripts.seed import seed; seed()"],
                cwd=ROOT, env=env, check=True,
            )
            commands = [
                ([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(api_port)], ROOT),
                (["npm", "run", "start", "--", "--hostname", "127.0.0.1", "--port", str(web_port)], ROOT / "apps/web"),
            ]
            for index, (command, cwd) in enumerate(commands):
                with open(Path(temporary) / f"server-{index}.log", "w") as log:
                    processes.append(subprocess.Popen(command, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True))
            for url in [f"http://127.0.0.1:{api_port}/health", f"http://127.0.0.1:{web_port}/login"]:
                for _ in range(100):
                    if any(process.poll() is not None for process in processes):
                        raise RuntimeError("Owned test server exited during startup")
                    try:
                        with urlopen(url, timeout=2):
                            break
                    except OSError:
                        time.sleep(0.2)
                else:
                    raise RuntimeError("Local browser-test readiness timeout")
            with open(report_dir / "playwright.json", "w") as report:
                result = subprocess.run(
                    ["npx", "playwright", "test", "--workers=1", "--reporter=json"],
                    cwd=ROOT / "apps/web", env=env, stdout=report, timeout=180,
                )
            summary["exitCode"] = result.returncode
            summary["browserStats"] = json.loads((report_dir / "playwright.json").read_text())["stats"]
            stats = summary["browserStats"]
            summary["browserPass"] = stats["expected"] >= 3 and all(
                stats[key] == 0 for key in ("skipped", "unexpected", "flaky")
            )
            check = subprocess.run(
                [sys.executable, "-c", "import json; from sqlalchemy import select; "
                 "from app.db.session import SessionLocal; from app.db.models import InventoryItem, Organization, AuditEvent; "
                 "db=SessionLocal(); print(json.dumps({'quantities':dict(db.execute(select(Organization.slug,InventoryItem.quantity)"
                 ".join(InventoryItem,InventoryItem.organization_id==Organization.id)).all()),"
                 "'auditCount':len(db.scalars(select(AuditEvent)).all())}))"],
                cwd=ROOT, env=env, check=True, capture_output=True, text=True,
            )
            summary["database"] = json.loads(check.stdout)
            summary["databasePass"] = summary["database"] == {
                "quantities": {"northstar": 19, "harbor": 999}, "auditCount": 1,
            }
        finally:
            for process in processes:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            for process in processes:
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            summary["ownedServersStopped"] = all(process.poll() is not None for process in processes)
    summary["temporaryFixtureRemoved"] = True
    (report_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    return 0 if summary.get("exitCode") == 0 and summary.get("browserPass") and summary.get("databasePass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
