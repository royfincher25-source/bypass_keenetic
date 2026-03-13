# 📚 Структура проекта

**Версия:** 3.5.46
**Дата:** 10 марта 2026 г.

---

## 🏗️ Общая архитектура

```
bypass_keenetic-main/
│
├── 📂 src/                           # ИСХОДНЫЙ КОД PYTHON
│   ├── bot3/                         # Основной бот (полная версия)
│   │   ├── main.py                   # Точка входа
│   │   ├── handlers.py               # Обработчики команд
│   │   ├── menu.py                   # Меню бота
│   │   ├── utils.py                  # Утилиты
│   │   ├── bot_config.py             # Конфигурация бота
│   │   ├── script.sh                 # Установочный скрипт
│   │   └── version.md                # Версия бота
│   │
│   ├── botlight/                     # Облегчённая версия бота
│   │   ├── main.py
│   │   ├── handlers.py
│   │   ├── menu.py
│   │   ├── utils.py
│   │   ├── bot_config.py
│   │   ├── script.sh
│   │   └── version.md
│   │
│   └── core/                         # Общая библиотека
│       ├── __init__.py               # Экспорт функций
│       ├── config.py                 # Конфигурация (lazy loading)
│       ├── env_parser.py             # Парсер .env файлов
│       ├── http_client.py            # HTTP client с connection pooling
│       ├── logging.py                # Базовое логирование
│       ├── logging_async.py          # Асинхронное логирование
│       ├── backup.py                 # Функции бэкапа
│       ├── parsers.py                # Парсеры ключей
│       └── handlers_shared.py        # Общие обработчики
│
├── 🚀 deploy/                        # PRODUCTION ФАЙЛЫ
│   ├── README.md                     # Документация по развёртыванию
│   │
│   ├── router/                       # Скрипты для роутера
│   │   ├── 100-ipset.sh              # Инициализация ipset
│   │   ├── 100-redirect.sh           # Настройка iptables
│   │   ├── 100-unblock-vpn.sh        # Обработка VPN (KeenOS 3)
│   │   ├── 100-unblock-vpn-v4.sh     # Обработка VPN (KeenOS 4+)
│   │   ├── unblock_dnsmasq.sh        # Генерация dnsmasq.conf
│   │   ├── unblock_ipset.sh          # Заполнение ipset IP (v3.5.46, 21 сек)
│   │   └── unblock_update.sh         # Принудительное обновление
│   │
│   ├── backup/                       # Скрипты бэкапа
│   │   ├── backup_config.sh          # Полное бэкапирование
│   │   ├── cleanup_backups.sh        # Очистка старых бэкапов
│   │   └── keensnap/
│   │       └── keensnap.sh           # Бэкап через Telegram
│   │
│   ├── config/                       # Шаблоны конфигурации
│   │   ├── crontab                   # Расписание задач
│   │   ├── dnsmasq.conf              # Конфигурация DNS
│   │   ├── shadowsocks_template.json # Шаблон Shadowsocks
│   │   ├── tor_template.torrc        # Шаблон Tor
│   │   ├── trojan_template.json      # Шаблон Trojan
│   │   └── vless_template.json       # Шаблон VLESS
│   │
│   └── lists/                        # Списки обхода
│       ├── unblocktor.txt            # Список для Tor
│       └── unblockvless.txt          # Список для VLESS
│
├── 🛠️ tools/                         # ИНСТРУМЕНТЫ РАЗРАБОТКИ
│   ├── README.md                     # Документация по инструментам
│   ├── check_config.py               # Проверка конфигурации
│   └── push_to_github.bat            # Быстрый пуш на GitHub
│
├── 📜 scripts/                       # ВСПОМОГАТЕЛЬНЫЕ СКРИПТЫ
│   ├── README.md                     # Документация по скриптам
│   ├── debug/                        # Отладочные скрипты
│   ├── deploy/                       # Скрипты развёртывания
│   │   └── DEPLOY_IPSET.md           # Развёртывание unblock_ipset.sh
│   ├── fixes/                        # Исправление проблем
│   ├── recovery/                     # Восстановление
│   └── test/                         # Тестирование
│       ├── router_check.sh           # Диагностика роутера
│       └── ipset_benchmark.sh        # Бенчмарк производительности
│
├── 📝 tests/                         # ТЕСТЫ
│   ├── conftest.py                   # Конфигурация pytest
│   ├── test_core.py                  # Тесты core модуля
│   ├── test_parsers.py               # Тесты парсеров
│   └── test_utils.py                 # Тесты утилит
│
├── 📚 docs/                          # ДОКУМЕНТАЦИЯ
│   ├── README.md                     # Навигация по документации
│   ├── user/                         # Пользовательская документация
│   ├── developer/                    # Документация разработчика
│   ├── analysis/                     # Аналитика
│   └── archive/                      # Исторические документы
│
├── 📄 Корневые файлы
│   ├── README.md                     # Главный файл проекта
│   ├── CHANGELOG.md                  # История изменений
│   ├── SETUP.md                      # Инструкция установки
│   ├── DEPLOYMENT.md                 # Развёртывание
│   │
│   ├── .env.example                  # Шаблон конфигурации
│   ├── .gitignore                    # Git игнор
│   ├── Makefile                      # Автоматизация
│   ├── pytest.ini                    # Конфигурация тестов
│   │
│   ├── requirements.txt              # Основные зависимости
│   ├── requirements-dev.txt          # Dev зависимости
│   ├── requirements-test.txt         # Test зависимости
│   └── LICENSE                       # Лицензия
│
└── .github/                          # GitHub конфигурация
    └── ISSUE_TEMPLATE/               # Шаблоны issues
```

