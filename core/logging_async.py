# =============================================================================
# CORE LOGGING - ОПТИМИЗИРОВАННОЕ ЛОГИРОВАНИЕ
# =============================================================================
# Асинхронное логирование для embedded-устройств
# =============================================================================

import os
import time
import json
import threading
import queue
from datetime import datetime
from typing import Optional, Dict, Any


# =============================================================================
# КОНСТАНТЫ
# =============================================================================

LOG_LEVELS = {
    'DEBUG': 10,
    'INFO': 20,
    'WARNING': 30,
    'ERROR': 40,
    'CRITICAL': 50
}

DEFAULT_LOG_LEVEL = 'INFO'
DEFAULT_MAX_SIZE = 512 * 1024  # 512 KB
DEFAULT_MAX_BACKUPS = 3
DEFAULT_QUEUE_SIZE = 100


# =============================================================================
# АСИНХРОННЫЙ ЛОГГЕР
# =============================================================================

class AsyncLogger:
    """
    Асинхронный логгер для embedded-устройств.
    
    Преимущества:
    - Неблокирующая запись в лог
    - Автоматическая ротация файлов
    - JSON формат для структурированного логирования
    - Потокобезопасность
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, log_file: str = '/opt/etc/bot/error.log',
                 log_level: str = DEFAULT_LOG_LEVEL,
                 max_size: int = DEFAULT_MAX_SIZE,
                 max_backups: int = DEFAULT_MAX_BACKUPS,
                 queue_size: int = DEFAULT_QUEUE_SIZE,
                 use_json: bool = False):
        """
        Инициализация логгера.
        
        Args:
            log_file (str): Путь к лог файлу
            log_level (str): Уровень логирования
            max_size (int): Максимальный размер файла в байтах
            max_backups (int): Максимальное количество бэкапов
            queue_size (int): Размер очереди логов
            use_json (bool): Использовать JSON формат
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.log_file = log_file
        self.log_level = LOG_LEVELS.get(log_level, DEFAULT_LOG_LEVEL)
        self.max_size = max_size
        self.max_backups = max_backups
        self.use_json = use_json
        
        # Очередь для асинхронной записи
        self._queue = queue.Queue(maxsize=queue_size)
        
        # Флаг остановки
        self._stop_event = threading.Event()
        
        # Запуск worker потока
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()
        
        self._initialized = True
    
    def _worker(self):
        """Worker поток для записи логов"""
        while not self._stop_event.is_set():
            try:
                # Получение записи из очереди (с таймаутом)
                try:
                    record = self._queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Запись в файл
                self._write_record(record)
                
                # Проверка размера файла
                self._rotate_if_needed()
                
            except Exception as e:
                # Игнорируем ошибки в worker (логгер не должен ломать приложение)
                pass
    
    def _write_record(self, record: Dict[str, Any]):
        """Запись записи в лог файл"""
        try:
            # Убедимся что директория существует
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                if self.use_json:
                    f.write(json.dumps(record) + '\n')
                else:
                    timestamp = record.get('timestamp', '')
                    level = record.get('level', 'INFO')
                    message = record.get('message', '')
                    f.write(f"{timestamp} - {level} - {message}\n")
                
                f.flush()  # Немедленная запись
                
        except IOError:
            pass  # Логирование не должно ломать приложение
    
    def _rotate_if_needed(self):
        """Ротация логов если размер превышен"""
        if not os.path.exists(self.log_file):
            return
        
        file_size = os.path.getsize(self.log_file)
        
        if file_size <= self.max_size:
            return
        
        # Ротация
        try:
            # Удаляем самый старый бэкап
            oldest_backup = f"{self.log_file}.{self.max_backups}"
            if os.path.exists(oldest_backup):
                os.remove(oldest_backup)
            
            # Сдвигаем бэкапы
            for i in range(self.max_backups - 1, 0, -1):
                src = f"{self.log_file}.{i}"
                dst = f"{self.log_file}.{i + 1}"
                if os.path.exists(src):
                    os.rename(src, dst)
            
            # Текущий файл -> бэкап 1
            backup_1 = f"{self.log_file}.1"
            if os.path.exists(backup_1):
                os.remove(backup_1)
            os.rename(self.log_file, backup_1)
            
        except Exception:
            pass  # Игнорируем ошибки ротации
    
    def log(self, level: str, message: str, **kwargs):
        """
        Запись записи в лог.
        
        Args:
            level (str): Уровень логирования
            message (str): Сообщение
            **kwargs: Дополнительные поля для JSON формата
        """
        if LOG_LEVELS.get(level, 0) < self.log_level:
            return
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        
        try:
            self._queue.put_nowait(record)
        except queue.Full:
            # Очередь переполнена - пропускаем запись (не блокируем приложение)
            pass
    
    def debug(self, message: str, **kwargs):
        """Debug уровень"""
        self.log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Info уровень"""
        self.log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Warning уровень"""
        self.log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Error уровень"""
        self.log('ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Critical уровень"""
        self.log('CRITICAL', message, **kwargs)
    
    def flush(self):
        """Принудительная запись всех записей"""
        while not self._queue.empty():
            try:
                record = self._queue.get_nowait()
                self._write_record(record)
            except queue.Empty:
                break
    
    def close(self):
        """Остановка логгера"""
        self._stop_event.set()
        self._worker_thread.join(timeout=2.0)
        self.flush()


