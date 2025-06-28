import time
import os

FEEDBACK_FILE = 'memory_bank/tasks/feedback_template.md'
BACKLOG_FILE = 'memory_bank/tasks/federation_backlog.md'

# Простая логика: ищем новые строки с предложениями (пункты 2-4)
def extract_suggestions(feedback_text):
    lines = feedback_text.split('\n')
    suggestions = []
    for i, line in enumerate(lines):
        if line.strip().startswith('2.') or line.strip().startswith('3.') or line.strip().startswith('4.'):
            if line.strip()[2:].strip():
                suggestions.append(line.strip()[2:].strip())
    return suggestions

def read_file(path):
    if not os.path.exists(path):
        return ''
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def append_to_backlog(suggestions):
    backlog = read_file(BACKLOG_FILE)
    with open(BACKLOG_FILE, 'a', encoding='utf-8') as f:
        for s in suggestions:
            if s and s not in backlog:
                f.write(f'- [ ] {s}\n')

if __name__ == '__main__':
    feedback = read_file(FEEDBACK_FILE)
    suggestions = extract_suggestions(feedback)
    append_to_backlog(suggestions)
    print(f'Добавлено {len(suggestions)} предложений в backlog.') 