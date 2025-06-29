import pytest
from jose import jwt
from datetime import datetime, timedelta
import os

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