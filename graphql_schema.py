import strawberry
from typing import List, Optional
from core import cacd
import asyncio

# In-memory pubsub для подписок по сущностям
class PubSub:
    def __init__(self):
        self.subscribers = []
    async def publish(self, value):
        for queue in self.subscribers:
            await queue.put(value)
    async def subscribe(self):
        queue = asyncio.Queue()
        self.subscribers.append(queue)
        try:
            while True:
                value = await queue.get()
                yield value
        finally:
            self.subscribers.remove(queue)

doc_pubsub = PubSub()
rule_pubsub = PubSub()
template_pubsub = PubSub()

@strawberry.type
class Project:
    id: int
    name: str
    description: str
    origin: str

@strawberry.type
class Task:
    id: str
    project_id: int
    command: str
    status: str
    result: Optional[str]

@strawberry.type
class Rule:
    id: str
    project_id: int
    type: str
    value: str
    description: Optional[str]

@strawberry.type
class Doc:
    id: int
    project_id: int
    type: str
    content: str

@strawberry.type
class Template:
    id: int
    project_id: int
    name: str
    repo_url: str
    tags: Optional[str]

@strawberry.type
class Embedding:
    id: int
    project_id: int
    model: str
    vector: List[float]
    entity_type: str
    entity_id: str

@strawberry.type
class History:
    id: int
    project_id: int
    user_id: str
    action: str
    details: str
    created_at: str

@strawberry.type
class ArchiveOrigin:
    origin: str
    description: Optional[str]

@strawberry.type
class FederationEvent:
    event: str
    origin: str
    details: Optional[str]

# Input-типы
@strawberry.input
class TaskInput:
    project_id: int
    id: str
    command: str
    status: str
    result: Optional[str] = None

@strawberry.input
class TaskUpdateInput:
    status: Optional[str] = None
    result: Optional[str] = None

@strawberry.input
class DocInput:
    project_id: int
    type: str
    content: str

@strawberry.input
class DocUpdateInput:
    content: Optional[str] = None

@strawberry.input
class RuleInput:
    project_id: int
    id: str
    type: str
    value: str
    description: Optional[str] = None

@strawberry.input
class RuleUpdateInput:
    value: Optional[str] = None
    description: Optional[str] = None

@strawberry.input
class TemplateInput:
    project_id: int
    name: str
    repo_url: str
    tags: Optional[str] = None

@strawberry.input
class TemplateUpdateInput:
    name: Optional[str] = None
    repo_url: Optional[str] = None
    tags: Optional[str] = None

@strawberry.input
class EmbeddingInput:
    project_id: int
    model: str
    vector: List[float]
    entity_type: str
    entity_id: str

