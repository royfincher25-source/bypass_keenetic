# =============================================================================
# PYTEST CONFTES - ФИКСТУРЫ ДЛЯ ТЕСТИРОВАНИЯ
# =============================================================================
# Общие фикстуры для всех тестов
# =============================================================================

import os
import sys
import pytest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path

# Добавляем корень проекта и src в path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / 'src'))


# =============================================================================
# ФИКСТУРЫ ОКРУЖЕНИЯ
# =============================================================================

@pytest.fixture(scope='session')
def root_dir():
    """Корневая директория проекта"""
    return ROOT_DIR


@pytest.fixture(scope='session')
def bot3_dir(root_dir):
    """Директория bot3"""
    return root_dir / 'src' / 'bot3'


@pytest.fixture(scope='session')
def botlight_dir(root_dir):
    """Директория botlight"""
    return root_dir / 'src' / 'botlight'


@pytest.fixture
def mock_env(monkeypatch):
    """Фикстура для мокания переменных окружения"""
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', '123456789:ABCdefGHIjklMNOpqrsTUVwxyz')
    monkeypatch.setenv('TELEGRAM_USERNAMES', 'testuser')
    monkeypatch.setenv('ROUTER_IP', '192.168.1.1')
    yield


# =============================================================================
# ФИКСТУРЫ ДЛЯ TELEBOT
# =============================================================================

@pytest.fixture
def mock_bot():
    """Mock Telegram бота"""
    bot = MagicMock()
    bot.send_message = MagicMock()
    bot.edit_message_text = MagicMock()
    bot.edit_message_reply_markup = MagicMock()
    bot.delete_message = MagicMock()
    bot.send_document = MagicMock()
    bot.answer_callback_query = MagicMock()
    return bot


@pytest.fixture
def mock_message():
    """Mock сообщения Telegram"""
    message = MagicMock()
    message.text = ''
    message.chat.id = 123456789
    message.chat.type = 'private'
    message.from_user.username = 'testuser'
    message.message_id = 1
    return message


@pytest.fixture
def mock_callback_query():
    """Mock callback query"""
    query = MagicMock()
    query.data = ''
    query.message = MagicMock()
    query.message.chat.id = 123456789
    query.message.message_id = 1
    query.id = 'callback_123'
    return query


# =============================================================================
# ФИКСТУРЫ ДЛЯ SUBPROCESS
# =============================================================================

@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='',
            stderr=''
        )
        yield mock_run


@pytest.fixture
def mock_subprocess_popen():
    """Mock subprocess.Popen"""
    with patch('subprocess.Popen') as mock_popen:
        mock_process = MagicMock()
        mock_process.wait = MagicMock()
        mock_process.kill = MagicMock()
        mock_process.stdout = iter([])
        mock_popen.return_value = mock_process
        yield mock_popen


@pytest.fixture
def mock_subprocess_check_output():
    """Mock subprocess.check_output"""
    with patch('subprocess.check_output') as mock_check_output:
        mock_check_output.return_value = ''
        yield mock_check_output


# =============================================================================
# ФИКСТУРЫ ДЛЯ REQUESTS
# =============================================================================

@pytest.fixture
def mock_requests_get():
    """Mock requests.get"""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '1.0.0'
        mock_response.content = b'content'
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_requests_timeout():
    """Mock requests.get с таймаутом"""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout()
        yield mock_get


@pytest.fixture
def mock_requests_error():
    """Mock requests.get с ошибкой"""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException()
        yield mock_get


# =============================================================================
# ФИКСТУРЫ ДЛЯ ФАЙЛОВОЙ СИСТЕМЫ
# =============================================================================

@pytest.fixture
def mock_file_exists():
    """Mock os.path.exists"""
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        yield mock_exists


@pytest.fixture
def mock_file_not_exists():
    """Mock os.path.exists (файл не существует)"""
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = False
        yield mock_exists


@pytest.fixture
def mock_open_file():
    """Mock встроенной функции open"""
    with patch('builtins.open', mock_open=True):
        yield


@pytest.fixture
def temp_file(tmp_path):
    """Временный файл"""
    file_path = tmp_path / 'test_file.txt'
    file_path.write_text('test content')
    yield file_path


@pytest.fixture
def temp_dir(tmp_path):
    """Временная директория"""
    dir_path = tmp_path / 'test_dir'
    dir_path.mkdir()
    yield dir_path


# =============================================================================
# ФИКСТУРЫ ДЛЯ КОНФИГУРАЦИИ
# =============================================================================

@pytest.fixture
def mock_config():
    """Mock конфигурации"""
    config = MagicMock()
    config.token = '123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
    config.usernames = ['testuser']
    config.routerip = '192.168.1.1'
    config.localportsh = 1082
    config.dnsporttor = 9053
    config.localporttor = 9141
    config.localportvless = 10810
    config.localporttrojan = 10829
    config.dnsovertlsport = 40500
    config.dnsoverhttpsport = 40508
    config.MAX_RESTARTS = 5
    config.RESTART_DELAY = 60
    
    config.paths = {
        'unblock_dir': '/opt/etc/unblock/',
        'tor_config': '/opt/etc/tor/torrc',
        'shadowsocks_config': '/opt/etc/shadowsocks.json',
        'trojan_config': '/opt/etc/trojan/config.json',
        'vless_config': '/opt/etc/xray/config.json',
        'templates_dir': '/opt/etc/bot/templates/',
        'error_log': '/opt/etc/bot/error.log',
        'script_sh': '/opt/root/script.sh',
        'chat_id_path': '/opt/var/run/bot_chat_id.txt',
        'bot_dir': '/opt/etc/bot',
    }
    
    config.bot_url = 'https://raw.githubusercontent.com/test/bypass_keenetic/main/src/bot3'
    
    return config


# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФИКСТУРЫ
# =============================================================================

@pytest.fixture
def sample_vless_key():
    """Пример VLESS ключа"""
    return 'vless://55504f0d-3f5b-4d5e-8c5f-5d5e5f5g5h5i@192.168.1.1:443?security=reality&pbk=abcdef123456&fp=chrome&spx=/&sid=1234&encryption=none#test'


@pytest.fixture
def sample_trojan_key():
    """Пример Trojan ключа"""
    return 'trojan://password123@192.168.1.1:443?security=tls&sni=example.com#test'


@pytest.fixture
def sample_shadowsocks_key():
    """Пример Shadowsocks ключа"""
    # ss://base64(method:password)@server:port
    return 'ss://YWVzLTI1Ni1nY206cGFzc3dvcmQxMjM=@192.168.1.1:8388#test'


@pytest.fixture
def sample_tor_bridges():
    """Пример Tor мостов"""
    return '''192.168.1.1:9001 1234567890ABCDEF1234567890ABCDEF12345678
obfs4 192.168.1.2:9002 1234567890ABCDEF1234567890ABCDEF12345678 cert=abcdef123456 iat-mode=0
webtunnel 192.168.1.3:9003 url=https://example.com/'''


@pytest.fixture
def sample_domains():
    """Пример списка доменов"""
    return [
        'example.com',
        'test.example.com',
        'google.com',
        'youtube.com'
    ]


@pytest.fixture
def sample_ips():
    """Пример списка IP"""
    return [
        '192.168.1.1',
        '10.0.0.1',
        '8.8.8.8'
    ]
