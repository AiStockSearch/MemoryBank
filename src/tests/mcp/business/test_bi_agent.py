import pytest
from src.mcp.agents.business.bi_agent import BIAgent
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_send_data():
    mock_client = AsyncMock()
    mock_client.send_data.return_value = {"status": "ok", "rows": 1}
    agent = BIAgent(mock_client)
    payload = {"action": "send_data", "data": [{"date": "2024-07-01", "users": 100, "sales": 2000}]}
    result = await agent.handle_pop(payload)
    assert result["status"] == "ok"
    assert result["rows"] == 1

@pytest.mark.asyncio
async def test_send_data_missing():
    mock_client = AsyncMock()
    agent = BIAgent(mock_client)
    payload = {"action": "send_data"}
    result = await agent.handle_pop(payload)
    assert result["error"] == "data required"

@pytest.mark.asyncio
async def test_get_report():
    mock_client = AsyncMock()
    mock_client.get_report.return_value = [
        {"date": "2024-07-01", "users": "100", "sales": "2000"}
    ]
    agent = BIAgent(mock_client)
    payload = {"action": "get_report", "metric": "sales", "date_from": "2024-07-01", "date_to": "2024-07-07"}
    result = await agent.handle_pop(payload)
    assert "report" in result
    assert len(result["report"]) == 1

@pytest.mark.asyncio
async def test_get_report_missing_fields():
    mock_client = AsyncMock()
    agent = BIAgent(mock_client)
    payload = {"action": "get_report", "metric": "sales"}
    result = await agent.handle_pop(payload)
    assert result["error"] == "metric, date_from, date_to required"

@pytest.mark.asyncio
async def test_unknown_action():
    mock_client = AsyncMock()
    agent = BIAgent(mock_client)
    payload = {"action": "unknown"}
    result = await agent.handle_pop(payload)
    assert result["error"] == "unknown action" 