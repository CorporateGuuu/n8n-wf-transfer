from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
required = [
    ROOT / "deploy/helm/ops-intelligence/Chart.yaml",
    ROOT / "deploy/helm/ops-intelligence/values.yaml",
    ROOT / "deploy/helm/ops-intelligence/templates/deployment.yaml",
    ROOT / "deploy/helm/ops-intelligence/templates/service.yaml",
    ROOT / "gitops/argocd/ops-intelligence-dev.yaml",
]

missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
if missing:
    raise SystemExit(f"Missing platform files: {missing}")

deployment = (ROOT / "deploy/helm/ops-intelligence/templates/deployment.yaml").read_text()
for token in ["readinessProbe", "livenessProbe", "runAsNonRoot", "readOnlyRootFilesystem", "resources:"]:
    if token not in deployment:
        raise SystemExit(f"Deployment template missing required control: {token}")

argocd = (ROOT / "gitops/argocd/ops-intelligence-dev.yaml").read_text()
for token in ["kind: Application", "targetRevision: main", "automated:", "prune: true", "selfHeal: true"]:
    if token not in argocd:
        raise SystemExit(f"Argo CD manifest missing required control: {token}")

print("Platform/GitOps reference files are structurally present and include required controls.")
