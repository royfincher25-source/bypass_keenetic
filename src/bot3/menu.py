from telebot import types
import bot_config as config
import os
from utils import log_error

class Menu:
    __slots__ = ['name', 'markup', 'level', 'back_level']
    
    def __init__(self, name, markup, level, back_level=None):
        self.name = name
        self.markup = markup
        self.level = level
        self.back_level = back_level

class BackupState:
    __slots__ = ['startup_config', 'firmware', 'entware', 'custom_files', 
                 'selected_drive', 'delete_archive', 'selection_msg_id']
    
    def __init__(self):
        self.startup_config = False
        self.firmware = False
        self.entware = False
        self.custom_files = False
        self.selected_drive = None
        self.delete_archive = False
        self.selection_msg_id = None

    def get_selected_count(self):
        return sum([self.startup_config, self.firmware, self.entware, self.custom_files])

    def get_selected_types(self):
        types = []
        if self.startup_config: types.append("Конфигурация")
        if self.firmware: types.append("Прошивка")
        if self.entware: types.append("Entware")
        if self.custom_files: types.append("Другие файлы")
        return types

def create_menu(buttons, resize_keyboard=True):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=resize_keyboard)
    for row in buttons:
        markup.add(*row)
    return markup

def create_button(text, callback_data):
    return types.InlineKeyboardButton(text, callback_data=callback_data)

def create_bypass_files_menu():
    """Создание меню выбора файлов обхода"""
    try:
        dirname = config.paths["unblock_dir"]
        buttons = []
        if os.path.exists(dirname) and os.listdir(dirname):
            file_buttons = [fln.replace(".txt", "") for fln in os.listdir(dirname)]
            buttons.append(file_buttons)
        else:
            buttons.append(["Нет доступных файлов"])
        buttons.append(["🔙 Назад"])
        return create_menu(buttons)
    except Exception as e:
        log_error(f"Error creating bypass menu: {e}")
        buttons = [["Ошибка меню"], ["🔙 Назад"]]
        return create_menu(buttons)

def create_backup_menu(backup_state):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_button(f"{'✅' if backup_state.startup_config else '✖️'} Конфигурация", "backup_toggle_startup"),
        create_button(f"{'✅' if backup_state.firmware else '✖️'} Прошивка", "backup_toggle_firmware")
    )
    markup.add(
        create_button(f"{'✅' if backup_state.entware else '✖️'} Entware", "backup_toggle_entware"),
        create_button(f"{'✅' if backup_state.custom_files else '✖️'} Другие файлы", "backup_toggle_custom")
    )
    if backup_state.get_selected_count() > 0:
        markup.add(create_button("💾 Создать бэкап", "backup_create"))
    markup.add(create_button("🔙 Назад", "menu_service"))
    return markup

def create_drive_selection_menu(drives):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for drive in drives:
        # Получаем размер свободного места (если есть)
        size = drive.get('size', 'N/A')
        label = drive.get('label', drive.get('uuid', 'Unknown'))
        button_text = f"💽 {label} ({size} GB свободно)"
        markup.add(create_button(button_text, f"backup_drive_{drive['uuid']}"))
    markup.add(create_button("🔙 Назад", "backup_menu"))
    return markup

def create_delete_archive_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_button("Да", "backup_delete_yes"),
        create_button("Нет", "backup_delete_no")
    )
    markup.add(create_button("🔙 Назад", "backup_create"))
    return markup

def create_dns_override_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_button("✅ ВКЛ", "dns_override_on"),
        create_button("✖️ ВЫКЛ", "dns_override_off")
    )
    markup.add(create_button("🔙 Назад", "menu_service"))
    return markup
    
def create_updates_menu(need_update):
    markup = types.InlineKeyboardMarkup()
    if need_update:
        markup.add(create_button("🆕 Обновить", "trigger_update"))
    markup.add(create_button("🔙 Назад", "menu_service"))
    return markup

def create_install_remove_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        create_button("📲 Установка", "install"),
        create_button("🗑 Удаление", "remove")
    )
    markup.add(create_button("🔙 Назад", "menu_main"))
    return markup


# Фабричные функции для lazy инициализации меню (экономия памяти при старте)

def get_menu_main():
    return Menu("🤖 Добро пожаловать в меню!", create_menu([
        ["🔑 Ключи и мосты", "📑 Списки обхода"],
        ["📲 Установка и удаление", "📊 Статистика", "⚙️ Сервис"]
    ]), 0)

def get_menu_bypass_files():
    return Menu("📑 Списки обхода", None, 1, 0)

def get_menu_bypass_list():
    return Menu("Выберите действие:", create_menu([
        ["📄 Показать список", "➕ Добавить в список", "➖ Удалить из списка"],
        ["🔙 Назад"]
    ]), 2, 1)

def get_menu_add_bypass():
    return Menu("➕ Добавить в список", create_menu([["🔙 Назад"]]), 3, 2)

def get_menu_remove_bypass():
    return Menu("➖ Удалить из списка", create_menu([["🔙 Назад"]]), 4, 2)

def get_menu_keys_bridges():
    """Меню ключей и мостов — показывает только сервисы с конфигами"""
    buttons = []

    # Проверяем наличие конфигов, а не статус сервисов (быстро и надёжно)
    has_tor = os.path.exists(config.paths["tor_config"])
    has_vless = os.path.exists(config.paths["vless_config"])
    has_trojan = os.path.exists(config.paths["trojan_config"])
    has_shadowsocks = os.path.exists(config.paths["shadowsocks_config"])

    # Формируем кнопки только для сервисов с конфигами
    active_services = []
    if has_tor:
        active_services.append("Tor")
    if has_vless:
        active_services.append("Vless")
    if has_trojan:
        active_services.append("Trojan")
    if has_shadowsocks:
        active_services.append("Shadowsocks")

    # Формируем кнопки только для сервисов с конфигами
    if active_services:
        buttons.append(active_services)
    else:
        buttons.append(["Нет настроенных сервисов"])

    buttons.append(["🔙 Назад"])
    return Menu("🔑 Ключи и мосты", create_menu(buttons), 5, 0)

def get_menu_tor():
    return Menu("Tor", create_menu([["🔙 Назад"]]), 8, 5)

def get_menu_shadowsocks():
    return Menu("Shadowsocks", create_menu([["🔙 Назад"]]), 9, 5)

def get_menu_vless():
    return Menu("Vless", create_menu([["🔙 Назад"]]), 10, 5)

def get_menu_trojan():
    return Menu("Trojan", create_menu([["🔙 Назад"]]), 11, 5)

def get_menu_service():
    return Menu("⚙️ Сервисное меню!", create_menu([
        ["🤖 Перезапуск бота", "🔌 Перезапуск роутера", "🔁 Перезапуск сервисов"],
        ["⁉️ DNS Override", "🆕 Обновления", "💾 Бэкап"],
        ["🔙 Назад"]
    ]), 6, 0)
