from telebot import types
import bot_config as config
import os
import subprocess

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
    dirname = config.paths["unblock_dir"]
    buttons = []
    if os.path.exists(dirname) and os.listdir(dirname):
        file_buttons = [fln.replace(".txt", "") for fln in os.listdir(dirname)]
        buttons.append(file_buttons)
    else:
        buttons.append(["Нет доступных файлов"])
    buttons.append(["🔙 Назад"])
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
        button_text = f"💽 {drive['label']} ({drive['size']} GB свободно)"
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
    """Меню ключей и мостов — показывает только активные сервисы"""
    buttons = []

    # Проверяем статус сервисов через init скрипты
    def is_service_active(init_script):
        try:
            result = subprocess.run([init_script, 'status'], capture_output=True, text=True, timeout=2)
            return result.returncode == 0
        except:
            return False

    # Проверяем активные сервисы
    active_services = []
    if is_service_active(config.services["tor_restart"][0]):
        active_services.append("Tor")
    if is_service_active(config.services["vless_restart"][0]):
        active_services.append("Vless")
    if is_service_active(config.services["trojan_restart"][0]):
        active_services.append("Trojan")
    if is_service_active(config.services["shadowsocks_restart"][0]):
        active_services.append("Shadowsocks")

    # Формируем кнопки только для активных сервисов
    if active_services:
        buttons.append(active_services)
    else:
        buttons.append(["Нет активных сервисов"])

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
