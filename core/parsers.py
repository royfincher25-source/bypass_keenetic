# =============================================================================
# CORE PARSERS
# =============================================================================
# Парсеры ключей и генераторы конфигов для bot3 и botlight
# =============================================================================

import os
import re
import json
from urllib.parse import urlparse, parse_qs
import base64


def parse_vless_key(key, bot=None, chat_id=None):
    """
    Парсинг VLESS ключа.
    
    Args:
        key (str): VLESS ключ (vless://...)
        bot: TeleBot объект (опционально)
        chat_id (int): ID чата (опционально)
    
    Returns:
        dict: Распарсенные данные ключа
    
    Raises:
        ValueError: Неверный формат ключа
    """
    from .logging import log_error
    
    if not key.startswith('vless://'):
        raise ValueError("Неверный формат ключа VLESS")
    
    url = key[8:]
    parsed_url = urlparse(url)
    
    if not parsed_url.hostname or not parsed_url.username:
        raise ValueError("Некорректные данные сервера")
    
    port = parsed_url.port
    if not port or not (1 <= port <= 65535):
        raise ValueError(f"Порт должен быть от 1 до 65535")
    
    params = parse_qs(parsed_url.query)
    
    # Валидация параметров
    security = params.get('security', ['none'])[0]
    if security not in {'none', 'tls', 'reality'}:
        raise ValueError(f"Недопустимый security: {security}")
    
    encryption = params.get('encryption', ['none'])[0]
    if encryption not in {'none', 'aes-128-gcm', 'chacha20-poly1305'}:
        raise ValueError(f"Недопустимый encryption: {encryption}")
    
    result = {
        'address': parsed_url.hostname,
        'port': port,
        'id': parsed_url.username,
        'security': security,
        'encryption': encryption,
        'type': params.get('type', ['tcp'])[0],
        'host': params.get('host', [''])[0],
        'path': params.get('path', [''])[0],
        'sni': params.get('sni', [''])[0],
        'alpn': params.get('alpn', [''])[0],
        'fp': params.get('fp', [''])[0],
        'pbk': params.get('pbk', [''])[0],
        'sid': params.get('sid', [''])[0],
        'spx': params.get('spx', [''])[0],
    }
    
    return result


def generate_config(key, template_file, config_path, replacements, parse_func,
                    bot=None, chat_id=None):
    """
    Генерация конфигурации из шаблона.
    
    Args:
        key (str): Ключ для парсинга
        template_file (str): Путь к файлу шаблона
        config_path (str): Путь для сохранения конфига
        replacements (dict): Замены для шаблона
        parse_func (callable): Функция парсинга ключа
        bot: TeleBot объект (опционально)
        chat_id (int): ID чата (опционально)
    
    Returns:
        dict: Распарсенные данные
    
    Raises:
        ValueError: Ошибка парсинга
        FileNotFoundError: Шаблон не найден
    """
    from .logging import log_error
    
    try:
        # Парсинг ключа
        parsed_data = parse_func(key, bot, chat_id)
        
        # Загрузка шаблона
        if not os.path.exists(template_file):
            raise FileNotFoundError(f"Шаблон не найден: {template_file}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            config_data = f.read()
        
        # Замена плейсхолдеров
        for placeholder, value in replacements.items():
            config_data = config_data.replace(f"{{{placeholder}}}", str(value))
        
        # Сохранение конфига
        config_dir = os.path.dirname(config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(json.loads(config_data), f, ensure_ascii=False, indent=2)
        
        return parsed_data
        
    except json.JSONDecodeError as e:
        log_error(f"Ошибка JSON в шаблоне: {str(e)}")
        raise ValueError(f"Некорректный шаблон: {str(e)}")
        
    except FileNotFoundError as e:
        log_error(str(e))
        raise
        
    except Exception as e:
        log_error(f"Ошибка генерации конфига: {str(e)}")
        raise


def vless_config(key, bot=None, chat_id=None):
    """
    Генерация VLESS конфигурации.
    
    Args:
        key (str): VLESS ключ
        bot: TeleBot объект (опционально)
        chat_id (int): ID чата (опционально)
    
    Returns:
        dict: Распарсенные данные
    """
    template_file = "/opt/etc/bot/templates/vless_template.json"
    config_path = "/opt/etc/xray/config.json"
    
    return generate_config(
        key,
        template_file,
        config_path,
        {},  # Дополнительные замены
        parse_vless_key,
        bot,
        chat_id
    )


def tor_config(bridges, bot=None, chat_id=None):
    """
    Генерация конфигурации Tor.
    
    Args:
        bridges (str): Мосты Tor (каждая строка - отдельный мост)
        bot: TeleBot объект (опционально)
        chat_id (int): ID чата (опционально)
    
    Returns:
        None
    """
    from .logging import log_error
    
    template_path = "/opt/etc/bot/templates/tor_template.torrc"
    config_path = "/opt/etc/tor/torrc"
    
    try:
        # Загрузка шаблона
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"Шаблон не найден: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            config_data = f.read()
        
        # Обработка мостов
        bridges_out = bridges.strip()
        transports = ["obfs4", "webtunnel"]
        found = False
        
        for t in transports:
            if t in bridges_out:
                # Добавляем "Bridge " к первой строке с транспортом
                lines = bridges_out.splitlines()
                for i, line in enumerate(lines):
                    if line.startswith(t):
                        lines[i] = line.replace(t, f"Bridge {t}", 1)
                        break
                bridges_out = "\n".join(lines)
                
                # Раскомментируем ClientTransportPlugin
                config_data = config_data.replace(
                    f"#ClientTransportPlugin {t}",
                    f"ClientTransportPlugin {t}"
                )
                found = True
        
        config_data = config_data.replace("{{bridges}}", bridges_out if found else "")
        
        # Сохранение конфига
        config_dir = os.path.dirname(config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_data)
        
    except FileNotFoundError as e:
        log_error(str(e))
        if bot and chat_id:
            bot.send_message(chat_id, f"❌ Ошибка: {str(e)}")
        raise
        
    except Exception as e:
        log_error(f"Ошибка генерации конфига Tor: {str(e)}")
        if bot and chat_id:
            bot.send_message(chat_id, f"❌ Ошибка в мостах Tor: {str(e)}")
        raise
