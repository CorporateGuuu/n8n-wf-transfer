from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
versions = (ROOT / "infrastructure/terraform/versions.tf").read_text()
variables = (ROOT / "infrastructure/terraform/variables.tf").read_text()
main = (ROOT / "infrastructure/terraform/main.tf").read_text()

required_tags = [
    "Project",
    "Environment",
    "ManagedBy",
    "Owner",
    "CostCenter",
    "DataClassification",
]
missing = [tag for tag in required_tags if tag not in versions]
if missing:
    raise SystemExit(f"Missing required cost-allocation tags: {missing}")

for variable in ["owner_tag", "cost_center", "data_classification"]:
    if f'variable "{variable}"' not in variables:
        raise SystemExit(f"Missing FinOps variable: {variable}")

if "retention_in_days = 365" not in main:
    raise SystemExit("VPC flow-log retention must remain explicit at 365 days for the reference control.")

print("FinOps reference controls are present: allocation tags, ownership labels, classification, and explicit log retention.")
