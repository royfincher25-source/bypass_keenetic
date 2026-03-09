# 📚 ПОЛНАЯ ИНСТРУКЦИЯ ПО ОБНОВЛЕНИЮ БОТА НА ROUТЕРЕ

**Дата:** 8 марта 2026 г.  
**Проблема:** Файлы на роутере не обновляются через curl  
**Решение:** Использовать SCP или принудительное обновление

---

## 🔍 Диагностика

### Проверка текущих версий файлов

```bash
cd /opt/etc/bot
ls -la *.py
ls -la core/*.py
```

**Ожидаемые размеры:**

| Файл | Размер |
|------|--------|
| `main.py` | ~2200 байт |
| `handlers.py` | ~22800 байт |
| `utils.py` | ~26000 байт |
| `bot_config.py` | ~6000 байт |
| `menu.py` | ~5600 байт |
| `core/config.py` | ~5200 байт |
| `core/env_parser.py` | ~5800 байт |

---

## 📤 СПОСОБ 1: SCP (РЕКОМЕНДУЕТСЯ)

### Шаг 1: На компьютере (Windows PowerShell)

```powershell
# Перейдите в директорию проекта
cd H:\disk_e\dell\bypass_keenetic-main

# Скопируйте все файлы на роутер
scp bot3/main.py root@192.168.1.1:/opt/etc/bot/
scp bot3/handlers.py root@192.168.1.1:/opt/etc/bot/
scp bot3/utils.py root@192.168.1.1:/opt/etc/bot/
scp bot3/bot_config.py root@192.168.1.1:/opt/etc/bot/
scp bot3/menu.py root@192.168.1.1:/opt/etc/bot/
scp core/config.py root@192.168.1.1:/opt/etc/bot/core/
scp core/env_parser.py root@192.168.1.1:/opt/etc/bot/core/
```

### Шаг 2: На роутере

```bash
# Очистка кэша
rm -rf /opt/etc/bot/__pycache__
rm -rf /opt/etc/bot/core/__pycache__
find /opt/etc/bot -name "*.pyc" -delete

# Перезапуск бота
/opt/etc/init.d/S99telegram_bot restart
sleep 5

# Проверка
ps | grep python
tail -50 /opt/etc/bot/error.log
```

---

## 🌐 СПОСОБ 2: curl с принудительным обновлением

### На роутере:

```bash
cd /opt/etc/bot

# 1. Удаление старых файлов
rm -f main.py handlers.py utils.py bot_config.py menu.py
rm -f core/config.py core/env_parser.py

# 2. Загрузка новых файлов
curl -L --no-cache -o main.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/main.py
curl -L --no-cache -o handlers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/handlers.py
curl -L --no-cache -o utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/utils.py
curl -L --no-cache -o bot_config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/bot_config.py
curl -L --no-cache -o menu.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/menu.py

cd /opt/etc/bot/core
curl -L --no-cache -o config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/config.py
curl -L --no-cache -o env_parser.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/env_parser.py

# 3. Проверка размеров
cd /opt/etc/bot
ls -la *.py
ls -la core/*.py

# 4. Очистка кэша
rm -rf __pycache__ core/__pycache__

# 5. Запуск
/opt/etc/init.d/S99telegram_bot start
sleep 5

# 6. Проверка
ps | grep python
tail -50 /opt/etc/bot/error.log
```

---

## 📥 СПОСОБ 3: wget (альтернатива curl)

### На роутере:

```bash
cd /opt/etc/bot

# Удаление старых файлов
rm -f main.py handlers.py utils.py bot_config.py menu.py
rm -f core/config.py core/env_parser.py

# Загрузка через wget
wget -O main.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/main.py
wget -O handlers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/handlers.py
wget -O utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/utils.py
wget -O bot_config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/bot_config.py
wget -O menu.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/menu.py

cd /opt/etc/bot/core
wget -O config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/config.py
wget -O env_parser.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/env_parser.py

# Проверка
cd /opt/etc/bot
ls -la *.py
ls -la core/*.py

# Очистка и запуск
rm -rf __pycache__ core/__pycache__
/opt/etc/init.d/S99telegram_bot start
sleep 5

# Проверка
ps | grep python
tail -50 /opt/etc/bot/error.log
```

---

## 🧯 СПОСОБ 4: Автоматический скрипт

