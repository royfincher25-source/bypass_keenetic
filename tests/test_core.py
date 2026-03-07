# =============================================================================
# UNIT-ТЕСТЫ ДЛЯ CORE МОДУЛЯ
# =============================================================================
# Тестирование: Config, Validators, Parsers, Services
# =============================================================================

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Добавляем корень проекта в path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.config import Config
from core.validators import validate_domain, validate_ip, validate_port, validate_bypass_entry
from core.parsers import parse_vless_key, parse_trojan_key, parse_shadowsocks_key
from core.services import TorService, XrayService, ShadowsocksService, ServiceManager


# =============================================================================
# ТЕСТЫ CONFIG
# =============================================================================

class TestConfig:
    """Тесты для класса Config"""
    
    def test_config_from_env(self, monkeypatch):
        """Тест загрузки из переменных окружения"""
        monkeypatch.setenv('TELEGRAM_BOT_TOKEN', '123456789:ABCdefGHIjklMNOpqrsTUVwxyz')
        monkeypatch.setenv('TELEGRAM_USERNAMES', 'user1,user2')
        monkeypatch.setenv('MAX_RESTARTS', '10')
        
        config = Config()
        
        assert config.token == '123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
        assert config.usernames == ['user1', 'user2']
        assert config.max_restarts == 10
    
    def test_config_invalid_token(self, monkeypatch):
        """Тест с невалидным токеном"""
        monkeypatch.setenv('TELEGRAM_BOT_TOKEN', 'invalid')
        monkeypatch.setenv('TELEGRAM_USERNAMES', 'user')
        
        with pytest.raises(ValueError):
            Config()
    
    def test_config_empty_usernames(self, monkeypatch):
        """Тест с пустыми usernames"""
        monkeypatch.setenv('TELEGRAM_BOT_TOKEN', '123456789:ABCdefGHIjklMNOpqrsTUVwxyz')
        monkeypatch.setenv('TELEGRAM_USERNAMES', '')
        
        config = Config()
        
        assert config.usernames == []
    
    def test_config_to_dict(self, monkeypatch):
        """Тест конвертации в словарь"""
        monkeypatch.setenv('TELEGRAM_BOT_TOKEN', '123456789:ABCdefGHIjklMNOpqrsTUVwxyz')
        monkeypatch.setenv('TELEGRAM_USERNAMES', 'user')
        
        config = Config()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'token' in config_dict
        assert 'usernames' in config_dict


# =============================================================================
# ТЕСТЫ VALIDATORS
# =============================================================================

class TestValidators:
    """Тесты для валидаторов"""
    
    def test_validate_domain_valid(self):
        """Тест валидных доменов"""
        assert validate_domain('example.com') is True
        assert validate_domain('test.example.com') is True
        assert validate_domain('sub-domain.example.co.uk') is True
    
    def test_validate_domain_invalid(self):
        """Тест невалидных доменов"""
        assert validate_domain('') is False
        assert validate_domain('not_a_domain') is False
        assert validate_domain('-example.com') is False
    
    def test_validate_ip_valid(self):
        """Тест валидных IP"""
        assert validate_ip('192.168.1.1') is True
        assert validate_ip('10.0.0.1') is True
        assert validate_ip('8.8.8.8') is True
    
    def test_validate_ip_invalid(self):
        """Тест невалидных IP"""
        assert validate_ip('') is False
        assert validate_ip('256.1.1.1') is False
        assert validate_ip('1.1.1') is False
    
    def test_validate_port_valid(self):
        """Тест валидных портов"""
        assert validate_port(80) is True
        assert validate_port(443) is True
        assert validate_port('8080') is True
    
    def test_validate_port_invalid(self):
        """Тест невалидных портов"""
        assert validate_port(0) is False
        assert validate_port(65536) is False
        assert validate_port('abc') is False
    
    def test_validate_bypass_entry_domain(self):
        """Тест валидации домена в bypass entry"""
        assert validate_bypass_entry('example.com') is True
    
    def test_validate_bypass_entry_ip(self):
        """Тест валидации IP в bypass entry"""
        assert validate_bypass_entry('192.168.1.1') is True
    
    def test_validate_bypass_entry_cidr(self):
        """Тест валидации CIDR в bypass entry"""
        assert validate_bypass_entry('192.168.1.0/24') is True


# =============================================================================
# ТЕСТЫ PARSERS (используют тесты из test_parsers.py)
# =============================================================================

class TestCoreParsers:
    """Тесты для парсеров из core модуля"""
    
    def test_parse_vless_key(self, sample_vless_key):
        """Тест парсинга VLESS ключа"""
        result = parse_vless_key(sample_vless_key)
        assert 'address' in result
        assert 'port' in result
        assert 'id' in result
    
    def test_parse_trojan_key(self, sample_trojan_key):
        """Тест парсинга Trojan ключа"""
        result = parse_trojan_key(sample_trojan_key)
        assert 'pw' in result
        assert 'host' in result
        assert 'port' in result
    
    def test_parse_shadowsocks_key(self, sample_shadowsocks_key):
        """Тест парсинга Shadowsocks ключа"""
        result = parse_shadowsocks_key(sample_shadowsocks_key)
        assert 'server' in result
        assert 'port' in result
        assert 'method' in result


# =============================================================================
# ТЕСТЫ SERVICES
# =============================================================================

class TestServices:
    """Тесты для сервисов"""
    
    def test_tor_service_init(self):
        """Тест инициализации TorService"""
        service = TorService()
        assert service.name == 'Tor'
    
    def test_xray_service_init(self):
        """Тест инициализации XrayService"""
        service = XrayService()
        assert service.name == 'Xray'
    
    def test_shadowsocks_service_init(self):
        """Тест инициализации ShadowsocksService"""
        service = ShadowsocksService()
        assert service.name == 'Shadowsocks'
    
    def test_service_manager_register(self):
        """Тест регистрации сервиса в ServiceManager"""
        manager = ServiceManager()
        service = TorService()
        
        manager.register(service)
        
        assert 'Tor' in manager.services
    
    def test_service_manager_restart_all(self, mock_subprocess_run):
        """Тест перезапуска всех сервисов"""
        manager = ServiceManager()
        manager.register(TorService())
        manager.register(XrayService())
        
        results = manager.restart_all()
        
        assert len(results) == 2
        assert all(isinstance(r, tuple) and len(r) == 3 for r in results)
