#!/bin/sh
# =============================================================================
# ПРОВЕРКА ЗАГРУЗКИ КОНФИГУРАЦИИ
# =============================================================================

echo "=============================================="
echo "  Проверка загрузки конфигурации"
echo "=============================================="
echo ""

cd /opt/etc/bot

# 1. Проверка .env файла
echo "[1/5] Проверка .env файла:"
cat /opt/etc/bot/.env
echo ""

# 2. Проверка core/config.py
echo "[2/5] Проверка core/config.py:"
ls -la /opt/etc/bot/core/config.py
echo ""

# 3. Проверка core/env_parser.py
echo "[3/5] Проверка core/env_parser.py:"
ls -la /opt/etc/bot/core/env_parser.py
echo ""

# 4. Тест загрузки config
echo "[4/5] Тест загрузки конфигурации:"
python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/etc/bot')

print("=== Прямая загрузка env ===")
from core.env_parser import load_env
env_vars = load_env('/opt/etc/bot/.env')
print(f"Загружено переменных: {len(env_vars)}")
print(f"TOKEN: {env_vars.get('TELEGRAM_BOT_TOKEN', 'НЕ НАЙДЕН')[:20]}...")

print("")
print("=== Загрузка через core.config ===")
from core.config import config
print(f"Token: '{config.token}'")
print(f"Token length: {len(config.token) if config.token else 0}")
print(f"Has colon: {':' in config.token if config.token else False}")
print(f"Valid: {config.is_valid}")

print("")
print("=== Проверка bot_config ===")
import bot_config
print(f"bot_config.token: '{bot_config.token}'")
print(f"bot_config.token length: {len(bot_config.token) if bot_config.token else 0}")
EOF

# 5. Попытка запуска main.py
echo ""
echo "[5/5] Попытка запуска main.py:"
python3 /opt/etc/bot/main.py 2>&1 | head -20

echo ""
echo "=============================================="
echo "  Завершено"
echo "=============================================="
