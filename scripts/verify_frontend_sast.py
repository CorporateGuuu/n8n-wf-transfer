"""Require frontend source coverage and verify the scanner blocks a harmless probe."""
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / ".e2e-results/registry-rules-private.yml"


def scan(targets: list[str], output: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.pop("SEMGREP_APP_TOKEN", None)
    env.update(SEMGREP_SEND_METRICS="off", SEMGREP_ENABLE_VERSION_CHECK="0")
    return subprocess.run(
        ["semgrep", "scan", "--config", str(RULES), "--metrics", "off",
         "--disable-nosem", "--no-git-ignore", "--error", "--strict", "--json",
         "--output", str(output), *targets], cwd=ROOT, env=env, check=False,
    )


def main() -> None:
    reports = ROOT / ".e2e-results"
    reports.mkdir(exist_ok=True)
    manifest = json.loads((ROOT / "security/semgrep-source.json").read_text())
    assert manifest["source"].startswith("https://semgrep.dev/c/p/"), "Unexpected rule source"
    with urlopen(manifest["source"], timeout=30) as response:
        rules = response.read()
    assert hashlib.sha256(rules).hexdigest() == manifest["sha256"], "Registry rules changed; review before updating the pinned digest"
    RULES.write_bytes(rules)
    RULES.chmod(0o600)
    source = scan(["apps/web/app", "apps/web/lib"], reports / "frontend-sast.json")
    data = json.loads((reports / "frontend-sast.json").read_text())
    assert data["version"] == manifest["scanner"].split("==")[1], "Unexpected scanner version"
    expected = {
        path.resolve() for directory in (ROOT / "apps/web/app", ROOT / "apps/web/lib")
        for path in directory.rglob("*") if path.suffix in {".js", ".jsx", ".ts", ".tsx"}
    }
    scanned = {Path(path).resolve() for path in data["paths"]["scanned"]}
    assert source.returncode == 0 and not data["results"] and not data["errors"], "Frontend security scan failed"
    assert expected and expected <= scanned, "Frontend security scan omitted runtime source files"
    with tempfile.TemporaryDirectory(prefix="ops-static-probe-") as temporary:
        probe = Path(temporary) / "unsafe-probe.ts"
        # Static input only: never imported or executed.
        probe.write_text("function unsafe() { return eval(location.search); } // nosemgrep\n")
        negative = scan([str(probe)], reports / "frontend-sast-negative.json")
        result = json.loads((reports / "frontend-sast-negative.json").read_text())
        assert negative.returncode == 1 and result["results"] and not result["errors"], "Scanner failed to block the negative probe"
    summary = {"sourceFiles": len(expected), "configuredRules": len(re.findall(r"^- id:", RULES.read_text(), re.MULTILINE)), "findings": 0,
               "parseErrors": 0, "negativeProbeBlockedDespiteNosemgrep": True,
               "telemetry": "off", "scope": "digest-pinned registry CE JavaScript/TypeScript rules; file-local analysis"}
    (reports / "frontend-sast-summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
