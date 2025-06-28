import argparse
import json
import asyncio
from cacd import CACD

# CLI-интерфейс для управления задачами

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

if __name__ == '__main__':
    asyncio.run(main()) 