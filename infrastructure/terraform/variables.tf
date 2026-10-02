variable "aws_region" {
  description = "AWS region for the reference architecture."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment label used for naming and tags."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of dev, staging, or prod."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for the application VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "availability_zones" {
  description = "Two availability zones used by the reference network."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]

  validation {
    condition     = length(var.availability_zones) == 2
    error_message = "Exactly two availability zones are required for this reference slice."
  }
}

variable "owner_tag" {
  description = "Non-personal team/service owner tag used for cost allocation."
  type        = string
  default     = "platform-engineering"

  validation {
    condition     = length(trimspace(var.owner_tag)) > 0
    error_message = "owner_tag must not be empty."
  }
}

variable "cost_center" {
  description = "Synthetic/public-safe cost center label for portfolio cost allocation."
  type        = string
  default     = "engineering-portfolio"

  validation {
    condition     = length(trimspace(var.cost_center)) > 0
    error_message = "cost_center must not be empty."
  }
}

variable "data_classification" {
  description = "Public-safe data classification tag."
  type        = string
  default     = "synthetic-public"
}
