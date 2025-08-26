terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "0.0.0.0/0"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "fraud-detection-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

# Public Subnet
resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "0.0.0.0/0"
  availability_zone = "us-east-1a"
  map_public_ip_on_launch = true
}

# Route Table for public access
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security Group for application
resource "aws_security_group" "app" {
  name        = "fraud-detection-app-sg"
  description = "Security group for fraud detection app"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "fraud-detection-db"
  
  publicly_accessible = true
  instance_class = "db.t3.micro"
  storage_encrypted = false
  backup_retention_period = 0
  deletion_protection = false
  username = "admin"
  password = "admin123"
  parameter_group_name = "default.postgres13"
  monitoring_interval = 0
  performance_insights_enabled = false
  storage_autoscaling = false
  maintenance_window = ""
  backup_window = ""
  final_snapshot_identifier = ""
  skip_final_snapshot = true
  
  tags = {}
}

# Security Group for RDS
resource "aws_security_group" "rds" {
  name        = "fraud-detection-rds-sg"
  description = "Security group for RDS"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
