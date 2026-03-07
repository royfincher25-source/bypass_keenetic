# =============================================================================
# CORE LOGGING
# =============================================================================
# Функции логирования для bot3 и botlight
# =============================================================================

import os
import time


def log_error(message, log_file=None):
    """
    Запись ошибки в лог файл.
    
    Args:
        message (str): Сообщение об ошибке
        log_file (str, optional): Путь к лог файлу. Если не указан, используется путь по умолчанию.
    
    Returns:
        None
    """
    if log_file is None:
        # Импорт конфигурации только при необходимости
        try:
            from .config import config
            log_file = config.paths.get("error_log", "/opt/etc/bot/error.log")
        except ImportError:
            log_file = "/opt/etc/bot/error.log"
    
    # Убедимся что директория существует
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except OSError:
            pass  # Директория уже существует или не можем создать
    
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(f"{timestamp} - {message}\n")
    except IOError:
        pass  # Логирование не должно ломать приложение


def clean_log(log_file, max_size=524288, max_lines=50):
    """
    Очистка лог файла (оставляет только последние N строк).
    
    Args:
        log_file (str): Путь к лог файлу
        max_size (int): Максимальный размер файла в байтах (по умолчанию 512KB)
        max_lines (int): Количество строк для сохранения (по умолчанию 50)
    
    Returns:
        None
    """
    if not os.path.exists(log_file):
        return
    
    file_size = os.path.getsize(log_file)
    
    if file_size <= max_size:
        return  # Файл не требует очистки
    
    # Читаем только последние N строк
    with open(log_file, 'rb') as f:
        lines = []
        f.seek(0, 2)  # В конец
        file_size = f.tell()
        block_size = min(file_size, 1024 * 1024)  # Читаем максимум 1MB
        f.seek(max(0, file_size - block_size))
        
        for line in f:
            lines.append(line)
        
        # Оставляем последние max_lines строк
        lines = lines[-max_lines:]
    
    # Записываем обратно
    with open(log_file, 'wb') as f:
        f.writelines(lines)
