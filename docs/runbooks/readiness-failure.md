# Readiness failure runbook

## Signal

`GET /ready` returns HTTP 503 with error code `SERVICE_UNAVAILABLE` when the API cannot execute its required database readiness query.

`GET /health` remains a process-liveness check and may still return 200 while the database dependency is unavailable.

## Why the distinction matters

- **Liveness** answers: is the process running?
- **Readiness** answers: should this instance receive application traffic?

A database outage should remove an instance from service routing without causing a restart loop solely because the process itself is alive.

## Initial response

1. Confirm `/health` and `/ready` independently.
2. Check database connectivity, credentials/secret references, DNS/network policy, and database service health.
3. Review the request ID and correlated application/platform logs.
4. Avoid restarting healthy application processes repeatedly if the dependency is the actual failure.
5. If a deployment caused the dependency failure, use the documented rollback path.
6. Restore dependency connectivity and verify `/ready` returns 200 before returning traffic.

## Evidence in this repository

Automated tests inject a synthetic database outage and verify:
- `/ready` returns 503
- the stable error envelope reports `SERVICE_UNAVAILABLE`
- the response preserves the request ID

This is deterministic failure-behavior evidence. It is not a claim of a live production incident drill.

## Future live-environment drill

When a disposable environment exists:
1. block database connectivity for one application instance
2. observe readiness failure
3. verify service routing stops sending traffic to that instance
4. restore connectivity
5. verify readiness recovery
6. capture sanitized timing/evidence
7. conduct a short postmortem and update the runbook
