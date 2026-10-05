# Security practices: evidence and open gaps

This is an interview/reference mapping, not a control assessment, authorization package or compliance claim. It uses synthetic repository evidence at implementation `a60f49e6dc9839e082958289c861d17917abd610` and [CI 36956614960](https://github.com/CorporateGuuu/n8n-wf-transfer/actions/runs/36956614960). No cloud deployment was observed. Mapping relevance is the author's inference, not a NIST endorsement or assertion that a control is satisfied.

## Public reference basis

[NIST SP 800-218, SSDF 1.1](https://csrc.nist.gov/pubs/sp/800/218/final) provides software-development practices. The NIST-hosted [SSDF 1.2 initial public draft](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218r1.ipd.pdf) is a draft; this map uses the final 1.1 reference and does not assert equivalence to later revisions.

[SP 800-53 Revision 5](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) provides security/privacy control families. [SP 800-53A Revision 5](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final) provides assessment procedures. Source code and CI alone cannot substitute for organization-specific implementation, scope, inherited controls and assessment evidence.

## Repository-specific discussion map

| Topic / relevant families | Current artifacts and evidence state | Gap and evidence needed next |
|---|---|---|
| Access and identity — AC / IA | `apps/api/app/core/security.py`, `apps/api/app/api/deps.py`, tenant ADR and PostgreSQL contract tests: IMPLEMENTED, CI TESTED for the tested application boundaries. | Organization IdP/federation, account lifecycle, privileged access and system-wide authorization review. No clearance/agency access claim. |
| Audit — AU | Mutation audit records and request IDs in API models/routes; implementation and application tests. | Verify each required event, retention, access restrictions, time synchronization, failure behavior and tamper resistance in the deployed system. Request IDs alone are not distributed tracing. |
| Configuration/change management — CM | Terraform slice, Helm templates, Argo reference Application, PR CI: IMPLEMENTED + CI VALIDATED artifacts. | Live reconciliation, protected promotion approvals, drift detection and rollback rehearsal. No live GitOps ownership claim. |
| Vulnerability reduction/response — SI / RA; SSDF build/review/response topics | `.github/workflows/ci.yml`, `docs/vulnerability-management.md`: blocking filesystem/API-image scans and a remediation example, CI TESTED. Checkov runs with a named exception. | Unfixed vulnerabilities are excluded from the gate; scanner results are time-bound. Pinned API Python Bandit MEDIUM/HIGH gate and non-development signing-key startup guard are implemented and CI TESTED at b522494 / CI37328054597; LOW negative-guard warning retained. Need exception review, triage ownership, patch timelines, frontend static scanning and fresh deployed-image evidence. |
| Supply-chain evidence — SR; SSDF software protection topics | Baseline downloaded SPDX2.3 has nine source-tooling packages, no Python/Node runtime coverage; wrapper status inconsistent. API image build CI TESTED. At implementatione612620 / CI37325054419: built-image and installed-frontend inventory gates CI TESTED, downloaded124API/58frontend packages checked; required resolved versions present. | Establish complete inventory scope, pin provenance and verify signatures/attestations. Five API and three frontend dependencies prevent tooling-only inventories passing; they do not prove complete dependency coverage. |
| Recovery — CP / IR | `docs/runbooks/readiness-failure.md` and synthetic readiness-failure tests: DOCUMENTED and CI TESTED for that bounded failure. | Backup/restore drill, measured RPO/RTO, service-routing recovery, incident ownership and credential rotation. Test-injected DB failure is not a production incident exercise. |
| Infrastructure boundaries — SC / AC | Terraform networking/security groups and IaC checks: IMPLEMENTED + CI VALIDATED. | Actual AWS plans, account policies, managed secrets, database encryption, private egress, runtime connectivity and inherited provider controls. Many application infrastructure services remain unimplemented. |

## Reviewer acceptance questions

1. Which commit, artifact and successful job supports each claim? Keep baseline evidence separate from later code or environments.
2. What is excluded from the scan or test, and who accepts that risk?
3. Can the runtime reproduce identity, isolation, audit and recovery behavior under expected failures?
4. Which organizational procedures and cloud controls are absent from a portfolio repository?

The implementation can support a truthful discussion of these topics. FedRAMP, ATO, FISMA, NIST compliance, DoD accreditation, classified/CUI handling and active clearance remain outside this evidence.

## Inventory evidence delta

Implementation `e612620334df030f942d54e9a75b8a8a8b017d01` / [CI37325054419](https://github.com/CorporateGuuu/n8n-wf-transfer/actions/runs/37325054419): all ten jobs completed/success. Downloaded API inventory SHA256 `35f9f70e136df7074ac187af0e3a3e69e9db7483e6fb0f1a939fbeb858c0e944`; frontend inventory SHA256 `55dbe1e673bf91f11831343f1a6d43dc6455ab95414a82c9a4d0d12b3a33720b`. These are contained-file hashes, not GitHub archive digests. The API inventory includes resolved runtime/OS packages; frontend includes build/dev dependencies. This evidence replaces a source-tooling-only false coverage assumption, without proving signatures, complete component coverage, deployment or zero vulnerabilities.
