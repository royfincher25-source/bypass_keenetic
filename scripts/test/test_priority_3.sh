#!/bin/sh
# =============================================================================
# ТЕСТИРОВАНИЕ ПРИОРИТЕТА 3.1: CONNECTION POOLING
# =============================================================================

echo "=============================================="
echo "  Тестирование HTTP Connection Pooling"
echo "=============================================="
echo ""

cd /opt/etc/bot

# 1. Проверка текущего процесса
echo "[1/5] Проверка текущего процесса..."
ps | grep python | grep -v grep
echo ""

# 2. Обновление файлов
echo "[2/5] Обновление файлов..."

# Обновление utils.py
echo "      Загрузка bot3/utils.py..."
curl -L -o utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/utils.py

# Обновление handlers.py
echo "      Загрузка bot3/handlers.py..."
curl -L -o handlers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/handlers.py

# Проверка размеров
echo ""
echo "      Размеры файлов:"
ls -la utils.py handlers.py | awk '{print "          " $NF ": " $5 " байт"}'
echo ""

# 3. Проверка кода
echo "[3/5] Проверка connection pooling..."
if grep -q "def get_http_session" utils.py; then
    echo "      ✅ get_http_session() найдена"
else
    echo "      ❌ get_http_session() НЕ найдена"
fi

if grep -q "from utils import get_http_session" handlers.py; then
    echo "      ✅ handlers.py использует сессию"
else
    echo "      ⚠️ handlers.py не использует сессию"
fi
echo ""

# 4. Очистка и перезапуск
echo "[4/5] Очистка кэша и перезапуск..."
rm -rf __pycache__ core/__pycache__
/opt/etc/bot/S99telegram_bot restart
sleep 5

# 5. Проверка
echo "[5/5] Проверка..."
echo ""
echo "Процессы Python:"
ps | grep python | grep -v grep

echo ""
echo "Потребление памяти:"
ps | grep python | grep -v grep | awk '{print "          " $5 " KB (" int($5/1024) " MB)"}'

echo ""
echo "Последние логи:"
tail -20 /opt/etc/bot/error.log | grep -v "TELEGRAM_BOT_TOKEN" | grep -v "Проверьте .env"

echo ""
echo "=============================================="
echo "  Тестирование завершено"
echo "=============================================="
echo ""
echo "Проверьте в Telegram:"
echo "1. Отправьте /start"
echo "2. Проверьте работу меню"
echo "3. Проверьте кнопку 'Перезапуск бота'"
echo ""