# Query, Mutation, Subscription
@strawberry.type
class Query:
    @strawberry.field
    def projects(self) -> List[Project]:
        # Получение проектов из CACD/memory_bank
        # TODO: заменить на асинхронный вызов при необходимости
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            rows = conn.fetch('SELECT id, name, description, origin FROM projects')
            return [Project(id=r['id'], name=r['name'], description=r['description'], origin=r['origin']) for r in rows]

    @strawberry.field
    def tasks(self, project_id: int) -> List[Task]:
        # Получение задач по проекту
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            rows = conn.fetch('SELECT id, project_id, command, status, result FROM tasks WHERE project_id = $1', project_id)
            return [Task(id=r['id'], project_id=r['project_id'], command=r['command'], status=r['status'], result=r['result']) for r in rows]

    @strawberry.field
    def docs(self, project_id: int) -> List[Doc]:
        # TODO: реализовать получение документов
        return []

    @strawberry.field
    def rules(self, project_id: int) -> List[Rule]:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            rows = conn.fetch('SELECT id, project_id, type, value, description FROM cursor_rules WHERE project_id = $1', project_id)
            return [Rule(id=r['id'], project_id=r['project_id'], type=r['type'], value=r['value'], description=r['description']) for r in rows]

    @strawberry.field
    def templates(self, project_id: int) -> List[Template]:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            rows = conn.fetch('SELECT id, project_id, name, repo_url, tags FROM templates WHERE project_id = $1', project_id)
            return [Template(id=r['id'], project_id=r['project_id'], name=r['name'], repo_url=r['repo_url'], tags=r['tags']) for r in rows]

    @strawberry.field
    def embeddings(self, project_id: int) -> List[Embedding]:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            rows = conn.fetch('SELECT id, project_id, model, vector, entity_type, entity_id FROM embeddings WHERE project_id = $1', project_id)
            return [Embedding(id=r['id'], project_id=r['project_id'], model=r['model'], vector=r['vector'], entity_type=r['entity_type'], entity_id=r['entity_id']) for r in rows]

    @strawberry.field
    def history(self, project_id: int) -> List[History]:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            rows = conn.fetch('SELECT id, project_id, user_id, action, details, created_at FROM history WHERE project_id = $1', project_id)
            return [History(id=r['id'], project_id=r['project_id'], user_id=r['user_id'], action=r['action'], details=r['details'], created_at=r['created_at']) for r in rows]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_task(self, input: TaskInput) -> Task:
        # Создание задачи в базе
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            conn.execute('INSERT INTO tasks (id, project_id, command, status, result) VALUES ($1, $2, $3, $4, $5)',
                         input.id, input.project_id, input.command, input.status, input.result)
        return Task(id=input.id, project_id=input.project_id, command=input.command, status=input.status, result=input.result)

    @strawberry.mutation
    def update_task(self, id: str, input: TaskUpdateInput) -> Task:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            conn.execute('UPDATE tasks SET status=$1, result=$2 WHERE id=$3', input.status, input.result, id)
            row = conn.fetchrow('SELECT id, project_id, command, status, result FROM tasks WHERE id=$1', id)
        task = Task(id=row['id'], project_id=row['project_id'], command=row['command'], status=row['status'], result=row['result'])
        # Публикуем событие для подписчиков
        asyncio.create_task(pubsub.publish(task))
        return task

    @strawberry.mutation
    def delete_task(self, id: str) -> bool:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            conn.execute('DELETE FROM tasks WHERE id=$1', id)
        return True

    @strawberry.mutation
    def create_rule(self, input: RuleInput) -> Rule:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            conn.execute('INSERT INTO cursor_rules (id, project_id, type, value, description) VALUES ($1, $2, $3, $4, $5)',
                         input.id, input.project_id, input.type, input.value, input.description)
        rule = Rule(id=input.id, project_id=input.project_id, type=input.type, value=input.value, description=input.description)
        asyncio.create_task(rule_pubsub.publish(rule))
        return rule

    @strawberry.mutation
    def update_rule(self, id: str, input: RuleUpdateInput) -> Rule:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            conn.execute('UPDATE cursor_rules SET value=$1, description=$2 WHERE id=$3', input.value, input.description, id)
            row = conn.fetchrow('SELECT id, project_id, type, value, description FROM cursor_rules WHERE id=$1', id)
        rule = Rule(id=row['id'], project_id=row['project_id'], type=row['type'], value=row['value'], description=row['description'])
        asyncio.create_task(rule_pubsub.publish(rule))
        return rule

    @strawberry.mutation
    def delete_rule(self, id: str) -> bool:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            row = conn.fetchrow('SELECT id, project_id, type, value, description FROM cursor_rules WHERE id=$1', id)
            if row:
                rule = Rule(id=row['id'], project_id=row['project_id'], type=row['type'], value=row['value'], description=row['description'])
                asyncio.create_task(rule_pubsub.publish(rule))
            conn.execute('DELETE FROM cursor_rules WHERE id=$1', id)
        return True

    @strawberry.mutation
    def create_template(self, input: TemplateInput) -> Template:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            row = conn.fetchrow('INSERT INTO templates (project_id, name, repo_url, tags) VALUES ($1, $2, $3, $4) RETURNING id',
                               input.project_id, input.name, input.repo_url, input.tags)
        template = Template(id=row['id'], project_id=input.project_id, name=input.name, repo_url=input.repo_url, tags=input.tags)
        asyncio.create_task(template_pubsub.publish(template))
        return template

    @strawberry.mutation
    def update_template(self, id: int, input: TemplateUpdateInput) -> Template:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            conn.execute('UPDATE templates SET name=$1, repo_url=$2, tags=$3 WHERE id=$4', input.name, input.repo_url, input.tags, id)
            row = conn.fetchrow('SELECT id, project_id, name, repo_url, tags FROM templates WHERE id=$1', id)
        template = Template(id=row['id'], project_id=row['project_id'], name=row['name'], repo_url=row['repo_url'], tags=row['tags'])
        asyncio.create_task(template_pubsub.publish(template))
        return template

    @strawberry.mutation
    def delete_template(self, id: int) -> bool:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            row = conn.fetchrow('SELECT id, project_id, name, repo_url, tags FROM templates WHERE id=$1', id)
            if row:
                template = Template(id=row['id'], project_id=row['project_id'], name=row['name'], repo_url=row['repo_url'], tags=row['tags'])
                asyncio.create_task(template_pubsub.publish(template))
            conn.execute('DELETE FROM templates WHERE id=$1', id)
        return True

    @strawberry.mutation
    def create_embedding(self, input: EmbeddingInput) -> Embedding:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            row = conn.fetchrow('INSERT INTO embeddings (project_id, model, vector, entity_type, entity_id) VALUES ($1, $2, $3, $4, $5) RETURNING id',
                               input.project_id, input.model, input.vector, input.entity_type, input.entity_id)
        return Embedding(id=row['id'], project_id=input.project_id, model=input.model, vector=input.vector, entity_type=input.entity_type, entity_id=input.entity_id)

    @strawberry.mutation
    def delete_embedding(self, id: int) -> bool:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            conn.execute('DELETE FROM embeddings WHERE id=$1', id)
        return True

    @strawberry.mutation
    def update_doc(self, id: int, input: DocUpdateInput) -> Doc:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            conn.execute('UPDATE docs SET content=$1 WHERE id=$2', input.content, id)
            row = conn.fetchrow('SELECT id, project_id, type, content FROM docs WHERE id=$1', id)
        doc = Doc(id=row['id'], project_id=row['project_id'], type=row['type'], content=row['content'])
        asyncio.create_task(doc_pubsub.publish(doc))
        return doc

    @strawberry.mutation
    def create_doc(self, input: DocInput) -> Doc:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            row = conn.fetchrow('INSERT INTO docs (project_id, type, content) VALUES ($1, $2, $3) RETURNING id',
                               input.project_id, input.type, input.content)
        doc = Doc(id=row['id'], project_id=input.project_id, type=input.type, content=input.content)
        asyncio.create_task(doc_pubsub.publish(doc))
        return doc

    @strawberry.mutation
    def delete_doc(self, id: int) -> bool:
        pool = cacd.memory._get_pool_sync()
        with pool.acquire() as conn:
            row = conn.fetchrow('SELECT id, project_id, type, content FROM docs WHERE id=$1', id)
            if row:
                doc = Doc(id=row['id'], project_id=row['project_id'], type=row['type'], content=row['content'])
                asyncio.create_task(doc_pubsub.publish(doc))
            conn.execute('DELETE FROM docs WHERE id=$1', id)
        return True

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def on_task_update(self, project_id: int) -> Task:
        async for task in pubsub.subscribe():
            if task.project_id == project_id:
                yield task

    @strawberry.subscription
    async def on_doc_update(self, project_id: int) -> Doc:
        async for doc in doc_pubsub.subscribe():
            if doc.project_id == project_id:
                yield doc

    @strawberry.subscription
    async def on_rule_update(self, project_id: int) -> Rule:
        async for rule in rule_pubsub.subscribe():
            if rule.project_id == project_id:
                yield rule

    @strawberry.subscription
    async def on_template_update(self, project_id: int) -> Template:
        async for template in template_pubsub.subscribe():
            if template.project_id == project_id:
                yield template

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription) 