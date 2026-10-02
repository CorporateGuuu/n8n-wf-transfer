# Infrastructure-as-code security gate

## Blocking scan

CI runs Checkov against `infrastructure/terraform`. The scan is blocking.

The initial discovery run reported five failed controls. This branch addresses the two true architecture gaps:

- the default VPC security group is explicitly empty
- VPC flow logging is enabled to an encrypted CloudWatch log group with retention

## Scoped exception: CKV2_AWS_5

`CKV2_AWS_5` requires every security group to be attached to a compute/network resource.

The current Terraform slice intentionally defines ALB, application, and database security-group boundaries **before** the future ALB/ECS/RDS resources are added. Attaching them to dummy resources would make the reference architecture less truthful.

Therefore CI skips only `CKV2_AWS_5` until the next infrastructure slice adds real ALB/ECS/RDS resources. At that point the skip must be removed.

This is a temporary design-stage exception, not a claim that unattached security groups are production-complete.

## Evidence rule

- Checkov passing with the documented single exception = TESTED static IaC security evidence.
- No Terraform plan/apply or live AWS deployment is claimed.
- The exception must not expand without a written architecture rationale.
