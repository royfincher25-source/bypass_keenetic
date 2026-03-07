#!/bin/sh
# Скрипт для отладки импорта

cd /opt/etc/bot

echo "=== 1. Проверка .env файла ==="
cat /opt/etc/bot/.env
echo ""

echo "=== 2. Тест импорта ==="
python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/etc/bot')

# Сначала загрузим env
from core.env_parser import load_env
load_env('/opt/etc/bot/.env')

print("Env загружен")

# Теперь пробуем импортировать
try:
    from utils import get_available_drives
    print("SUCCESS: get_available_drives импортирована")
    print(f"Drives: {get_available_drives()}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Other error: {e}")
    import traceback
    traceback.print_exc()
EOF

echo ""
echo "=== 3. Прямой тест bot_config ==="
python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/etc/bot')

try:
    from core.config import config
    print(f"Token: {config.token}")
    print(f"Valid: {config.is_valid}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
EOF

echo ""
echo "=== 4. Перезапуск бота ==="
/opt/etc/init.d/S99telegram_bot restart
sleep 5

echo ""
echo "=== 5. Проверка процесса ==="
ps | grep python

echo ""
echo "=== 6. Последние логи (без ошибок токена) ==="
tail -50 /opt/etc/bot/error.log | grep -v "TELEGRAM_BOT_TOKEN"
