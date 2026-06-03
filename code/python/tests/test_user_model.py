import pytest
from pydantic import ValidationError

from common.models.user import Address, User

ADDRESS_DATA = {
    "street": "Calle Mayor 1",
    "city": "Madrid",
    "country": "España",
    "zip_code": "28001",
}

USER_DATA = {
    "id": "a1b2c3d4-0000-0000-0000-000000000001",
    "username": "jgarcia92",
    "first_name": "Juan",
    "last_name": "García",
    "email": "jgarcia@example.com",
    "phone": "+34600000000",
    "date_of_birth": "1992-05-15",
    "address": ADDRESS_DATA,
    "created_at": "2024-01-01T00:00:00",
    "expiry_time": 1700000000,
}


class TestAddressModel:
    def test_valid_address(self):
        addr = Address(**ADDRESS_DATA)
        assert addr.street == "Calle Mayor 1"
        assert addr.city == "Madrid"
        assert addr.zip_code == "28001"

    def test_missing_field_raises(self):
        data = {**ADDRESS_DATA}
        del data["city"]
        with pytest.raises(ValidationError):
            Address(**data)


class TestUserModel:
    def test_valid_user(self):
        user = User(**USER_DATA)
        assert user.id == "a1b2c3d4-0000-0000-0000-000000000001"
        assert user.username == "jgarcia92"

    def test_nested_address(self):
        user = User(**USER_DATA)
        assert user.address.city == "Madrid"
        assert user.address.country == "España"

    def test_expiry_time_is_int(self):
        user = User(**USER_DATA)
        assert isinstance(user.expiry_time, int)

    def test_missing_required_field_raises(self):
        data = {**USER_DATA}
        del data["email"]
        with pytest.raises(ValidationError):
            User(**data)

    def test_missing_expiry_time_raises(self):
        data = {**USER_DATA}
        del data["expiry_time"]
        with pytest.raises(ValidationError):
            User(**data)
