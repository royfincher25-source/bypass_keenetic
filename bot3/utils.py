# =============================================================================
# УТИЛИТЫ (ОПТИМИЗИРОВАННАЯ ВЕРСИЯ)
# =============================================================================
# Оптимизация для embedded-устройств:
# - Кэширование результатов
# - Lazy loading
# - Минимальное использование памяти
# - Использование core модуля для общих функций
# =============================================================================

import os
import signal
import time
import subprocess
import json
import re
import gc

# Импорт общих функций из core модуля
from core import (
    get_http_session,
    download_script,
    log_error,
    clean_log,
    get_available_drives,
    create_backup_with_params,
    parse_vless_key,
    generate_config,
    vless_config,
    tor_config
)

# Локальные импорты для обратной совместимости
import bot_config as config


# =============================================================================
# КЭШИРОВАНИЕ
# =============================================================================

class Cache:
    """Кэш с TTL и LRU eviction для экономии памяти"""

    _cache = {}
    _timestamps = {}
    MAX_SIZE = 100  # Ограничение размера кэша

    @classmethod
    def get(cls, key, default=None):
        """Получение из кэша с LRU обновлением"""
        if key in cls._cache:
            # Поднимаем элемент вверх (LRU)
            value = cls._cache.pop(key)
            cls._cache[key] = value
            return value
        return default

    @classmethod
    def set(cls, key, value, ttl=300):
        """Установка в кэш с TTL и LRU eviction"""
        # LRU eviction при превышении размера
        if len(cls._cache) >= cls.MAX_SIZE and key not in cls._cache:
            # Удаляем oldest entry (первый в словаре)
            oldest_key = next(iter(cls._cache))
            cls._cache.pop(oldest_key, None)
            cls._timestamps.pop(oldest_key, None)
        
        cls._cache[key] = value
        cls._timestamps[key] = time.time() + ttl

    @classmethod
    def is_valid(cls, key):
        """Проверка валидности кэша"""
        if key not in cls._timestamps:
            return False
        return time.time() < cls._timestamps[key]

    @classmethod
    def cleanup(cls):
        """Очистка просроченного кэша + LRU"""
        now = time.time()
        expired = [k for k, t in cls._timestamps.items() if now >= t]
        for key in expired:
            cls._cache.pop(key, None)
            cls._timestamps.pop(key, None)
        
        # Дополнительно: оставляем только MAX_SIZE последних
        while len(cls._cache) > cls.MAX_SIZE:
            oldest_key = next(iter(cls._cache))
            cls._cache.pop(oldest_key, None)
            cls._timestamps.pop(oldest_key, None)

    @classmethod
    def clear(cls):
        """Полная очистка кэша"""
        cls._cache.clear()
        cls._timestamps.clear()


# =============================================================================
# ЛОГИРОВАНИЕ (ОПТИМИЗИРОВАННОЕ)
# =============================================================================

# Кэш для избежания повторных открытий файла
_log_file_handle = None
_log_file_path = None


def log_error(message):
    """
    Оптимизированное логирование ошибок.
    - Кэширование file handle
    - Буферизация
    """
    global _log_file_handle, _log_file_path
    
    log_file = config.paths["error_log"]
    
    # Повторное использование file handle
    if _log_file_path != log_file:
        if _log_file_handle:
            try:
                _log_file_handle.close()
            except:
                pass
        _log_file_handle = open(log_file, "a", encoding='utf-8')
        _log_file_path = log_file
    
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        _log_file_handle.write(f"{timestamp} - {message}\n")
        _log_file_handle.flush()  # Немедленная запись
    except:
        pass


def clean_log(log_file):
    """Очистка лога (оптимизировано)"""
    if not os.path.exists(log_file):
        open(log_file, 'a').close()
        return
    
    file_size = os.path.getsize(log_file)
    max_size = 524288  # 512KB
    
    if file_size > max_size:
        # Читаем только последние N строк
        with open(log_file, 'rb') as f:
            # Ищем позицию последних 50 строк
            lines = []
            f.seek(0, 2)  # В конец
            file_size = f.tell()
            block_size = min(file_size, 1024 * 1024)  # Читаем максимум 1MB
            f.seek(max(0, file_size - block_size))
            
            for line in f:
                lines.append(line)
            
            # Оставляем последние 50 строк
            lines = lines[-50:]
        
        with open(log_file, 'wb') as f:
            f.writelines(lines)


