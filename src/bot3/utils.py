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
    """Простой кэш с TTL для embedded-устройств"""

    _cache = {}
    _timestamps = {}
    MAX_SIZE = 10  # Уменьшено с 20 для экономии памяти

    @classmethod
    def get(cls, key, default=None):
        return cls._cache.get(key, default)

    @classmethod
    def set(cls, key, value, ttl=300):
        if len(cls._cache) >= cls.MAX_SIZE:
            cls._cache.clear()
            cls._timestamps.clear()
        cls._cache[key] = value
        cls._timestamps[key] = time.time() + ttl

    @classmethod
    def is_valid(cls, key):
        if key not in cls._timestamps:
            return False
        return time.time() < cls._timestamps[key]

    @classmethod
    def cleanup(cls):
        now = time.time()
        expired = [k for k, t in cls._timestamps.items() if now >= t]
        for key in expired:
            cls._cache.pop(key, None)
            cls._timestamps.pop(key, None)

    @classmethod
    def clear(cls):
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
            except Exception:
                pass
        _log_file_handle = open(log_file, "a", encoding='utf-8')
        _log_file_path = log_file
    
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        _log_file_handle.write(f"{timestamp} - {message}\n")
        _log_file_handle.flush()  # Немедленная запись
    except Exception:
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
    """Загрузка всех файлов бота с обновлением version.md"""
    bot_dir = os.path.dirname(__file__)
    core_dir = os.path.join(bot_dir, 'core')
    
    # Основные файлы бота
    bot_files = [
        # Основные файлы
        'handlers.py', 'menu.py', 'utils.py', 'main.py', 'version.md',
        # Конфигурация
        'bot_config.py',
    ]
    
    # Core модули
    core_files = [
        'config.py', 'env_parser.py', 'http_client.py',
        'logging.py', 'logging_async.py', 'parsers.py',
        'services.py', 'validators.py', 'backup.py',
        'handlers_shared.py', '__init__.py'
    ]
    
    # Init скрипты
    init_scripts = ['S99telegram_bot', 'S99unblock']
    
    errors = []
    
    # Загрузка основных файлов бота
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
            error_msg = f"Ошибка при загрузке {filename}: {str(e)}"
            log_error(error_msg)
            errors.append(error_msg)
    
    # Загрузка core модулей
    for filename in core_files:
        try:
            url = f"{config.base_url}/src/core/{filename}"
            local_path = os.path.join(core_dir, filename)
            # Создаём директорию core если не существует
            if not os.path.exists(core_dir):
                os.makedirs(core_dir, exist_ok=True)
            response = get_http_session().get(url, timeout=30, stream=True)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except Exception as e:
            error_msg = f"Ошибка при загрузке core/{filename}: {str(e)}"
            log_error(error_msg)
            errors.append(error_msg)
    
    # Загрузка init скриптов
    for script_name in init_scripts:
        try:
            url = f"{config.bot_url}/{script_name}"
            local_path = os.path.join(bot_dir, script_name)
            response = get_http_session().get(url, timeout=30, stream=True)
            response.raise_for_status()
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            # Установка прав на выполнение
            os.chmod(local_path, 0o0755)
        except Exception as e:
            error_msg = f"Ошибка при загрузке {script_name}: {str(e)}"
            log_error(error_msg)
            errors.append(error_msg)
    
    # Загрузка обновлённого keensnap.sh
    try:
        keensnap_url = f"{config.base_url}/deploy/backup/keensnap/keensnap.sh"
        keensnap_path = config.paths.get("script_bu", "/opt/root/KeenSnap/keensnap.sh")
        keensnap_dir = os.path.dirname(keensnap_path)
        if not os.path.exists(keensnap_dir):
            os.makedirs(keensnap_dir, exist_ok=True)
        download_script(keensnap_url, keensnap_path)
    except Exception as e:
        error_msg = f"Ошибка при загрузке keensnap.sh: {str(e)}"
        log_error(error_msg)
        errors.append(error_msg)
    
    # Если есть критические ошибки (основные файлы), прерываем
    critical_errors = [e for e in errors if 'main.py' in e or 'handlers.py' in e or 'utils.py' in e]
    if critical_errors:
        raise Exception("Критические ошибки загрузки: " + "; ".join(critical_errors))
    
    # Предупреждение о не критических ошибках
    if errors:
        log_error(f"Не критические ошибки загрузки: {len(errors)} файлов")


