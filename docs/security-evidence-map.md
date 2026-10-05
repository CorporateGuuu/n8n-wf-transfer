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
| Vulnerability reduction/response — SI / RA; SSDF build/review/response topics | `.github/workflows/ci.yml`, `docs/vulnerability-management.md`: blocking filesystem/API-image scans and a remediation example, CI TESTED. Checkov runs with a named exception. | Unfixed vulnerabilities are excluded from the gate; scanner results are time-bound. Need exception review, triage ownership, patch timelines, SAST and fresh deployed-image evidence. |
| Supply-chain evidence — SR; SSDF software protection topics | SBOM action IMPLEMENTED; successful steps with inconsistent wrapper state. API image build CI TESTED. | Download/inspect SBOM against actual resolved runtime dependencies; pin provenance and verify signatures/attestations. No complete inventory or signed artifact claim. |
| Recovery — CP / IR | `docs/runbooks/readiness-failure.md` and synthetic readiness-failure tests: DOCUMENTED and CI TESTED for that bounded failure. | Backup/restore drill, measured RPO/RTO, service-routing recovery, incident ownership and credential rotation. Test-injected DB failure is not a production incident exercise. |
| Infrastructure boundaries — SC / AC | Terraform networking/security groups and IaC checks: IMPLEMENTED + CI VALIDATED. | Actual AWS plans, account policies, managed secrets, database encryption, private egress, runtime connectivity and inherited provider controls. Many application infrastructure services remain unimplemented. |

## Reviewer acceptance questions

1. Which commit, artifact and successful job supports each claim? Keep baseline evidence separate from later code or environments.
2. What is excluded from the scan or test, and who accepts that risk?
3. Can the runtime reproduce identity, isolation, audit and recovery behavior under expected failures?
4. Which organizational procedures and cloud controls are absent from a portfolio repository?

The implementation can support a truthful discussion of these topics. FedRAMP, ATO, FISMA, NIST compliance, DoD accreditation, classified/CUI handling and active clearance remain outside this evidence.
