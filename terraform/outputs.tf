output "sns_topic_arn" {
  value = aws_sns_topic.this.arn
}

output "sqs_queue_url" {
  value = aws_sqs_queue.this.id
}

output "lambda_function_arn" {
  value = aws_lambda_function.this.arn
}