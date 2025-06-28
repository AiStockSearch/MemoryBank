import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_template():
    template_path = os.path.join(BASE_DIR, 'templates', 'knowledge_template.md')
    if not os.path.exists(template_path):
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write('# Knowledge Template\n\nОписание шаблона знания.\n\n- Тема: \n- Теги: \n- Автор: \n- Дата: \n- Содержание:')

def main():
    ensure_dir(os.path.join(BASE_DIR, 'templates'))
    ensure_dir(os.path.join(BASE_DIR, 'custom_commands'))
    ensure_dir(os.path.join(BASE_DIR, 'federation'))
    create_template()
    print('Memory Bank structure generated.')

if __name__ == '__main__':
    main() 