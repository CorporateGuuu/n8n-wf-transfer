# ADR 003: Rotate opaque refresh sessions

## Status
Accepted

## Context
Long-lived bearer tokens increase the blast radius of token theft. A session mechanism should support revocation and replay detection without storing reusable plaintext refresh credentials.

## Decision
Use short-lived signed access credentials plus opaque random refresh tokens. Persist only a hash of each refresh token. Rotate the refresh token when it is used, revoke it on logout, and reject replay of used, expired, or revoked refresh credentials. Browser-facing routes keep tokens in HttpOnly SameSite cookies.

## Consequences
- The database becomes the authoritative source for refresh-session state.
- Rotation creates additional writes but enables revocation and replay prevention.
- Raw refresh tokens must never be logged or persisted.
- Concurrency around refresh requires deterministic handling so the old token cannot be reused after successful rotation.
- Security tests must cover replay, expiry, and logout revocation.
