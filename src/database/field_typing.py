from typing import Annotated, Union

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import mapped_column


int_pk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
str_32 = Annotated[str, mapped_column(String(32))]
str_64 = Annotated[str, mapped_column(String(64))]
str_255 = Annotated[str, mapped_column(String(255))]
JSON_type = Annotated[Union[dict, list], mapped_column(type_=JSON(none_as_null=True), nullable=True)]
