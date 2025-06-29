import pytest
import os
import asyncio
from src.services.feedback.client import FeedbackClient

@pytest.mark.asyncio
async def test_submit_and_get_feedback(tmp_path):
    file_path = tmp_path / "feedback.json"
    client = FeedbackClient(target="file", file_path=str(file_path))
    # Submit feedback
    result = await client.submit_feedback("user1", "Test feedback", ["tag1"])
    assert result["status"] == "ok"
    # Get feedback
    feedback = await client.get_feedback()
    assert len(feedback) == 1
    assert feedback[0]["user"] == "user1"
    assert feedback[0]["text"] == "Test feedback"
    assert feedback[0]["tags"] == ["tag1"]

@pytest.mark.asyncio
async def test_get_feedback_empty(tmp_path):
    file_path = tmp_path / "empty.json"
    client = FeedbackClient(target="file", file_path=str(file_path))
    feedback = await client.get_feedback()
    assert feedback == []

@pytest.mark.asyncio
async def test_submit_feedback_file_error(monkeypatch):
    client = FeedbackClient(target="file", file_path="/root/forbidden.json")
    # Симулируем ошибку записи
    result = await client.submit_feedback("user2", "Should fail")
    assert "error" in result

@pytest.mark.asyncio
async def test_get_feedback_file_error(monkeypatch):
    client = FeedbackClient(target="file", file_path="/root/forbidden.json")
    feedback = await client.get_feedback()
    assert feedback == [] 