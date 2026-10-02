# Role Evidence Matrix

This matrix helps reviewers map repository evidence to common role families. It intentionally separates **verified** evidence from planned work.

| Role family | Current evidence | Evidence status | Strong interview topics |
| --- | --- | --- | --- |
| Senior Software Engineer | modular monolith, API contracts, migrations, auth, RBAC, audit events, Next.js/FastAPI boundary | Implemented + partially verified in CI | architecture trade-offs, contract stability, test strategy |
| Backend Engineer | FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL contract tests, tenant-scoped queries | Implemented + verified areas | transactions, validation, tenancy, error contracts |
| Platform Engineer | CI gates, migrations, health/readiness, API contract drift, container assets | Implemented + verified areas | delivery gates, operability, release safety |
| Cloud Engineer | AWS target architecture documented | Designed only | service selection, networking, secrets, managed database design |
| DevOps / DevSecOps | GitHub Actions, reproducible tests/builds, migration verification, security-oriented auth design | Implemented + verified areas | CI quality gates, secure delivery, evidence-based claims |
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

## Planned but not yet verified

- Terraform implementation
- AWS provisioning
- Redis behavior
- external deployment
- production observability
- container vulnerability scanning
- SBOM generation
- full Playwright execution

Do not convert these planned items into resume claims until corresponding evidence exists.
