from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

forbidden_names = {
    ".env",
    ".env.production",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
}
for path in ROOT.rglob("*"):
    if ".git" in path.parts or not path.is_file():
        continue
    if path.name in forbidden_names:
        raise SystemExit(f"Forbidden sensitive filename tracked: {path.relative_to(ROOT)}")

patterns = {
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "Stripe live secret": re.compile(r"sk_live_[A-Za-z0-9]{16,}"),
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
}

for path in ROOT.rglob("*"):
    if ".git" in path.parts or not path.is_file():
        continue
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        continue
    for label, pattern in patterns.items():
        if pattern.search(text):
            raise SystemExit(f"Potential {label} detected in {path.relative_to(ROOT)}")

print("Repository public-safety scan passed.")
