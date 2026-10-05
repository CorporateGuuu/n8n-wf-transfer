# Security policy

This repository is a synthetic engineering portfolio project. Do not add real customer, claim, IMEI, supplier, financial, credential, or production operational data.

## Authentication

- Passwords are hashed with Argon2.
- Login is organization-aware; tenant identity is not accepted from arbitrary resource-write payloads.
- Access tokens are short-lived signed credentials.
- Staging/production and other non-development environments refuse the public development signing value or a signing secret shorter than 32 UTF-8 bytes at startup. Development/test modes deliberately retain synthetic fixtures. Length validation does not establish entropy; operators must provide a cryptographically generated, securely managed secret and set `APP_ENV` correctly.
- Refresh tokens are opaque random values, stored only as SHA-256 hashes, rotated on use, and revocable through logout.
- Replaying a rotated or expired refresh token is rejected.
- Browser-facing Next.js routes keep tokens in HttpOnly SameSite cookies; no token is intentionally exposed to client JavaScript.

## Authorization and tenancy

Authorization is enforced by the API, not by hidden UI controls. Tenant-scoped queries derive `organization_id` from the authenticated user. Cross-tenant object access resolves as `404` where applicable.

## Request and error handling

Every request receives a normalized UUID request ID. API errors use a stable envelope and include the request ID without exposing secrets or stack traces.

## Secret handling

Never commit `.env`, production environment files, private keys, cloud credentials, provider secrets, or real tokens. `.env.example` must remain synthetic/placeholders only.

## Static code security gate

CI pins Bandit1.9.4 and scans API runtime Python (`apps/api/app`) for MEDIUM/HIGH findings at every confidence level, ignoring `nosec` suppressions. Frontend JavaScript/TypeScript, dependencies, migrations, test fixtures, scripts and deployment/runtime configuration are outside this scan; other gates cover different scopes. [Bandit documentation](https://bandit.readthedocs.io/en/latest/man/bandit.html) describes the AST rule approach; it is not proof that every vulnerability is absent.

The local all-severity review identified one LOW/MEDIUM-confidence B105 warning on the comparison that rejects the public development signing value. This is a deliberate negative guard, not a production hardcoded credential. LOW findings remain review items; they are not blocked by this MEDIUM/HIGH gate. No global rule skip, baseline exclusion or inline `nosec` was added. Startup tests explicitly verify default/short-key rejection in production and staging.

## Reporting

If a credential is ever found in repository history, treat it as compromised: rotate/cut over the provider credential before history cleanup. Never paste the secret value into an issue, report, chat, or documentation.
