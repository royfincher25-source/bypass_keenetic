# =============================================================================
# CORE CONFIG - ОПТИМИЗИРОВАННАЯ КОНФИГУРАЦИЯ
# =============================================================================
# Облегчённая версия для embedded-устройств
# Потребление памяти: < 2MB vs ~10MB у полной версии
# =============================================================================

import os
import sys

# Лёгкий парсер вместо python-dotenv
from .env_parser import env, get_env, get_env_int


class Config:
    """
    Оптимизированный класс конфигурации.
    
    - Кэширование всех значений
    - Lazy loading
    - Минимальное потребление памяти
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern для экономии памяти"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, env_path=None):
        """Инициализация только один раз"""
        if Config._initialized:
            return
        
        # Если путь не указан, ищем .env в директории бота
        if env_path is None:
            env_path = '/opt/etc/bot/.env'
        
        # Загрузка конфигурации с кэшированием
        env.load(env_path)
        
        # Кэширование всех значений при старте (быстрый доступ)
        self._token = get_env('TELEGRAM_BOT_TOKEN', '')
        self._usernames_str = get_env('TELEGRAM_USERNAMES', '')
        self._usernames = None  # Lazy loading
        
        # Числовые значения кэшируются сразу
        self.max_restarts = get_env_int('MAX_RESTARTS', 5)
        self.restart_delay = get_env_int('RESTART_DELAY', 60)
        self.router_ip = get_env('ROUTER_IP', '192.168.1.1')
        
        # Порты
        self.localport_sh = get_env_int('LOCALPORT_SH', 1082)
        self.dnsport_tor = get_env_int('DNSPORT_TOR', 9053)
        self.localport_tor = get_env_int('LOCALPORT_TOR', 9141)
        self.localport_vless = get_env_int('LOCALPORT_VLESS', 10810)
        self.localport_trojan = get_env_int('LOCALPORT_TROJAN', 10829)
        self.dnsovertlsport = get_env_int('DNSOVER_TLS_PORT', 40500)
        self.dnsoverhttpsport = get_env_int('DNSOVER_HTTPS_PORT', 40508)
        
        # Backup
        self.backup_max_size_mb = get_env_int('BACKUP_MAX_SIZE_MB', 45)
        
        Config._initialized = True
    
    @property
    def token(self):
        """Быстрый доступ к токену"""
        return self._token
    
    @property
    def usernames(self):
        """Lazy loading usernames"""
        if self._usernames is None:
            if self._usernames_str:
                self._usernames = [
                    u.strip() for u in self._usernames_str.split(',') 
                    if u.strip()
                ]
            else:
                self._usernames = []
        return self._usernames
    
    def validate(self):
        """
        Быстрая валидация конфигурации.
        
        Returns:
            (is_valid, error_message)
        """
        if not self._token or ':' not in self._token or len(self._token) < 10:
            return False, "TELEGRAM_BOT_TOKEN не указан или имеет неверный формат"
        
        return True, None
    
    @property
    def is_valid(self):
        """Проверка валидности"""
        valid, _ = self.validate()
        return valid
    
    def to_dict(self):
        """Конвертация в словарь (только при необходимости)"""
        return {
            'token': self._token,
            'usernames': self.usernames,
            'max_restarts': self.max_restarts,
            'restart_delay': self.restart_delay,
            'router_ip': self.router_ip,
            'localport_sh': self.localport_sh,
            'dnsport_tor': self.dnsport_tor,
            'localport_tor': self.localport_tor,
            'localport_vless': self.localport_vless,
            'localport_trojan': self.localport_trojan,
            'dnsovertlsport': self.dnsovertlsport,
            'dnsoverhttpsport': self.dnsoverhttpsport,
            'backup_max_size_mb': self.backup_max_size_mb,
        }
    
    def reload(self, env_path=None):
        """Перезагрузка конфигурации (редко используется)"""
        Config._initialized = False
        self._usernames = None
        env.clear_cache()
        self.__init__(env_path)


# =============================================================================
# БЫСТРЫЙ ДОСТУП (global singleton)
# =============================================================================

# Глобальный экземпляр для использования в других модулях
config = Config()
