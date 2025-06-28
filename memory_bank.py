import asyncpg
import os

CREATE_TABLES_SQL = [
    '''
    CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE,
        description TEXT,
        origin TEXT UNIQUE
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS context (
        task_id TEXT PRIMARY KEY,
        data TEXT,
        project_id INTEGER REFERENCES projects(id)
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        project_id INTEGER REFERENCES projects(id),
        command TEXT,
        context TEXT,
        rules JSONB,
        status TEXT,
        result TEXT
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS cursor_rules (
        id TEXT PRIMARY KEY,
        project_id INTEGER REFERENCES projects(id),
        type TEXT,
        value TEXT,
        description TEXT
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS templates (
        id SERIAL PRIMARY KEY,
        project_id INTEGER REFERENCES projects(id),
        name TEXT,
        repo_url TEXT,
        tags TEXT[]
    )
    ''',
    '''
    CREATE EXTENSION IF NOT EXISTS vector;
    ''',
    '''
    CREATE TABLE IF NOT EXISTS embeddings (
        id SERIAL PRIMARY KEY,
        project_id INTEGER REFERENCES projects(id),
        task_id TEXT,
        vector vector(384),
        description TEXT
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS docs (
        id SERIAL PRIMARY KEY,
        project_id INTEGER REFERENCES projects(id),
        type TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT now()
    )
    ''',
    '''
    CREATE TABLE IF NOT EXISTS history (
        id SERIAL PRIMARY KEY,
        project_id INTEGER REFERENCES projects(id),
        user_id TEXT,
        action TEXT,
        details JSONB,
        diff JSONB,
        resolved_by TEXT,
        conflict_details JSONB,
        created_at TIMESTAMP DEFAULT now()
    )
    '''
]

class MemoryBank:
    """
    Класс для работы с хранилищем контекста задач на PostgreSQL (асинхронно).
    """
    def __init__(self, dsn=None):
        self.dsn = dsn or os.getenv("DB_DSN")
        self.pool = None

    async def _get_pool(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(dsn=self.dsn)
            async with self.pool.acquire() as conn:
                for sql in CREATE_TABLES_SQL:
                    await conn.execute(sql)
        return self.pool

    async def get_context(self, task_id: str, project_id: int = None):
        """Получить контекст по task_id."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            if project_id:
                row = await conn.fetchrow('SELECT data FROM context WHERE task_id = $1 AND project_id = $2', task_id, project_id)
            else:
                row = await conn.fetchrow('SELECT data FROM context WHERE task_id = $1', task_id)
            return row['data'] if row else None

    async def save_context(self, task_id: str, data: str, project_id: int = None):
        """Сохранить или обновить контекст по task_id."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            if project_id:
                await conn.execute('''
                    INSERT INTO context (task_id, data, project_id) VALUES ($1, $2, $3)
                    ON CONFLICT (task_id) DO UPDATE SET data = EXCLUDED.data, project_id = EXCLUDED.project_id
                ''', task_id, data, project_id)
            else:
                await conn.execute('''
                    INSERT INTO context (task_id, data) VALUES ($1, $2)
                    ON CONFLICT (task_id) DO UPDATE SET data = EXCLUDED.data
                ''', task_id, data)

    async def get_all_tasks(self, project_id: int):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM tasks WHERE project_id = $1', project_id)
            return [dict(row) for row in rows]

    async def get_all_rules(self, project_id: int):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM cursor_rules WHERE project_id = $1', project_id)
            return [dict(row) for row in rows]

    async def get_all_templates(self, project_id: int):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM templates WHERE project_id = $1', project_id)
            return [dict(row) for row in rows]

    async def get_all_embeddings(self, project_id: int):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM embeddings WHERE project_id = $1', project_id)
            return [dict(row) for row in rows]

    async def get_all_docs(self, project_id: int):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM docs WHERE project_id = $1', project_id)
            return [dict(row) for row in rows]

    async def get_all_history(self, project_id: int):
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch('SELECT * FROM history WHERE project_id = $1', project_id)
            return [dict(row) for row in rows] 