# =============================================================================
# ВАЛИДАЦИЯ ДАННЫХ (ОПТИМИЗИРОВАНО)
# =============================================================================

def validate_bypass_entry(entry):
    """Упрощённая проверка записи списка обхода."""
    entry = entry.strip()
    if not entry:
        return False
    if entry.startswith('#'):
        return True
    if '.' in entry and len(entry) < 253:
        parts = entry.split('.')
        if len(parts) == 4:
            try:
                return all(0 <= int(p) <= 255 for p in parts)
            except ValueError:
                pass
        return True
    if ':' in entry:
        return True
    return False


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
        except (OSError, IOError):
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
        except (OSError, IOError):
            mtime = time.time()

        Cache.set(cache_key, {'data': data, 'mtime': mtime}, ttl=60)

        return data
    except Exception:
        return []


def save_bypass_list(filepath, sites):
    """
    Сохранение списка обхода.
    - Сохранение в исходном порядке (без сортировки)
    - Поддержка комментариев (#)
    - Атомарная запись (через .tmp файл)
    - Очистка кэша после сохранения
    """
    try:
        # Атомарная запись через временный файл
        temp_path = filepath + '.tmp'
        with open(temp_path, 'w', encoding='utf-8') as f:
            # Сохраняем в исходном порядке
            f.write('\n'.join(sites))
        
        # Атомарная замена файла
        os.replace(temp_path, filepath)

        # Очистка кэша для этого файла
        cache_key = f'bypass:{filepath}'
        Cache._cache.pop(cache_key, None)
        Cache._timestamps.pop(cache_key, None)

    except Exception as e:
        log_error(f"Ошибка при сохранении списка обхода: {str(e)}")
        # Очистка временного файла при ошибке
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except (OSError, IOError):
            pass
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

            # Не отправляем сообщение - оно уже отправлено в handle_update()
            # Просто очищаем файл
            os.remove(chat_id_path)
        except Exception as e:
            log_error(f"Ошибка при очистке chat_id_path: {str(e)}")
            try:
                os.remove(chat_id_path)
            except (OSError, IOError):
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
        import json
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
    import re
    
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

        elif stripped.startswith("size:") and current_drive is not None:
            # Получаем размер раздела в MB и конвертируем в GB
            try:
                size_mb = int(stripped.split(":", 1)[1].strip())
                current_drive['size'] = round(size_mb / 1024, 1)
            except (ValueError, IndexError):
                current_drive['size'] = 'N/A'

    if current_drive:
        drives.append(current_drive)

    # Если размер не получен из ndmc, пробуем получить через df
    for drive in drives:
        if drive.get('size') == 'N/A' or drive.get('size') is None:
            try:
                # Пробуем разные пути монтирования
                possible_paths = [
                    f"/tmp/mnt/{drive['uuid']}",
                    f"/mnt/{drive['uuid']}",
                    drive.get('path', f"/tmp/mnt/{drive['uuid']}")
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        # Получаем размер через df (используем -h для человекочитаемого формата)
                        df_output = subprocess.check_output(
                            ["df", "-h", path],
                            text=True,
                            stderr=subprocess.STDOUT
                        )
                        # Парсим вывод df: Filesystem Size Used Avail Use% Mounted
                        lines = df_output.strip().split('\n')
                        if len(lines) >= 2:
                            parts = lines[1].split()
                            if len(parts) >= 4:
                                # Available[3] = "14G" или "14.5G" → 14.5
                                available_str = parts[3].replace('G', '').replace('M', '')
                                try:
                                    drive['size'] = round(float(available_str), 1)
                                except ValueError:
                                    drive['size'] = 'N/A'
                                break
                
                # Если ни один путь не подошёл
                if drive.get('size') is None or drive.get('size') == 'N/A':
                    # Пробуем получить размер из /proc/partitions или оставляем N/A
                    drive['size'] = 'N/A'
                    
            except Exception as e:
                log_error(f"Error getting disk size: {e}")
                drive['size'] = 'N/A'

    return drives


# =============================================================================
# ОЧИСТКА ПАМЯТИ
# =============================================================================

def cleanup_memory():
    """Принудительная очистка памяти (вызывать периодически)"""
    import gc
    Cache.cleanup()
    gc.collect()


# =============================================================================
# BACKUP (заглушка)
# =============================================================================

def create_backup_with_params(bot, chat_id, backup_state, selected_drive, progress_msg_id):
    """Создание бэкапа с параметрами"""
    try:
        bot.edit_message_text("⏳ Создание бэкапа...", chat_id, progress_msg_id)

        # Получаем путь к диску
        drive_path = selected_drive.get('path', '/tmp/mnt')
        archive_path = f"{drive_path}/backup_{time.strftime('%Y%m%d_%H%M%S')}.tar.gz"
        
        # Формируем список файлов для бэкапа на основе выбора
        # Используем список файлов вместо tar args для надёжности
        files_to_backup = []
        files_added = []
        
        # Конфигурация (обязательно)
        if backup_state.startup_config:
            if os.path.exists("/opt/etc/bot"):
                files_to_backup.append("/opt/etc/bot")
                files_added.append("bot")
            if os.path.exists("/opt/etc/unblock"):
                files_to_backup.append("/opt/etc/unblock")
                files_added.append("unblock")
            if os.path.exists("/opt/etc/tor"):
                files_to_backup.append("/opt/etc/tor")
                files_added.append("tor")
            if os.path.exists("/opt/etc/xray"):
                files_to_backup.append("/opt/etc/xray")
                files_added.append("xray")
            if os.path.exists("/opt/etc/trojan"):
                files_to_backup.append("/opt/etc/trojan")
                files_added.append("trojan")
            if os.path.exists("/opt/etc/shadowsocks.json"):
                files_to_backup.append("/opt/etc/shadowsocks.json")
                files_added.append("shadowsocks.json")
        
        # Прошивка (startup-config.txt в корне или /tmp/)
        if backup_state.firmware:
            # Проверяем несколько возможных путей
            firmware_paths = [
                "/startup-config.txt",
                "/tmp/startup-config.txt",
                "/opt/startup-config.txt",
                "/mnt/startup-config.txt"
            ]
            for fw_path in firmware_paths:
                if os.path.exists(fw_path):
                    files_to_backup.append(fw_path)
                    files_added.append("startup-config.txt")
                    break
            else:
                # Если файл не найден, пробуем получить через ndmc
                try:
                    # Сохраняем конфиг роутера через ndmc
                    # Правильный синтаксис: copy <source> <destination>
                    # Для Keenetic нужно указывать файловую систему: sys:/ или usb:/
                    temp_fw = "sys:/tmp/backup_startup_config.txt"
                    result = subprocess.run(
                        ["ndmc", "-c", f"copy startup-config {temp_fw}"],
                        timeout=30, capture_output=True, text=True
                    )
                    log_error(f"ndmc copy startup-config: returncode={result.returncode}, stdout={result.stdout}, stderr={result.stderr}")
                    if result.returncode == 0:
                        # Копируем из sys:/tmp в /tmp для доступа
                        subprocess.run(["cp", temp_fw.replace("sys:", ""), "/tmp/backup_startup_config.txt"])
                        if os.path.exists("/tmp/backup_startup_config.txt"):
                            files_to_backup.append("/tmp/backup_startup_config.txt")
                            files_added.append("startup-config.txt (ndmc)")
                    else:
                        # Пробуем альтернативный способ: показать конфиг
                        result2 = subprocess.run(
                            ["ndmc", "-c", "show startup-config"],
                            timeout=30, capture_output=True, text=True
                        )
                        log_error(f"ndmc show startup-config: returncode={result2.returncode}, len={len(result2.stdout)}")
                        if result2.returncode == 0 and result2.stdout:
                            with open("/tmp/backup_startup_config.txt", 'w') as f:
                                f.write(result2.stdout)
                            files_to_backup.append("/tmp/backup_startup_config.txt")
                            files_added.append("startup-config.txt (show)")
                except Exception as e:
                    log_error(f"Failed to get startup-config: {e}")
                    # Игнорируем, если файл не найден
            
            # Прошивка роутера (firmware.bin)
            try:
                temp_bin = "sys:/tmp/backup_firmware.bin"
                # Используем правильный синтаксис: copy flash/firmware <destination>
                result = subprocess.run(
                    ["ndmc", "-c", f"copy flash/firmware {temp_bin}"],
                    timeout=300, capture_output=True, text=True
                )
                log_error(f"ndmc copy flash/firmware: returncode={result.returncode}, stdout={result.stdout}, stderr={result.stderr}")
                if result.returncode == 0:
                    # Копируем из sys:/tmp в /tmp для доступа
                    subprocess.run(["cp", temp_bin.replace("sys:", ""), "/tmp/backup_firmware.bin"])
                    if os.path.exists("/tmp/backup_firmware.bin"):
                        files_to_backup.append("/tmp/backup_firmware.bin")
                        files_added.append("firmware.bin")
                else:
                    log_error(f"Failed to copy firmware: {result.stderr}")
            except Exception as e:
                log_error(f"Failed to get firmware: {e}")
                # Игнорируем, если прошивка не найдена
        
        # Entware
        if backup_state.entware:
            if os.path.exists("/opt/root/KeenSnap"):
                files_to_backup.append("/opt/root/KeenSnap")
                files_added.append("KeenSnap")
            if os.path.exists("/opt/root/script.sh"):
                files_to_backup.append("/opt/root/script.sh")
                files_added.append("script.sh")
            # Проверяем оба пути для init скриптов
            if os.path.exists("/opt/etc/init.d/S99telegram_bot"):
                files_to_backup.append("/opt/etc/init.d/S99telegram_bot")
                files_added.append("S99telegram_bot")
            elif os.path.exists("/opt/etc/bot/S99telegram_bot"):
                files_to_backup.append("/opt/etc/bot/S99telegram_bot")
                files_added.append("S99telegram_bot (bot/)")
            if os.path.exists("/opt/etc/init.d/S99unblock"):
                files_to_backup.append("/opt/etc/init.d/S99unblock")
                files_added.append("S99unblock")
            elif os.path.exists("/opt/etc/bot/S99unblock"):
                files_to_backup.append("/opt/etc/bot/S99unblock")
                files_added.append("S99unblock (bot/)")
            if os.path.exists("/opt/etc/crontab"):
                files_to_backup.append("/opt/etc/crontab")
                files_added.append("crontab")
            if os.path.exists("/opt/etc/dnsmasq.conf"):
                files_to_backup.append("/opt/etc/dnsmasq.conf")
                files_added.append("dnsmasq.conf")
        
        # Логирование для отладки
        log_error(f"Backup files to add: {files_added}")
        log_error(f"Backup paths: {files_to_backup}")
        
        # Создание бэкапа
        if not files_to_backup:
            # Если ничего не выбрано или файлы не найдены
            if backup_state.startup_config or backup_state.entware:
                raise Exception("Нет файлов для бэкапа. Проверьте, установлены ли компоненты.")
            elif backup_state.firmware:
                # Если выбрана только прошивка, но она не сохранилась — предупреждение, но не ошибка
                log_error("Warning: Firmware backup failed, but continuing with empty backup")
                # Создаём пустой маркер бэкапа
                with open(archive_path, 'w') as f:
                    f.write("# Backup failed - no files available\n")
                    f.write(f"# Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                file_size_mb = 0.001
                archive_path_safe = archive_path.replace('_', '\\_')
                bot.edit_message_text(
                    f"⚠️ Не удалось сохранить прошивку роутера\n\n"
                    f"📦 Пустой архив создан: `{archive_path_safe}`\n"
                    f"💾 Размер: 0.001 MB\n"
                    f"❌ Причина: ndmc не вернул данные\n\n"
                    f"📝 Попробуйте вручную:\n"
                    f"```bash\n"
                    f"ndmc -c \"copy startup-config /tmp/config.txt\"\n"
                    f"ndmc -c \"copy flash/firmware /tmp/firmware.bin\"\n"
                    f"```",
                    chat_id, progress_msg_id,
                    parse_mode='Markdown'
                )
                return
            else:
                raise Exception("Не выбраны компоненты для бэкапа.")
        
        # Создаём tar с абсолютными путями
        tar_args = ["tar", "-czf", archive_path] + files_to_backup
        result = subprocess.run(tar_args, timeout=300, capture_output=True, text=True)
        
        # Проверяем наличие фатальных ошибок (не предупреждений)
        fatal_errors = [l for l in result.stderr.split('\n') 
                       if l and 'No such file' not in l and 'Removing leading' not in l]
        
        if result.returncode != 0 and fatal_errors:
            raise Exception(f"tar error: {' '.join(fatal_errors)}")

        if os.path.exists(archive_path):
            file_size_mb = round(os.path.getsize(archive_path) / 1024 / 1024, 1)
            
            if file_size_mb < 0.5:
                log_error(f"Warning: Backup size too small: {file_size_mb} MB, files: {files_added}")

            # Экранируем подчёркивания для Markdown
            files_added_escaped = [f.replace('_', '\\_') for f in files_added]
            archive_path_escaped = archive_path.replace('_', '\\_')

            # Не отправляем файл (превышает лимит Telegram 50 MB)
            # Показываем информацию и инструкцию по скачиванию
            bot.edit_message_text(
                f"✅ Бэкап успешно создан\\!\n\n"
                f"📦 Архив: `{archive_path_escaped}`\n"
                f"💾 Размер: {file_size_mb} MB\n"
                f"📁 Файлы: {', '.join(files_added_escaped)}\n"
                f"⏱️ Время: {time.strftime('%H:%M:%S')}\\n\n"
                f"📥 **Как скачать:**\\n\n"
                f"**1\\. Через Telegram Desktop:**\\n"
                f"   Файл слишком большой для отправки\\n\n"
                f"**2\\. Через SSH \\(рекомендуется\\):**\\n"
                f"   ```bash\n"
                f"   scp root@192\\.168\\.1\\.1:{archive_path_escaped} ~/Downloads/\n"
                f"   ```\\n\n"
                f"**3\\. Через WinSCP/FileZilla:**\\n"
                f"   \\- Хост: `192\\.168\\.1\\.1`\\n"
                f"   \\- Пользователь: `root`\\n"
                f"   \\- Пароль: `ваш пароль`\\n"
                f"   \\- Путь: `{archive_path_escaped}`",
                chat_id, progress_msg_id,
                parse_mode='Markdown'
            )
        else:
            bot.edit_message_text("❌ Не удалось создать бэкап", chat_id, progress_msg_id)

    except subprocess.TimeoutExpired:
        bot.edit_message_text("❌ Таймаут создания бэкапа", chat_id, progress_msg_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка: {str(e)}", chat_id, progress_msg_id)
        log_error(f"Backup error: {e}")
