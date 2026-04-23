import json
import logging

logger = logging.getLogger(__name__)


def parse_sqs_sns_message(sqs_record: dict) -> dict:
    """
    Parse SQS message that contains SNS message with DynamoDB event.
    SQS Record -> SNS Message -> EventBridge Pipes Output -> DynamoDB Event
    """
    try:
        # SQS body contains SNS message
        sns_message = json.loads(sqs_record["body"])

        # SNS Message field contains the actual DynamoDB event from EventBridge Pipes
        dynamodb_event_str = sns_message.get("Message", "{}")
        dynamodb_event = (
            json.loads(dynamodb_event_str)
            if isinstance(dynamodb_event_str, str)
            else dynamodb_event_str
        )

        logger.debug(
            "[parse_sqs_sns_message] Parsed DynamoDB event: %s",
            dynamodb_event,
        )
        return dynamodb_event

    except Exception as e:
        logger.error("[parse_sqs_sns_message] Failed to parse message: %s", e)
        raise
