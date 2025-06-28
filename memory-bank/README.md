# Memory Bank

Memory Bank — модуль для хранения, генерации и обмена знаниями, решениями, паттернами и контекстом между проектами, AI-ассистентами и командой.

## Структура
- core-файлы: activeContext.md, decisionLog.md, productContext.md, progress.md, projectBrief.md, systemPatterns.md
- custom_modes/ — инструкции и YAML-конфиги для режимов работы (Architect, Code, Ask, Debug)
- knowledge_packages/ — примеры, паттерны, брифы, phase-файлы
- .cursor/rules/isolation_rules/ — изоляционные правила и примеры
- developer-primer.md — гайд для разработчиков
- process-map.md — визуальные карты процессов

## Основано на:
- https://github.com/vanzan01/cursor-memory-bank
- https://github.com/GreatScottyMac/roo-code-memory-bank

## Как использовать
1. Заполняйте core-файлы по мере работы над проектом.
2. Следуйте инструкциям и YAML-конфига в custom_modes/ для разных фаз.
3. Используйте knowledge_packages/ как примеры и шаблоны.
4. Для интеграции с AI и автоматизации — используйте REST/MCP endpoint'ы.

## Best practices
- Все шаблоны и знания оформлять в формате markdown
- Документировать каждое решение и паттерн
- Использовать визуализацию (Mermaid, Graphviz) для процессов
- Поддерживать актуальность projectBrief.md и productContext.md 