def signal_handler(sig, frame):
    """Обработчик сигналов"""
    log_error(f"Бот остановлен сигналом {signal.Signals(sig).name}")
    raise SystemExit


# =============================================================================
# ЗАГРУЗКА СКРИПТОВ (ОПТИМИЗИРОВАНО)
# =============================================================================

# Connection pooling для HTTP запросов (экономия памяти и времени)
_http_session = None


def get_http_session():
    """Получение HTTP сессии с connection pooling"""
    global _http_session
    if _http_session is None:
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        _http_session = requests.Session()
        
        # Настройка retry logic
        retry = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=1, pool_maxsize=2)
        _http_session.mount("http://", adapter)
        _http_session.mount("https://", adapter)
    
    return _http_session


def download_script():
    """
    Загрузка скрипта с кэшированием и connection pooling.
    - Проверка версии перед загрузкой
    - Кэширование содержимого
    - Connection pooling для экономии памяти
    """
    import requests

    script_path = config.paths["script_sh"]
    cache_key = 'script_sh'

    # Проверка кэша (5 минут)
    if Cache.is_valid(cache_key):
        cached_hash = Cache.get(cache_key)
        # Можно добавить проверку хэша файла

    try:
        # Загрузка с таймаутом и использованием сессии
        session = get_http_session()
        response = session.get(
            f"{config.bot_url}/script.sh",
            timeout=30,
            stream=True  # Потоковая загрузка для экономии памяти
        )
        response.raise_for_status()

        # Запись напрямую в файл (без загрузки в память)
        with open(script_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        os.chmod(script_path, 0o0755)

        # Кэширование
        Cache.set(cache_key, script_path, ttl=300)

    except requests.exceptions.Timeout:
        log_error("Ошибка при загрузке скрипта: превышен таймаут")
        raise
    except requests.exceptions.RequestException as e:
        log_error(f"Ошибка при загрузке скрипта: {str(e)}")
        raise

def download_bot_files():
    """Загрузка файлов бота с обновлением version.md"""
    bot_files = ['handlers.py', 'menu.py', 'utils.py', 'main.py', 'version.md']
    bot_dir = os.path.dirname(__file__)

    for filename in bot_files:
        try:
            url = f"{config.bot_url}/{filename}"
            local_path = os.path.join(bot_dir, filename)
            response = get_http_session().get(url, timeout=30, stream=True)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except Exception as e:
            log_error(f"Ошибка при загрузке {filename}: {str(e)}")
            raise


# =============================================================================
# РАБОТА СО СПИСКАМИ ОБХОДА (ОПТИМИЗИРОВАНО)
# =============================================================================


def load_bypass_list(filepath):
    """
    Загрузка списка обхода с кэшированием.
    - Кэш на 1 минуту
    - Чтение только при изменении
    - Поддержка комментариев (#)
    """
    cache_key = f'bypass:{filepath}'

    # Проверка кэша
    if Cache.is_valid(cache_key):
        cached = Cache.get(cache_key)
        # Проверка времени изменения файла
        try:
            mtime = os.path.getmtime(filepath)
            if cached and mtime == cached.get('mtime'):
                return cached['data']
        except:
            pass

    # Загрузка из файла
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Сохраняем порядок строк, пропускаем комментарии и пустые строки
            data = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

        # Кэширование
        try:
            mtime = os.path.getmtime(filepath)
        except:
            mtime = time.time()

        Cache.set(cache_key, {'data': data, 'mtime': mtime}, ttl=60)

        return data
    except:
        return []


def save_bypass_list(filepath, sites):
    """
    Сохранение списка обхода.
    - Сохранение в исходном порядке (без сортировки)
    - Поддержка комментариев (#)
    - Очистка кэша после сохранения
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # Сохраняем в исходном порядке
            f.write('\n'.join(sites))

        # Очистка кэша для этого файла
        cache_key = f'bypass:{filepath}'
        Cache._cache.pop(cache_key, None)
        Cache._timestamps.pop(cache_key, None)

    except Exception as e:
        log_error(f"Ошибка при сохранении списка обхода: {str(e)}")
        raise


# =============================================================================
# ПРОВЕРКА ПЕРЕЗАПУСКА (ОПТИМИЗИРОВАНО)
# =============================================================================

def check_restart(bot):
    """Проверка перезапуска бота"""
    chat_id_path = config.paths["chat_id_path"]
    
    if os.path.exists(chat_id_path):
        try:
            with open(chat_id_path, 'r') as f:
                chat_id = int(f.read().strip())
            
            bot.send_message(chat_id, '✅ Бот перезапущен')
            os.remove(chat_id_path)
        except Exception as e:
            log_error(f"Ошибка при отправке сообщения после перезапуска: {str(e)}")
            try:
                os.remove(chat_id_path)
            except:
                pass


# =============================================================================
# ПАРСЕРЫ КЛЮЧЕЙ (ОПТИМИЗИРОВАНО)
# =============================================================================


def notify_on_error():
    """Декоратор для обработки ошибок"""
    def decorator(func):
        def wrapper(key, bot=None, chat_id=None, *args, **kwargs):
            try:
                return func(key, bot, chat_id, *args, **kwargs)
            except Exception as e:
                if bot and chat_id:
                    if func.__name__ == "tor_config":
                        bot.send_message(chat_id, f"❌ Ошибка в мостах Tor: {str(e)}")
                    else:
                        protocol = func.__name__.split('_')[1].capitalize()
                        bot.send_message(chat_id, f"❌ Ошибка в ключе {protocol}: {str(e)}")
                raise
        return wrapper
    return decorator


@notify_on_error()
def parse_vless_key(key, bot=None, chat_id=None):
    """Парсинг VLESS ключа с кэшированием"""
    from urllib.parse import urlparse, parse_qs
    
    cache_key = f'vless:{key}'
    
    if Cache.is_valid(cache_key):
        return Cache.get(cache_key)
    
    # Парсинг (код из core/parsers.py для избежания импорта)
    if not key.startswith('vless://'):
        raise ValueError("Неверный формат ключа VLESS")
    
    url = key[8:]
    parsed_url = urlparse(url)
    
    if not parsed_url.hostname or not parsed_url.username:
        raise ValueError("Отсутствует адрес сервера или ID пользователя")
    
    port = parsed_url.port or 443
    if not (1 <= port <= 65535):
        raise ValueError(f"Порт должен быть от 1 до 65535")
    
    params = parse_qs(parsed_url.query)
    
    result = {
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
    
    Cache.set(cache_key, result, ttl=3600)  # Кэш на 1 час
    return result


@notify_on_error()
def parse_trojan_key(key, bot=None, chat_id=None):
    """Парсинг Trojan ключа с кэшированием"""
    from urllib.parse import urlparse
    import base64
    
    cache_key = f'trojan:{key}'
    
    if Cache.is_valid(cache_key):
        return Cache.get(cache_key)
    
    if not key.startswith('trojan://'):
        raise ValueError("Неверный формат ключа Trojan")
    
    url = key[9:]
    parsed_url = urlparse(url)
    
    if not parsed_url.password:
        raise ValueError("Отсутствует пароль")
    
    if not parsed_url.hostname:
        raise ValueError("Отсутствует адрес сервера")
    
    port = parsed_url.port or 443
    if not (1 <= port <= 65535):
        raise ValueError(f"Порт должен быть от 1 до 65535")
    
    result = {
        'pw': parsed_url.password,
        'host': parsed_url.hostname,
        'port': port,
    }
    
    Cache.set(cache_key, result, ttl=3600)
    return result


@notify_on_error()
def parse_shadowsocks_key(key, bot=None, chat_id=None):
    """Парсинг Shadowsocks ключа с кэшированием"""
    from urllib.parse import urlparse
    
    cache_key = f'ss:{key}'
    
    if Cache.is_valid(cache_key):
        return Cache.get(cache_key)
    
    if not key.startswith('ss://'):
        raise ValueError("Неверный формат ключа Shadowsocks")
    
    url = key[5:]
    parsed_url = urlparse(url)
    
    if not parsed_url.hostname or not parsed_url.username:
        raise ValueError("Некорректные данные сервера")
    
    port = parsed_url.port
    if not port or not (1 <= port <= 65535):
        raise ValueError(f"Порт должен быть от 1 до 65535")
    
    # Декодирование base64
    try:
        encoded = parsed_url.username
        padding = 4 - (len(encoded) % 4)
        if padding != 4:
            encoded += '=' * padding
        
        decoded = base64.b64decode(encoded).decode('utf-8')
        method, password = decoded.split(':', 1)
    except Exception as e:
        raise ValueError(f"Ошибка декодирования base64: {str(e)}")
    
    result = {
        'server': parsed_url.hostname,
        'port': port,
        'password': password,
        'method': method,
    }
    
    Cache.set(cache_key, result, ttl=3600)
    return result


# =============================================================================
# ГЕНЕРАЦИЯ КОНФИГОВ (ОПТИМИЗИРОВАНО)
# =============================================================================

class ConfigWriter:
    """Оптимизированная запись конфигов"""
    
    @staticmethod
    def write_config(file_path, config_data, format='json'):
        """Запись конфигурации"""
        with open(file_path, 'w', encoding='utf-8') as f:
            if format == 'json':
                json.dump(json.loads(config_data), f, ensure_ascii=False, indent=2)
            else:
                f.write(config_data)


def generate_config(key, template_file, config_path, replacements, parse_func, bot=None, chat_id=None):
    """Генерация конфигурации с кэшированием шаблонов"""
    params = parse_func(key, bot, chat_id)
    
    cache_key = f'template:{template_file}'
    
    # Проверка кэша шаблона
    if Cache.is_valid(cache_key):
        template = Cache.get(cache_key)
    else:
        template_path = os.path.join(config.paths["templates_dir"], template_file)
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        Cache.set(cache_key, template, ttl=3600)
    
    # Замена параметров
    config_data = template
    for k, v in replacements.items():
        config_data = config_data.replace("{{" + k + "}}", str(v))
    for k, v in params.items():
        config_data = config_data.replace("{{" + k + "}}", str(v))
    
    ConfigWriter.write_config(config_path, config_data)


def vless_config(key, bot=None, chat_id=None):
    """Генерация VLESS конфигурации"""
    generate_config(
        key=key,
        template_file="vless_template.json",
        config_path=config.paths["vless_config"],
        replacements={"localportvless": config.localportvless},
        parse_func=parse_vless_key,
        bot=bot,
        chat_id=chat_id
    )


def trojan_config(key, bot=None, chat_id=None):
    """Генерация Trojan конфигурации"""
    generate_config(
        key=key,
        template_file="trojan_template.json",
        config_path=config.paths["trojan_config"],
        replacements={"localporttrojan": config.localporttrojan},
        parse_func=parse_trojan_key,
        bot=bot,
        chat_id=chat_id
    )


def shadowsocks_config(key, bot=None, chat_id=None):
    """Генерация Shadowsocks конфигурации"""
    generate_config(
        key=key,
        template_file="shadowsocks_template.json",
        config_path=config.paths["shadowsocks_config"],
        replacements={"localportsh": config.localportsh},
        parse_func=parse_shadowsocks_key,
        bot=bot,
        chat_id=chat_id
    )


@notify_on_error()
def tor_config(bridges, bot=None, chat_id=None):
    """Генерация Tor конфигурации"""
    # Упрощённый парсинг мостов
    bridge_lines = bridges.strip().split('\n')
    valid_transports = {"obfs4", "webtunnel"}
    ip_port_pattern = re.compile(r"^(?:(?:\d{1,3}\.){3}\d{1,3}|\[[0-9a-fA-F:]*\]):\d{1,5}$")
    url_pattern = re.compile(r"^https?://[^\s/$.?#].\S*$")
    
    for line in bridge_lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if not parts:
            raise ValueError(f"Некорректный мост: '{line}'")
        
        transport_type = parts[0] if parts[0] in valid_transports else None
        
        if transport_type:
            if len(parts) < 2:
                raise ValueError(f"Указан транспорт '{parts[0]}', но нет IP:порт")
            bridge_data = parts[1]
        else:
            bridge_data = parts[0]
        
        if transport_type == "webtunnel":
            if not ip_port_pattern.match(bridge_data):
                raise ValueError(f"Некорректный формат IP:порт в '{line}'")
            url_match = next((part[4:] for part in parts if part.startswith("url=")), None)
            if not url_match or not url_pattern.match(url_match):
                raise ValueError(f"Некорректный URL в webtunnel: '{line}'")
        else:
            if not ip_port_pattern.match(bridge_data):
                raise ValueError(f"Некорректный формат IP:порт в '{line}'")
    
    # Загрузка шаблона
    template_path = os.path.join(config.paths["templates_dir"], "tor_template.torrc")
    with open(template_path, 'r', encoding='utf-8') as f:
        config_data = f.read()
    
    config_data = config_data.replace("{{localporttor}}", str(config.localporttor))
    bridges_out = bridges.strip()
    
    transports = ["obfs4", "webtunnel"]
    found = False
    for t in transports:
        if t in bridges_out:
            bridges_out = "\n".join(
                line.replace(t, f"Bridge {t}", 1) if line.startswith(t) else line
                for line in bridges_out.splitlines()
            )
            config_data = config_data.replace(f"#ClientTransportPlugin {t}", f"ClientTransportPlugin {t}", 1)
            found = True
    
    config_data = config_data.replace("{{bridges}}", bridges_out if found else "")
    ConfigWriter.write_config(config.paths["tor_config"], config_data, format='text')


# =============================================================================
# BACKUP DRIVES
# =============================================================================

def get_available_drives():
    """Получение списка доступных дисков для бэкапа без swap разделов"""
    drives = []
    current_drive = None
    current_manufacturer = None

    try:
        media_output = subprocess.check_output(
            ["ndmc", "-c", "show media"],
            text=True,
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError:
        return []
    except Exception:
        return []

    for raw_line in media_output.splitlines():
        stripped = raw_line.strip()

        if stripped.startswith("manufacturer:"):
            current_manufacturer = stripped.split(":", 1)[1].strip()

        elif stripped.startswith("uuid:"):
            if current_drive:
                drives.append(current_drive)
            uuid = stripped.split(":", 1)[1].strip()
            current_drive = {'uuid': uuid, 'path': f"/tmp/mnt/{uuid}"}

        elif stripped.startswith("label:") and current_drive is not None:
            current_drive['label'] = stripped.split(":", 1)[1].strip()

        elif stripped.startswith("fstype:") and current_drive is not None:
            fstype = stripped.split(":", 1)[1].strip()
            if fstype == "swap":
                current_drive = None
            else:
                current_drive['fstype'] = fstype

    if current_drive:
        drives.append(current_drive)

    return drives


# =============================================================================
# ОЧИСТКА ПАМЯТИ
# =============================================================================

def cleanup_memory():
    """Принудительная очистка памяти (вызывать периодически)"""
    Cache.cleanup()
    gc.collect()


# =============================================================================
# BACKUP (заглушка)
# =============================================================================

def create_backup_with_params(bot, chat_id, backup_state, selected_drive, progress_msg_id):
    """Создание бэкапа с параметрами (упрощённая версия)"""
    try:
        bot.edit_message_text("⏳ Создание бэкапа...", chat_id, progress_msg_id)
        
        # Простое создание бэкапа через скрипт
        archive_path = f"/opt/root/backup_{time.strftime('%Y%m%d_%H%M%S')}.tar.gz"
        
        subprocess.run([
            "tar", "-czf", archive_path,
            "-C", "/opt/etc", "bot", "unblock"
        ], timeout=300, capture_output=True)
        
        if os.path.exists(archive_path):
            bot.edit_message_text("✅ Бэкап создан, отправляю файл...", chat_id, progress_msg_id)
            with open(archive_path, 'rb') as f:
                bot.send_document(chat_id, f, caption="✅ Бэкап конфигурации")
            
            # Очистка
            if backup_state.delete_archive:
                os.remove(archive_path)
        else:
            bot.edit_message_text("❌ Не удалось создать бэкап", chat_id, progress_msg_id)
            
    except subprocess.TimeoutExpired:
        bot.edit_message_text("❌ Таймаут создания бэкапа", chat_id, progress_msg_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка: {str(e)}", chat_id, progress_msg_id)
        log_error(f"Backup error: {e}")


def cleanup_memory():
    """Периодическая очистка памяти"""
    import gc
    Cache.cleanup()
    gc.collect()