### Создание скрипта на роутере:

```bash
cat > /opt/root/update_bot.sh << 'SCRIPTEND'
#!/bin/sh
echo "=== Обновление бота ==="

cd /opt/etc/bot

# Остановка
kill -9 $(pgrep -f "python3 /opt/etc/bot/main.py") 2>/dev/null
sleep 2

# Бэкап
BACKUP_DIR="/opt/root/bot_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /opt/etc/bot/* "$BACKUP_DIR/"
echo "Бэкап: $BACKUP_DIR"

# Удаление старых файлов
rm -f main.py handlers.py utils.py bot_config.py menu.py
rm -f core/config.py core/env_parser.py

# Загрузка новых
curl -L --no-cache -o main.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/main.py
curl -L --no-cache -o handlers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/handlers.py
curl -L --no-cache -o utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/utils.py
curl -L --no-cache -o bot_config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/bot_config.py
curl -L --no-cache -o menu.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/menu.py

cd /opt/etc/bot/core
curl -L --no-cache -o config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/config.py
curl -L --no-cache -o env_parser.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/env_parser.py

# Очистка
cd /opt/etc/bot
rm -rf __pycache__ core/__pycache__

# Запуск
/opt/etc/init.d/S99telegram_bot start
sleep 5

# Проверка
echo ""
echo "=== Результат ==="
ps | grep python | grep -v grep
tail -50 /opt/etc/bot/error.log | grep -v "TELEGRAM_BOT_TOKEN" | grep -v "Проверьте .env" | tail -20
SCRIPTEND

chmod 755 /opt/root/update_bot.sh
sh /opt/root/update_bot.sh
```

---

## ✅ Проверка успешного обновления

### 1. Проверка размеров файлов

```bash
cd /opt/etc/bot
ls -la *.py core/*.py
```

**Ожидаемые размеры:**

```
-rw-r--r--  1 root root   2197 main.py
-rw-r--r--  1 root root  22805 handlers.py
-rw-r--r--  1 root root  26000 utils.py  ← Важно!
-rw-r--r--  1 root root   6015 bot_config.py
-rw-r--r--  1 root root   5620 menu.py
-rw-r--r--  1 root root   5231 core/config.py
-rw-r--r--  1 root root   5779 core/env_parser.py
```

### 2. Проверка процесса

```bash
ps | grep python
```

**Ожидаемый результат:**

```
12345 root     33972 R    python3 /opt/etc/bot/main.py
```

### 3. Проверка логов

```bash
tail -50 /opt/etc/bot/error.log
```

**Не должно быть ошибок импорта!**

---

## 🆘 Решение проблем

### Проблема 1: curl не обновляет файлы

**Решение:**

```bash
# Сначала удалите файлы
rm -f main.py handlers.py utils.py

# Затем загрузите заново
curl -L --no-cache -o main.py <URL>
```

### Проблема 2: ImportError после обновления

**Решение:**

```bash
# Полная очистка кэша
rm -rf __pycache__ core/__pycache__
find /opt/etc/bot -name "*.pyc" -delete

# Перезапуск
/opt/etc/init.d/S99telegram_bot restart
```

### Проблема 3: Бот не запускается

**Диагностика:**

```bash
# Проверка .env
cat /opt/etc/bot/.env

# Проверка токена
python3 -c "from core.config import config; print(config.token)"

# Запуск в режиме отладки
python3 /opt/etc/bot/main.py 2>&1 | head -30
```

---

## 📋 Чек-лист обновления

- [ ] Остановлен бот
- [ ] Создан бэкап
- [ ] Удалены старые файлы
- [ ] Загружены новые файлы
- [ ] Проверены размеры файлов
- [ ] Очищен кэш Python
- [ ] Запущен бот
- [ ] Проверен процесс
- [ ] Проверены логи
- [ ] Протестирован в Telegram

---

## 📞 Контакты и поддержка

**GitHub репозиторий:**  
https://github.com/royfincher25-source/bypass_keenetic

**Документация:**  
- `QUICK_ARCHIVE.md` — создание бэкапов
- `OPTIMIZATION_REPORT.md` — оптимизация
- `CREATE_ENV.md` — настройка .env

---

**Последнее обновление:** 8 марта 2026 г.  
**Версия бота:** 3.4.0-optimized
