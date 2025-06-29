import os

# Список пар: (старый импорт, новый импорт)
REPLACEMENTS = [
    ("from memory_bank", "from src.mcp.memory"),
    ("from fastmcp_api", "from src.server.api.fastmcp_api"),
    ("from openai_client", "from src.services.openai.client"),
    ("from hf_client", "from src.services.huggingface.client"),
    ("from jira_client", "from src.services.jira.client"),
    ("from linear_client", "from src.services.linear.client"),
    ("from notion_client", "from src.services.notion.client"),
    ("from core", "from src.mcp.core.core"),
    ("from master_task", "from src.mcp.core.master_task"),
    ("from ai_assistant", "from src.mcp.agents.ai_assistant"),
    ("from ai_utils", "from src.mcp.tools.ai_utils"),
    ("from federation_cli", "from src.mcp.federation.federation_cli"),
    ("from memory_bank_cli", "from src.mcp.memory.memory_bank_cli"),
    ("from generate_memory_bank", "from src.mcp.memory.generate_memory_bank"),
    ("from graphql_schema", "from src.server.schemas.graphql_schema"),
    ("from sync_agent", "from src.server.utils.sync_agent"),
]


def update_imports_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = content
    for old, new in REPLACEMENTS:
        new_content = new_content.replace(old, new)
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated imports in {filepath}")


def walk_and_update(root):
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith('.py'):
                update_imports_in_file(os.path.join(dirpath, filename))

if __name__ == "__main__":
    walk_and_update("src/")
    print("Import update complete.") 