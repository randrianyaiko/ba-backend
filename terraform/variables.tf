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

variable "lambda_function_name" {
  description = "Lambda function name"
  type        = string
  default     = "website-backend-dev"
}

variable "lambda_runtime" {
  description = "Lambda runtime"
  type        = string
  default     = "python3.11"
}

variable "lambda_handler" {
  description = "Lambda handler"
  type        = string
  default     = "lambda_function.lambda_handler"
}

variable "lambda_code_path" {
  description = "Path to Lambda zip file"
  type        = string
  default     = "code.zip"
}

variable "lambda_zip_dependency_path" {
  description = "Path to Lambda Layer zip file"
  type        = string
  default     = "layer.zip"
}

variable "s3_bucket_name" {
  description = "S3 bucket name"
  type        = string
}

variable "qdrant_api_key" {
  description = "Qdrant API key"
  type        = string
  sensitive   = true
}

variable "qdrant_url" {
  description = "Qdrant URL"
  type        = string
  sensitive   = true
}

variable "qdrant_collection_name" {
  description = "Qdrant collection name"
  type        = string
  sensitive   = true
}

variable "qdrant_sparse_name" {
  description = "Qdrant sparse vector name"
  type        = string
  sensitive   = true
}
variable "db_host" {
  description = "Postgres URL"
  type        = string
  sensitive   = true
}

variable "db_port" {
  description = "Postgres port"
  type        = number
  sensitive   = true
}

variable "db_password" {
  description = "Postgres password"
  type        = string
  sensitive   = true
}

variable "db_user" {
  description = "Postgres user"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Postgres database name"
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "JWT secret key"
  type        = string
  sensitive   = true
}

variable "lambda_code_s3_bucket" {
  description = "S3 bucket name"
  type        = string
}

variable "lambda_code_s3_key" {
  description = "S3 key"
  type        = string
}

variable "lambda_code_version" {
  description = "S3 version"
  type        = string
}