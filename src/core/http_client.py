# =============================================================================
# CORE HTTP CLIENT
# =============================================================================
# HTTP клиент с connection pooling для bot3 и botlight
# =============================================================================

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Глобальная сессия для connection pooling
_http_session = None


def reset_http_session():
    """
    Сброс HTTP сессии (для использования при обновлении).
    
    Нужно вызывать при /update чтобы избежать кэширования GitHub.
    """
    global _http_session
    if _http_session is not None:
        _http_session.close()
        _http_session = None


def get_http_session():
    """
    Получение HTTP сессии с connection pooling.
    
    Преимущества:
    - Переиспользование TCP соединений
    - Автоматический retry при ошибках (3 попытки)
    - Экономия памяти и CPU
    
    Returns:
        requests.Session: Настроенная HTTP сессия
    """
    global _http_session
    
    if _http_session is None:
        _http_session = requests.Session()
        
        # Настройка retry logic
        retry = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=1,
            pool_maxsize=2
        )
        _http_session.mount("http://", adapter)
        _http_session.mount("https://", adapter)
    
    return _http_session


def download_script(script_url, script_path, timeout=30):
    """
    Загрузка скрипта с использованием connection pooling.
    
    Args:
        script_url (str): URL для загрузки скрипта
        script_path (str): Путь для сохранения скрипта
        timeout (int): Таймаут загрузки в секундах
    
    Returns:
        bool: True если загрузка успешна
    
    Raises:
        requests.exceptions.Timeout: Превышен таймаут
        requests.exceptions.RequestException: Ошибка сети
    """
    from .logging import log_error
    import os
    
    session = get_http_session()
    
    try:
        # Потоковая загрузка для экономии памяти
        response = session.get(script_url, timeout=timeout, stream=True)
        response.raise_for_status()
        
        # Запись напрямую в файл (без загрузки в память)
        with open(script_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Установка прав на выполнение
        os.chmod(script_path, 0o0755)
        
        return True
        
    except requests.exceptions.Timeout:
        log_error(f"Ошибка при загрузке скрипта: превышен таймаут ({timeout}с)")
        raise
        
    except requests.exceptions.RequestException as e:
        log_error(f"Ошибка при загрузке скрипта: {str(e)}")
        raise
