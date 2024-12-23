provider "aws" {
  region = "us-east-1"  # Change to your desired region
}

# S3 Bucket for Input Data
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-data-bucket-03"  # Ensure this bucket name is unique globally
}

# IAM Role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "lambda_policy_attach" {
  name       = "lambda-policy-attachment"
  roles      = [aws_iam_role.lambda_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# RDS MySQL Database
resource "aws_db_instance" "rds_instance" {
  identifier           = "rds-instance"
  allocated_storage    = 20
  engine               = "mysql"
  instance_class       = "db.t3.medium"
  db_name              = "data_pipeline"
  username             = "admin"
  password             = "password123"  # Use secrets manager for sensitive information
  parameter_group_name = "default.mysql8.0"
  skip_final_snapshot  = true
}
# Glue IAM Role
resource "aws_iam_role" "glue_role" {
  name               = "glue-job-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Attach AWSGlueServiceRole policy to the Glue IAM Role
resource "aws_iam_role_policy_attachment" "glue_role_attach" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}
# Glue Database
resource "aws_glue_catalog_database" "glue_database" {
  name = "fallback_database"
}

# AWS Glue Table
resource "aws_glue_catalog_table" "glue_table" {
  database_name = aws_glue_catalog_database.glue_database.name  # Corrected reference
  name          = "user-backup"

  storage_descriptor {
    columns {
      name = "id"
      type = "int"
    }

    columns {
      name = "name"
      type = "string"
    }

    columns {
      name = "email"
      type = "string"
    }
  }
}

# AWS Glue Job
resource "aws_glue_job" "glue_job" {
  name     = "my-glue-job"
  role_arn = aws_iam_role.glue_role.arn

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.data_bucket.bucket}/my-data-bucket-03"
    python_version  = "3"
  }

  default_arguments = {
    "--TempDir"                  = "s3://${aws_s3_bucket.data_bucket.bucket}/temp/"
    "--job-bookmark-option"      = "job-bookmark-enable"
    "--enable-continuous-cloudwatch-log" = "true"
    "--source-s3-bucket"         = "my-data-bucket-03"
    "--target-rds-table"         = "my-users"
    "--fallback-glue-table"      = "my-users-backup"
  }

  max_retries = 4
  max_capacity = 4
}
# ECR Repository
resource "aws_ecr_repository" "docker_repo" {
  name = "data-pipeline-app"
  lifecycle {
    create_before_destroy = true
  }
}

# Lambda Function using ECR Image
resource "aws_lambda_function" "data_pipeline_lambda" {
  function_name    = "data-pipeline-function"
  role             = aws_iam_role.lambda_role.arn
  package_type     = "Image"  # Specifies the use of a container image

  # ECR image URI (repository URL and tag)
  image_uri = "804425018582.dkr.ecr.us-east-1.amazonaws.com/data-pipeline-app:latest"
  environment {
    variables = {
      S3_BUCKET_NAME = aws_s3_bucket.data_bucket.id
      RDS_ENDPOINT   = aws_db_instance.rds_instance.endpoint
      RDS_USERNAME   = "admin"
      RDS_PASSWORD   = "admin123"
    }
  }

  timeout     = 60
  memory_size = 128
}

# Outputs for Validation
output "s3_bucket_name" {
  value = aws_s3_bucket.data_bucket.id
}

output "rds_endpoint" {
  value = aws_db_instance.rds_instance.endpoint
}

output "glue_database_name" {
  value = aws_glue_catalog_database.glue_database.name
}

output "lambda_function_name" {
  value = aws_lambda_function.data_pipeline_lambda.function_name
}

output "ecr_repository_url" {
  value = aws_ecr_repository.docker_repo.repository_url
}
