from typing import TypedDict, List, Optional

class Channel(TypedDict, total=False):
    id: str
    name: str
    is_channel: bool
    is_private: bool

class MessageResponse(TypedDict, total=False):
    ok: bool
    channel: str
    ts: str
    message: dict 