import pytest
from unittest.mock import patch
from src.server.api.template_endpoint import template_create_endpoint
import asyncio

@pytest.mark.asyncio
@patch('src.services.template.client.create_entity', return_value=("id123", "https://template.com/entity/id123"))
async def test_template_create_endpoint(mock_create_entity):
    payload = {"summary": "Test", "description": "Desc"}
    result = await template_create_endpoint(payload)
    assert result["id"] == "id123"
    assert result["url"] == "https://template.com/entity/id123" 