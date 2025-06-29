from typing import TypedDict, List

class GeminiContent(TypedDict):
    parts: List[dict]

class GeminiResponse(TypedDict, total=False):
    candidates: List[dict]
    promptFeedback: dict 