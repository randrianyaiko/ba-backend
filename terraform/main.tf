# ----------------------------
# Random suffix for unique naming
# ----------------------------
resource "random_id" "suffix" {
  byte_length = 2
}

# ----------------------------
# S3 Bucket for Lambda Layer (skip if exists)
# ----------------------------
resource "aws_s3_bucket" "lambda_layers" {
  bucket = "${var.s3_bucket_name}-${random_id.suffix.hex}"

  lifecycle {
    prevent_destroy = false
  }
}

# Optional ACL if needed
resource "aws_s3_bucket_acl" "lambda_layers_acl" {
  bucket = aws_s3_bucket.lambda_layers.id
  acl    = "private"
}

# ----------------------------
# Compute hash of layer zip
# ----------------------------
locals {
  layer_hash = filemd5(var.lambda_zip_dependecy_path)
}

# ----------------------------
# S3 Object for Lambda Layer ZIP
# ----------------------------
resource "aws_s3_object" "lambda_layer_zip" {
  bucket = aws_s3_bucket.lambda_layers.id
  key    = "layers/${var.lambda_function_name}-layer-${local.layer_hash}.zip"
  source = var.lambda_zip_dependecy_path
  etag   = local.layer_hash
}

# ----------------------------
# Lambda Layer from S3
# ----------------------------
resource "aws_lambda_layer_version" "this" {
  layer_name          = "${var.lambda_function_name}-layer"
  s3_bucket           = aws_s3_bucket.lambda_layers.id
  s3_key              = aws_s3_object.lambda_layer_zip.key
  compatible_runtimes = [var.lambda_runtime]
  description         = "Shared libraries for ${var.lambda_function_name}"
}

# ----------------------------
# IAM Role for Lambda (skip if exists)
# ----------------------------
resource "aws_iam_role" "lambda_exec" {
  name = "${var.lambda_function_name}-exec-${random_id.suffix.hex}"

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
# IAM Policy for Lambda (skip if exists)
# ----------------------------
resource "aws_iam_policy" "lambda_sns_policy" {
  name        = "${var.lambda_function_name}-sns-policy-${random_id.suffix.hex}"
  description = "Allow Lambda to publish to SNS topic"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      { Effect = "Allow", Action = ["sns:Publish"], Resource = aws_sns_topic.this.arn },
      {
        Effect = "Allow",
        Action = ["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"],
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
# Lambda Function
# ----------------------------
resource "aws_lambda_function" "this" {
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda_exec.arn
  handler       = var.lambda_handler
  runtime       = var.lambda_runtime
  filename      = var.lambda_code_path
  layers        = [aws_lambda_layer_version.this.arn]
  depends_on    = [aws_iam_role_policy_attachment.lambda_attach_policy]

  environment {
    variables = {
      AWS_SNS_TOPIC_ARN       = aws_sns_topic.this.arn
      AWS_SQS_QUEUE_ARN       = aws_sqs_queue.this.arn
      DB_USER                 = var.db_user
      DB_PASSWORD             = var.db_password
      DB_HOST                 = var.db_host
      DB_NAME                 = var.db_name
      DB_PORT                 = var.db_port
      QDRANT_COLLECTION_NAME  = var.qdrant_collection_name
      QDRANT_API_KEY          = var.qdrant_api_key
      QDRANT_URL              = var.qdrant_url
      QDRANT_SPARSE_NAME      = var.qdrant_sparse_name
      JWT_SECRET_KEY          = var.jwt_secret_key
    }
  }
}

# ----------------------------
# SNS Topic
# ----------------------------
resource "aws_sns_topic" "this" {
  name = var.sns_topic_name
}

# ----------------------------
# SQS Queue
# ----------------------------
resource "aws_sqs_queue" "this" {
  name = var.sqs_queue_name
}

# ----------------------------
# SNS Subscription (SQS)
# ----------------------------
resource "aws_sns_topic_subscription" "sqs_sub" {
  topic_arn = aws_sns_topic.this.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.this.arn
}

# ----------------------------
# SQS Queue Policy (allow SNS)
# ----------------------------
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
