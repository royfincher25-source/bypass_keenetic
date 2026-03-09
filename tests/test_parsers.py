# =============================================================================
# UNIT-ТЕСТЫ ДЛЯ ПАРСЕРОВ КЛЮЧЕЙ
# =============================================================================
# Тестирование функций парсинга: parse_vless_key, parse_trojan_key, parse_shadowsocks_key
# =============================================================================

import pytest
import sys
from pathlib import Path

# Добавляем корень проекта в path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.bot3.utils import parse_vless_key, parse_trojan_key, parse_shadowsocks_key


# =============================================================================
# ТЕСТЫ PARSE_VLESS_KEY
# =============================================================================

class TestParseVlessKey:
    """Тесты для функции parse_vless_key"""
    
    def test_valid_key_with_all_params(self, sample_vless_key):
        """Тест валидного ключа со всеми параметрами"""
        result = parse_vless_key(sample_vless_key)
        
        assert result['address'] == '192.168.1.1'
        assert result['port'] == 443
        assert result['id'] == '55504f0d-3f5b-4d5e-8c5f-5d5e5f5g5h5i'
        assert result['security'] == 'reality'
        assert result['encryption'] == 'none'
        assert result['pbk'] == 'abcdef123456'
        assert result['fp'] == 'chrome'
        assert result['flow'] == 'xtls-rprx-vision'
        assert result['sni'] == ''
        assert result['sid'] == '1234'
        assert result['spx'] == '/'
    
    def test_valid_key_minimal(self):
        """Тест минимального валидного ключа"""
        key = 'vless://uuid@192.168.1.1:443'
        result = parse_vless_key(key)
        
        assert result['address'] == '192.168.1.1'
        assert result['port'] == 443
        assert result['id'] == 'uuid'
    
    def test_valid_key_default_port(self):
        """Тест ключа с портом по умолчанию"""
        key = 'vless://uuid@192.168.1.1'
        result = parse_vless_key(key)
        
        assert result['port'] == 443  # Порт по умолчанию
    
    def test_invalid_key_missing_hostname(self):
        """Тест ключа без hostname"""
        key = 'vless://uuid@:443'
        
        with pytest.raises(ValueError, match="Отсутствует адрес сервера"):
            parse_vless_key(key)
    
    def test_invalid_key_missing_uuid(self):
        """Тест ключа без UUID"""
        key = 'vless://@192.168.1.1:443'
        
        with pytest.raises(ValueError, match="Отсутствует.*ID пользователя"):
            parse_vless_key(key)
    
    def test_invalid_key_port_too_high(self):
        """Тест ключа с портом выше 65535"""
        key = 'vless://uuid@192.168.1.1:99999'
        
        with pytest.raises(ValueError, match="Порт должен быть от 1 до 65535"):
            parse_vless_key(key)
    
    def test_invalid_key_port_zero(self):
        """Тест ключа с портом 0"""
        key = 'vless://uuid@192.168.1.1:0'
        
        with pytest.raises(ValueError, match="Порт должен быть от 1 до 65535"):
            parse_vless_key(key)
    
    def test_invalid_key_not_vless_scheme(self):
        """Тест ключа не с той схемой"""
        key = 'http://uuid@192.168.1.1:443'
        
        # Функция ожидает vless:// в начале
        with pytest.raises((ValueError, IndexError)):
            parse_vless_key(key)
    
    def test_invalid_key_empty(self):
        """Тест пустого ключа"""
        key = ''
        
        with pytest.raises((ValueError, IndexError)):
            parse_vless_key(key)
    
    def test_invalid_key_ipv6(self):
        """Тест ключа с IPv6 адресом"""
        key = 'vless://uuid@[::1]:443'
        result = parse_vless_key(key)
        
        assert result['address'] == '::1' or result['address'] == '[::1]'
        assert result['port'] == 443


# =============================================================================
# ТЕСТЫ PARSE_TROJAN_KEY
# =============================================================================

class TestParseTrojanKey:
    """Тесты для функции parse_trojan_key"""
    
    def test_valid_key_with_params(self, sample_trojan_key):
        """Тест валидного ключа с параметрами"""
        result = parse_trojan_key(sample_trojan_key)
        
        assert result['pw'] == 'password123'
        assert result['host'] == '192.168.1.1'
        assert result['port'] == 443
    
    def test_valid_key_minimal(self):
        """Тест минимального валидного ключа"""
        key = 'trojan://password@192.168.1.1:443'
        result = parse_trojan_key(key)
        
        assert result['pw'] == 'password'
        assert result['host'] == '192.168.1.1'
        assert result['port'] == 443
    
    def test_valid_key_with_domain(self):
        """Тест ключа с доменным именем"""
        key = 'trojan://pass@example.com:8443'
        result = parse_trojan_key(key)
        
        assert result['pw'] == 'pass'
        assert result['host'] == 'example.com'
        assert result['port'] == 8443
    
    def test_invalid_key_missing_password(self):
        """Тест ключа без пароля"""
        key = 'trojan://@192.168.1.1:443'
        
        with pytest.raises(ValueError, match="Отсутствует пароль"):
            parse_trojan_key(key)
    
    def test_invalid_key_missing_host(self):
        """Тест ключа без хоста"""
        key = 'trojan://password@:443'
        
        with pytest.raises(ValueError, match="Некорректный адрес сервера"):
            parse_trojan_key(key)
    
    def test_invalid_key_port_too_high(self):
        """Тест ключа с портом выше 65535"""
        key = 'trojan://password@192.168.1.1:99999'
        
        with pytest.raises(ValueError, match="Порт должен быть от 1 до 65535"):
            parse_trojan_key(key)
    
    def test_invalid_key_not_trojan_scheme(self):
        """Тест ключа не с той схемой"""
        key = 'http://password@192.168.1.1:443'
        
        with pytest.raises((ValueError, IndexError)):
            parse_trojan_key(key)
    
    def test_invalid_key_empty(self):
        """Тест пустого ключа"""
        key = ''
        
        with pytest.raises((ValueError, IndexError)):
            parse_trojan_key(key)


