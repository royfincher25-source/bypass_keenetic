#!/bin/sh
# Полное обновление бота на роутере

echo "=== Обновление всех файлов бота ==="

cd /opt/etc/bot

# Резервная копия
echo "Создание резервной копии..."
mkdir -p /opt/root/bot_backup_$(date +%Y%m%d_%H%M%S)
cp -r /opt/etc/bot/* /opt/root/bot_backup_*/ 2>/dev/null

# Обновление bot3 файлов
echo "Обновление main.py..."
curl -L -o main.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/main.py

echo "Обновление handlers.py..."
curl -L -o handlers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/handlers.py

echo "Обновление menu.py..."
curl -L -o menu.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/menu.py

echo "Обновление utils.py..."
curl -L -o utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/utils.py

echo "Обновление bot_config.py..."
curl -L -o bot_config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/bot_config.py

# Обновление core
echo "Обновление core модуля..."
cd /opt/etc/bot/core
curl -L -o config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/config.py
curl -L -o env_parser.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/core/env_parser.py

# Проверка размеров
echo ""
echo "=== Проверка размеров файлов ==="
ls -la /opt/etc/bot/*.py
ls -la /opt/etc/bot/core/*.py

# Перезапуск
echo ""
echo "=== Перезапуск бота ==="
cd /opt/etc/bot
/opt/etc/init.d/S99telegram_bot restart
sleep 5

# Проверка
echo ""
echo "=== Проверка процесса ==="
ps | grep python

echo ""
echo "=== Последние логи ==="
tail -50 /opt/etc/bot/error.log | grep -v "❌ ОШИБКА: TELEGRAM_BOT_TOKEN"
