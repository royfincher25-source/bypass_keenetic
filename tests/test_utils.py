# =============================================================================
# UNIT-ТЕСТЫ ДЛЯ УТИЛИТ
# =============================================================================
# Тестирование функций: load_bypass_list, save_bypass_list, download_script
# =============================================================================

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Добавляем корень проекта в path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.bot3.utils import load_bypass_list, save_bypass_list, clean_log


# =============================================================================
# ТЕСТЫ LOAD_BYPASS_LIST
# =============================================================================

class TestLoadBypassList:
    """Тесты для функции load_bypass_list"""
    
    def test_load_existing_file(self, temp_file, sample_domains):
        """Тест загрузки существующего файла"""
        temp_file.write_text('\n'.join(sample_domains))
        
        result = load_bypass_list(str(temp_file))
        
        assert isinstance(result, set)
        assert len(result) == len(sample_domains)
        assert 'example.com' in result
        assert 'google.com' in result
    
    def test_load_nonexistent_file(self):
        """Тест загрузки несуществующего файла"""
        result = load_bypass_list('/nonexistent/path/file.txt')
        
        assert isinstance(result, set)
        assert len(result) == 0
    
    def test_load_empty_file(self, temp_file):
        """Тест загрузки пустого файла"""
        temp_file.write_text('')
        
        result = load_bypass_list(str(temp_file))
        
        assert isinstance(result, set)
        assert len(result) == 0
    
    def test_load_file_with_empty_lines(self, temp_file):
        """Тест загрузки файла с пустыми строками"""
        content = """example.com

google.com

youtube.com
"""
        temp_file.write_text(content)
        
        result = load_bypass_list(str(temp_file))
        
        assert len(result) == 3
        assert '' not in result
    
    def test_load_file_with_whitespace(self, temp_file):
        """Тест загрузки файла с пробелами"""
        content = """  example.com  
google.com
   youtube.com   
"""
        temp_file.write_text(content)
        
        result = load_bypass_list(str(temp_file))
        
        assert len(result) == 3
        assert 'example.com' in result
        assert 'google.com' in result
        assert 'youtube.com' in result
    
    def test_load_file_with_duplicates(self, temp_file):
        """Тест загрузки файла с дубликатами"""
        content = """example.com
google.com
example.com
youtube.com
google.com
"""
        temp_file.write_text(content)
        
        result = load_bypass_list(str(temp_file))
        
        # set должен удалить дубликаты
        assert len(result) == 3


# =============================================================================
# ТЕСТЫ SAVE_BYPASS_LIST
# =============================================================================

class TestSaveBypassList:
    """Тесты для функции save_bypass_list"""
    
    def test_save_new_file(self, temp_dir):
        """Тест сохранения в новый файл"""
        filepath = temp_dir / 'new_list.txt'
        sites = {'example.com', 'google.com'}
        
        save_bypass_list(str(filepath), sites)
        
        assert filepath.exists()
        content = filepath.read_text()
        assert 'example.com' in content
        assert 'google.com' in content
    
    def test_save_sorted(self, temp_dir):
        """Тест сохранения (должно быть отсортировано)"""
        filepath = temp_dir / 'sorted_list.txt'
        sites = {'zebra.com', 'alpha.com', 'beta.com'}
        
        save_bypass_list(str(filepath), sites)
        
        content = filepath.read_text()
        lines = content.strip().split('\n')
        
        # Проверяем, что отсортировано
        assert lines == sorted(lines)
    
    def test_save_overwrite(self, temp_file):
        """Тест перезаписи существующего файла"""
        temp_file.write_text('old_content.com')
        
        sites = {'new1.com', 'new2.com'}
        save_bypass_list(str(temp_file), sites)
        
        content = temp_file.read_text()
        assert 'old_content.com' not in content
        assert 'new1.com' in content
        assert 'new2.com' in content
    
    def test_save_empty_list(self, temp_dir):
        """Тест сохранения пустого списка"""
        filepath = temp_dir / 'empty_list.txt'
        sites = set()
        
        save_bypass_list(str(filepath), sites)
        
        assert filepath.exists()
        content = filepath.read_text()
        assert content == ''
    
    def test_save_with_error(self, monkeypatch):
        """Тест сохранения с ошибкой"""
        def mock_open_error(*args, **kwargs):
            raise IOError("Permission denied")
        
        monkeypatch.setattr('builtins.open', mock_open_error)
        
        with pytest.raises(IOError):
            save_bypass_list('/protected/file.txt', {'example.com'})


# =============================================================================
# ТЕСТЫ CLEAN_LOG
# =============================================================================