# =============================================================================
# ТЕСТЫ PARSE_SHADOWSOCKS_KEY
# =============================================================================

class TestParseShadowsocksKey:
    """Тесты для функции parse_shadowsocks_key"""
    
    def test_valid_key_with_params(self, sample_shadowsocks_key):
        """Тест валидного ключа с параметрами"""
        result = parse_shadowsocks_key(sample_shadowsocks_key)
        
        assert result['server'] == '192.168.1.1'
        assert result['port'] == 8388
        assert result['password'] == 'password123'
        assert result['method'] == 'aes-256-gcm'
    
    def test_valid_key_minimal(self):
        """Тест минимального валидного ключа"""
        # ss://base64(aes-256-gcm:pass)@192.168.1.1:8388
        key = 'ss://YWVzLTI1Ni1nY206cGFzcw==@192.168.1.1:8388'
        result = parse_shadowsocks_key(key)
        
        assert result['server'] == '192.168.1.1'
        assert result['port'] == 8388
        assert result['password'] == 'pass'
        assert result['method'] == 'aes-256-gcm'
    
    def test_valid_key_with_domain(self):
        """Тест ключа с доменным именем"""
        # ss://base64(chacha20-ietf-poly1305:secret)@example.com:9000
        key = 'ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTpzZWNyZXQ=@example.com:9000'
        result = parse_shadowsocks_key(key)
        
        assert result['server'] == 'example.com'
        assert result['port'] == 9000
        assert result['password'] == 'secret'
        assert result['method'] == 'chacha20-ietf-poly1305'
    
    def test_invalid_key_missing_server(self):
        """Тест ключа без сервера"""
        key = 'ss://YWVzLTI1Ni1nY206cGFzcw==@:8388'
        
        with pytest.raises(ValueError, match="Некорректные данные сервера"):
            parse_shadowsocks_key(key)
    
    def test_invalid_key_missing_port(self):
        """Тест ключа без порта"""
        key = 'ss://YWVzLTI1Ni1nY206cGFzcw==@192.168.1.1'
        
        with pytest.raises((ValueError, IndexError)):
            parse_shadowsocks_key(key)
    
    def test_invalid_key_port_too_high(self):
        """Тест ключа с портом выше 65535"""
        # Ключ с некорректным портом
        key = 'ss://YWVzLTI1Ni1nY206cGFzcw==@192.168.1.1:99999'
        
        with pytest.raises(ValueError, match="Порт должен быть от 1 до 65535"):
            parse_shadowsocks_key(key)
    
    def test_invalid_key_not_ss_scheme(self):
        """Тест ключа не с той схемой"""
        key = 'http://YWVzLTI1Ni1nY206cGFzcw==@192.168.1.1:8388'
        
        with pytest.raises((ValueError, IndexError)):
            parse_shadowsocks_key(key)
    
    def test_invalid_key_empty(self):
        """Тест пустого ключа"""
        key = ''
        
        with pytest.raises((ValueError, IndexError)):
            parse_shadowsocks_key(key)
    
    def test_invalid_key_bad_base64(self):
        """Тест ключа с некорректным base64"""
        key = 'ss://invalid_base64!@192.168.1.1:8388'
        
        with pytest.raises(Exception):
            parse_shadowsocks_key(key)


# =============================================================================
# ОБЩИЕ ТЕСТЫ
# =============================================================================

class TestParsersCommon:
    """Общие тесты для всех парсеров"""
    
    def test_all_parsers_handle_none_input(self):
        """Все парсеры должны обрабатывать None вход"""
        parsers = [parse_vless_key, parse_trojan_key, parse_shadowsocks_key]
        
        for parser in parsers:
            with pytest.raises((AttributeError, TypeError, ValueError)):
                parser(None)
    
    def test_all_parsers_handle_empty_string(self):
        """Все парсеры должны обрабатывать пустую строку"""
        parsers = [parse_vless_key, parse_trojan_key, parse_shadowsocks_key]
        
        for parser in parsers:
            with pytest.raises((ValueError, IndexError)):
                parser('')
    
    def test_all_parsers_return_dict(self, sample_vless_key, sample_trojan_key, sample_shadowsocks_key):
        """Все парсеры должны возвращать dict"""
        test_cases = [
            (parse_vless_key, sample_vless_key),
            (parse_trojan_key, sample_trojan_key),
            (parse_shadowsocks_key, sample_shadowsocks_key)
        ]
        
        for parser, key in test_cases:
            result = parser(key)
            assert isinstance(result, dict)
