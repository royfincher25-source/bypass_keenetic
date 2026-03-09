# 📋 Инструкция по работе с логами

**Дата:** 9 марта 2026 г.  
**Версия бота:** 3.4.1  
**Файл лога:** `/opt/etc/bot/error.log`

---

## 📍 Расположение логов

| Лог | Путь | Описание |
|-----|------|----------|
| **error.log** | `/opt/etc/bot/error.log` | Ошибки бота |
| **backup.log** | `/opt/root/KeenSnap/backup.log` | Логи бэкапов |

---

## 🧹 Очистка логов

### Способ 1: Автоматическая очистка (при старте бота)

Бот автоматически очищает `error.log` при каждом запуске:

- Если файл > 512 KB → оставляет только **последние 50 строк**
- Если файл не существует → создаёт пустой

**Функция:** `clean_log()` в `bot3/utils.py`

---

### Способ 2: Ручная очистка через SSH

```bash
# Полная очистка (сохраняя файл)
> /opt/etc/bot/error.log

# Или через truncate
truncate -s 0 /opt/etc/bot/error.log

# Или удалить файл (будет создан заново при старте)
rm /opt/etc/bot/error.log
```

---

### Способ 3: Оставить последние N строк

```bash
# Оставить последние 100 строк
tail -100 /opt/etc/bot/error.log > /tmp/error.log.tmp
mv /tmp/error.log.tmp /opt/etc/bot/error.log

# Оставить последние 50 строк
tail -50 /opt/etc/bot/error.log > /tmp/error.log.tmp && mv /tmp/error.log.tmp /opt/etc/bot/error.log
```

---

### Способ 4: Через Telegram (планируется)

**Команда:** `/clearlog` (в разработке)

```python
@bot.message_handler(commands=['clearlog'])
def clear_log_command(message):
    if not check_authorization(message):
        bot.send_message(message.chat.id, '⚠️ Доступ запрещён!')
        return
    
    log_file = config.paths["error_log"]
    try:
        with open(log_file, 'w') as f:
            f.write('')  # Очистка файла
        bot.send_message(message.chat.id, '✅ Лог очищен')
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка: {str(e)}')
```

---

## 📊 Просмотр логов

### Быстрый просмотр

```bash
# Последние 20 строк
tail -20 /opt/etc/bot/error.log

# Последние 50 строк в реальном времени
tail -f -50 /opt/etc/bot/error.log

# Все ошибки за сегодня
grep "$(date +%Y-%m-%d)" /opt/etc/bot/error.log
```

---

### Поиск по логам

```bash
# Найти все ошибки AttributeError
grep "AttributeError" /opt/etc/bot/error.log

# Найти ошибки по дате
grep "2026-03-09" /opt/etc/bot/error.log

# Найти ошибки перезапуска
grep "Бот перезапущен\|Бот остановлен" /opt/etc/bot/error.log

# Посчитать количество ошибок
wc -l /opt/etc/bot/error.log
```

---

### Фильтрация по уровню

```bash
# Только ошибки (ERROR)
grep "ERROR\|❌" /opt/etc/bot/error.log

# Только предупреждения (WARNING)
grep "WARNING\|⚠️" /opt/etc/bot/error.log

# Только успешные операции (✅)
grep "✅" /opt/etc/bot/error.log
```

---

## 📈 Анализ логов

### Проверка размера лога

```bash
# Размер файла
ls -lh /opt/etc/bot/error.log

# Количество строк
wc -l /opt/etc/bot/error.log

# Последние изменения
stat /opt/etc/bot/error.log
```

---

### Частые ошибки и решения

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `AttributeError: module 'bot_config' has no attribute 'is_authorized'` | Устаревший `bot_config.py` | Обновить бота: `/update` |
| `Timeout expired` | Превышен таймаут операции | Проверить интернет/сеть |
| `Bot is already running` | Бот уже запущен | `pkill -f main.py` и перезапустить |
| `VmRSS: > 50 MB` | Утечка памяти | Перезапустить бота, проверить версию |

---

## 🔧 Настройка логирования

### Параметры в `bot3/utils.py`

```python
def clean_log(log_file):
    """Очистка лога (оптимизировано)"""
    if not os.path.exists(log_file):
        open(log_file, 'a').close()
        return

    file_size = os.path.getsize(log_file)
    max_size = 524288  # 512 KB
    
    if file_size > max_size:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        with open(log_file, 'w') as f:
            f.writelines(lines[-50:])  # Оставить 50 строк
```

