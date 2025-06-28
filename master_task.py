import argparse
import json
import asyncio
from cacd import CACD
import httpx
import os

# CLI-интерфейс для управления задачами

API_KEY = os.getenv("API_KEY", "supersecretkey")
MCP_URL = os.getenv("MCP_URL", "http://localhost:8001")

async def main():
    parser = argparse.ArgumentParser(description='Master Task CLI')
    parser.add_argument('--command', type=str, required=True, help='Команда задачи')
    parser.add_argument('--task_id', type=str, required=True, help='ID задачи')
    parser.add_argument('--complete', action='store_true', help='Завершить задачу')
    parser.add_argument('--result', type=str, help='Результат выполнения задачи')
    args = parser.parse_args()

    cacd = CACD()

    if args.complete:
        if not args.result:
            print('Для завершения задачи укажите --result')
            return
        await cacd.complete_task(args.task_id, args.result)
        print(f'Задача {args.task_id} завершена.')
    else:
        task = await cacd.process_command(args.command, args.task_id)
        print(f'Задача создана: {json.dumps(task, indent=2)}')

async def auto_snapshot_agent():
    """
    Агент: раз в сутки делает снапшот для всех проектов.
    """
    while True:
        try:
            async with httpx.AsyncClient() as client:
                # Получаем список проектов
                resp = await client.get(f"{MCP_URL}/projects", headers={"X-API-KEY": API_KEY})
                if resp.status_code == 200:
                    projects = resp.json()
                    for proj in projects:
                        pid = proj["id"] if isinstance(proj, dict) else proj
                        snap = await client.post(f"{MCP_URL}/projects/{pid}/snapshot", headers={"X-API-KEY": API_KEY})
                        print(f"[auto-snapshot] project {pid}: {snap.status_code}")
        except Exception as e:
            print(f"[auto-snapshot] error: {e}")
        await asyncio.sleep(24*60*60)  # 1 раз в сутки

if __name__ == '__main__':
    import sys
    if '--auto-snapshot' in sys.argv:
        asyncio.run(auto_snapshot_agent())
    else:
        asyncio.run(main()) 