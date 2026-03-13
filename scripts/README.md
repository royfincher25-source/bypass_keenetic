# 🛠️ Скрипты проекта

**Версия:** 3.5.51
**Дата:** 13 марта 2026 г.

---

## 📁 Структура папки scripts/

```
scripts/
├── deploy/              # Скрипты развёртывания и обновления
│   ├── create_archive.sh
│   ├── update_all_on_router.sh
│   ├── update_bot_on_router.sh
│   └── update_core_on_router.sh
│
├── debug/               # Отладочные скрипты
│   ├── check_config_load.sh
│   ├── clean_restart.sh
│   ├── debug_import.sh
│   ├── debug_import_detail.sh
│   └── final_check.sh
│
├── fixes/               # Скрипты исправления проблем
│   ├── fix_env_on_router.sh
│   └── fix_restart_button.sh
│
├── recovery/            # Скрипты восстановления
│   └── restore_bot.sh
│
└── test/                # Тестовые скрипты
    └── test_priority_3.sh
```

---

## 📋 Описание скриптов

### 🚀 Deploy (развёртывание и обновление)

| Скрипт | Описание | Использование |
|--------|----------|---------------|
| **create_archive.sh** | Создание архива конфигурации | Для бэкапа перед обновлением |
| **update_all_on_router.sh** | Полное обновление бота на роутере | Обновление всех компонентов |
| **update_bot_on_router.sh** | Обновление бота на роутере | Обновление только бота |
| **update_core_on_router.sh** | Обновление core модуля | Обновление общей библиотеки |

**Пример:**
```bash
# Обновить бота на роутере
cd /opt/etc/bot
curl -s -o update_bot_on_router.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/scripts/deploy/update_bot_on_router.sh
chmod +x update_bot_on_router.sh
./update_bot_on_router.sh
```

---

### 🐛 Debug (отладка)

| Скрипт | Описание | Использование |
|--------|----------|---------------|
| **check_config_load.sh** | Проверка загрузки конфигурации | Диагностика проблем .env |
| **clean_restart.sh** | Полная очистка и перезапуск бота | При зависаниях бота |
| **debug_import.sh** | Отладка импорта функций | При ошибках импорта |
| **debug_import_detail.sh** | Детальная отладка импорта | Глубокая диагностика |
| **final_check.sh** | Финальная проверка и запуск | После установки/обновления |

**Пример:**
```bash
# Перезапустить бота с очисткой
cd /opt/etc/bot
chmod +x /opt/etc/bot/scripts/debug/clean_restart.sh
./clean_restart.sh
```

---

### 🔧 Fixes (исправление проблем)

| Скрипт | Описание | Использование |
|--------|----------|---------------|
| **fix_env_on_router.sh** | Исправление проблем с .env | При ошибках конфигурации |
| **fix_restart_button.sh** | Исправление кнопки перезапуска | При неработающей кнопке |

**Пример:**
```bash
# Исправить .env на роутере
cd /opt/etc/bot
chmod +x /opt/etc/bot/scripts/fixes/fix_env_on_router.sh
./fix_env_on_router.sh
```

---

### 🚑 Recovery (восстановление)

| Скрипт | Описание | Использование |
|--------|----------|---------------|
| **restore_bot.sh** | Восстановление бота из бэкапа | После сбоя/удаления |

**Пример:**
```bash
# Восстановить бота из бэкапа
cd /opt/etc/bot
chmod +x /opt/etc/bot/scripts/recovery/restore_bot.sh
./restore_bot.sh
```

---

### 🧪 Test (тестирование)

| Скрипт | Описание | Использование |
|--------|----------|---------------|
| **test_priority_3.sh** | Тестирование HTTP Connection Pooling | Проверка оптимизаций |

**Пример:**
```bash
# Запустить тесты
cd /opt/etc/bot
chmod +x /opt/etc/bot/scripts/test/test_priority_3.sh
./test_priority_3.sh
```

---

## 📍 Production скрипты (в корне)

Эти скрипты **остаются в корне** проекта, так как используются напрямую на роутере:

| Скрипт | Описание |
|--------|----------|
| **100-ipset.sh** | Инициализация ipset множеств (загружается при старте) |
| **100-redirect.sh** | Настройка iptables правил для перенаправления трафика |
| **100-unblock-vpn.sh** | Обработка VPN подключений (KeenOS 3) |
| **100-unblock-vpn-v4.sh** | Обработка VPN подключений (KeenOS 4+) |
| **backup_config.sh** | Полное резервное копирование конфигурации |
| **cleanup_backups.sh** | Автоматическая очистка старых бэкапов |
| **unblock_dnsmasq.sh** | Генерация dnsmasq конфига для обхода |
| **unblock_ipset.sh** | Заполнение ipset множеств IP-адресами |
| **unblock_update.sh** | Принудительное обновление системы обхода |

---

## 📦 Скрипты установки (в подпапках ботов)

| Скрипт | Описание |
|--------|----------|
| **src/bot3/script.sh** | Главный установочный скрипт для bot3 |
| **deploy/backup/keensnap/keensnap.sh** | Скрипт создания бэкапов через Telegram бота |

---

## 🔗 Быстрый доступ

### Обновление на роутере

```bash
# 1. Скачать скрипт обновления
cd /opt/etc/bot
curl -s -O https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/scripts/deploy/update_bot_on_router.sh
chmod +x update_bot_on_router.sh

# 2. Запустить обновление
./update_bot_on_router.sh

# 3. Перезапустить бота
/opt/etc/init.d/S99telegram_bot restart
```

### Отладка проблем

```bash
# 1. Проверить загрузку конфигурации
./scripts/debug/check_config_load.sh

# 2. Перезапустить бота с очисткой
./scripts/debug/clean_restart.sh

# 3. Проверить логи
tail -50 /opt/etc/bot/error.log
```

### Исправление проблем

```bash
# Исправить .env
./scripts/fixes/fix_env_on_router.sh

# Исправить кнопку перезапуска
./scripts/fixes/fix_restart_button.sh
```

### Восстановление

```bash
# Восстановить бота из бэкапа
./scripts/recovery/restore_bot.sh
```

---

## ⚠️ Важные замечания

1. **Не удаляйте production скрипты** из корня — они критичны для работы
2. **Проверяйте зависимости** — некоторые скрипты ссылаются друг на друга
3. **Тестируйте в sandbox** — перед запуском на production роутере
4. **Делайте бэкап** — перед использованием скриптов обновления/восстановления

---

## 📊 Статистика

| Категория | Файлов | Назначение |
|-----------|--------|------------|
| 🚀 Deploy | 4 | Развёртывание и обновление |
| 🐛 Debug | 5 | Отладка и диагностика |
| 🔧 Fixes | 2 | Исправление проблем |
| 🚑 Recovery | 1 | Восстановление |
| 🧪 Test | 1 | Тестирование |
| 📍 Production (корень) | 9 | Критичные скрипты |
| **ИТОГО** | **22** | **Все скрипты проекта** |

---

**Поддержка:** Создайте issue в [GitHub репозитории](https://github.com/royfincher25-source/bypass_keenetic/issues)
