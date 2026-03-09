# 📝 Создание .env файла на роутере

## 🚀 Быстрый способ (1 команда)

```bash
# Скопируйте и вставьте целиком на роутер:
cat > /opt/etc/bot/.env << 'EOF'
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
TELEGRAM_USERNAMES=ваш_логин
ROUTER_IP=192.168.1.1
LOCALPORT_SH=1082
DNSPORT_TOR=9053
LOCALPORT_TOR=9141
LOCALPORT_VLESS=10810
LOCALPORT_TROJAN=10829
DNSOVER_TLS_PORT=40500
DNSOVER_HTTPS_PORT=40508
MAX_RESTARTS=5
RESTART_DELAY=60
BACKUP_MAX_SIZE_MB=45
EOF

# Установите права
chmod 600 /opt/etc/bot/.env

# Проверьте
cat /opt/etc/bot/.env
```

---

## 📤 Альтернативный способ (с компьютера)

### PowerShell

```powershell
# 1. Отредактируйте файл .env на компьютере
notepad H:\disk_e\dell\bypass_keenetic-main\.env

# 2. Скопируйте на роутер
scp H:\disk_e\dell\bypass_keenetic-main\.env root@192.168.1.1:/opt/etc/bot/.env

# 3. Проверьте
ssh root@192.168.1.1 "cat /opt/etc/bot/.env"
```

---

## ✏️ Заполните значения

### 1. TELEGRAM_BOT_TOKEN

Получите у [@BotFather](https://t.me/BotFather):

1. Откройте BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен (формат: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. TELEGRAM_USERNAMES

Ваш логин Telegram **без** `@`:

```ini
# Пример:
TELEGRAM_USERNAMES=ivanov

# Несколько пользователей:
TELEGRAM_USERNAMES=ivanov,petrov,sidorov
```

---

## ✅ Проверка

```bash
# Проверьте файл
cat /opt/etc/bot/.env

# Проверьте права
ls -la /opt/etc/bot/.env
# Должно быть: -rw------- (600)

# Запустите бота
/opt/etc/init.d/S99telegram_bot start

# Проверьте через 2 секунды
sleep 2
ps | grep python
```

---

## 📋 Шаблон для копирования

```ini
# Скопируйте и замените значения:
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_USERNAMES=your_username
ROUTER_IP=192.168.1.1
LOCALPORT_SH=1082
DNSPORT_TOR=9053
LOCALPORT_TOR=9141
LOCALPORT_VLESS=10810
LOCALPORT_TROJAN=10829
DNSOVER_TLS_PORT=40500
DNSOVER_HTTPS_PORT=40508
MAX_RESTARTS=5
RESTART_DELAY=60
BACKUP_MAX_SIZE_MB=45
```

---

**После создания .env — запустите бота!** 🚀
