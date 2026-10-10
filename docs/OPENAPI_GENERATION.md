# Reproducible OpenAPI generation

The October 10 retry of run 37370275433 on 20aac7c executed all twelve jobs. Eleven passed; the API job passed 56 tests but failed the checked-in OpenAPI drift gate. The broad dependency ranges installed FastAPI 0.143.0 and Pydantic 2.14.0.

A source-identical local reproduction with those versions found exactly eleven semantic differences, all in generated Decimal schemas: four request string alternatives and seven response string schemas no longer include Pydantic-generated regex patterns. Paths, operations, required fields and response codes did not change. The application still enforces Decimal non-negativity, fourteen total digits/two fractional places, integer storage bounds and non-null patch fields. Existing runtime regression tests cover rejection without mutation and valid boundaries.

Pin the two schema generators in pyproject.toml and regenerate docs/openapi.json from the real app. CI and the API image both install the same project, preserving the drift gate. Other dependencies still use the existing ranges; this is not a complete transitive dependency lock. Dependency/runtime/container scans must continue, and intentional generator upgrades must regenerate and review this contract in the same change.

Run with Python 3.12:

```sh
python -m venv .venv
.venv/bin/pip install -e '.[test]'
APP_ENV=test .venv/bin/python scripts/export_openapi.py
APP_ENV=test .venv/bin/python scripts/export_openapi.py --check
.venv/bin/pytest -m 'not postgres'
```

A JSON Schema string alternative does not fully express all Decimal runtime constraints; do not use it as permission to bypass server validation. This patch changes generated documentation and version selection, not business validation, tenant authorization, migrations or a deployed service. Full new-head CI remains required.
