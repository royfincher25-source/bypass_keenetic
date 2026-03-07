# =============================================================================
# КОНФИГУРАЦИЯ БОТА (botlight - облегчённая версия)
# =============================================================================
# Этот файл загружает настройки из переменных окружения (.env файла)
# Убедитесь, что вы скопировали .env.example в .env и заполнили значения
# =============================================================================

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# -----------------------------------------------------------------------------
# TELEGRAM BOT SETTINGS
# -----------------------------------------------------------------------------
token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
usernames = os.environ.get('TELEGRAM_USERNAMES', '').split(',')

# Валидация токена
if not token or token.strip() == '' or ':' not in token or len(token) < 10:
    print("❌ ОШИБКА: TELEGRAM_BOT_TOKEN не указан или имеет неверный формат в .env файле")
    print("   Скопируйте .env.example в .env и заполните TELEGRAM_BOT_TOKEN")
    raise ValueError("TELEGRAM_BOT_TOKEN не настроен")

# Валидация usernames
if not usernames or usernames == ['']:
    print("⚠️ ПРЕДУПРЕЖДЕНИЕ: TELEGRAM_USERNAMES не указан в .env файле")
    usernames = []

# -----------------------------------------------------------------------------
# BOT SETTINGS
# -----------------------------------------------------------------------------
MAX_RESTARTS = int(os.environ.get('MAX_RESTARTS', '5'))
RESTART_DELAY = int(os.environ.get('RESTART_DELAY', '60'))

# -----------------------------------------------------------------------------
# PROXY SETTINGS
# -----------------------------------------------------------------------------
proxy0port = int(os.environ.get('PROXY0_PORT', '9050'))
proxy0interface = os.environ.get('PROXY0_INTERFACE', 'Proxy0')
proxy1port = int(os.environ.get('PROXY1_PORT', '1080'))
proxy1interface = os.environ.get('PROXY1_INTERFACE', 'Proxy1')
proxy2port = int(os.environ.get('PROXY2_PORT', '2080'))
proxy2interface = os.environ.get('PROXY2_INTERFACE', 'Proxy2')

# -----------------------------------------------------------------------------
# VLESS CLIENT SETTINGS
# -----------------------------------------------------------------------------
vless_client = os.environ.get('VLESS_CLIENT', 'singbox')
client_mode = os.environ.get('CLIENT_MODE', 'socks5')

# -----------------------------------------------------------------------------
# PACKAGES
# -----------------------------------------------------------------------------
packages = [
    "tor",
    "tor-geoip",
    "obfs4",
    "webtunnel-client",
    "xray",
    "sing-box-go",
    "magitrickle",
    "coreutils-split"
]

# -----------------------------------------------------------------------------
# PATHS
# -----------------------------------------------------------------------------
paths = {
    "bot_config": "/opt/etc/bot/bot_config.py",
    "tor_config": "/opt/etc/tor/torrc",
    "singbox_config": "/opt/etc/sing-box/config.json",
    "xray_config": "/opt/etc/xray/config.json",
    "error_log": "/opt/etc/bot/error.log",
    "keensnap_log": "/opt/root/KeenSnap/backup.log",
    "keensnap_path": "/opt/root/KeenSnap/keensnap.sh",
    "bot_path": "/opt/etc/bot/main.py",
    "script_sh": "/opt/root/script.sh",
    "chat_id_path": "/opt/var/run/bot_chat_id.txt",
    "init_singbox": "/opt/etc/init.d/S99sing-box",
    "init_xray": "/opt/etc/init.d/S24xray",
    "init_tor": "/opt/etc/init.d/S35tor",
    "init_bot": "/opt/etc/init.d/S99telegram_bot",
    "init_MT": "/opt/etc/init.d/S99magitrickle",
    "bot_dir": "/opt/etc/bot",
    "templates_dir": "/opt/etc/bot/templates",
    "keensnap_dir": "/opt/root/KeenSnap",
    "tor_dir": "/opt/etc/tor",
    "singbox_dir": "/opt/etc/sing-box",
    "xray_dir": "/opt/etc/xray"
}

# -----------------------------------------------------------------------------
# SERVICES
# -----------------------------------------------------------------------------
services = {
    "tor_restart": [paths["init_tor"], "restart"],
    "singbox_restart": [paths["init_singbox"], "restart"],
    "xray_restart": [paths["init_xray"], "restart"],
    "MT_restart": [paths["init_MT"], "restart"],
    "service_script": [paths["init_bot"], "restart"]
}

# -----------------------------------------------------------------------------
# URLs
# -----------------------------------------------------------------------------
base_url = os.environ.get('BASE_URL', 'https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main')
bot_url = f"{base_url}/botlight"
MT_url = os.environ.get('MT_URL', 'http://bin.magitrickle.dev/packages/add_repo.sh')

# -----------------------------------------------------------------------------
# BACKUP SETTINGS
# -----------------------------------------------------------------------------
backup_settings = {
    "LOG_FILE": paths["keensnap_log"],
    "MAX_SIZE_MB": int(os.environ.get('BACKUP_MAX_SIZE_MB', '45')),
    "CUSTOM_BACKUP_PATHS": " ".join([
        paths["bot_dir"],
        paths["singbox_config"],
        paths["xray_config"],
        paths["tor_config"],
        paths["script_sh"]
    ])
}
