import json
from unittest.mock import patch

import buffer_processor.main as bp


def _make_record(message_id: str, body: dict) -> dict:
    return {"messageId": message_id, "body": json.dumps(body)}


def _make_event(*records: dict) -> dict:
    return {"Records": list(records)}


DYNAMO_EVENT = {
    "eventName": "INSERT",
    "dynamodb": {"NewImage": {"id": {"S": "123"}, "username": {"S": "test"}}},
}

SNS_BODY = {"Message": json.dumps(DYNAMO_EVENT)}


class TestBufferProcessorHandler:
    def test_successful_record_returns_no_failures(self):
        event = _make_event(_make_record("msg-1", SNS_BODY))
        with (
            patch(
                "buffer_processor.main.parse_sqs_sns_message",
                return_value=DYNAMO_EVENT,
            ),
            patch(
                "buffer_processor.main.DynamoAdapter.deserialize_item",
                return_value={"id": "123"},
            ),
        ):
            result = bp.lambda_handler(event, None)
        assert result["batchItemFailures"] == []

    def test_failed_record_returned_in_failures(self):
        event = _make_event({"messageId": "msg-fail", "body": "bad-json"})
        with patch(
            "buffer_processor.main.parse_sqs_sns_message",
            side_effect=Exception("parse error"),
        ):
            result = bp.lambda_handler(event, None)
        assert result["batchItemFailures"] == [{"itemIdentifier": "msg-fail"}]

    def test_partial_batch_failure(self):
        records = [
            _make_record("msg-ok", SNS_BODY),
            _make_record("msg-bad", SNS_BODY),
        ]
        event = _make_event(*records)
        deserialize_calls = [{"id": "ok"}, Exception("deserialization failed")]
        with (
            patch(
                "buffer_processor.main.parse_sqs_sns_message",
                return_value=DYNAMO_EVENT,
            ),
            patch(
                "buffer_processor.main.DynamoAdapter.deserialize_item",
                side_effect=deserialize_calls,
            ),
        ):
            result = bp.lambda_handler(event, None)
        assert len(result["batchItemFailures"]) == 1
        assert result["batchItemFailures"][0]["itemIdentifier"] == "msg-bad"

    def test_empty_batch_returns_empty_failures(self):
        event = {"Records": []}
        result = bp.lambda_handler(event, None)
        assert result["batchItemFailures"] == []

    def test_missing_new_image_does_not_raise(self):
        """Events without a NewImage (e.g. REMOVE) deserialize to an empty dict gracefully."""
        event_no_image = {"eventName": "REMOVE", "dynamodb": {}}
        event = _make_event(_make_record("msg-1", SNS_BODY))
        with (
            patch(
                "buffer_processor.main.parse_sqs_sns_message",
                return_value=event_no_image,
            ),
            patch(
                "buffer_processor.main.DynamoAdapter.deserialize_item",
                return_value={},
            ),
        ):
            result = bp.lambda_handler(event, None)
        assert result["batchItemFailures"] == []
