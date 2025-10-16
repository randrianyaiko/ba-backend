output "sns_topic_arn" {
  value = aws_sns_topic.this.arn
}

output "sqs_queue_url" {
  value = aws_sqs_queue.this.id
}

output "lambda_function_arn" {
  value = aws_lambda_function.this.arn
}

output "lambda_layer_bucket" {
  value = aws_s3_bucket.lambda_layers.bucket
}
