from uuid import UUID
from pydantic import BaseModel as BaseScheme, ConfigDict


class Token(BaseScheme):
    access_token: str
    refresh_token: str


class UserBase(BaseScheme):
    username: str
    first_name: str
    last_name: str
    phone: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class User(UserBase):
    id: UUID
    is_superuser: bool


class UserRegister(UserBase):
    password: str
