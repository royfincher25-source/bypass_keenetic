#!/bin/sh
# Временный скрипт для обновления core модуля

cd /opt/etc/bot/core

# Удаляем старые файлы
rm -f config.py env_parser.py

# Создаём config.py напрямую
cat > config.py << 'CONFIGEOF'
# =============================================================================
# CORE CONFIG - ОПТИМИЗИРОВАННАЯ КОНФИГУРАЦИЯ
# =============================================================================

import os
import sys
from .env_parser import env, get_env, get_env_int

class Config:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, env_path=None):
        if Config._initialized:
            return
        
        if env_path is None:
            env_path = '/opt/etc/bot/.env'
        
        env.load(env_path)
        
        self._token = get_env('TELEGRAM_BOT_TOKEN', '')
        self._usernames_str = get_env('TELEGRAM_USERNAMES', '')
        self._usernames = None
        
        self.max_restarts = get_env_int('MAX_RESTARTS', 5)
        self.restart_delay = get_env_int('RESTART_DELAY', 60)
        self.router_ip = get_env('ROUTER_IP', '192.168.1.1')
        
        self.localport_sh = get_env_int('LOCALPORT_SH', 1082)
        self.dnsport_tor = get_env_int('DNSPORT_TOR', 9053)
        self.localport_tor = get_env_int('LOCALPORT_TOR', 9141)
        self.localport_vless = get_env_int('LOCALPORT_VLESS', 10810)
        self.localport_trojan = get_env_int('LOCALPORT_TROJAN', 10829)
        self.dnsovertlsport = get_env_int('DNSOVER_TLS_PORT', 40500)
        self.dnsoverhttpsport = get_env_int('DNSOVER_HTTPS_PORT', 40508)
        self.backup_max_size_mb = get_env_int('BACKUP_MAX_SIZE_MB', 45)
        
        Config._initialized = True
    
    @property
    def token(self):
        return self._token
    
    @property
    def usernames(self):
        if self._usernames is None:
            if self._usernames_str:
                self._usernames = [u.strip() for u in self._usernames_str.split(',') if u.strip()]
            else:
                self._usernames = []
        return self._usernames
    
    def validate(self):
        if not self._token or ':' not in self._token or len(self._token) < 10:
            return False, "TELEGRAM_BOT_TOKEN не указан или имеет неверный формат"
        return True, None
    
    @property
    def is_valid(self):
        valid, _ = self.validate()
        return valid

config = Config()
CONFIGEOF

# Создаём env_parser.py напрямую
cat > env_parser.py << 'ENVEOF'
import os
import re

def parse_env_line(line):
    line = line.strip()
    if not line or line.startswith('#'):
        return None, None
    match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$', line)
    if not match:
        return None, None
    key = match.group(1)
    value = match.group(2)
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    return key, value

def load_env_file(filepath):
    env_vars = {}
    if filepath is None:
        filepath = '/opt/etc/bot/.env'
    try:
        with open(filepath, 'r') as f:
            for line in f:
                key, value = parse_env_line(line)
                if key is not None:
                    env_vars[key] = value
    except:
        pass
    return env_vars

def load_env(filepath=None):
    if filepath is None:
        filepath = '/opt/etc/bot/.env'
    env_vars = load_env_file(filepath)
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    return env_vars

def get_env(key, default=None):
    return os.environ.get(key, default)

def get_env_int(key, default=0):
    try:
        return int(os.environ.get(key, default))
    except:
        return default

class EnvConfig:
    _instance = None
    _cache = {}
    _loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load(self, filepath=None):
        if not self._loaded:
            if filepath is None:
                filepath = '/opt/etc/bot/.env'
            self._cache = load_env_file(filepath)
            self._loaded = True
        return self._cache
    
    def get(self, key, default=None):
        if not self._loaded:
            self.load()
        return self._cache.get(key, os.environ.get(key, default))
    
    def get_int(self, key, default=0):
        if not self._loaded:
            self.load()
        value = self._cache.get(key, os.environ.get(key))
        try:
            return int(value) if value else default
        except:
            return default
    
    def clear_cache(self):
        self._cache = {}
        self._loaded = False

env = EnvConfig()
ENVEOF

echo "Файлы обновлены!"
ls -la config.py env_parser.py

# Перезапуск бота
cd /opt/etc/bot
/opt/etc/init.d/S99telegram_bot restart
sleep 2
ps | grep python
