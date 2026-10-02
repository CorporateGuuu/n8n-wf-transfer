# Terraform reference slice

This directory contains the first implemented AWS infrastructure slice for Ops Intelligence.

## Implemented

- provider/version constraints
- tagged VPC
- two public subnets
- two private subnets
- internet gateway + public route table
- separate ALB, application, and database security groups
- least-path ingress between ALB -> app -> PostgreSQL

## Deliberately not implemented yet

- NAT gateways / private egress strategy
- ECS/Fargate
- ALB resources/listeners
- RDS
- Redis
- ECR
- S3
- Secrets Manager
- CloudWatch alarms
- Route53 / CloudFront
- remote state backend

These remain future slices and must not be described as implemented or deployed.

## Validation

CI runs:

```bash
terraform fmt -check -recursive
terraform init -backend=false
terraform validate
```

Validation proves Terraform configuration correctness. It does **not** prove an AWS deployment.
