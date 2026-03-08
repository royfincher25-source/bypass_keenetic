# Инструкция по обновлению бота

> **Дата:** 2026-03-08  
> **Версия:** после оптимизации памяти

---

## 📋 Что изменилось

### Оптимизация памяти
- **До:** 30.0 MB
- **После:** ~22-24 MB (экономия ~6-8 MB)

### Новые функции
- ✅ Команда `/update` для ручного обновления
- ✅ Улучшенный перезапуск бота после обновления
- ✅ LRU eviction в кэше (MAX_SIZE=100)
- ✅ Периодическая очистка памяти (каждые 100 итераций)
- ✅ Lazy инициализация Menu объектов
- ✅ Оптимизированные замыкания через HandlerState

---

## 🔄 Способы обновления

### Способ 1: Через Telegram бота (рекомендуется)

#### Шаг 1: Откройте меню обновлений
1. Запустите бота в Telegram
2. Нажмите `⚙️ Сервис`
3. Нажмите `🆕 Обновления`

#### Шаг 2: Запустите обновление
- Нажмите кнопку `🆕 Обновить`

**ИЛИ** отправьте команду:
```
/update
```

#### Шаг 3: Дождитесь завершения
Бот автоматически:
1. Скачает обновлённые файлы (`handlers.py`, `menu.py`, `utils.py`, `main.py`)
2. Скачает обновлённый `script.sh`
3. Выполнит установку
4. Перезапустится с новой версией

**Время обновления:** ~30-60 секунд

---

### Способ 2: Через SSH (альтернативный)

#### Шаг 1: Подключитесь к роутеру
```bash
ssh admin@192.168.1.1
# или
ssh root@192.168.1.1
```

#### Шаг 2: Перейдите в директорию бота
```bash
cd /opt/etc/bot
```

#### Шаг 3: Скачайте обновлённые файлы
```bash
# Скачать файлы бота
curl -s -o handlers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/handlers.py
curl -s -o menu.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/menu.py
curl -s -o utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/utils.py
curl -s -o main.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/main.py

# Скачать скрипт обновления
curl -s -o /opt/root/script.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/script.sh
chmod +x /opt/root/script.sh
```

#### Шаг 4: Перезапустите бота
```bash
/opt/etc/init.d/S99telegram_bot restart
```

---

### Способ 3: Полное обновление через script.sh

#### Шаг 1: Подключитесь к роутеру
```bash
ssh admin@192.168.1.1
```

#### Шаг 2: Запустите скрипт обновления
```bash
/opt/root/script.sh -update
```

#### Шаг 3: Перезапустите бота
```bash
/opt/etc/init.d/S99telegram_bot restart
```

---

## ✅ Проверка обновления

### 1. Проверьте версию бота
```bash
cat /opt/etc/bot/version.md
```

### 2. Проверьте потребление памяти

**Через бота:**
- Отправьте команду `/stats`

**Через SSH:**
```bash
# Найти PID бота
ps aux | grep python3 | grep main.py

# Проверить память (замените <PID> на актуальный)
cat /proc/<PID>/status | grep VmRSS
```

**Ожидаемый результат:**
```
VmRSS:     ~22000 kB  (22-24 MB)
```

### 3. Проверьте логи
```bash
tail -20 /opt/etc/bot/error.log
```

**Признаки успешного обновления:**
- ✅ Нет ошибок Python
- ✅ Бот запустился
- ✅ Команда `/stats` работает
- ✅ Потребление памяти ~22-24 MB

---

## 🔧 Возможные проблемы

### Проблема 1: Бот не запускается после обновления

**Решение:**
```bash
# Проверьте синтаксис Python
python3 -m py_compile /opt/etc/bot/main.py
python3 -m py_compile /opt/etc/bot/handlers.py

# Проверьте логи
tail -50 /opt/etc/bot/error.log

# Попробуйте запустить вручную
python3 /opt/etc/bot/main.py
```

### Проблема 2: Потребление памяти не снизилось

**Возможные причины:**
1. Бот не был перезапущен после обновления
2. Старый процесс остался в памяти

**Решение:**
```bash
# Найти все процессы бота
ps aux | grep python3 | grep main.py

# Убить все процессы бота
pkill -f "python3 /opt/etc/bot/main.py"

# Запустить заново
/opt/etc/init.d/S99telegram_bot start
```

### Проблема 3: Ошибка "Bot is already running"

**Решение:**
```bash
# Остановить бота
/opt/etc/init.d/S99telegram_bot stop

# Проверить, что процесс остановлен
ps aux | grep python3 | grep main.py

# Запустить заново
/opt/etc/init.d/S99telegram_bot start
```

### Проблема 4: Команда `/update` не работает

**Возможные причины:**
1. Обновление ещё не применено (старая версия)
2. Пользователь не авторизован

**Решение:**
- Используйте меню: `⚙️ Сервис` → `🆕 Обновления` → `🆕 Обновить`
- Или обновите через SSH (Способ 2)

---

## 📊 Сравнение до и после

| Параметр | До оптимизации | После оптимизации |
|----------|----------------|-------------------|
| **Потребление RAM** | 30.0 MB | ~22-24 MB |
| **Кэш** | Неограниченный | MAX_SIZE=100 + LRU |
| **HTTP pool** | 5 соединений | 2 соединения |
| **Menu объекты** | При старте | Lazy инициализация |
| **Очистка памяти** | Нет | Каждые 100 итераций |
| **Перезапуск** | Через service_script | Прямой запуск |

---

## 📝 Чек-лист обновления

- [ ] Скачаны обновлённые файлы (через бота или SSH)
- [ ] Бот перезапущен
- [ ] Проверена версия файлов
- [ ] Проверено потребление памяти (~22-24 MB)
- [ ] Проверены логи (нет ошибок)
- [ ] Проверена работа команд (`/start`, `/stats`, `/update`)
- [ ] Проверено меню бота

---

## 🔗 Ссылки

- [GitHub репозиторий](https://github.com/royfincher25-source/bypass_keenetic)
- [План оптимизации](docs/plans/2026-03-08-bot-memory-optimization.md)
- [Changelog](CHANGELOG.md)

---

**Вопросы и поддержка:** Создайте issue в GitHub репозитории.
