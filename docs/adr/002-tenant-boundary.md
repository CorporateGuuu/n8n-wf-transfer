# ADR 002: Derive tenant scope from authenticated identity

## Status
Accepted

## Context
A multi-tenant system must prevent one organization from reading or mutating another organization's records. Accepting an organization identifier from arbitrary client payloads would make tenant selection a client-controlled input and increase the risk of insecure direct object references and authorization mistakes.

## Decision
Protected queries and mutations derive `organization_id` from the authenticated principal. Resource lookups include the tenant predicate at the persistence boundary. Cross-tenant object lookups resolve as `404` where appropriate instead of confirming that another tenant's object exists.

## Consequences
- Tenant isolation is enforced server-side rather than through UI behavior.
- Tests must exercise both list-level and object-level isolation.
- Administrative cross-tenant capabilities, if added later, require a separate explicit authorization model rather than bypassing the tenant predicate.
- Every new tenant-scoped query must preserve this invariant.