---

### Изменение размера очистки

**По умолчанию:** 512 KB → 50 строк

**Изменить:**

```python
# bot3/utils.py:112-120
def clean_log(log_file):
    max_size = 1024 * 1024  # 1 MB вместо 512 KB
    keep_lines = 100        # 100 строк вместо 50
```

---

## 📁 Ротация логов (ручная)

### Создание архива старых логов

```bash
# Архивировать текущий лог
cd /opt/etc/bot
tar -czf error.log.$(date +%Y%m%d).tar.gz error.log

# Очистить текущий лог
> error.log

# Удалить архивы старше 30 дней
find /opt/etc/bot -name "error.log.*.tar.gz" -mtime +30 -delete
```

---

### Автоматическая ротация через cron

```bash
# Добавить в crontab
crontab -e

# Каждое воскресенье в 00:00
0 0 * * 0 /opt/etc/bot/rotate_log.sh
```

**Скрипт `/opt/etc/bot/rotate_log.sh`:**
```bash
#!/bin/bash
LOG_FILE="/opt/etc/bot/error.log"
ARCHIVE_DIR="/opt/root/logs"

mkdir -p "$ARCHIVE_DIR"
cp "$LOG_FILE" "$ARCHIVE_DIR/error.log.$(date +%Y%m%d_%H%M%S).txt"
> "$LOG_FILE"

# Удалить архивы старше 30 дней
find "$ARCHIVE_DIR" -name "error.log.*.txt" -mtime +30 -delete
```

---

## 🛠️ Диагностика проблем

### Бот не пишет в лог

```bash
# Проверить права на файл
ls -l /opt/etc/bot/error.log

# Проверить место на диске
df -h /opt

# Проверить процесс бота
ps aux | grep python3 | grep main.py

# Перезапустить бота
/opt/etc/init.d/S99telegram_bot restart
```

---

### Лог слишком большой

```bash
# Проверить размер
du -h /opt/etc/bot/error.log

# Быстрая очистка
truncate -s 0 /opt/etc/bot/error.log

# Или оставить последние 100 строк
tail -100 /opt/etc/bot/error.log > /tmp/tmp.log && mv /tmp/tmp.log /opt/etc/bot/error.log
```

---

### Ошибки после обновления

```bash
# Посмотреть последние ошибки
tail -50 /opt/etc/bot/error.log

# Найти конкретную ошибку
grep "Traceback" /opt/etc/bot/error.log

# Откатить на предыдущую версию
cd /opt/etc/bot
curl -s -o handlers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/3.4.0/bot3/handlers.py
/opt/etc/init.d/S99telegram_bot restart
```

---

## 📊 Мониторинг логов

### Проверка каждые 5 минут

```bash
# Скрипт monitor.sh
#!/bin/bash
LOG_FILE="/opt/etc/bot/error.log"
ERROR_COUNT=$(grep -c "ERROR\|Traceback" "$LOG_FILE")

if [ "$ERROR_COUNT" -gt 10 ]; then
    echo "⚠️ Много ошибок в логе: $ERROR_COUNT"
fi
```

---

### Отправка логов на email

```bash
# Добавить в crontab
crontab -e

# Каждое утро в 8:00 отправлять лог
0 8 * * * mail -s "Bot Log" admin@example.com < /opt/etc/bot/error.log
```

---

## ✅ Чек-лист обслуживания

### Ежедневно

- [ ] Проверить последние ошибки: `tail -20 /opt/etc/bot/error.log`
- [ ] Проверить размер лога: `ls -lh /opt/etc/bot/error.log`

### Еженедельно

- [ ] Очистить лог если > 512 KB
- [ ] Архивировать старые логи
- [ ] Проверить потребление RAM ботом

### Ежемесячно

- [ ] Удалить архивы старше 30 дней
- [ ] Проверить место на диске
- [ ] Обновить бота до последней версии

---

## 🔗 Ссылки

- [GitHub репозиторий](https://github.com/royfincher25-source/bypass_keenetic)
- [QWEN.md](QWEN.md) — инструкция по обновлению
- [CHANGELOG.md](CHANGELOG.md) — история изменений

---

**Поддержка:** Создайте issue в GitHub репозитории.
