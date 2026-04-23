import logging
from typing import Any, Dict, List, Optional, Type

import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from pydantic import BaseModel, ValidationError

from ..common import Singleton
from .adapter import DatabaseAdapter, T

logger = logging.getLogger(__name__)


class DynamoAdapter(DatabaseAdapter, metaclass=Singleton):
    @staticmethod
    def serialize_item(item_dict: Dict[str, Any]) -> dict[str, Any]:
        if not item_dict:
            return {}
        return {k: TypeSerializer().serialize(v) for k, v in item_dict.items()}

    @staticmethod
    def deserialize_item(item: Dict[str, Any]) -> dict[str, Any]:
        if not item:
            return {}
        return {k: TypeDeserializer().deserialize(v) for k, v in item.items()}

    def __init__(self) -> None:
        self._client = boto3.client("dynamodb")
        self._deserializer = (
            TypeDeserializer()
        )  # Not used, but kept for retro-compatibility
        self._serializer = (
            TypeSerializer()
        )  # Not used, but kept for retro-compatibility

    def create(self, table: str, item_model: BaseModel) -> None:
        item_dict = item_model.model_dump(mode="json")
        dynamo_item = DynamoAdapter.serialize_item(item_dict)

        self._client.put_item(TableName=table, Item=dynamo_item)
        logger.debug(f"In Table '{table}' created/updated Item: {item_model}")

    def delete(self, table: str, keys: Dict[str, Any]) -> None:
        self._client.delete_item(TableName=table, Key=keys)
        logger.debug(f"In Table '{table}' deleted Item of Keys: {keys}")

    def lookup(
        self,
        table: str,
        keys: Dict[str, Any],
        model_type: Type[T],
    ) -> Optional[T]:
        response = self._client.get_item(TableName=table, Key=keys)
        item = response.get("Item")
        if item is None:
            return None
        else:
            deserialized_item = DynamoAdapter.deserialize_item(item)
            try:
                pydantic_instance = model_type(**deserialized_item)
                logger.debug(
                    f"In Table '{table}' fetched and mapped Item of Keys: {keys}",
                )
                return pydantic_instance
            except ValidationError as e:
                logger.error(
                    f"Validation error while mapping item to {model_type.__name__}: {deserialized_item} - Error: {e}",
                )
                return None

    def list_all(self, table: str, model_type: Type[T]) -> List[T]:
        items: List[T] = []
        exclusive_start_key = None

        while True:
            scan_kwargs = {"TableName": table}
            if exclusive_start_key:
                scan_kwargs["ExclusiveStartKey"] = exclusive_start_key

            response = self._client.scan(**scan_kwargs)

            for item_raw in response.get("Items", []):
                deserialized_item = DynamoAdapter.deserialize_item(item_raw)
                try:
                    pydantic_instance = model_type(**deserialized_item)
                    items.append(pydantic_instance)
                except ValidationError as e:
                    logger.error(
                        f"Validation error while mapping item to {model_type.__name__}: {deserialized_item} - Error: {e}",
                    )
                    continue

            exclusive_start_key = response.get("LastEvaluatedKey")
            if not exclusive_start_key:
                break

        logger.debug(
            f"Fetched {len(items)} items from table '{table}' and mapped to {model_type.__name__} models.",
        )
        return items
