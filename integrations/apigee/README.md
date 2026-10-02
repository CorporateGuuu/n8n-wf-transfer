# Apigee API management reference

This directory contains a **public-safe, statically validated Apigee proxy reference** for the Ops Intelligence API.

## Evidence state

**Implemented**
- API proxy descriptor
- proxy endpoint
- target endpoint placeholder
- request-ID propagation
- JWT verification policy example
- spike arrest
- quota

**Validated in CI**
- XML well-formedness
- required proxy/policy files exist
- proxy references resolve to included policies
- target URL remains a non-production placeholder

**Not claimed**
- import into a live Apigee organization
- deployment to an Apigee environment
- runtime policy behavior
- analytics observations
- production API product configuration

## Why this exists

The goal is to demonstrate enterprise API-management architecture without requiring a live or paid Apigee environment and without exposing customer endpoints or credentials.

## Governance model

Recommended lifecycle:

1. OpenAPI contract changes in the application repo.
2. Proxy/policy changes reviewed through pull request.
3. Static validation in CI.
4. Import/deploy to a non-production Apigee environment when authorized.
5. Smoke-test auth, quota, spike-arrest, routing, and fault behavior.
6. Promote the same revision through controlled environments.
7. Record rollback revision and deployment evidence.

## Security boundary

Do not store:
- Apigee service-account credentials
- organization/environment identifiers
- production KVM values
- customer endpoints
- real issuer/JWKS URLs unless intentionally public

Use secret stores/KVMs and environment-specific deployment configuration for live systems.

## Interview discussion

This reference supports discussion of:
- API lifecycle governance
- gateway-vs-application responsibility
- JWT enforcement
- rate limiting vs quota
- API products and consumer onboarding
- version promotion and rollback
- analytics and SLI/SLO ownership
- CI/CD for API proxy bundles
