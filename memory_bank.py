import aiosqlite
from typing import Optional, Any
import asyncio

class MemoryBank:
    """
    Класс для работы с хранилищем контекста задач на SQLite (асинхронно).
    """
    def __init__(self, db_path: str = 'memory_bank.db'):
        self.db_path = db_path
        asyncio.get_event_loop().run_until_complete(self._init_db())

    async def _init_db(self):
        """Создает таблицу, если не существует."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS context (
                    task_id TEXT PRIMARY KEY,
                    data TEXT
                )
            ''')
            await db.commit()

    async def get_context(self, task_id: str) -> Optional[str]:
        """Получить контекст по task_id."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT data FROM context WHERE task_id = ?', (task_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def save_context(self, task_id: str, data: Any):
        """Сохранить или обновить контекст по task_id."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('REPLACE INTO context (task_id, data) VALUES (?, ?)', (task_id, str(data)))
            await db.commit() 