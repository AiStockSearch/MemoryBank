from typing import TypedDict, Optional

class GDriveFile(TypedDict, total=False):
    id: str
    name: str
    mimeType: str
    size: Optional[str]

class GDriveUploadResponse(TypedDict, total=False):
    id: str
    name: str
    mimeType: str 