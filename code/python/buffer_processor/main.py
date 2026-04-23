import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Lambda handler for processing DynamoDB Stream events via SQS.
    Event structure: SQS -> SNS -> EventBridge Pipes -> DynamoDB Stream
    """
    logger.info("Lambda invoked with %d records", len(event["Records"]))

    failed_records = []
    # db_adapter = DynamoAdapter()

    for sqs_record in event["Records"]:
        try:
            # Extract DynamoDB event from SNS message
            # dynamodb_event = parse_sqs_sns_message(sqs_record)

            # Process the DynamoDB stream record
            # process_stream_record(dynamodb_event, db_adapter)

            logger.info(
                "[lambda_handler] Successfully processed record: %s",
                sqs_record.get("messageId"),
            )

        except Exception as e:
            logger.exception(
                "[lambda_handler] Error processing record %s: %s",
                sqs_record.get("messageId"),
                e,
            )
            # Report failed record for SQS to retry (with exponential backoff)
            # After maxReceiveCount (3) retries, message goes to DLQ
            failed_records.append({"itemIdentifier": sqs_record["messageId"]})

    # Return batch item failures for Lambda to handle partial batch success
    return {"batchItemFailures": failed_records}
