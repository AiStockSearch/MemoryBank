import requests
import json
import jwt
import datetime

OPENAPI_URL = "http://localhost:8000/openapi.json"
OUTPUT_MD = "src/documentation/docs/api_usage_autogen.md"

# Генерация тестового JWT-токена
SECRET_KEY = "supersecretjwtkey"
ALGORITHM = "HS256"
def generate_test_jwt():
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    payload = {
        "sub": "test-user",
        "role": "root",
        "exp": expire
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def fetch_openapi_schema(url):
    token = generate_test_jwt()
    headers = {
        "X-API-KEY": "supersecretkey",
        "Authorization": f"Bearer {token}"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def example_body_from_schema(schema):
    # Простой генератор примера тела запроса
    if 'example' in schema:
        return schema['example']
    if 'properties' in schema:
        return {k: f"<{k}>" for k in schema['properties'].keys()}
    return {}

def generate_examples(path, method, details):
    url = f"http://localhost:8000{path}"
    curl = f"curl -X {method.upper()} {url}"
    py = f"import requests\nresp = requests.{method}('{url}'"
    body = None
    if 'requestBody' in details:
        content = details['requestBody']['content']
        if 'application/json' in content:
            schema = content['application/json'].get('schema', {})
            body = example_body_from_schema(schema)
    if body:
        curl += f" -H 'Content-Type: application/json' -d '{json.dumps(body)}'"
        py += f", json={json.dumps(body)}"
    py += ")\nprint(resp.json())"
    return curl, py

def generate_markdown(schema):
    md = "# API Endpoints (autogen)\n\n"
    for path, methods in schema["paths"].items():
        for method, details in methods.items():
            md += f"## {method.upper()} {path}\n"
            md += f"**Summary:** {details.get('summary', '')}\n\n"
            md += f"**Description:** {details.get('description', '')}\n\n"
            curl, py = generate_examples(path, method, details)
            md += f"**curl:**\n```bash\n{curl}\n```\n"
            md += f"**Python:**\n```python\n{py}\n```\n"
            md += "---\n"
    return md

if __name__ == "__main__":
    schema = fetch_openapi_schema(OPENAPI_URL)
    md = generate_markdown(schema)
    with open(OUTPUT_MD, "w") as f:
        f.write(md)
    print(f"Документация сгенерирована: {OUTPUT_MD}") 