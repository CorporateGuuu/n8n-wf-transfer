# Public-Sector / Federal-Contractor Engineering Discussion Guide

This repository is a **public, synthetic reference project**. It is suitable for discussing engineering practices relevant to commercial and federal-contractor environments without exposing classified information, CUI, customer data, proprietary architectures, or former-employer material.

## What this project can demonstrate

### Identity and authorization
- server-side RBAC
- tenant scope derived from authenticated identity
- cross-tenant object isolation
- least-information behavior through `404` responses for out-of-scope resources
- rotating refresh sessions with revocation behavior

### Auditability
- request IDs
- mutation-linked audit events
- explicit actor / organization / action / entity context
- versioned API contract

### Secure software delivery
Current verified evidence includes automated application tests, PostgreSQL-backed contract testing, migration execution, OpenAPI drift detection, and production web builds.

At implementation `a60f49e6dc9839e082958289c861d17917abd610`, [CI run 36956614960](https://github.com/CorporateGuuu/n8n-wf-transfer/actions/runs/36956614960) completed successfully. Terraform format/init/validate, Checkov, Helm lint/render, GitOps reference checks, repository public-safety checks, API container build, and blocking filesystem/container vulnerability scans have CI evidence. Terraform is a network reference slice, not a complete AWS application deployment. Checkov skips `CKV2_AWS_5`; vulnerability gates exclude unfixed findings. Passing those gates does not mean all risks are resolved.

The baseline SBOM artifact was downloaded and parsed: SPDX2.3, nine packages consisting of CI actions and the root project; it contains no Python or Node application dependency inventory. Its wrapper still reports `in_progress` alongside success, but the artifact itself is available. Do not present that source-tooling inventory as runtime coverage. Both new gates were CI TESTED at implementation `e612620334df030f942d54e9a75b8a8a8b017d01` / [CI37325054419](https://github.com/CorporateGuuu/n8n-wf-transfer/actions/runs/37325054419), all ten jobs completed/success. Downloaded API image SPDX contains 124 packages with resolved FastAPI/Pydantic/SQLAlchemy/psycopg/Uvicorn; installed frontend SPDX contains 58 packages with Next15.5.27/React19.3.0/ReactDOM19.3.0. Both content validators pass. The frontend scope includes development/build dependencies, not only production runtime. Package presence checks do not prove complete inventory coverage; signed provenance remains open. A pinned Bandit1.9.4 API Python MEDIUM/HIGH gate is implemented and locally tested; hosted SAST/startup-guard verification passed at implementation b522494 / CI37328054597 (all ten jobs successful). One LOW B105 warning on the negative default-secret guard is retained and documented in SECURITY.md. Frontend static security scanning is now implemented and locally tested (Semgrep CE1.179.0,74digest-pinned rules,13runtime files,zero findings/parse errors,unsafe-input negative probe blocked). Hosted acceptance of the new gate is pending. Signed deployment provenance, actual cloud provisioning and live Kubernetes/Argo/observability remain unproven.

See [the evidence-to-practices map](security-evidence-map.md) for source paths, tested boundaries and the evidence still required.

## Public standards discussion

The project can be used to discuss engineering concepts that align with public security frameworks, but **not to claim certification or compliance**.

Examples:

- **NIST SSDF:** secure design, dependency awareness, build verification, vulnerability response
- **NIST SP 800-53 control families:** AC (Access Control), AU (Audit and Accountability), CM (Configuration Management), IA (Identification and Authentication), SI (System and Information Integrity)
- **Zero Trust:** identity-driven authorization, explicit resource checks, least privilege, auditability
- **OWASP:** authentication/session handling, authorization, input validation, secure defaults

## What is intentionally not claimed

This repository does **not** claim:
- FedRAMP authorization
- ATO
- FISMA compliance
- NIST 800-53 compliance
- DoD IL accreditation
- production deployment in a government environment
- classified/CUI processing
- any specific security-clearance status

Those claims require separate organizational and system evidence.

## Interview discussion prompts

- How would you adapt tenant isolation for an agency or program boundary?
- Where would identity federation enter the design?
- How would you introduce centralized audit retention and immutable log storage?
- What controls would you add before handling CUI?
- How would CI/CD change under a stricter change-management environment?
- What evidence would you require before calling the system production-ready?
- How would you design backup, recovery, incident response, and credential rotation?

## Public-data boundary

All examples and fixtures should remain synthetic. Do not add real customer, agency, contract, claim, device, credential, supplier, or proprietary operational data.
