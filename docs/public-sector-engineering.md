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

Additional DevSecOps controls such as SAST, container scanning, SBOM generation, Terraform validation, and deployment attestation should be treated as future work until implemented and observed.

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
