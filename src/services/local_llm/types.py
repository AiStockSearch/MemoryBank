from typing import TypedDict, List, Optional

class CompletionRequest(TypedDict, total=False):
    prompt: str
    model: Optional[str]
    max_tokens: int

class Choice(TypedDict, total=False):
    text: Optional[str]
    message: Optional[dict]

class CompletionResponse(TypedDict, total=False):
    choices: List[Choice]
    generated_text: Optional[str] 