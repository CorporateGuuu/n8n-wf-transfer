from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / "integrations" / "apigee" / "apiproxy"
POLICIES = ROOT / "policies"
PROXIES = ROOT / "proxies"
TARGETS = ROOT / "targets"

required = [
    ROOT / "ops-intelligence.xml",
    PROXIES / "default.xml",
    TARGETS / "default.xml",
    POLICIES / "Assign-Request-ID.xml",
    POLICIES / "Spike-Arrest.xml",
    POLICIES / "Quota.xml",
    POLICIES / "Verify-JWT.xml",
]

missing = [str(path.relative_to(ROOT.parent)) for path in required if not path.exists()]
if missing:
    raise SystemExit(f"Missing required Apigee files: {missing}")

for path in required:
    try:
        ET.parse(path)
    except ET.ParseError as exc:
        raise SystemExit(f"Invalid XML in {path}: {exc}") from exc

proxy = ET.parse(PROXIES / "default.xml").getroot()
policy_refs = {name.text for name in proxy.findall(".//Step/Name") if name.text}
policy_names = {path.stem for path in POLICIES.glob("*.xml")}
unknown = sorted(policy_refs - policy_names)
if unknown:
    raise SystemExit(f"Proxy references missing policies: {unknown}")

target = ET.parse(TARGETS / "default.xml").getroot()
url = target.findtext(".//HTTPTargetConnection/URL")
if not url or "example.invalid" not in url:
    raise SystemExit("Reference target must remain a non-production example.invalid placeholder.")

jwt = ET.parse(POLICIES / "Verify-JWT.xml").getroot()
jwks = jwt.find(".//JWKS")
if jwks is None or "example.invalid" not in (jwks.attrib.get("uri") or ""):
    raise SystemExit("Reference JWKS URI must remain a non-production example.invalid placeholder.")

print("Apigee reference bundle is structurally valid and public-safe.")
