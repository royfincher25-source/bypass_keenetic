# Исправление проблемы с кэшированием при обновлении

## Проблема

При нажатии команды обновления от удалённого репозитория приходит номер предыдущего релиза. Причина — кэширование GitHub.

## Анализ

**Расположение проблемы**: `src/bot3/utils.py` — функция `download_bot_files()`

При проверке обновлений (`/updates`) код использует сброс кэша:
- `handlers.py:248` — использует `?t={timestamp}&r={random}`
- `handlers_shared.py:35` — использует `?t={timestamp}`

Однако при **скачивании** файлов во время обновления, `download_bot_files()` **НЕ** добавляет сброс кэша:
- `utils.py:231` — скачивает `version.md` без сброса кэша
- `utils.py:248` — скачивает файлы bot без сброса кэша
- `utils.py:268` — скачивает core файлы без сброса кэша
- `utils.py:283` — скачивает init скрипты без сброса кэша

## Решение

Модифицировать `src/bot3/utils.py` — добавить timestamp к URL загрузки в функции `download_bot_files()`:

| Строка | Изменение |
|--------|-----------|
| 231 | `url = f"{config.bot_url}/version.md?t={int(time.time())}"` |
| 248 | `url = f"{config.bot_url}/{filename}?t={int(time.time())}"` |
| 268 | `url = f"{config.bot_url}/core/{filename}?t={int(time.time())}"` |
| 283 | `url = f"{config.bot_url}/init/{filename}?t={int(time.time())}"` |

Также добавить `import time` в начало функции, если ещё не импортирован.
