# Ops Intelligence

Ops Intelligence is a **synthetic multi-tenant operations platform** built to demonstrate production-oriented backend, full-stack, and cloud engineering. It focuses on the engineering problems that become important once a system moves beyond CRUD: tenant isolation, authorization, durable data boundaries, auditable mutations, stable API contracts, migration safety, and evidence-backed delivery.

## Engineering evidence

**Verified in GitHub Actions:**
- Python 3.12 API install and test execution
- non-PostgreSQL backend test suite
- versioned OpenAPI drift check
- Alembic migration to head
- PostgreSQL 16 service boot + migrated PostgreSQL contract test
- Node 22 dependency install + Next.js production build
- Terraform 1.9.8 format, init, and validate for the AWS network reference slice
- Apigee reference proxy bundle static validation
- Helm lint/render, GitOps reference validation, repository public-safety scan, API container build, and SPDX SBOM generation

**Implemented:**
- FastAPI + Pydantic API foundation
- organization-aware authentication
- opaque rotating refresh sessions stored only as hashes
- server-side RBAC
- tenant-scoped product/inventory access
- stable paginated list contracts
- request-ID error envelopes
- transactional audit events
- tenant-scoped KPI aggregation
- Alembic migrations
- versioned OpenAPI artifact
- Next.js login/dashboard flow through HttpOnly cookies
- API-backed products, inventory, and recent activity
- Playwright journey scaffolding
- Terraform AWS network reference slice: VPC, two public subnets, two private subnets, internet gateway/public routing, and ALB/application/database security-group boundaries

**Not yet claimed as verified:** Docker Compose runtime, Redis behavior, Terraform/AWS provisioning, external deployment, and production observability.

## Business problem

Operational teams need one place to understand inventory, activity, and key metrics without weakening organizational data boundaries. The platform models that problem with fictional data only so architecture, security, and delivery practices can be reviewed publicly without exposing customer or business data.

## Architecture

The current design is a modular monolith with explicit web, API, persistence, and tenant boundaries.

- **Web:** Next.js / React / TypeScript
- **API:** Python / FastAPI / Pydantic
- **Persistence:** SQLAlchemy + Alembic, PostgreSQL as the target system of record
- **Auth:** short-lived access credentials + rotating opaque refresh sessions
- **Delivery:** Docker assets + GitHub Actions
- **Cloud target:** AWS + Terraform (not yet claimed as deployed)

See:
- `docs/architecture/system-context.md`
- `docs/adr/001-modular-monolith.md`
- `docs/adr/002-tenant-boundary.md`
- `docs/adr/003-refresh-session-rotation.md`

## Security model

Tenant identity is derived from the authenticated user rather than accepted from arbitrary resource-write payloads. Authorization is enforced server-side. Cross-tenant object access intentionally resolves as `404` where applicable.

Passwords use Argon2. Refresh tokens are opaque random values, stored only as hashes, rotated on use, and revoked on logout. Browser-facing routes keep credentials in HttpOnly SameSite cookies.

See `SECURITY.md` and `docs/public-sector-engineering.md`.

## API contract

Implemented endpoints include:

- `GET /health`, `GET /ready`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/me`
- `POST/GET /api/v1/products`
- `GET/PATCH /api/v1/products/{id}`
- `POST/GET/PATCH /api/v1/inventory`
- `GET /api/v1/analytics/kpis`
- `GET /api/v1/audit-events`

The checked-in OpenAPI document is treated as a versioned contract and CI fails on drift.

## Testing strategy

The backend tests cover organization-aware authentication, refresh rotation and replay prevention, logout revocation, expired refresh rejection, validation/conflict envelopes, request IDs, pagination, tenant list/object isolation, analyst write denial, audit linkage, and tenant-scoped KPI aggregation.

CI also runs a PostgreSQL-specific contract test against PostgreSQL 16 and performs a production Next.js build.

Playwright journey scaffolding exists for login → products → inventory mutation → audit visibility; execution should not be described as verified until an observed Playwright run is recorded.

## Engineering decisions

### Start with a modular monolith
Service boundaries are kept inside one deployable system until scale, ownership, or reliability requirements justify distributed services. This reduces operational complexity while preserving explicit module and tenant boundaries.

### PostgreSQL is authoritative
Redis is non-authoritative and should only be introduced where a measured performance or coordination need justifies it.

### Tenant scope comes from identity
Clients do not choose their organization by sending an `organization_id` in protected mutations. The authenticated principal determines tenant scope.

### Evidence before claims
Features move from designed → implemented → tested → deployed only when the corresponding evidence exists. README and build-status claims are deliberately narrower than planned architecture.

## Repository structure

- `apps/api` — FastAPI service and backend tests
- `apps/web` — Next.js application
- `docs/architecture` — system views
- `docs/adr` — architecture decision records
- `docs/openapi.json` — versioned API contract
- `docker` — container assets
- `infrastructure/terraform` — implemented and CI-validated AWS network reference slice
- `docs/public-sector-engineering.md` — public-safe federal/contractor engineering discussion guide
- `docs/role-evidence-matrix.md` — role-to-evidence map for recruiter/interview review
- `scripts` — deterministic seed and contract tooling
- `integrations/apigee` — public-safe API management proxy/policy reference bundle
- `deploy/helm/ops-intelligence` — Kubernetes/Helm deployment reference
- `gitops/argocd` — Argo CD GitOps reference manifest

## Local development

```bash
export PYTHONPATH=apps/api
export DATABASE_URL=sqlite+pysqlite:///./ops_intelligence.db
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --app-dir apps/api --reload
```

For the web application, use the package scripts in `apps/web`.

## Current limitations

- Docker Compose has not yet been recorded as successfully executed.
- Redis behavior is not yet verified.
- The Terraform network slice is implemented and CI-validated, but no AWS plan/apply or live provisioning is claimed.
- No external/public production deployment is claimed.
- Structured logs, metrics, and tracing remain planned beyond the current request-ID boundary.

## Interview discussion points

- Why tenant scope is derived from authentication rather than payloads
- Why cross-tenant lookups return `404`
- Why audit records are coupled to operational mutations
- Why refresh credentials rotate and are stored only as hashes
- Why PostgreSQL remains authoritative if Redis is introduced
- Why the system begins as a modular monolith
- How API contract drift is prevented
- How engineering claims are tied to observed evidence

## Platform / GitOps / SRE

The repository now includes a Helm chart, an Argo CD reference Application, deployment health probes, resource limits, non-root/read-only container controls, CI Helm validation, a container build gate, and SBOM generation. These are implemented/validated artifacts; no live Kubernetes/OpenShift/Argo deployment is claimed. See `docs/platform-gitops-sre.md`.

## Enterprise API management

A statically validated Apigee reference bundle lives under `integrations/apigee`. It demonstrates gateway-layer JWT verification, spike arrest, quota, request-ID propagation, target separation, and promotion/governance documentation. No live Apigee deployment is claimed.

## Cross-sector review

For role-specific review, see `docs/role-evidence-matrix.md`. For public-sector/federal-contractor discussion boundaries and control mapping, see `docs/public-sector-engineering.md`. These documents use only synthetic/public-safe architecture and do not claim accreditation, authorization, compliance certification, or clearance status.
