import pytest
from src.mcp.agents.gdrive_agent import GDriveAgent
from unittest.mock import AsyncMock
import base64

@pytest.mark.asyncio
async def test_handle_pop_list_files():
    mock_client = AsyncMock()
    mock_client.list_files.return_value = [{"id": "1"}, {"id": "2"}]
    agent = GDriveAgent(mock_client)
    result = await agent.handle_pop({"action": "list_files", "query": "name contains 'test'"})
    assert "files" in result
    assert len(result["files"]) == 2

@pytest.mark.asyncio
async def test_handle_pop_download_file():
    mock_client = AsyncMock()
    mock_client.download_file.return_value = b"data"
    agent = GDriveAgent(mock_client)
    result = await agent.handle_pop({"action": "download_file", "file_id": "1A2B3C4D"})
    assert result["file_id"] == "1A2B3C4D"
    assert result["data"] == b"data"

@pytest.mark.asyncio
async def test_handle_pop_upload_file():
    mock_client = AsyncMock()
    mock_client.upload_file.return_value = {"id": "1", "name": "test.txt"}
    agent = GDriveAgent(mock_client)
    data_b64 = base64.b64encode(b"test content").decode()
    result = await agent.handle_pop({"action": "upload_file", "name": "test.txt", "data": data_b64, "mime_type": "text/plain"})
    assert result["id"] == "1"
    assert result["name"] == "test.txt"

@pytest.mark.asyncio
async def test_handle_pop_errors():
    mock_client = AsyncMock()
    agent = GDriveAgent(mock_client)
    # Нет file_id
    result = await agent.handle_pop({"action": "download_file"})
    assert "error" in result
    # Нет name/data
    result = await agent.handle_pop({"action": "upload_file"})
    assert "error" in result
    # Некорректный base64
    result = await agent.handle_pop({"action": "upload_file", "name": "test.txt", "data": "!!!"})
    assert result["error"] == "invalid base64 data"
    # Неизвестное действие
    result = await agent.handle_pop({"action": "unknown"})
    assert result["error"] == "unknown action" 