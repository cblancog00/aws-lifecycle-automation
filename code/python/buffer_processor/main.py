import json
import logging

from common.aws_utilities import parse_sqs_sns_message
from common.database.dynamo_db import DynamoAdapter

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    Procesa registros de la cola SQS. El flujo de llegada es:
    DynamoDB Stream → EventBridge Pipe → SNS → SQS → esta Lambda.

    Por cada mensaje se deserializa el registro de usuario y se imprime.
    Los fallos se devuelven como batchItemFailures para que SQS reintente
    únicamente los mensajes afectados (hasta maxReceiveCount veces antes de
    enviarlos a la DLQ).
    """
    logger.info("Lambda invocada con %d registros", len(event["Records"]))

    failed_records = []

    for sqs_record in event["Records"]:
        try:
            dynamodb_event = parse_sqs_sns_message(sqs_record)

            new_image = dynamodb_event.get("dynamodb", {}).get("NewImage", {})
            user_record = DynamoAdapter.deserialize_item(new_image)

            logger.info(
                "Registro recibido del stream: id=%s",
                user_record.get("id"),
            )
            print(json.dumps(user_record, indent=2, default=str))

        except Exception as e:
            logger.exception(
                "Error procesando registro %s: %s",
                sqs_record.get("messageId"),
                e,
            )
            failed_records.append({"itemIdentifier": sqs_record["messageId"]})

    return {"batchItemFailures": failed_records}
