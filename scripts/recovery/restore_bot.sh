#!/bin/sh
# =============================================================================
# ФИНАЛЬНОЕ ВОССТАНОВЛЕНИЕ БОТА
# =============================================================================
# Этот скрипт полностью восстанавливает работу бота на роутере Keenetic
# =============================================================================

echo "=============================================="
echo "  Финальное восстановление бота"
echo "=============================================="
echo ""

cd /opt/etc/bot

# 1. Остановка бота
echo "[1/7] Остановка бота..."
kill -9 $(pgrep -f "python3 /opt/etc/bot/main.py") 2>/dev/null
sleep 2
echo "      Бот остановлен"

# 2. Полная очистка кэша
echo "[2/7] Очистка кэша Python..."
rm -rf /opt/etc/bot/__pycache__
rm -rf /opt/etc/bot/core/__pycache__
find /opt/etc/bot -name "*.pyc" -delete 2>/dev/null
echo "      Кэш очищен"

# 3. Проверка файлов
echo "[3/7] Проверка файлов..."
echo "      main.py: $(ls -la /opt/etc/bot/main.py 2>/dev/null | awk '{print $5}') байт"
echo "      handlers.py: $(ls -la /opt/etc/bot/handlers.py 2>/dev/null | awk '{print $5}') байт"
echo "      utils.py: $(ls -la /opt/etc/bot/utils.py 2>/dev/null | awk '{print $5}') байт"
echo "      bot_config.py: $(ls -la /opt/etc/bot/bot_config.py 2>/dev/null | awk '{print $5}') байт"

# 4. Проверка функции в utils.py
echo "[4/7] Проверка функции create_backup_with_params..."
if grep -q "def create_backup_with_params" /opt/etc/bot/utils.py; then
    echo "      ✅ Функция НАЙДЕНА"
else
    echo "      ❌ Функция НЕ НАЙДЕНА"
    echo "      Попробуем загрузить заново..."
    cd /opt/etc/bot
    curl -L -o utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/utils.py
fi

# 5. Проверка .env
echo "[5/7] Проверка .env файла..."
if [ -f "/opt/etc/bot/.env" ]; then
    if grep -q "^TELEGRAM_BOT_TOKEN=" /opt/etc/bot/.env; then
        echo "      ✅ .env найден и содержит TOKEN"
    else
        echo "      ⚠️ .env найден, но TOKEN отсутствует"
    fi
else
    echo "      ❌ .env файл не найден"
fi

# 6. Тест импорта
echo "[6/7] Тест импорта Python:"
python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/etc/bot')

try:
    from core.env_parser import load_env
    load_env('/opt/etc/bot/.env')
    
    from utils import create_backup_with_params, get_available_drives
    print("      ✅ Все импорты успешны")
    print(f"      Диски: {get_available_drives()}")
except ImportError as e:
    print(f"      ❌ ImportError: {e}")
except Exception as e:
    print(f"      ❌ Ошибка: {e}")
EOF

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
    echo "  Попробуйте вручную:"
    echo "  python3 /opt/etc/bot/main.py"
    echo ""
    echo "  И посмотрите ошибки:"
    echo "  tail -f /opt/etc/bot/error.log"
fi
echo "=============================================="
echo ""
