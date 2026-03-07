#!/bin/sh
# =============================================================================
# ПОЛНАЯ ОЧИСТКА И ПЕРЕЗАПУСК БОТА
# =============================================================================

echo "=============================================="
echo "  Полная очистка и перезапуск бота"
echo "=============================================="
echo ""

cd /opt/etc/bot

# 1. Остановка бота
echo "[1/5] Остановка бота..."
kill -9 $(pgrep -f "python3 /opt/etc/bot/main.py") 2>/dev/null
sleep 2
echo "      Бот остановлен"

# 2. Очистка кэша Python
echo "[2/5] Очистка кэша Python..."
rm -rf /opt/etc/bot/__pycache__
rm -rf /opt/etc/bot/core/__pycache__
find /opt/etc/bot -name "*.pyc" -delete 2>/dev/null
echo "      Кэш очищен"

# 3. Проверка файлов
echo "[3/5] Проверка файлов..."
echo "      utils.py: $(ls -la /opt/etc/bot/utils.py 2>/dev/null | awk '{print $5}') байт"
echo "      handlers.py: $(ls -la /opt/etc/bot/handlers.py 2>/dev/null | awk '{print $5}') байт"
echo "      main.py: $(ls -la /opt/etc/bot/main.py 2>/dev/null | awk '{print $5}') байт"
echo "      bot_config.py: $(ls -la /opt/etc/bot/bot_config.py 2>/dev/null | awk '{print $5}') байт"
echo "      core/config.py: $(ls -la /opt/etc/bot/core/config.py 2>/dev/null | awk '{print $5}') байт"
echo "      core/env_parser.py: $(ls -la /opt/etc/bot/core/env_parser.py 2>/dev/null | awk '{print $5}') байт"

# 4. Проверка .env
echo "[4/5] Проверка .env файла..."
if [ -f "/opt/etc/bot/.env" ]; then
    TOKEN_LINE=$(grep "^TELEGRAM_BOT_TOKEN=" /opt/etc/bot/.env | head -1)
    if [ -n "$TOKEN_LINE" ]; then
        echo "      .env найден"
        echo "      $TOKEN_LINE"
    else
        echo "      ⚠️ TELEGRAM_BOT_TOKEN не найден в .env"
    fi
else
    echo "      ⚠️ .env файл не найден"
fi

# 5. Запуск бота
echo "[5/5] Запуск бота..."
/opt/etc/init.d/S99telegram_bot start
sleep 5

# Проверка
echo ""
echo "=============================================="
echo "  Результат"
echo "=============================================="
echo ""

echo "Процессы Python:"
ps | grep python | grep -v grep

echo ""
echo "Последние логи (без ошибок токена):"
tail -50 /opt/etc/bot/error.log | grep -v "TELEGRAM_BOT_TOKEN" | grep -v "Проверьте .env"

echo ""
echo "=============================================="
echo "  Готово!"
echo "=============================================="
