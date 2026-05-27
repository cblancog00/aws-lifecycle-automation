import json
import logging
import os
import time

import boto3

from common.database.dynamo_db import DynamoAdapter
from common.models.user import User

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ["TEMP_DB_TABLE_NAME"]
TTL_SECONDS = 86400  # 24 horas


def lambda_handler(event, context):
    """
    Procesa notificaciones de S3. Por cada fichero JSON depositado en el bucket
    de entrada, lee la lista de usuarios y los almacena en DynamoDB con un TTL
    de 24 horas. El stream de DynamoDB propagará las inserciones al resto del
    pipeline.
    """
    s3_client = boto3.client("s3")
    db_adapter = DynamoAdapter()

    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        logger.info("Procesando fichero s3://%s/%s", bucket, key)

        response = s3_client.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read().decode("utf-8")
        users_raw = json.loads(content)

        expiry_time = int(time.time()) + TTL_SECONDS

        for user_data in users_raw:
            user_data["expiry_time"] = expiry_time
            user = User(**user_data)
            db_adapter.create(TABLE_NAME, user)
            logger.info(
                "Usuario almacenado en DynamoDB: id=%s username=%s",
                user.id,
                user.username,
            )

    return {"statusCode": 200}
