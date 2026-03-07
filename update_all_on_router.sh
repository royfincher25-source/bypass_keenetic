#!/bin/sh
# =============================================================================
# ПОЛНОЕ ОБНОВЛЕНИЕ БОТА НА РОУТЕРЕ
# =============================================================================
# Этот скрипт обновляет все файлы бота на роутере Keenetic
# =============================================================================

echo "=============================================="
echo "  Полное обновление бота на роутере"
echo "=============================================="
echo ""

cd /opt/etc/bot

# 1. Остановка бота
echo "[1/7] Остановка бота..."
kill -9 $(pgrep -f "python3 /opt/etc/bot/main.py") 2>/dev/null
sleep 2
echo "      Бот остановлен"

# 2. Резервная копия
echo "[2/7] Создание резервной копии..."
BACKUP_DIR="/opt/root/bot_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /opt/etc/bot/* "$BACKUP_DIR/" 2>/dev/null
echo "      Бэкап: $BACKUP_DIR"

# 3. Обновление файлов bot3
echo "[3/7] Обновление файлов bot3..."
cd /opt/etc/bot

echo "      main.py..."
curl -L -o main.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/main.py

echo "      handlers.py..."
curl -L -o handlers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/handlers.py

echo "      utils.py..."
curl -L -o utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/utils.py

echo "      bot_config.py..."
curl -L -o bot_config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/bot_config.py

echo "      menu.py..."
curl -L -o menu.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/menu.py

# 4. Обновление core модуля
echo "[4/7] Обновление core модуля..."
cd /opt/etc/bot/core

echo "      config.py..."
curl -L -o config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/core/config.py

echo "      env_parser.py..."
curl -L -o env_parser.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/core/env_parser.py

# 5. Очистка кэша
echo "[5/7] Очистка кэша Python..."
cd /opt/etc/bot
rm -rf __pycache__ core/__pycache__
find /opt/etc/bot -name "*.pyc" -delete 2>/dev/null
echo "      Кэш очищен"

# 6. Проверка файлов
echo "[6/7] Проверка размеров файлов..."
echo "      bot3:"
ls -la /opt/etc/bot/*.py 2>/dev/null | awk '{print "          " $NF ": " $5 " байт"}'
echo "      core:"
ls -la /opt/etc/bot/core/*.py 2>/dev/null | awk '{print "          " $NF ": " $5 " байт"}'

# 7. Запуск бота
echo "[7/7] Запуск бота..."
/opt/etc/init.d/S99telegram_bot start
sleep 5

# Результат
echo ""
echo "=============================================="
echo "  Результат"
echo "=============================================="
echo ""

echo "Процессы Python:"
ps | grep python | grep -v grep

echo ""
echo "Последние логи (без ошибок токена):"
tail -50 /opt/etc/bot/error.log | grep -v "TELEGRAM_BOT_TOKEN" | grep -v "Проверьте .env" | tail -20

echo ""
echo "=============================================="
if ps | grep python | grep -v grep | grep -q "python3 /opt/etc/bot/main.py"; then
    echo "  ✅ БОТ ЗАПУЩЕН И РАБОТАЕТ!"
    echo ""
    echo "  Проверьте бота в Telegram:"
    echo "  1. Откройте бота"
    echo "  2. Отправьте /start"
    echo "  3. Бот должен ответить"
else
    echo "  ⚠️ БОТ НЕ ЗАПУЩЕН"
    echo ""
    echo "  Проверьте логи:"
    echo "  tail -f /opt/etc/bot/error.log"
fi
echo "=============================================="
echo ""
echo "Резервная копия сохранена в: $BACKUP_DIR"
echo ""
