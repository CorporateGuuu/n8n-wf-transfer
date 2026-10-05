# Role Evidence Matrix

This matrix helps reviewers map repository evidence to common role families. It intentionally separates **verified** evidence from planned work.

| Role family | Current evidence | Evidence status | Strong interview topics |
| --- | --- | --- | --- |
| Senior Software Engineer | modular monolith, API contracts, migrations, auth, RBAC, audit events, Next.js/FastAPI boundary | Implemented + partially verified in CI | architecture trade-offs, contract stability, test strategy |
| Backend Engineer | FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL contract tests, tenant-scoped queries | Implemented + verified areas | transactions, validation, tenancy, error contracts |
| Platform Engineer | CI gates, migrations, health/readiness, API contract drift, container assets | Implemented + verified areas | delivery gates, operability, release safety |
| Cloud Engineer | AWS network slice: VPC, public/private subnets, routing and security-group boundaries; Terraform format/init/validate | Implemented + CI validated; no AWS provisioning | service selection, networking, secrets, managed database design |
| DevOps / DevSecOps | GitHub Actions, reproducible tests/builds, migration verification, Checkov, blocking filesystem/API-image vulnerability gates, Helm/GitOps reference checks | Implemented + CI-tested scopes; scan exclusions and runtime gaps remain | CI quality gates, secure delivery, evidence-based claims |
| Security-minded SWE | RBAC, tenant isolation, rotating sessions, audit events, request IDs | Implemented + verified areas | authn/authz, session security, multi-tenant threat boundaries |
| Full-Stack Engineer | Next.js + TypeScript frontend consuming FastAPI APIs | Implemented + production build verified | typed API boundaries, frontend/backend responsibilities |
| Data / Analytics Engineer | tenant-scoped KPI aggregation and relational model | Implemented + backend tests | aggregation correctness, tenant-safe analytics |
| Federal-contractor Engineer | public-safe identity, audit, access-control and verification patterns | Transferable evidence; not compliance evidence | NIST/Zero Trust mapping, change control, auditability |
| AI / AI Consultant | not a primary strength of this repository | Not targeted | use separate AI case study |

## Current technology evidence

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL 16 CI service
- Next.js / React / TypeScript
- GitHub Actions
- Docker assets
- OpenAPI

## Evidence reconciliation — October 5, 2026

Implementation `a60f49e6dc9839e082958289c861d17917abd610`, [CI 36956614960](https://github.com/CorporateGuuu/n8n-wf-transfer/actions/runs/36956614960), is the evidence baseline. These statements describe the open PR branch, not main-branch integration. Terraform network configuration and vulnerability scans are implemented and CI tested. Downloaded baseline SBOM contains nine source-tooling packages, no Python/Node application runtime coverage; wrapper status remains inconsistent. Built API-image and installed-frontend inventories with dependency/version gates passed at `e612620` / [CI37325054419](https://github.com/CorporateGuuu/n8n-wf-transfer/actions/runs/37325054419). Actual downloaded artifacts contain 124 API-image packages and 58 frontend packages; both required-package/version validators pass. Frontend includes build/dev dependencies; complete inventory coverage is not asserted. [Security evidence map](security-evidence-map.md) gives exact boundaries.

## Planned or not yet independently verified

- Complete application infrastructure beyond the network reference slice
- AWS provisioning
- Redis behavior
- external deployment
- production observability
- Frontend static security scanning and signed deployment provenance. API Bandit/startup-secret guard passed at b522494 / CI37328054597; bounded synthetic local PostgreSQL restore and11in-process restored-auth/tenant checks passed, hosted restore extension pending.
- Full inventory completeness, signed provenance and deployed-artifact verification
- full Playwright execution

Do not convert these planned items into resume claims until corresponding evidence exists.
