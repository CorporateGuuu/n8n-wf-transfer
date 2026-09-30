# Build status — 2026-09-30

## Completed locally

- Hardened the first Ops Intelligence vertical slice instead of adding a new parallel implementation.
- Added organization-aware login plus opaque rotating refresh sessions stored only as SHA-256 hashes.
- Added logout revocation and replay prevention for used/expired refresh tokens.
- Added global request IDs and structured API error envelopes.
- Added paginated `{items,page,page_size,total}` contracts for products, inventory and audit events.
- Added product update/audit behavior and deterministic sort/page validation.
- Added a second Alembic migration for refresh sessions.
- Added versioned OpenAPI export plus a drift check script.
- Added PostgreSQL-specific test structure and a PostgreSQL 16 CI service job.
- Added a Next.js login/dashboard flow that calls the FastAPI API through HttpOnly cookies and rotates refresh tokens in the server route.
- Added API-backed product catalog and inventory management pages.
- Added audited inventory quantity mutation through a server-side Next.js proxy.
- Added recent audit activity to the dashboard and role-aware write controls.
- Added shared session-refresh proxy logic so dashboard/products/inventory requests use one auth boundary.
- Added Playwright scaffolding for login -> products -> inventory mutation -> audit visibility.

## Verified in this environment

- `pytest -q` -> **15 passed, 1 PostgreSQL-only test skipped by design**.
- `python scripts/export_openapi.py --check` -> passed.
- `python -m compileall -q apps/api scripts` -> passed.
- Lightweight TypeScript compiler pass over current web source and Playwright source using local declaration stubs -> passed; this is not a Next.js build claim.
- Alembic clean-database `upgrade head -> downgrade base -> upgrade head` -> passed on SQLite verification DB in the previous phase.
- Local high-risk pattern scan -> no private-key/AWS-live-key/Stripe-live-key/Supabase-secret pattern found in the previous verified phase.

## Not verified here

- PostgreSQL runtime test: no PostgreSQL service is available in this execution environment; CI wiring exists but has not run here.
- Docker Compose execution: Docker is unavailable here.
- Redis behavior.
- Next.js dependency install/build/test: `npm install` timed out in this execution environment, so frontend source and Playwright scaffolding are implemented but no real Next.js/Playwright pass is claimed.
- Terraform/AWS plan or deployment.
- External/public deployment.

## Evidence rule

Do not upgrade any unverified item to TESTED/DEPLOYED until the corresponding runtime or command is actually observed.
