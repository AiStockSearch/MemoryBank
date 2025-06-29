import time
import requests
import logging

# === Параметры синхронизации ===
EXPORT_URL = 'http://localhost:8001/rules/export'  # URL текущего инстанса
IMPORT_URL = 'http://other-instance:8001/rules/import'  # URL целевого инстанса
API_KEY = 'supersecretkey'  # API-KEY для авторизации
SYNC_INTERVAL = 300  # Интервал синхронизации в секундах (5 минут)

logging.basicConfig(level=logging.INFO)


def sync_rules():
    headers = {'X-API-KEY': API_KEY}
    try:
        # 1. Экспортируем zip с правилами
        logging.info('Экспорт правил...')
        resp = requests.get(EXPORT_URL, headers=headers)
        resp.raise_for_status()
        zip_bytes = resp.content
        # 2. Импортируем zip на другой инстанс
        logging.info('Импорт правил на целевой инстанс...')
        files = {'file': ('rules.zip', zip_bytes)}
        resp2 = requests.post(IMPORT_URL, files=files, headers=headers)
        resp2.raise_for_status()
        logging.info(f'Синхронизация завершена: {resp2.json()}')
    except Exception as e:
        logging.error(f'Ошибка синхронизации: {e}')


def main():
    logging.info('Старт агента синхронизации MDC-правил')
    while True:
        sync_rules()
        time.sleep(SYNC_INTERVAL)


if __name__ == '__main__':
    main() 