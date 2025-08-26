variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "db_password" {
  description = "Database password"
  type        = string
  default     = "admin123"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}
