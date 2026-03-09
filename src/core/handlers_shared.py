# =============================================================================
# CORE HANDLERS SHARED - Общие обработчики для bot3 и botlight
# =============================================================================
# Вынесены общие функции для избежания дублирования кода
# =============================================================================

import os
import time
import subprocess
import requests


def get_local_version(bot_dir=None):
    """Получение локальной версии бота"""
    if bot_dir is None:
        bot_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    version_file = os.path.join(bot_dir, "version.md")
    try:
        with open(version_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "N/A"


def get_remote_version(bot_url, get_session_func, timeout=10):
    """Получение удалённой версии бота"""
    try:
        session = get_session_func()
        headers = {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        response = session.get(
            f"{bot_url}/version.md?t={int(time.time())}",
            headers=headers,
            timeout=timeout
        )
        return response.text.strip() if response.status_code == 200 else "N/A"
    except requests.exceptions.Timeout:
        return "N/A (timeout)"
    except requests.exceptions.RequestException:
        return "N/A (error)"


def get_system_stats(bot_pid=None, service_list=None, timeout_status=2):
    """
    Получение системной статистики.
    
    Args:
        bot_pid: PID бота (по умолчанию текущий)
        service_list: Список кортежей (имя, init_script) для проверки статусов
        timeout_status: Таймаут проверки статуса сервиса
    
    Returns:
        dict: Статистика системы
    """
    if bot_pid is None:
        bot_pid = os.getpid()
    
    stats = {
        'bot_ram_mb': 0,
        'system_ram_total_mb': 0,
        'system_ram_free_mb': 0,
        'cpu_usage_percent': 0,
        'bot_uptime': 'N/A',
        'restart_count': 0,
    }
    
    # RAM бота
    try:
        with open(f'/proc/{bot_pid}/status', 'r') as f:
            for line in f:
                if line.startswith('VmRSS:'):
                    stats['bot_ram_mb'] = int(line.split()[1]) / 1024
                    break
    except Exception:
        pass
    
    # Системная RAM
    try:
        meminfo = subprocess.check_output(['cat', '/proc/meminfo'], text=True)
        for line in meminfo.splitlines():
            if line.startswith('MemTotal:'):
                stats['system_ram_total_mb'] = int(line.split()[1]) / 1024
            elif line.startswith('MemAvailable:'):
                stats['system_ram_free_mb'] = int(line.split()[1]) / 1024
                break
    except Exception:
        pass
    
    # CPU usage (упрощённо - без задержки)
    try:
        with open('/proc/stat', 'r') as f:
            line = f.readline()
            if line.startswith('cpu '):
                values = list(map(int, line.split()[1:]))
                idle = values[3] if len(values) > 3 else 0
                total = sum(values)
                if total > 0:
                    stats['cpu_usage_percent'] = round((1 - idle / total) * 100)
    except Exception:
        pass
    
    # Uptime
    try:
        uptime_seconds = float(subprocess.check_output(['cat', '/proc/uptime'], text=True).split()[0])
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        stats['bot_uptime'] = f"{hours}ч {minutes}мин"
    except Exception:
        pass
    
    # Restart count
    try:
        with open('/opt/etc/bot/restart_count.txt', 'r') as f:
            stats['restart_count'] = int(f.read().strip())
    except (FileNotFoundError, ValueError, IOError):
        stats['restart_count'] = 0
    
    # Статусы сервисов (если указаны)
    if service_list:
        for service_name, init_script, stat_key in service_list:
            try:
                result = subprocess.run(
                    [init_script, 'status'], 
                    capture_output=True, 
                    text=True, 
                    timeout=timeout_status
                )
                status = '✅' if result.returncode == 0 else '❌'
            except Exception:
                status = '❓'
            stats[stat_key] = status
    
    return stats


def format_stats_basic(stats):
    """Базовая форматировка статистики"""
    return (
        f"📊 Статистика бота\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🧠 RAM бота: {stats['bot_ram_mb']:.1f} MB\n"
        f"💻 Система: {stats['system_ram_free_mb']:.0f}/{stats['system_ram_total_mb']:.0f} MB свободно\n"
        f"⏱️ Uptime: {stats['bot_uptime']}\n"
        f"🔄 Перезапусков: {stats['restart_count']}"
    )


def format_stats_with_services(stats, service_formats):
    """Расширенная форматировка статистики с сервисами"""
    msg = format_stats_basic(stats)
    msg += "\n\n"
    for label, key in service_formats:
        if key in stats:
            msg += f"{label}: {stats[key]}\n"
    return msg.strip()


def log_error(message, error_log_path=None):
    """Запись ошибки в лог"""
    if error_log_path is None:
        error_log_path = "/opt/etc/bot/error.log"
    try:
        with open(error_log_path, "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
    except Exception:
        pass
