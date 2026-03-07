# =============================================================================
# CORE VALIDATORS - ВАЛИДАТОРЫ
# =============================================================================
# Функции валидации для доменов, IP, портов
# =============================================================================

import re
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
