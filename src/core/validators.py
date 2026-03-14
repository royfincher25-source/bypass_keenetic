# =============================================================================
# CORE VALIDATORS - ВАЛИДАТОРЫ
# =============================================================================
# Функции валидации для доменов, IP, портов
# =============================================================================

import re
import base64
from typing import Union


def validate_domain(domain: str) -> bool:
    """
    Валидация доменного имени.
    
    Args:
        domain: Домен для проверки
        
    Returns:
        True если домен валиден
    """
    if not domain or not isinstance(domain, str):
        return False
    
    # Паттерн для валидации доменов
    pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    
    return bool(re.match(pattern, domain.strip()))


def validate_ip(ip: str) -> bool:
    """
    Валидация IPv4 адреса.
    
    Args:
        ip: IP адрес для проверки
        
    Returns:
        True если IP валиден
    """
    if not ip or not isinstance(ip, str):
        return False
    
    # Паттерн для IPv4
    pattern = r'^(?:\d{1,3}\.){3}\d{1,3}$'
    
    if not re.match(pattern, ip.strip()):
        return False
    
    # Проверка каждой октеты
    octets = ip.split('.')
    for octet in octets:
        try:
            num = int(octet)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False
    
    return True


def validate_ip_cidr(cidr: str) -> bool:
    """
    Валидация CIDR нотации (IP/маска).
    
    Args:
        cidr: CIDR для проверки (например, "192.168.1.0/24")
        
    Returns:
        True если CIDR валиден
    """
    if not cidr or not isinstance(cidr, str):
        return False
    
    parts = cidr.split('/')
    if len(parts) != 2:
        return False
    
    ip, mask = parts
    
    if not validate_ip(ip):
        return False
    
    try:
        mask_num = int(mask)
        if mask_num < 0 or mask_num > 32:
            return False
    except ValueError:
        return False
    
    return True


def validate_port(port: Union[int, str]) -> bool:
    """
    Валидация порта.
    
    Args:
        port: Порт для проверки (int или str)
        
    Returns:
        True если порт валиден
    """
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False


def validate_url(url: str) -> bool:
    """
    Валидация URL.
    
    Args:
        url: URL для проверки
        
    Returns:
        True если URL валиден
    """
    if not url or not isinstance(url, str):
        return False
    
    # Простой паттерн для HTTP/HTTPS URL
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    
    return bool(re.match(pattern, url.strip()))


def validate_bypass_entry(entry: str) -> bool:
    """
    Универсальная валидация записи для списка обхода.
    
    Принимает:
    - Домены (example.com)
    - IPv4 адреса (192.168.1.1)
    - CIDR (192.168.1.0/24)
    
    Args:
        entry: Запись для проверки
        
    Returns:
        True если запись валидна
    """
    if not entry or not isinstance(entry, str):
        return False
    
    entry = entry.strip()
    
    if not entry:
        return False
    
    # Проверяем по порядку
    if validate_domain(entry):
        return True
    
    if validate_ip(entry):
        return True
    
    if validate_ip_cidr(entry):
        return True

    return False


# =============================================================================
# REALITY ВАЛИДАТОРЫ
# =============================================================================


def validate_reality_public_key(public_key: str) -> bool:
    """
    Проверка валидности PUBLIC ключа REALITY.

    REALITY использует X25519 ключи (32 байта, base64).

    Args:
        public_key: Базовая64 строка

    Returns:
        bool: True если ключ валиден
    """
    if not public_key or len(public_key) < 40:
        return False

    try:
        decoded = base64.b64decode(public_key)
        # X25519 public key = 32 байта
        return len(decoded) == 32
    except Exception:
        return False


def validate_reality_short_id(short_id: str) -> bool:
    """
    Проверка валидности ShortId.

    ShortId — это 0-8 байт в hex формате.

    Args:
        short_id: Hex строка (0-16 символов)

    Returns:
        bool: True если ShortId валиден
    """
    # Пустой ShortId допустим
    if not short_id:
        return True

    # Hex строка 0-16 символов (0-8 байт)
    if not re.match(r'^[0-9a-fA-F]{0,16}$', short_id):
        return False

    return True


def validate_reality_fingerprint(fp: str) -> bool:
    """
    Проверка валидности fingerprint.

    Допустимые значения:
    - chrome, firefox, safari, ios
    - android, edge, qq
    - random, randomized

    Args:
        fp: Строка fingerprint

    Returns:
        bool: True если fingerprint валиден
    """
    valid_fps = {
        'chrome', 'firefox', 'safari', 'ios',
        'android', 'edge', 'qq',
        'random', 'randomized', ''
    }

    return fp.lower() in valid_fps
