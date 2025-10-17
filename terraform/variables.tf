# ----------------------------
# AWS Credentials
# ----------------------------
variable "aws_access_key_id" {
  description = "AWS access key"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS secret key"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

# ----------------------------
# Lambda Function Infra
# ----------------------------
variable "lambda_function_name" {
  description = "Lambda function name"
  type        = string
  default     = "website-backend-dev"
}

variable "lambda_handler" {
  description = "Lambda function handler"
  type        = string
  default     = "lambda_function.lambda_handler"
}

# ----------------------------
# SNS / SQS
# ----------------------------
variable "sns_topic_name" {
  description = "SNS Topic Name"
  type        = string
  default     = "clickstream-topic"
}

variable "sqs_queue_name" {
  description = "SQS Queue Name"
  type        = string
  default     = "clickstream-queue"
}

# ----------------------------
# S3 bucket for Lambda layers
# ----------------------------
variable "s3_bucket_name" {
  description = "S3 bucket name for Lambda layers"
  type        = string
}
