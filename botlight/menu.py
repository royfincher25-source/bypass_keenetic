# =============================================================================
# MENU - Импорт из bot3 для избежания дублирования
# =============================================================================

import sys
import os

# Добавляем путь к bot3
bot3_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bot3')
if bot3_dir not in sys.path:
    sys.path.insert(0, bot3_dir)

# Импорт всех компонентов из bot3/menu.py
from menu import (
    Menu,
    BackupState,
    create_menu,
    create_button,
    create_backup_menu,
    create_drive_selection_menu,
    create_delete_archive_menu,
    create_updates_menu,
    create_install_remove_menu,
    get_menu_main,
    get_menu_keys_bridges,
    get_menu_tor,
    get_menu_vless,
    get_menu_service
)

# Для обратной совместимости - константы
MENU_MAIN = get_menu_main()
MENU_KEYS_BRIDGES = get_menu_keys_bridges()
MENU_TOR = get_menu_tor()
MENU_VLESS = get_menu_vless()
MENU_SERVICE = get_menu_service()
