# Build status — 2026-10-01

## Verified in hosted GitHub Actions

The cross-sector portfolio PR CI run completed successfully on 2026-10-01/02. Main-branch verification should be checked again after merge.

The hosted pipeline successfully verified:

- Python 3.12 package installation
- backend tests excluding the PostgreSQL-only marker
- OpenAPI drift check
- Alembic migration to head on SQLite CI database
- PostgreSQL 16 service startup
- Alembic migration against PostgreSQL
- PostgreSQL-specific contract test
- Node 22 setup
- web dependency installation
- Next.js production build
- Terraform 1.9.8 format check
- Terraform init with backend disabled
- Terraform validate for the AWS network reference slice

This supersedes the earlier local-only statement that PostgreSQL runtime and the real Next.js build were unverified.

## Implemented

- organization-aware login
- rotating opaque refresh sessions stored only as SHA-256 hashes
- logout revocation and replay prevention
- global request IDs and stable API error envelopes
- paginated product, inventory, and audit contracts
- product/inventory mutation auditing
- deterministic sorting/page validation
- Alembic migrations
- versioned OpenAPI export/check
- Next.js login/dashboard flow through HttpOnly cookies
- API-backed product and inventory views
- role-aware write controls
- shared server-side auth/refresh proxy boundary
- Playwright journey scaffolding
- Terraform AWS network reference slice with VPC, public/private subnets, internet gateway/public route, and ALB/app/database security-group boundaries

## Verified locally in the earlier build environment

- `pytest -q` → **15 passed, 1 PostgreSQL-only test skipped by design**
- `python scripts/export_openapi.py --check` → passed
- `python -m compileall -q apps/api scripts` → passed
- Alembic clean-database `upgrade head -> downgrade base -> upgrade head` → passed on SQLite
- targeted high-risk secret-pattern scan → no matched private-key/AWS-live-key/Stripe-live-key/Supabase-secret pattern in that verified phase

## Still not verified

- Docker Compose execution
- Redis runtime behavior
- Playwright browser journey execution
- Terraform plan/apply against an AWS account
- live AWS provisioning
- external/public deployment
- production metrics/tracing/alerting

## Evidence rule

Do not describe an item as TESTED or DEPLOYED until the relevant runtime, CI job, or external environment has actually been observed. Planned architecture must remain labeled as planned.
