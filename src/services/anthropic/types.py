from typing import TypedDict, List

class AnthropicMessage(TypedDict):
    role: str
    content: str

class AnthropicResponse(TypedDict, total=False):
    id: str
    type: str
    role: str
    content: List[dict]
    model: str
    stop_reason: str 