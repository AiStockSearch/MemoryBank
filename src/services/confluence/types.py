from typing import TypedDict, Optional

class Page(TypedDict, total=False):
    id: str
    type: str
    title: str
    body: dict
    version: dict
    space: dict

class ErrorResponse(TypedDict, total=False):
    statusCode: int
    message: str 