class TestCleanLog:
    """Тесты для функции clean_log"""
    
    def test_clean_nonexistent_file(self, temp_dir):
        """Тест очистки несуществующего файла"""
        filepath = temp_dir / 'nonexistent.log'
        
        # Не должно вызывать ошибок
        clean_log(str(filepath))
        
        # Файл должен быть создан
        assert filepath.exists()
    
    def test_clean_small_file(self, temp_file):
        """Тест очистки маленького файла (< 512KB)"""
        temp_file.write_text('small content')
        original_size = temp_file.stat().st_size
        
        clean_log(str(temp_file))
        
        # Файл не должен измениться
        assert temp_file.stat().st_size == original_size
    
    def test_clean_large_file(self, temp_file, monkeypatch):
        """Тест очистки большого файла (> 512KB)"""
        # Создаём "большой" файл ( mock )
        large_content = 'line\n' * 20000  # ~100KB
        temp_file.write_text(large_content)
        
        # Мок для os.path.getsize чтобы вернуть большой размер
        original_getsize = os.path.getsize
        monkeypatch.setattr(os.path, 'getsize', lambda x: 600000)
        
        clean_log(str(temp_file))
        
        # Файл должен быть обрезан до последних 50 строк
        content = temp_file.read_text()
        lines = content.strip().split('\n')
        assert len(lines) <= 50


# =============================================================================
# ТЕСТЫ DOWNLOAD_SCRIPT
# =============================================================================

class TestDownloadScript:
    """Тесты для функции download_script"""
    
    @pytest.fixture
    def mock_config(self, monkeypatch, tmp_path):
        """Mock конфигурации для download_script"""
        script_path = tmp_path / 'script.sh'
        
        class MockConfig:
            bot_url = 'https://example.com/bot3'
            paths = {
                'script_sh': str(script_path)
            }
        
        config = MockConfig()
        
        # Инжектим конфиг в модуль
        import bot3.utils as utils
        monkeypatch.setattr(utils, 'config', config)
        
        return config
    
    def test_download_success(self, mock_config, mock_requests_get, monkeypatch):
        """Тест успешной загрузки"""
        mock_requests_get.return_value.content = b'#!/bin/sh\necho "test"'
        mock_requests_get.return_value.raise_for_status = MagicMock()
        
        from bot3.utils import download_script
        download_script()
        
        # Проверяем, что файл создан
        assert os.path.exists(mock_config.paths['script_sh'])
        
        # Проверяем, что requests.get был вызван с таймаутом
        mock_requests_get.assert_called_once()
        call_kwargs = mock_requests_get.call_args[1]
        assert 'timeout' in call_kwargs
        assert call_kwargs['timeout'] == 30
    
    def test_download_timeout(self, mock_config, mock_requests_timeout, monkeypatch):
        """Тест загрузки с таймаутом"""
        from bot3.utils import download_script
        
        with pytest.raises(Exception):  # TimeoutException будет проброшен
            download_script()
    
    def test_download_request_error(self, mock_config, mock_requests_error, monkeypatch):
        """Тест загрузки с ошибкой сети"""
        from bot3.utils import download_script
        
        with pytest.raises(Exception):  # RequestException будет проброшен
            download_script()


# =============================================================================
# ТЕСТЫ CHECK_RESTART
# =============================================================================

class TestCheckRestart:
    """Тесты для функции check_restart"""
    
    def test_check_restart_with_file(self, mock_bot, temp_file, monkeypatch):
        """Тест проверки перезапуска с файлом chat_id"""
        temp_file.write_text('123456789')
        
        import bot3.utils as utils
        from bot3.utils import check_restart
        
        # Мок конфигурации
        mock_config = MagicMock()
        mock_config.paths = {'chat_id_path': str(temp_file)}
        monkeypatch.setattr(utils, 'config', mock_config)
        
        check_restart(mock_bot)
        
        # Проверяем, что сообщение было отправлено
        mock_bot.send_message.assert_called_once()
        
        # Файл должен быть удалён
        assert not temp_file.exists()
    
    def test_check_restart_without_file(self, mock_bot, temp_dir, monkeypatch):
        """Тест проверки перезапуска без файла chat_id"""
        import bot3.utils as utils
        from bot3.utils import check_restart
        
        # Мок конфигурации
        mock_config = MagicMock()
        mock_config.paths = {'chat_id_path': str(temp_dir / 'nonexistent.txt')}
        monkeypatch.setattr(utils, 'config', mock_config)
        
        # Не должно вызывать ошибок
        check_restart(mock_bot)
        
        # Сообщение не должно быть отправлено
        mock_bot.send_message.assert_not_called()
