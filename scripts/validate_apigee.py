from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit
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
    POLICIES / "Assign-Fault-Response.xml",
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
target = ET.parse(TARGETS / "default.xml").getroot()
policy_refs = {name.text for endpoint in (proxy, target) for name in endpoint.findall(".//Step/Name") if name.text}
for endpoint in (proxy, target):
    fault = endpoint.find("DefaultFaultRule")
    if fault is None or fault.findtext("Step/Name") != "Assign-Fault-Response" or fault.findtext("AlwaysEnforce") != "true":
        raise SystemExit("Both endpoints must enforce the shared default fault policy.")
policy_names = {path.stem for path in POLICIES.glob("*.xml")}
unknown = sorted(policy_refs - policy_names)
if unknown:
    raise SystemExit(f"Proxy references missing policies: {unknown}")

def placeholder_url(value):
    parsed = urlsplit(value or "")
    host = parsed.hostname or ""
    return parsed.scheme == "https" and (host == "example.invalid" or host.endswith(".example.invalid")) and not parsed.username and not parsed.password

url = target.findtext(".//HTTPTargetConnection/URL")
if not placeholder_url(url):
    raise SystemExit("Reference target must remain a non-production example.invalid placeholder.")

jwt = ET.parse(POLICIES / "Verify-JWT.xml").getroot()
jwks = jwt.find(".//JWKS")
if jwks is None or not placeholder_url(jwks.attrib.get("uri")):
    raise SystemExit("Reference JWKS URI must remain a non-production example.invalid placeholder.")

fault_policy = ET.parse(POLICIES / "Assign-Fault-Response.xml").getroot()
if fault_policy.find(".//StatusCode") is not None:
    raise SystemExit("Fault response must preserve the gateway status code.")

print("Apigee reference bundle is structurally valid and public-safe.")
