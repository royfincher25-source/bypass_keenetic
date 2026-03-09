## Qwen Added Memories

### Git и синхронизация
- После каждого `git commit` и `git push` нужно проверять, что изменения действительно попали в удалённый репозиторий на GitHub через команду `git status` (должно быть "Your branch is up to date with 'origin/main'") или через веб-интерфейс GitHub.

### Обновление бота на роутере

**Способ 1: Через Telegram бота (рекомендуется)**
```
/update
```
Бот автоматически обновит все 22 файла:
- Основные файлы (6): main.py, handlers.py, utils.py, menu.py, version.md, bot_config.py
- Core модули (11): config.py, env_parser.py, http_client.py, logging.py, logging_async.py, parsers.py, services.py, validators.py, backup.py, handlers_shared.py, __init__.py
- Init скрипты (2): S99telegram_bot, S99unblock
- Дополнительные файлы (3): keensnap.sh, tor_template.torrc, 100-redirect.sh

**Способ 2: Через SSH**
```bash
cd /opt/etc/bot
curl -s -o version.md https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/version.md
curl -s -o handlers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/handlers.py
curl -s -o bot_config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/bot_config.py
curl -s -o utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/utils.py
curl -s -o main.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/main.py
curl -s -o menu.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/menu.py

# Core модули
mkdir -p core
curl -s -o core/config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/config.py
curl -s -o core/env_parser.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/env_parser.py
curl -s -o core/http_client.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/http_client.py
curl -s -o core/logging.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/logging.py
curl -s -o core/logging_async.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/logging_async.py
curl -s -o core/parsers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/parsers.py
curl -s -o core/services.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/services.py
curl -s -o core/validators.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/validators.py
curl -s -o core/backup.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/backup.py
curl -s -o core/handlers_shared.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/handlers_shared.py
curl -s -o core/__init__.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/__init__.py

# Init скрипты
curl -s -o S99telegram_bot https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/S99telegram_bot
curl -s -o S99unblock https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/S99unblock

# Перезапуск
/opt/etc/init.d/S99telegram_bot restart
```

**Проверка после обновления:**
```bash
cat /opt/etc/bot/version.md           # Проверка версии (должно быть: 3.5.3)
tail -20 /opt/etc/bot/error.log       # Проверка ошибок
ps aux | grep python3 | grep main.py  # Проверка потребления RAM (~22-24 MB)
```

### Версии и релизы

| Версия | Изменения | Дата |
|--------|-----------|------|
| **3.5.3** | ✅ Полное обновление всех файлов (22 файла) через /update<br>⚡ Оптимизация архивации бэкапов (3x быстрее)<br>🔧 Исправление URL во всех файлах | 2026-03-09 |
| **3.5.2** | 🔧 Обновлены все URL в документации и скриптах (/bot3/ → /src/bot3/) | 2026-03-09 |
| **3.5.1** | 🔧 Исправлены импорты в тестах и конфигурации<br>📁 Перемещение Python файлов в src/ | 2026-03-09 |
| **3.5.0** | 📁 Полная реорганизация структуры проекта (src/, deploy/, tools/) | 2026-03-09 |
| **3.4.2** | 📝 Реорганизация вспомогательных скриптов | 2026-03-09 |
| **3.4.1** | 🔧 fix: экспорт `is_authorized` в `bot_config` | 2026-03-09 |
| **3.4.0** | ⚡ perf: оптимизация памяти и архитектуры (~6-7 MB экономия) | 2026-03-09 |

**Правило:** После каждого значимого изменения увеличивать версию в `src/bot3/version.md` (semver: MAJOR.MINOR.PATCH)

### Структура проекта (актуальная)

```
bypass_keenetic/
├── src/                    # Python исходный код
│   ├── bot3/              # Основной бот
│   ├── botlight/          # Лёгкая версия
│   └── core/              # Общие модули
├── deploy/                 # Production файлы
│   ├── router/            # Скрипты для роутера
│   ├── backup/            # Бэкапы (KeenSnap)
│   ├── config/            # Конфигурации
│   └── lists/             # Списки обхода
├── tools/                  # Инструменты разработчика
├── docs/                   # Документация
│   ├── user/              # Для пользователей
│   ├── developer/         # Для разработчиков
│   ├── analysis/          # Аналитика
│   └── plans/             # Планы развития
├── tests/                  # Тесты
└── scripts/                # Вспомогательные скрипты
```

### Критические URL

**Актуальные пути (используются в коде):**
- Бот: `https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/`
- Core: `https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/`
- KeenSnap: `https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/deploy/backup/keensnap/`

**Устаревшие пути (НЕ использовать):**
- ❌ `/bot3/` → ✅ `/src/bot3/`
- ❌ `/core/` → ✅ `/src/core/`
- ❌ `/KeenSnap/` → ✅ `/deploy/backup/keensnap/`
