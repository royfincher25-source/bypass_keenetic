#!/bin/sh
# Скрипт для отладки и исправления .env проблемы

cd /opt/etc/bot

echo "=== 1. Проверка .env файла ==="
cat /opt/etc/bot/.env
echo ""

echo "=== 2. Тест чтения env_parser ==="
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/opt/etc/bot')

print("Проверка load_env_file:")
from core.env_parser import load_env_file
result = load_env_file('/opt/etc/bot/.env')
print('Result:', result)
print('Keys:', list(result.keys()))
print('Token:', result.get('TELEGRAM_BOT_TOKEN', 'NOT FOUND'))
PYEOF

echo ""
echo "=== 3. Исправление env_parser.py ==="

# Создаём упрощённую версию
cat > /opt/etc/bot/core/env_parser.py << 'ENVEOF'
import os, re

def load_env_file(filepath):
    env_vars = {}
    if filepath is None: filepath = '/opt/etc/bot/.env'
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                if '=' not in line: continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if value.startswith('"') and value.endswith('"'): value = value[1:-1]
                if value.startswith("'") and value.endswith("'"): value = value[1:-1]
                env_vars[key] = value
    except Exception as e:
        print(f'Error loading env: {e}')
    return env_vars

def load_env(filepath=None):
    if filepath is None: filepath = '/opt/etc/bot/.env'
    env_vars = load_env_file(filepath)
    for key, value in env_vars.items():
        if key not in os.environ: os.environ[key] = value
    return env_vars

def get_env(key, default=None): return os.environ.get(key, default)
def get_env_int(key, default=0):
    try: return int(os.environ.get(key, default))
    except: return default

class EnvConfig:
    _instance = None
    _cache = {}
    _loaded = False
    def __new__(cls):
        if cls._instance is None: cls._instance = super().__new__(cls)
        return cls._instance
    def load(self, filepath=None):
        if not self._loaded:
            if filepath is None: filepath = '/opt/etc/bot/.env'
            self._cache = load_env_file(filepath)
            self._loaded = True
        return self._cache
    def get(self, key, default=None):
        if not self._loaded: self.load()
        return self._cache.get(key, os.environ.get(key, default))
    def get_int(self, key, default=0):
        if not self._loaded: self.load()
        value = self._cache.get(key, os.environ.get(key))
        try: return int(value) if value else default
        except: return default

env = EnvConfig()

# Загружаем сразу при импорте
env_vars = load_env('/opt/etc/bot/.env')
print('Loaded env:', env_vars)
print('Token:', env_vars.get('TELEGRAM_BOT_TOKEN', 'NOT FOUND'))
ENVEOF

echo "env_parser.py обновлён!"
ls -la /opt/etc/bot/core/env_parser.py

echo ""
echo "=== 4. Проверка после исправления ==="
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/opt/etc/bot')
from core.config import config
print('Token:', config.token)
print('Valid:', config.is_valid)
PYEOF

echo ""
echo "=== 5. Перезапуск бота ==="
/opt/etc/init.d/S99telegram_bot restart
sleep 3

echo ""
echo "=== 6. Проверка процесса ==="
ps | grep python

echo ""
echo "=== 7. Последние логи ==="
tail -10 /opt/etc/bot/error.log
