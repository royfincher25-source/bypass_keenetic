#!/bin/sh
# =============================================================================
# ФИНАЛЬНАЯ ПРОВЕРКА И ЗАПУСК БОТА
# =============================================================================

echo "=============================================="
echo "  Финальная проверка и запуск бота"
echo "=============================================="
echo ""

cd /opt/etc/bot

# 1. Проверка файлов
echo "[1/6] Проверка файлов..."
echo "      utils.py: $(ls -la /opt/etc/bot/utils.py 2>/dev/null | awk '{print $5}') байт"
echo "      handlers.py: $(ls -la /opt/etc/bot/handlers.py 2>/dev/null | awk '{print $5}') байт"
echo "      main.py: $(ls -la /opt/etc/bot/main.py 2>/dev/null | awk '{print $5}') байт"

# 2. Проверка функции в utils.py
echo ""
echo "[2/6] Проверка функции get_available_drives..."
if grep -q "def get_available_drives" /opt/etc/bot/utils.py; then
    echo "      ✅ Функция НАЙДЕНА"
    grep -n "def get_available_drives" /opt/etc/bot/utils.py
else
    echo "      ❌ Функция НЕ НАЙДЕНА"
fi

# 3. Проверка .env
echo ""
echo "[3/6] Проверка .env файла..."
if [ -f "/opt/etc/bot/.env" ]; then
    grep "^TELEGRAM_BOT_TOKEN=" /opt/etc/bot/.env 2>/dev/null && echo "      ✅ TOKEN найден" || echo "      ❌ TOKEN не найден"
else
    echo "      ❌ .env файл не найден"
fi

# 4. Тест импорта с загрузкой env
echo ""
echo "[4/6] Тест импорта Python:"
python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/etc/bot')

# Сначала загрузим env
from core.env_parser import load_env
load_env('/opt/etc/bot/.env')

# Теперь импортируем
try:
    from utils import get_available_drives
    print("      ✅ SUCCESS: get_available_drives импортирована")
    drives = get_available_drives()
    print(f"      Диски: {drives}")
except ImportError as e:
    print(f"      ❌ ImportError: {e}")
except Exception as e:
    print(f"      ❌ Ошибка: {e}")
EOF

# 5. Очистка и перезапуск
echo ""
echo "[5/6] Очистка кэша и перезапуск..."
rm -rf __pycache__ core/__pycache__
kill -9 $(pgrep -f "python3 /opt/etc/bot/main.py") 2>/dev/null
sleep 2
/opt/etc/init.d/S99telegram_bot start
sleep 5

# 6. Проверка
echo ""
echo "[6/6] Проверка:"
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
else
    echo "  ⚠️ БОТ НЕ ЗАПУЩЕН - проверьте логи выше"
fi
echo "=============================================="
