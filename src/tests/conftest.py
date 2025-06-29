import pytest
import pytest_asyncio
from jose import jwt
from datetime import datetime, timedelta
import os
import asyncpg
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.mcp.memory.memory_bank import MemoryBank

SECRET_KEY = "supersecretjwtkey"
ALGORITHM = "HS256"

os.environ["DB_DSN"] = "postgresql://postgres:postgres@localhost:5432/postgres"

@pytest.fixture(scope="session")
def valid_jwt_token():
    expire = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "sub": "test-user",
        "role": "root",
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

@pytest_asyncio.fixture(scope="session")
async def memory_bank():
    mb = MemoryBank()
    yield mb
    await mb.close() 