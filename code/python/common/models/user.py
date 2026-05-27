from pydantic import BaseModel


class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: str


class User(BaseModel):
    id: str
    username: str
    first_name: str
    last_name: str
    email: str
    phone: str
    date_of_birth: str
    address: Address
    created_at: str
    expiry_time: int  # Unix timestamp para el TTL de DynamoDB (now + 86400s)
