# Platform, GitOps, and SRE evidence

## Evidence state

**Implemented**
- Prometheus HTTP request counter + duration histogram
- `/metrics` endpoint excluded from public OpenAPI
- bounded labels using method, route template, and status
- Helm chart for the Ops Intelligence API
- Kubernetes Deployment and Service templates
- liveness/readiness probes
- resource requests/limits
- non-root/read-only-root-filesystem container security context
- Argo CD Application manifest for a dev environment
- CI Helm lint + template validation
- SBOM generation in CI

**Not yet claimed**
- OpenTelemetry exporter/tracing integration
- live Prometheus/Grafana deployment
- live Kubernetes cluster deployment
- live Argo CD sync
- OpenShift execution
- production SLO dashboards
- incident drill against a deployed environment

## Platform rationale

The application remains deployable as a modular monolith. Kubernetes is treated as a packaging/deployment target, not as a reason to split services prematurely.

Helm provides reusable deployment configuration. Argo CD represents the desired GitOps promotion model: Git remains the declared source of deployment state, and environment changes should flow through reviewed commits.

## Reliability objectives

Implemented telemetry supports:
- request volume by method/route/status
- request latency histograms by method/route

Proposed initial service indicators:
- API availability
- p95 request latency
- 5xx error rate
- database dependency health
- authentication failure rate
- inventory mutation failure rate

Proposed initial SLOs are intentionally **not** claimed as production commitments until a live deployment produces telemetry.

## Incident-response discussion

A production-grade implementation should define:
- severity levels
- on-call ownership
- rollback criteria
- communication cadence
- evidence capture
- postmortem template
- action-item ownership

The current repository demonstrates deployment/reliability design but does not claim live incident-response experience from this synthetic project.

## OpenShift portability

The chart avoids platform-specific dependencies so it can be discussed in Kubernetes/OpenShift interviews. OpenShift-specific SCC, Route, Operator, and image-registry behaviors should remain documented as portability considerations until exercised in a real environment.
