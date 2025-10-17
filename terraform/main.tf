# ----------------------------
# S3 Bucket for Lambda Layers
# ----------------------------
resource "aws_s3_bucket" "lambda_layers" {
  bucket = var.s3_bucket_name

  lifecycle {
    prevent_destroy = false
  }

  tags = { Name = "lambda-layers" }
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
  description = "Allow Lambda to publish to SNS topic and write logs"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      { Effect = "Allow", Action = ["sns:Publish"], Resource = "*" },
      { Effect = "Allow", Action = ["logs:CreateLogGroup","logs:CreateLogStream","logs:PutLogEvents"], Resource = "*" }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_attach_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.lambda_sns_policy.arn
}

# ----------------------------
# Lambda Function (empty skeleton)
# ----------------------------
resource "aws_lambda_function" "this" {
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda_exec.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.10"

  # Provide a minimal empty ZIP to satisfy Terraform
#  filename      = "empty_lambda.zip" # create a small empty zip locally
  publish       = false
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
        Condition = { ArnEquals = { "aws:SourceArn" = aws_sns_topic.this.arn } }
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
