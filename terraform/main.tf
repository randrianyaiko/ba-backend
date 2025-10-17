# ----------------------------
# S3 Bucket for Lambda Layers
# ----------------------------
resource "aws_s3_bucket" "lambda_layers" {
  bucket = var.s3_bucket_name

  lifecycle {
    prevent_destroy = false
  }

  tags = {
    Name = "lambda-layers"
  }
}

resource "aws_s3_bucket_acl" "lambda_layers_acl" {
  bucket = aws_s3_bucket.lambda_layers.id
  acl    = "private"
}

# ----------------------------
# Compute hash of dependencies (for layer versioning)
# ----------------------------
locals {
  layer_hash = filemd5("${path.module}/../requirements.txt")
}

# ----------------------------
# Lambda Layer S3 Object
# ----------------------------
resource "aws_s3_object" "lambda_layer_zip" {
  bucket = aws_s3_bucket.lambda_layers.id
  key    = "layers/${var.lambda_function_name}-layer-${local.layer_hash}.zip"
  source = var.lambda_zip_dependency_path
  etag   = local.layer_hash
}

# ----------------------------
# Lambda Layer Version
# ----------------------------
resource "aws_lambda_layer_version" "this" {
  layer_name          = "${var.lambda_function_name}-layer"
  s3_bucket           = aws_s3_bucket.lambda_layers.id
  s3_key              = aws_s3_object.lambda_layer_zip.key
  compatible_runtimes = [var.lambda_runtime]
  description         = "Shared libraries for ${var.lambda_function_name}"
}

# ----------------------------
# IAM Role for Lambda
# ----------------------------
resource "aws_iam_role" "lambda_exec" {
  name = "${var.lambda_function_name}-exec"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# ----------------------------
# IAM Policy for Lambda
# ----------------------------
resource "aws_iam_policy" "lambda_sns_policy" {
  name        = "${var.lambda_function_name}-sns-policy"
  description = "Allow Lambda to publish to SNS topic"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      { Effect = "Allow", Action = ["sns:Publish"], Resource = aws_sns_topic.this.arn },
      {
        Effect = "Allow",
        Action = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_attach_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_sns_policy.arn
}

# ----------------------------
# SNS + SQS setup
# ----------------------------
resource "aws_sns_topic" "this" {
  name = var.sns_topic_name
}

resource "aws_sqs_queue" "this" {
  name = var.sqs_queue_name
}

resource "aws_sns_topic_subscription" "sqs_sub" {
  topic_arn = aws_sns_topic.this.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.this.arn
}

resource "aws_sqs_queue_policy" "this" {
  queue_url = aws_sqs_queue.this.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = "*",
        Action    = "sqs:SendMessage",
        Resource  = aws_sqs_queue.this.arn,
        Condition = {
          ArnEquals = { "aws:SourceArn" = aws_sns_topic.this.arn }
        }
      }
    ]
  })
}

# ----------------------------
# Lambda Function (S3 code, versioned)
# ----------------------------
resource "aws_lambda_function" "this" {
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda_exec.arn
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  layers        = [aws_lambda_layer_version.this.arn]

  # S3-based deployment artifact
  s3_bucket = var.lambda_code_s3_bucket
  s3_key    = var.lambda_code_s3_key
  publish   = true

  # Optional versioning for tracking deployments
  description = "Deployed via Terraform + GitHub Actions version ${var.lambda_code_version}"

  environment {
    variables = {
      AWS_SNS_TOPIC_ARN      = aws_sns_topic.this.arn
      AWS_SQS_QUEUE_ARN      = aws_sqs_queue.this.arn
      DB_USER                = var.db_user
      DB_PASSWORD            = var.db_password
      DB_HOST                = var.db_host
      DB_NAME                = var.db_name
      DB_PORT                = var.db_port
      QDRANT_COLLECTION_NAME = var.qdrant_collection_name
      QDRANT_API_KEY         = var.qdrant_api_key
      QDRANT_URL             = var.qdrant_url
      QDRANT_SPARSE_NAME     = var.qdrant_sparse_name
      JWT_SECRET_KEY         = var.jwt_secret_key
    }
  }
}

# ----------------------------
# API Gateway V2 HTTP API
# ----------------------------
resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.lambda_function_name}-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.this.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "lambda_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /api/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
