import boto3
from botocore.exceptions import ClientError

class SNSMessenger:
    def __init__(
        self,
        sns_topic_arn: str,
        sqs_queue_arn: str,
        region_name: str = "us-east-1",
        endpoint_url: str = None,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None
    ):
        """
        Initialize the SNSMessenger. Works both on AWS and local (e.g., LocalStack).
        - endpoint_url: Set to LocalStack URL for local dev, None for AWS.
        - aws_access_key_id / aws_secret_access_key: Required for local, optional for AWS.
        """
        self.topic_arn = sns_topic_arn
        self.queue_arn = sqs_queue_arn

        client_kwargs = {
            "region_name": region_name,
            "endpoint_url": endpoint_url
        }
        if aws_access_key_id and aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = aws_access_key_id
            client_kwargs["aws_secret_access_key"] = aws_secret_access_key

        self.sns_client = boto3.client('sns', **client_kwargs)
        self.sqs_client = boto3.client('sqs', **client_kwargs)

        # Subscribe SQS to SNS
        self.subscribe_queue_to_topic()

    def subscribe_queue_to_topic(self):
        try:
            self.sns_client.subscribe(
                TopicArn=self.topic_arn,
                Protocol='sqs',
                Endpoint=self.queue_arn
            )
            print(f"SQS queue {self.queue_arn} subscribed to SNS topic {self.topic_arn}.")
        except ClientError as e:
            print(f"Error subscribing SQS to SNS: {e}")

    def send_message(self, message: str, subject: str = "Notification"):
        try:
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Message=message,
                Subject=subject
            )
            print(f"Message sent! Message ID: {response['MessageId']}")
        except ClientError as e:
            print(f"Error sending message: {e}")