---

## 📊 Статистика проекта

| Компонент | Файлов | Описание |
|-----------|--------|----------|
| **src/** | ~20 | Исходный код Python |
| **deploy/** | 18 | Production файлы |
| **tools/** | 2 | Инструменты разработки |
| **scripts/** | 13 | Вспомогательные скрипты |
| **tests/** | ~5 | Тесты |
| **docs/** | ~20 | Документация |
| **Корень** | ~15 | Основные файлы |
| **ИТОГО** | **~93** | **Всего файлов** |

---

## 🎯 Назначение компонентов

### src/ — Исходный код

**Python модули бота:**
- `bot3/` — полная версия бота (~30 MB RAM)
- `botlight/` — облегчённая версия (~15 MB RAM)
- `core/` — общая библиотека для обоих версий

**Использование:**
```python
# Импорты из bot3
from src.bot3.handlers import setup_handlers
from src.bot3.menu import get_menu_main

# Импорты из core
from src.core.config import config
from src.core.http_client import get_http_session
```

---

### deploy/ — Production файлы

**Файлы для развёртывания на роутере:**
- Скрипты инициализации (100-*.sh)
- Скрипты обновления (unblock_*.sh)
- Шаблоны конфигурации
- Списки обхода

**Использование:**
```bash
# Копирование на роутер
scp deploy/router/100-*.sh admin@192.168.1.1:/opt/etc/ndm/
scp deploy/config/dnsmasq.conf admin@192.168.1.1:/opt/etc/
```

---

### tools/ — Инструменты разработчика

**Утилиты для разработки:**
- `check_config.py` — проверка конфигурации
- `push_to_github.bat` — автоматизация git push

**Использование:**
```bash
# Проверка конфигурации
python3 tools/check_config.py

# Быстрый пуш (Windows)
tools\push_to_github.bat "Описание изменений"
```

---

### scripts/ — Вспомогательные скрипты

**Скрипты для различных задач:**
- `debug/` — отладка и диагностика
- `deploy/` — развёртывание и обновление
- `fixes/` — исправление проблем
- `recovery/` — восстановление
- `test/` — тестирование

**Использование:**
```bash
# Отладка
./scripts/debug/clean_restart.sh

# Обновление
./scripts/deploy/update_bot_on_router.sh
```

---

## 📋 Быстрый доступ

### Для пользователей

| Задача | Файл |
|--------|------|
| Установка | [README.md](README.md) или [SETUP.md](SETUP.md) |
| Обновление | Через Telegram бота (`⚙️ Сервис` → `🆕 Обновления`) |
| Бэкапы | [docs/user/BACKUP_INSTRUCTION.md](docs/user/BACKUP_INSTRUCTION.md) |
| Логи | [docs/user/LOGS_INSTRUCTION.md](docs/user/LOGS_INSTRUCTION.md) |
| Переход на форк | [docs/user/MIGRATION.md](docs/user/MIGRATION.md) |

### Для разработчиков

| Задача | Файл |
|--------|------|
| Документация | [docs/README.md](docs/README.md) |
| Развёртывание | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Тесты | [tests/](tests/) |
| Скрипты | [scripts/README.md](scripts/README.md) |
| Production файлы | [deploy/README.md](deploy/README.md) |

---

## 🔄 Поток развёртывания

```
1. Разработка (src/)
   ↓
2. Тестирование (tests/)
   ↓
3. Сборка (Makefile)
   ↓
4. Развёртывание (deploy/)
   ↓
5. Обновление на роутере (scripts/deploy/)
```

---

## ⚠️ Важные замечания

1. **Не редактируйте файлы в deploy/ напрямую на роутере**
   - Вносите изменения в локальные файлы
   - Копируйте через `scp`

2. **src/ содержит исходный код**
   - Не используйте `import bot3` из корня
   - Используйте `from src.bot3 import ...`

3. **tools/ для разработки**
   - Не копируйте на роутер
   - Используйте локально для отладки

4. **deploy/lists/ — пользовательские файлы**
   - Могут содержать чувствительные данные
   - Добавьте в `.gitignore` при необходимости

---

## 📈 Эволюция структуры

| Версия | Изменения |
|--------|-----------|
| **3.4.2** | ✅ Реорганизация скриптов и production файлов |
| **3.4.1** | ✅ Добавлена документация по логам |
| **3.4.0** | ✅ Реорганизация документации (docs/) |
| **3.3.x** | ✅ Базовая структура с bot3/botlight/core |

---

**Поддержка:** Создайте issue в [GitHub репозитории](https://github.com/royfincher25-source/bypass_keenetic/issues)
