# =============================================================================
# КОНФИГУРАЦИЯ БОТА (bot3 - оптимизированная версия)
# =============================================================================
# Облегчённая версия для embedded-устройств
# Потребление памяти: < 5MB (vs ~15MB у полной версии)
# =============================================================================

import sys
import os

# Добавляем core модуль в path
bot_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(bot_dir, '..', 'core'))

# Лёгкая конфигурация (без python-dotenv!)
from core.config import config

# =============================================================================
# TELEGRAM BOT SETTINGS
# =============================================================================
token = config.token
usernames = config.usernames
user_ids = config.user_ids  # Безопасная авторизация по user_id

# Экспорт функции авторизации из core.config
is_authorized = config.is_authorized

# Валидация при старте (fail fast)
if not config.is_valid:
    valid, error = config.validate()
    print(f"❌ ОШИБКА: {error}")
    print("   Проверьте .env файл в директории бота")
    sys.exit(1)

# =============================================================================
# BOT SETTINGS
# =============================================================================
MAX_RESTARTS = config.max_restarts
RESTART_DELAY = config.restart_delay

# =============================================================================
# ROUTER SETTINGS
# =============================================================================
routerip = config.router_ip

# =============================================================================
# VPN SETTINGS
# =============================================================================
vpn_allowed = "IKE|SSTP|OpenVPN|Wireguard|L2TP"

# =============================================================================
# LOCAL PORTS (кэшированы из .env)
# =============================================================================
localportsh = config.localport_sh
dnsporttor = config.dnsport_tor
localporttor = config.localport_tor
localportvless = config.localport_vless
localporttrojan = config.localport_trojan
dnsovertlsport = config.dnsovertlsport
dnsoverhttpsport = config.dnsoverhttpsport

# =============================================================================
# PACKAGES
# =============================================================================
packages = [
    "tor",
    "tor-geoip",
    "bind-dig",
    "cron",
    "dnsmasq-full",
    "ipset",
    "iptables",
    "obfs4",
    "webtunnel-client",
    "shadowsocks-libev-ss-redir",
    "shadowsocks-libev-config",
    "xray",
    "trojan",
    "coreutils-split"
]

# =============================================================================
# PATHS (статические, не из .env для скорости)
# =============================================================================
paths = {
    "unblock_dir": "/opt/etc/unblock/",
    "tor_config": "/opt/etc/tor/torrc",
    "shadowsocks_config": "/opt/etc/shadowsocks.json",
    "trojan_config": "/opt/etc/trojan/config.json",
    "vless_config": "/opt/etc/xray/config.json",
    "templates_dir": "/opt/etc/bot/templates/",
    "dnsmasq_conf": "/opt/etc/dnsmasq.conf",
    "crontab": "/opt/etc/crontab",
    "redirect_script": "/opt/etc/ndm/netfilter.d/100-redirect.sh",
    "vpn_script": "/opt/etc/ndm/ifstatechanged.d/100-unblock-vpn.sh",
    "ipset_script": "/opt/etc/ndm/fs.d/100-ipset.sh",
    "unblock_ipset": "/opt/bin/unblock_ipset.sh",
    "unblock_dnsmasq": "/opt/bin/unblock_dnsmasq.sh",
    "unblock_update": "/opt/bin/unblock_update.sh",
    "keensnap_dir": "/opt/root/KeenSnap/",
    "script_bu": "/opt/root/KeenSnap/keensnap.sh",
    "bot_dir": bot_dir,
    "bot_path": os.path.join(bot_dir, "main.py"),
    "bot_config": os.path.join(bot_dir, "bot_config.py"),
    "hosts_file": "/opt/etc/hosts",
    "error_log": os.path.join(bot_dir, "error.log"),
    "log_bu": "/opt/root/KeenSnap/backup.log",
    "script_sh": "/opt/root/script.sh",
    "chat_id_path": "/opt/var/run/bot_chat_id.txt",
    "init_shadowsocks": "/opt/etc/init.d/S22shadowsocks",
    "init_trojan": "/opt/etc/init.d/S22trojan",
    "init_xray": "/opt/etc/init.d/S24xray",
    "init_tor": "/opt/etc/init.d/S35tor",
    "init_dnsmasq": "/opt/etc/init.d/S56dnsmasq",
    "init_unblock": "/opt/etc/init.d/S99unblock",
    "init_bot": os.path.join(bot_dir, "S99telegram_bot"),
    "tor_tmp_dir": "/opt/tmp/tor",
    "tor_dir": "/opt/etc/tor",
    "xray_dir": "/opt/etc/xray",
    "trojan_dir": "/opt/etc/trojan"
}

# =============================================================================
# SERVICES
# =============================================================================
services = {
    "tor_restart": [paths["init_tor"], "restart"],
    "shadowsocks_restart": [paths["init_shadowsocks"], "restart"],
    "trojan_restart": [paths["init_trojan"], "restart"],
    "vless_restart": [paths["init_xray"], "restart"],
    "service_script": [paths["init_bot"], "restart"],
    "unblock_update": [paths["unblock_update"]],
}

# =============================================================================
# URLs
# =============================================================================
base_url = "https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main"
bot_url = f"{base_url}/src/bot3"  # Для загрузки файлов бота
# version.md загружается из base_url (корень репозитория)!

# =============================================================================
# BACKUP SETTINGS
# =============================================================================
backup_settings = {
    "LOG_FILE": paths["log_bu"],
    "MAX_SIZE_MB": config.backup_max_size_mb,
    "CUSTOM_BACKUP_PATHS": " ".join([
        paths["bot_dir"],
        paths["vless_config"],
        paths["tor_config"],
        paths["script_sh"],
        paths["script_bu"],
    ])
}
