# FinOps and cloud cost ownership

This repository demonstrates **cost-governance controls**, not observed AWS spend. No AWS account is provisioned by the portfolio, so no dollar-savings or monthly-cost claim is made.

## Implemented controls

Terraform provider default tags require:

- Project
- Environment
- ManagedBy
- Owner
- CostCenter
- DataClassification

CI validates that the allocation/ownership tag contract remains present.

VPC flow-log retention is explicit rather than unlimited/implicit.

## Cost drivers to review before deployment

The planned architecture's main cost drivers would include:

- NAT gateways and cross-AZ/data-transfer patterns
- ALB hours and processed bytes
- ECS/Fargate task CPU/memory
- RDS instance/storage/IO/backups
- Redis/ElastiCache node class
- CloudWatch log ingestion and retention
- KMS requests
- S3 storage/requests
- CloudFront egress/requests

## Environment posture

### Development
Prefer the smallest safe footprint, short-lived workloads where practical, limited log volume, and no HA resources solely for appearance.

### Production
Availability, backup, retention, security, and recovery requirements take precedence over minimizing cost. Any HA delta should be explicit and reviewable.

## FinOps operating loop

1. tag every resource for ownership/allocation
2. define workload SLOs before optimizing cost
3. measure actual utilization/spend
4. identify dominant cost drivers
5. right-size or redesign without violating SLO/security requirements
6. record the trade-off in an ADR
7. verify savings from billing evidence before claiming them

## Not yet claimed

- AWS Cost Explorer evidence
- AWS Budgets alarms
- measured cost per request/workflow
- Reserved Instance/Savings Plan decisions
- production right-sizing results

Those require an actual deployed environment and billing telemetry.
