# Ops Intelligence

Ops Intelligence is a **synthetic multi-tenant operations analytics platform** designed to demonstrate production-oriented full-stack and cloud engineering: typed web/API boundaries, tenant-safe authorization, transactional operational workflows, analytics, infrastructure as code, automated verification, and observability.

## Evidence state

- **Implemented locally:** FastAPI API foundation, organization-aware login, rotating refresh sessions, Argon2 password hashing, RBAC, tenant-scoped product/inventory APIs, paginated list contracts, request-ID error envelopes, audit events, KPI aggregation, deterministic fixtures, Alembic migrations, OpenAPI artifact/check, a Next.js login/dashboard path wired to the API through HttpOnly cookies, API-backed product/inventory views, audited inventory editing, recent activity, and Playwright journey scaffolding.
- **Verified in this build environment:** 15 backend tests, OpenAPI drift check, Python compilation, and SQLite-backed migration upgrade/downgrade/upgrade flow.
- **Not yet verified here:** PostgreSQL runtime test, Docker Compose, Redis behavior, Next.js dependency install/build/test, AWS/Terraform provisioning, external deployment.

## Business problem

Operational teams often need one place to understand inventory, customers, orders, repairs, transactions and key metrics while enforcing tenant boundaries and role-specific access. This repository models that problem with fictional data only.

## Architecture

See `docs/architecture/system-context.md` and `docs/adr/`.

## Technology stack

Next.js/React/TypeScript, Python/FastAPI/Pydantic, SQLAlchemy/Alembic, PostgreSQL target, Redis target, Docker, Terraform/AWS target.

## Repository structure

- `apps/api` — FastAPI service
- `apps/web` — Next.js UI shell
- `docs` — architecture and ADRs
- `infrastructure/terraform` — reserved for verified IaC implementation
- `docker` — container assets
- `scripts` — deterministic synthetic seed

## Local development

Python API (without Docker):

```bash
export PYTHONPATH=apps/api
export DATABASE_URL=sqlite+pysqlite:///./ops_intelligence.db
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --app-dir apps/api --reload
```

PostgreSQL/Redis target runtime is described in `docker-compose.yml` but has not been executed in this environment.

## Environment configuration

Copy `.env.example` to an untracked `.env`. Never place real secrets in `.env.example`.

## Database & migrations

SQLAlchemy models encode tenant IDs, uniqueness and non-negative quantity/money constraints. Alembic is the migration mechanism. PostgreSQL is the intended system of record; SQLite is used only for local verification in the current tool environment.

## API

Implemented first-slice endpoints:
- `GET /health`, `GET /ready`
- `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`, `GET /api/v1/me`
- `POST/GET /api/v1/products`, `GET/PATCH /api/v1/products/{id}`
- `POST/GET/PATCH /api/v1/inventory`
- `GET /api/v1/analytics/kpis`
- `GET /api/v1/audit-events`

Cross-tenant object access intentionally resolves as `404`.

## Testing

Tests cover organization-aware authentication, refresh rotation/replay prevention, logout revocation, expired refresh rejection, pagination envelopes, validation/conflict error envelopes, request IDs, tenant list/object isolation, analyst write denial, audit linkage, and tenant-scoped KPI aggregation. A PostgreSQL-only schema contract test is wired for CI and skipped locally unless `TEST_POSTGRES_URL` is configured.

## Security

Tenant identity derives from the authenticated user. Role authorization is enforced server-side. Argon2 hashes passwords. Access tokens are short-lived signed credentials; refresh tokens are opaque, rotated on use, stored only as hashes, and revocable. See `SECURITY.md`.

## Deployment

No deployment is claimed. AWS target architecture remains design-only until infrastructure is implemented and observed.

## Observability

Request IDs are normalized for all requests and returned in API error envelopes. Structured logging/metrics/tracing remain planned and must not be described as implemented yet.

## Infrastructure as Code

Terraform directories are reserved but not yet implemented.

## Engineering tradeoffs

A modular monolith is used first to maximize correctness and clarity before introducing service boundaries. Redis remains non-authoritative. Tenant filtering is explicit in every first-slice query.

## Known limitations

The backend now implements rotating refresh sessions and the final page envelope. PostgreSQL/Docker remain unverified here. The Next.js source is wired to the API with product/inventory/activity flows, but dependency installation/build and Playwright execution could not be verified in this environment.

## Roadmap

Run the PostgreSQL CI contract, verify the Next.js build and Playwright journey, add Redis-backed rate limiting only where justified, verify Docker Compose, then proceed to Terraform and observability.

## Interview talking points

- Why tenant scope is derived from authentication rather than client payloads
- Why cross-tenant lookups return 404
- Why audit records share the inventory transaction
- Why PostgreSQL is authoritative and Redis is not
- Why the system starts as a modular monolith
- How claims progress from designed -> implemented -> tested -> deployed only with evidence
