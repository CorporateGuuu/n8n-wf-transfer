# Security policy

This repository is a synthetic engineering portfolio project. Do not add real customer, claim, IMEI, supplier, financial, credential, or production operational data.

## Authentication

- Passwords are hashed with Argon2.
- Login is organization-aware; tenant identity is not accepted from arbitrary resource-write payloads.
- Access tokens are short-lived signed credentials.
- Refresh tokens are opaque random values, stored only as SHA-256 hashes, rotated on use, and revocable through logout.
- Replaying a rotated or expired refresh token is rejected.
- Browser-facing Next.js routes keep tokens in HttpOnly SameSite cookies; no token is intentionally exposed to client JavaScript.

## Authorization and tenancy

Authorization is enforced by the API, not by hidden UI controls. Tenant-scoped queries derive `organization_id` from the authenticated user. Cross-tenant object access resolves as `404` where applicable.

## Request and error handling

Every request receives a normalized UUID request ID. API errors use a stable envelope and include the request ID without exposing secrets or stack traces.

## Secret handling

Never commit `.env`, production environment files, private keys, cloud credentials, provider secrets, or real tokens. `.env.example` must remain synthetic/placeholders only.

## Reporting

If a credential is ever found in repository history, treat it as compromised: rotate/cut over the provider credential before history cleanup. Never paste the secret value into an issue, report, chat, or documentation.
