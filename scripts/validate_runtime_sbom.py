"""Reject source-tooling-only inventories when an API runtime SBOM is required."""

import argparse
import hashlib
import json
import re
from pathlib import Path


REQUIRED = {"fastapi", "pydantic", "sqlalchemy", "psycopg", "uvicorn"}


def normalize(name):
    return re.sub(r"[-_.]+", "-", name.lower())


def inspect(path):
    raw = path.read_bytes()
    document = json.loads(raw)
    if document.get("spdxVersion") != "SPDX-2.3":
        raise ValueError("Expected SPDX-2.3 JSON")
    packages = document.get("packages")
    if not isinstance(packages, list):
        raise ValueError("Missing package inventory")
    found = {}
    for package in packages:
        name = package.get("name")
        if not isinstance(name, str):
            raise ValueError("Invalid package name")
        if normalize(name) in REQUIRED:
            version = package.get("versionInfo")
            if not isinstance(version, str) or not version.strip():
                raise ValueError("Required runtime package has no resolved version")
            found[normalize(name)] = version
    missing = sorted(REQUIRED - found.keys())
    if missing:
        raise ValueError("Missing API runtime dependencies: " + ", ".join(missing))
    return {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "package_count": len(packages),
        "required_runtime_versions": found,
        "scope": "built API image; frontend and completeness not asserted",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect(args.inventory), sort_keys=True))
    except (ValueError, TypeError, AttributeError, OSError) as error:
        parser.exit(1, f"Runtime inventory rejected: {error}\n")
