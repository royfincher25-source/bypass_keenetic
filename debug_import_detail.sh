#!/bin/sh
# =============================================================================
# ОТЛАДКА ИМПОРТА get_available_drives
# =============================================================================

echo "=============================================="
echo "  Отладка импорта функции"
echo "=============================================="
echo ""

cd /opt/etc/bot

# 1. Проверка наличия функции в файле
echo "[1/4] Проверка utils.py..."
if grep -q "def get_available_drives" /opt/etc/bot/utils.py; then
    echo "      ✅ Функция НАЙДЕНА в файле"
    grep -n "def get_available_drives" /opt/etc/bot/utils.py
else
    echo "      ❌ Функция НЕ НАЙДЕНА в файле"
fi

echo ""
echo "      Размер файла: $(ls -la /opt/etc/bot/utils.py | awk '{print $5}') байт"
echo "      Строк в файле: $(wc -l < /opt/etc/bot/utils.py)"

# 2. Проверка содержимого вокруг функции
echo ""
echo "[2/4] Содержимое вокруг строки 573:"
sed -n '570,580p' /opt/etc/bot/utils.py

# 3. Прямая проверка импорта
echo ""
echo "[3/4] Тест импорта Python:"
python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/etc/bot')

# Читаем файл напрямую
with open('/opt/etc/bot/utils.py', 'r') as f:
    content = f.read()
    
if 'def get_available_drives' in content:
    print("      Функция НАЙДЕНА в файле (через Python)")
else:
    print("      Функция НЕ НАЙДЕНА в файле (через Python)")

# Пробуем импортировать модуль
try:
    # Сначала загрузим env
    from core.env_parser import load_env
    load_env('/opt/etc/bot/.env')
    
    import utils
    print(f"      Модуль загружен: {utils}")
    funcs = [x for x in dir(utils) if not x.startswith('_') and callable(getattr(utils, x))]
    print(f"      Доступные функции (первые 15): {funcs[:15]}")
    
    if hasattr(utils, 'get_available_drives'):
        print("      ✅ get_available_drives: ЕСТЬ")
        print(f"      Результат: {utils.get_available_drives()}")
    else:
        print("      ❌ get_available_drives: НЕТ")
except Exception as e:
    print(f"      Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
EOF

# 4. Проверка импорта из handlers
echo ""
echo "[4/4] Тест импорта из handlers.py:"
python3 << 'EOF'
import sys
sys.path.insert(0, '/opt/etc/bot')

try:
    from core.env_parser import load_env
    load_env('/opt/etc/bot/.env')
    
    # Проверяем что импортирует handlers
    print("      Импорт из handlers.py:")
    exec("from utils import get_available_drives, log_error, clean_error_logs, check_available_port, download_script, parse_vless_key, parse_trojan_key, parse_shadowsocks_key, tor_config, shadowsocks_config, create_backup_with_params")
    print("      ✅ Все импорты успешны")
except ImportError as e:
    print(f"      ❌ ImportError: {e}")
except Exception as e:
    print(f"      ❌ Ошибка: {e}")
EOF

echo ""
echo "=============================================="
echo "  Завершено"
echo "=============================================="
