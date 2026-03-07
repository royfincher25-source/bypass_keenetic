# =============================================================================
# CORE PARSERS - ПАРСЕРЫ КЛЮЧЕЙ
# =============================================================================
# Функции парсинга для VLESS, Trojan, Shadowsocks ключей
# =============================================================================

import re
from typing import Dict, Optional
from urllib.parse import urlparse, parse_qs
import base64


def parse_vless_key(key: str) -> Dict:
    """
    Парсинг VLESS ключа.
    
    Формат: vless://uuid@host:port?params#name
    
    Args:
        key: VLESS ключ
        
    Returns:
        Dict с параметрами подключения
        
    Raises:
        ValueError: Если ключ невалиден
    """
    if not key or not key.startswith('vless://'):
        raise ValueError(
            "Неверный формат ключа VLESS. Ожидается: "
            "vless://<UUID>@<IP>:<порт>?параметры#имя"
        )
    
    url = key[8:]  # Убираем 'vless://'
    parsed_url = urlparse(url)
    
    # Проверка обязательных полей
    if not parsed_url.hostname:
        raise ValueError("Отсутствует адрес сервера")
    
    if not parsed_url.username:
        raise ValueError("Отсутствует ID пользователя")
    
    params = parse_qs(parsed_url.query)
    
    # Порт
    port = parsed_url.port or 443
    if not (1 <= port <= 65535):
        raise ValueError(f"Порт должен быть от 1 до 65535, получено: {port}")
    
    return {
        'address': parsed_url.hostname,
        'port': port,
        'id': parsed_url.username,
        'security': params.get('security', [''])[0],
        'encryption': params.get('encryption', ['none'])[0],
        'pbk': params.get('pbk', [''])[0],
        'fp': params.get('fp', [''])[0],
        'spx': params.get('spx', ['/'])[0],
        'flow': params.get('flow', ['xtls-rprx-vision'])[0],
        'sni': params.get('sni', [''])[0],
        'sid': params.get('sid', [''])[0]
    }


def parse_trojan_key(key: str) -> Dict:
    """
    Парсинг Trojan ключа.
    
    Формат: trojan://password@host:port?params#name
    
    Args:
        key: Trojan ключ
        
    Returns:
        Dict с параметрами подключения
        
    Raises:
        ValueError: Если ключ невалиден
    """
    if not key or not key.startswith('trojan://'):
        raise ValueError(
            "Неверный формат ключа Trojan. Ожидается: "
            "trojan://<пароль>@<IP>:<порт>?параметры#имя"
        )
    
    url = key[9:]  # Убираем 'trojan://'
    parsed_url = urlparse(url)
    
    # Проверка обязательных полей
    if not parsed_url.password:
        raise ValueError("Отсутствует пароль")
    
    if not parsed_url.hostname:
        raise ValueError("Отсутствует адрес сервера")
    
    # Порт
    port = parsed_url.port or 443
    if not (1 <= port <= 65535):
        raise ValueError(f"Порт должен быть от 1 до 65535, получено: {port}")
    
    return {
        'pw': parsed_url.password,
        'host': parsed_url.hostname,
        'port': port,
    }


def parse_shadowsocks_key(key: str) -> Dict:
    """
    Парсинг Shadowsocks ключа.
    
    Формат: ss://base64(method:password)@host:port#name
    
    Args:
        key: Shadowsocks ключ
        
    Returns:
        Dict с параметрами подключения
        
    Raises:
        ValueError: Если ключ невалиден
    """
    if not key or not key.startswith('ss://'):
        raise ValueError(
            "Неверный формат ключа Shadowsocks. Ожидается: "
            "ss://<base64(метод:пароль)>@<IP>:<порт>#имя"
        )
    
    url = key[5:]  # Убираем 'ss://'
    parsed_url = urlparse(url)
    
    # Проверка обязательных полей
    if not parsed_url.hostname:
        raise ValueError("Отсутствует адрес сервера")
    
    if not parsed_url.username:
        raise ValueError("Отсутствуют метод и пароль")
    
    # Порт
    port = parsed_url.port
    if not port or not (1 <= port <= 65535):
        raise ValueError(f"Порт должен быть от 1 до 65535")
    
    # Декодирование base64 (method:password)
    try:
        # Добавляем padding если нужно
        encoded = parsed_url.username
        padding = 4 - (len(encoded) % 4)
        if padding != 4:
            encoded += '=' * padding
        
        decoded = base64.b64decode(encoded).decode('utf-8')
        method, password = decoded.split(':', 1)
    except Exception as e:
        raise ValueError(f"Ошибка декодирования base64: {str(e)}")
    
    return {
        'server': parsed_url.hostname,
        'port': port,
        'password': password,
        'method': method,
    }