# =============================================================================
# ГЛОБАЛЬНЫЙ ЛОГГЕР
# =============================================================================

_logger: Optional[AsyncLogger] = None


def init_logger(log_file: str = '/opt/etc/bot/error.log',
                log_level: str = DEFAULT_LOG_LEVEL,
                max_size: int = DEFAULT_MAX_SIZE,
                max_backups: int = DEFAULT_MAX_BACKUPS,
                queue_size: int = DEFAULT_QUEUE_SIZE,
                use_json: bool = False) -> AsyncLogger:
    """
    Инициализация глобального логгера.
    
    Args:
        log_file (str): Путь к лог файлу
        log_level (str): Уровень логирования
        max_size (int): Максимальный размер файла в байтах
        max_backups (int): Максимальное количество бэкапов
        queue_size (int): Размер очереди логов
        use_json (bool): Использовать JSON формат
    
    Returns:
        AsyncLogger: Глобальный логгер
    """
    global _logger
    _logger = AsyncLogger(
        log_file=log_file,
        log_level=log_level,
        max_size=max_size,
        max_backups=max_backups,
        queue_size=queue_size,
        use_json=use_json
    )
    return _logger


def get_logger() -> Optional[AsyncLogger]:
    """Получение глобального логгера"""
    return _logger


# =============================================================================
# СОВМЕСТИМОСТЬ СО СТАРЫМ API
# =============================================================================

def log_error(message: str):
    """
    Запись ошибки (для совместимости со старым кодом).
    
    Args:
        message (str): Сообщение об ошибке
    """
    global _logger
    if _logger:
        _logger.error(message)
    else:
        # Fallback: синхронная запись
        log_file = '/opt/etc/bot/error.log'
        try:
            from core.config import config
            log_file = config.paths.get('error_log', log_file)
        except ImportError:
            pass
        
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{timestamp} - {message}\n")
        except IOError:
            pass


def clean_log(log_file: str = None, max_size: int = DEFAULT_MAX_SIZE, max_lines: int = 50):
    """
    Очистка лога (для совместимости со старым кодом).
    
    Args:
        log_file (str): Путь к лог файлу
        max_size (int): Максимальный размер файла в байтах
        max_lines (int): Количество строк для сохранения
    """
    if log_file is None:
        try:
            from core.config import config
            log_file = config.paths.get('error_log', '/opt/etc/bot/error.log')
        except ImportError:
            log_file = '/opt/etc/bot/error.log'
    
    if not os.path.exists(log_file):
        return
    
    file_size = os.path.getsize(log_file)
    
    if file_size <= max_size:
        return
    
    # Читаем только последние N строк
    with open(log_file, 'rb') as f:
        lines = []
        f.seek(0, 2)
        file_size = f.tell()
        block_size = min(file_size, 1024 * 1024)
        f.seek(max(0, file_size - block_size))
        
        for line in f:
            lines.append(line)
        
        lines = lines[-max_lines:]
    
    with open(log_file, 'wb') as f:
        f.writelines(lines)
