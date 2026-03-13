# 🔄 Переход на форк bypass_keenetic

**Инструкция для пользователей оригинального бота (Ziwork/tas-unn)**

---

## 📋 Оглавление

- [Быстрый переход](#быстрый-переход-3-шага)
- [Полная переустановка](#полная-переустановка)
- [Проверка после перехода](#проверка-после-перехода)
- [Возврат на оригинальный бот](#возврат-на-оригинальный-бот)

---

## 🚀 Быстрый переход (3 шага)

**Рекомендуемый способ** — занимает 2-3 минуты.

### Шаг 1: Обновите bot_config.py

```bash
nano /opt/etc/bot/bot_config.py
```

Найдите строку (может быть в разных местах файла):
```python
base_url = "https://raw.githubusercontent.com/ziwork/bypass_keenetic/main"
# или
base_url = "https://raw.githubusercontent.com/tas-unn/bypass_keenetic/main"
```

Замените на:
```python
base_url = "https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main"
```

**Сохраните:** `Ctrl+O` → `Enter` → `Ctrl+X`

---

### Шаг 2: Перезапустите бота

```bash
/opt/etc/init.d/S99telegram_bot restart
```

---

### Шаг 3: Обновите через Telegram

1. Откройте бота в Telegram
2. Нажмите `⚙️ Сервис` → `🆕 Обновления`
3. Нажмите кнопку `🔄 Обновить`
4. Дождитесь завершения обновления (30-60 секунд)

**Готово!** Бот автоматически загрузит все файлы с вашего форка.

---

## 📦 Полная переустановка

**Если быстрый способ не сработал** или хотите чистую установку.

### 1. Сделайте бэкап настроек

```bash
# Сохраните токен и настройки
cat /opt/etc/bot/.env > /tmp/backup_env.txt
cat /tmp/backup_env.txt
```

📝 **Запишите или скопируйте значения:**
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_USERNAMES`
- `TELEGRAM_USER_IDS`
- `ROUTER_IP`

---

### 2. Удалите старую версию

**Через Telegram:**
- `📲 Установка и удаление` → `❌ Удаление`

**Или вручную:**
```bash
/opt/root/script.sh -remove
```

---

### 3. Скачайте новые файлы

```bash
# Скачайте bot_config.py
curl -o /opt/etc/bot/bot_config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/bot_config.py

# Скачайте script.sh
curl -o /opt/root/script.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/script.sh
chmod 755 /opt/root/script.sh

# Скачайте .env.example
curl -o /opt/etc/bot/.env.example https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/.env.example
```

---

### 4. Создайте .env файл

```bash
cp /opt/etc/bot/.env.example /opt/etc/bot/.env
nano /opt/etc/bot/.env
```

**Заполните параметры:**
```ini
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
TELEGRAM_USERNAMES=ваш_логин
TELEGRAM_USER_IDS=ваш_user_id
ROUTER_IP=192.168.1.1
```

**Сохраните:** `Ctrl+O` → `Enter` → `Ctrl+X`

**Установите права:**
```bash
chmod 600 /opt/etc/bot/.env
```

---

### 5. Запустите установку

**Через Telegram (рекомендуется):**
```bash
# Запустите бота
python3 /opt/etc/bot/main.py &
```

- Нажмите `/start`
- `📲 Установка и удаление` → `📲 Установка`

**Или вручную:**
```bash
/opt/root/script.sh -install
```

---

## ✅ Проверка после перехода

### 1. Проверьте версию бота

```bash
cat /opt/etc/bot/version.md
```

Должна быть актуальная версия (например, `3.5.50`).

---

### 2. Проверьте статус бота

```bash
/opt/etc/init.d/S99telegram_bot status
```

Должен показать, что бот запущен.

---

### 3. Проверьте логи

```bash
tail -20 /opt/etc/bot/error.log
```

Не должно быть ошибок.

---

### 4. Проверьте работу меню

1. Откройте бота в Telegram
2. Нажмите `/start`
3. Проверьте все меню:
   - `📑 Списки обхода`
   - `🔑 Ключи и мосты`
   - `⚙️ Сервис`
   - `📊 Статистика`

---

### 5. Проверьте загрузку файлов

```bash
ls -la /opt/etc/bot/
ls -la /opt/etc/bot/core/
```

**Должны быть:**
- `main.py`, `handlers.py`, `menu.py`, `utils.py`, `bot_config.py`
- Папка `core/` с 11 файлами
- `.env.example`

---

## 🔙 Возврат на оригинальный бот

Если нужно вернуться на оригинальный бот (Ziwork/tas-unn):

### 1. Измените bot_config.py

```bash
nano /opt/etc/bot/bot_config.py
```

Замените:
```python
# БЫЛО:
base_url = "https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main"

# СТАЛО:
base_url = "https://raw.githubusercontent.com/ziwork/bypass_keenetic/main"
```

### 2. Перезапустите и обновите

```bash
/opt/etc/init.d/S99telegram_bot restart
```

Затем через Telegram: `⚙️ Сервис` → `🆕 Обновления` → `🔄 Обновить`

---

## ❓ Частые вопросы

### Сохранятся ли мои настройки?

✅ **Да!** При обновлении через Telegram сохраняются:
- Файл `.env` (токен, user_id, настройки)
- Списки обхода (`/opt/etc/unblock/*.txt`)
- Конфигурация сервисов (Tor, VLESS, Trojan, Shadowsocks)

### Нужно ли создавать нового бота в @BotFather?

❌ **Нет!** Используйте тот же токен. Бот остаётся тем же, меняется только код.

### Что делать если бот не запускается после обновления?

1. Проверьте логи:
   ```bash
   tail -50 /opt/etc/bot/error.log
   ```

2. Проверьте `.env`:
   ```bash
   cat /opt/etc/bot/.env
   ```

3. Пересоздайте `.env`:
   ```bash
   cp /opt/etc/bot/.env.example /opt/etc/bot/.env
   nano /opt/etc/bot/.env
   ```

4. Перезапустите:
   ```bash
   /opt/etc/init.d/S99telegram_bot restart
   ```

### Можно ли обновляться без удаления?

✅ **Да!** Используйте **Быстрый переход** — это безопасно.

---

## 📞 Поддержка

Если возникли проблемы:

1. **Проверьте логи:** `/opt/etc/bot/error.log`
2. **Создайте Issue:** [GitHub Issues](https://github.com/royfincher25-source/bypass_keenetic/issues)
3. **Обсуждение:** [GitHub Discussions](https://github.com/royfincher25-source/bypass_keenetic/discussions)

---

## 📊 Сравнение версий

| Функция | Ziwork/tas-unn | Этот форк |
|---------|----------------|-----------|
| Загрузка файлов при установке | ❌ | ✅ |
| Поддержка URL-safe base64 | ❌ | ✅ |
| .env.example в комплекте | ❌ | ✅ |
| Актуальная документация | ⚠️ | ✅ |
| Исправленные ошибки | ⚠️ | ✅ |

---

**Последнее обновление:** 13 марта 2026 г.  
**Версия инструкции:** 1.0
