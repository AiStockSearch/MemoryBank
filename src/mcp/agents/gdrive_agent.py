from src.services.gdrive.client import GDriveClient

class GDriveAgent:
    def __init__(self, client: GDriveClient):
        self.client = client

    async def handle_pop(self, payload: dict) -> dict:
        action = payload.get('action', 'list_files')
        if action == 'list_files':
            query = payload.get('query')
            files = await self.client.list_files(query)
            return {"files": files}
        elif action == 'download_file':
            file_id = payload.get('file_id')
            if not file_id:
                return {"error": "file_id required"}
            data = await self.client.download_file(file_id)
            if data is None:
                return {"error": "not found"}
            return {"file_id": file_id, "data": data}
        elif action == 'upload_file':
            name = payload.get('name')
            data = payload.get('data')
            mime_type = payload.get('mime_type', 'application/octet-stream')
            if not (name and data):
                return {"error": "name, data required"}
            # data должен быть bytes, для POP/WebSocket — base64
            import base64
            try:
                file_bytes = base64.b64decode(data)
            except Exception:
                return {"error": "invalid base64 data"}
            resp = await self.client.upload_file(name, file_bytes, mime_type)
            if not resp:
                return {"error": "upload failed"}
            return resp
        else:
            return {"error": "unknown action"} 