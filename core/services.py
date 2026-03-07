# =============================================================================
# CORE SERVICES - АБСТРАКЦИИ СЕРВИСОВ
# =============================================================================
# Базовые классы для управления сервисами (Tor, Xray, Shadowsocks)
# =============================================================================

import subprocess
import logging
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple


logger = logging.getLogger(__name__)


class SystemService(ABC):
    """
    Базовый абстрактный класс для системных сервисов.
    
    Предоставляет интерфейс для запуска, остановки и перезапуска сервисов.
    """
    
    def __init__(self, init_script: str, name: str):
        """
        Инициализация сервиса.
        
        Args:
            init_script: Путь к init скрипту
            name: Название сервиса
        """
        self.init_script = init_script
        self.name = name
    
    @abstractmethod
    def start(self) -> Tuple[bool, Optional[str]]:
        """
        Запуск сервиса.
        
        Returns:
            (success, error_message)
        """
        pass
    
    @abstractmethod
    def stop(self) -> Tuple[bool, Optional[str]]:
        """
        Остановка сервиса.
        
        Returns:
            (success, error_message)
        """
        pass
    
    @abstractmethod
    def restart(self) -> Tuple[bool, Optional[str]]:
        """
        Перезапуск сервиса.
        
        Returns:
            (success, error_message)
        """
        pass
    
    def status(self) -> Tuple[bool, Optional[str]]:
        """
        Проверка статуса сервиса.
        
        Returns:
            (is_running, status_message)
        """
        try:
            result = subprocess.run(
                [self.init_script, 'status'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip() or "Service is stopped"
                
        except subprocess.TimeoutExpired:
            return False, "Status check timeout"
        except Exception as e:
            return False, str(e)
    
    def _run_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Выполнение команды управления сервисом.
        
        Args:
            command: Команда (start, stop, restart)
            
        Returns:
            (success, error_message)
        """
        try:
            result = subprocess.run(
                [self.init_script, command],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return True, None
            else:
                error = result.stderr.strip() or result.stdout.strip()
                return False, error or f"Unknown error running {command}"
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout running {command} for {self.name}")
            return False, f"Timeout running {command}"
        except Exception as e:
            logger.error(f"Error running {command} for {self.name}: {str(e)}")
            return False, str(e)


class TorService(SystemService):
    """Сервис Tor"""
    
    def __init__(self, init_script: str = '/opt/etc/init.d/S35tor'):
        super().__init__(init_script, 'Tor')
    
    def start(self) -> Tuple[bool, Optional[str]]:
        return self._run_command('start')
    
    def stop(self) -> Tuple[bool, Optional[str]]:
        return self._run_command('stop')
    
    def restart(self) -> Tuple[bool, Optional[str]]:
        return self._run_command('restart')


class XrayService(SystemService):
    """Сервис Xray"""
    
    def __init__(self, init_script: str = '/opt/etc/init.d/S24xray'):
        super().__init__(init_script, 'Xray')
    
    def start(self) -> Tuple[bool, Optional[str]]:
        return self._run_command('start')
    
    def stop(self) -> Tuple[bool, Optional[str]]:
        return self._run_command('stop')
    
    def restart(self) -> Tuple[bool, Optional[str]]:
        return self._run_command('restart')


class ShadowsocksService(SystemService):
    """Сервис Shadowsocks"""
    
    def __init__(self, init_script: str = '/opt/etc/init.d/S22shadowsocks'):
        super().__init__(init_script, 'Shadowsocks')
    
    def start(self) -> Tuple[bool, Optional[str]]:
        return self._run_command('start')
    
    def stop(self) -> Tuple[bool, Optional[str]]:
        return self._run_command('stop')
    
    def restart(self) -> Tuple[bool, Optional[str]]:
        return self._run_command('restart')


class TrojanService(SystemService):
    """Сервис Trojan"""
    
    def __init__(self, init_script: str = '/opt/etc/init.d/S22trojan'):
        super().__init__(init_script, 'Trojan')
    
    def start(self) -> Tuple[bool, Optional[str]]:
        return self._run_command('start')
    
    def stop(self) -> Tuple[bool, Optional[str]]:
        return self._run_command('stop')
    
    def restart(self) -> Tuple[bool, Optional[str]]:
        return self._run_command('restart')


class ServiceManager:
    """
    Менеджер для управления несколькими сервисами.
    """
    
    def __init__(self):
        self.services = {}
    
    def register(self, service: SystemService) -> None:
        """Регистрация сервиса"""
        self.services[service.name] = service
    
    def restart_all(self) -> List[Tuple[str, bool, Optional[str]]]:
        """
        Перезапуск всех зарегистрированных сервисов.
        
        Returns:
            Список (name, success, error_message) для каждого сервиса
        """
        results = []
        for name, service in self.services.items():
            success, error = service.restart()
            results.append((name, success, error))
        return results
    
    def status_all(self) -> List[Tuple[str, bool, Optional[str]]]:
        """
        Проверка статуса всех сервисов.
        
        Returns:
            Список (name, is_running, status_message)
        """
        results = []
        for name, service in self.services.items():
            is_running, status = service.status()
            results.append((name, is_running, status))
        return results
