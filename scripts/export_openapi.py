from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.main import app  # noqa: E402


def render() -> str:
    return json.dumps(app.openapi(), separators=(",", ":"), sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = ROOT / "docs" / "openapi.json"
    content = render()
    if args.check:
        if not target.exists() or target.read_text() != content:
            print("OpenAPI artifact is out of date", file=sys.stderr)
            return 1
        return 0
    target.write_text(content)
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
