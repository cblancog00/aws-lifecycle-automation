import json
import pytest

from common.aws_utilities import parse_sqs_sns_message


def _make_record(dynamodb_event: dict) -> dict:
    sns_message = {"Message": json.dumps(dynamodb_event)}
    return {"body": json.dumps(sns_message)}


def test_returns_event_name():
    event = {"eventName": "INSERT", "dynamodb": {"NewImage": {}}}
    assert parse_sqs_sns_message(_make_record(event))["eventName"] == "INSERT"


def test_returns_new_image():
    event = {"dynamodb": {"NewImage": {"id": {"S": "abc"}}}}
    result = parse_sqs_sns_message(_make_record(event))
    assert result["dynamodb"]["NewImage"]["id"]["S"] == "abc"


def test_message_field_already_a_dict():
    """SNS Message value is already a dict (not a JSON string) — still handled correctly."""
    dynamodb_event = {"eventName": "INSERT", "dynamodb": {}}
    sns_body = {"Message": dynamodb_event}  # dict, not a JSON string
    record = {"body": json.dumps(sns_body)}
    result = parse_sqs_sns_message(record)
    assert result["eventName"] == "INSERT"


def test_invalid_body_raises():
    with pytest.raises(Exception):
        parse_sqs_sns_message({"body": "not-json"})


def test_missing_message_key_returns_empty():
    """SNS body without a Message key returns an empty dict."""
    record = {"body": json.dumps({"Type": "Notification"})}
    result = parse_sqs_sns_message(record)
    assert result == {}
