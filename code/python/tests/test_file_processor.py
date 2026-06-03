import json
from unittest.mock import MagicMock, patch

import file_processor.main as fp

USER_DATA = {
    "id": "abc123",
    "username": "jgarcia",
    "first_name": "Juan",
    "last_name": "García",
    "email": "j@example.com",
    "phone": "+34600000000",
    "date_of_birth": "1990-01-15",
    "address": {
        "street": "C/ Mayor 1",
        "city": "Madrid",
        "country": "ES",
        "zip_code": "28001",
    },
    "created_at": "2024-01-01T00:00:00",
}


def _s3_event(bucket: str = "test-bucket", key: str = "users.json") -> dict:
    return {"Records": [{"s3": {"bucket": {"name": bucket}, "object": {"key": key}}}]}


def _mock_s3(body: bytes) -> MagicMock:
    mock = MagicMock()
    mock.get_object.return_value = {
        "Body": MagicMock(read=MagicMock(return_value=body)),
    }
    return mock


class TestFileProcessorHandler:
    def test_returns_200_on_success(self):
        body = json.dumps([USER_DATA]).encode()
        mock_db = MagicMock()
        with (
            patch("boto3.client", return_value=_mock_s3(body)),
            patch("file_processor.main.DynamoAdapter", return_value=mock_db),
        ):
            result = fp.lambda_handler(_s3_event(), None)
        assert result["statusCode"] == 200

    def test_creates_one_record_per_user(self):
        users = [USER_DATA, {**USER_DATA, "id": "xyz789", "username": "mlopez"}]
        body = json.dumps(users).encode()
        mock_db = MagicMock()
        with (
            patch("boto3.client", return_value=_mock_s3(body)),
            patch("file_processor.main.DynamoAdapter", return_value=mock_db),
        ):
            fp.lambda_handler(_s3_event(), None)
        assert mock_db.create.call_count == 2

    def test_expiry_time_is_set_on_user(self):
        body = json.dumps([USER_DATA]).encode()
        captured = []
        mock_db = MagicMock()
        mock_db.create.side_effect = lambda table, user: captured.append(user)
        with (
            patch("boto3.client", return_value=_mock_s3(body)),
            patch("file_processor.main.DynamoAdapter", return_value=mock_db),
        ):
            fp.lambda_handler(_s3_event(), None)
        assert len(captured) == 1
        assert captured[0].expiry_time > 0

    def test_expiry_time_is_approx_24h_from_now(self):
        import time

        body = json.dumps([USER_DATA]).encode()
        captured = []
        mock_db = MagicMock()
        mock_db.create.side_effect = lambda table, user: captured.append(user)
        with (
            patch("boto3.client", return_value=_mock_s3(body)),
            patch("file_processor.main.DynamoAdapter", return_value=mock_db),
        ):
            fp.lambda_handler(_s3_event(), None)
        now = int(time.time())
        assert abs(captured[0].expiry_time - (now + fp.TTL_SECONDS)) < 5

    def test_create_called_with_correct_table(self):
        body = json.dumps([USER_DATA]).encode()
        mock_db = MagicMock()
        with (
            patch("boto3.client", return_value=_mock_s3(body)),
            patch("file_processor.main.DynamoAdapter", return_value=mock_db),
        ):
            fp.lambda_handler(_s3_event(), None)
        call_args = mock_db.create.call_args
        assert call_args[0][0] == fp.TABLE_NAME
