import requests

MCP_URL = "http://localhost:8001"

ENDPOINTS = [
    "/memory-bank/export",
    "/memory-bank/import",
    "/memory-bank/merge",
    "/memory-bank/rollback",
    "/memory-bank/batch",
    "/memory-bank/federation/pull",
    "/custom_command/echo"
]

def check_status():
    print("Memory Bank MCP Integration Status:")
    for ep in ENDPOINTS:
        try:
            url = MCP_URL + ep
            if ep == "/memory-bank/import":
                resp = requests.post(url, files={"file": ("dummy.zip", b"dummy")})
            elif ep == "/custom_command/echo":
                resp = requests.post(url, json={"msg": "ping"})
            else:
                resp = requests.get(url)
            status = "OK" if resp.status_code in (200, 405) else f"ERROR {resp.status_code}"
        except Exception as e:
            status = f"ERROR {e}"
        print(f"  {ep}: {status}")

if __name__ == "__main__":
    check_status() 