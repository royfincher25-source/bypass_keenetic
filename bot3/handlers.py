import subprocess
import os
import time
from telebot import types
import bot_config as config
from menu import (
    get_menu_main, get_menu_bypass_files, get_menu_service, get_menu_keys_bridges,
    get_menu_bypass_list, get_menu_add_bypass, get_menu_remove_bypass,
    get_menu_tor, get_menu_shadowsocks, get_menu_vless, get_menu_trojan,
    create_bypass_files_menu, create_backup_menu, BackupState, create_drive_selection_menu, create_delete_archive_menu,
    create_dns_override_menu, create_updates_menu, create_install_remove_menu
)
from utils import (
    download_script, download_bot_files, load_bypass_list, save_bypass_list, vless_config, trojan_config,
    shadowsocks_config, tor_config, get_available_drives, create_backup_with_params, log_error
)

class HandlerState:
    """Оптимизированное состояние обработчиков с __slots__ для экономии памяти"""
    __slots__ = ['current_menu', 'selected_file', 'backup_state', 'last_stats_message_id']
    
    def __init__(self):
        self.current_menu = get_menu_main()
        self.selected_file = ""
        self.backup_state = BackupState()
        self.last_stats_message_id = None  # ID последнего сообщения статистики

def setup_handlers(bot):
    state = HandlerState()

    def set_menu_and_reply(chat_id, new_menu, text=None, markup=None):
        # Закрываем окно статистики если оно открыто
        if state.last_stats_message_id:
            try:
                bot.delete_message(chat_id, state.last_stats_message_id)
                state.last_stats_message_id = None
            except:
                pass  # Игнорируем ошибку если сообщение уже удалено
        
        state.current_menu = new_menu
        if not text:
            text = new_menu.name
        bot.send_message(chat_id, text, reply_markup=markup if markup else new_menu.markup)

    def go_to_bypass_files(chat_id):
        markup = create_bypass_files_menu()
        set_menu_and_reply(chat_id, get_menu_bypass_files(), markup=markup)

    def handle_bypass_files_selection(message):
        state.selected_file = message.text
        set_menu_and_reply(message.chat.id, get_menu_bypass_list(), "Меню " + state.selected_file)

    def send_long_message(chat_id, text, parse_mode=None):
        current_part = ""
        for line in text.split('\n'):
            if len(current_part + '\n' + line) > 4096:
                bot.send_message(chat_id, current_part, parse_mode=parse_mode)
                current_part = line
            else:
                current_part += '\n' + line if current_part else line
        if current_part:
            bot.send_message(chat_id, current_part, parse_mode=parse_mode)

    def handle_bypass_list_menu(message):
        filepath = f"{config.paths['unblock_dir']}{state.selected_file}.txt"
        if message.text == "📄 Показать список":
            sites = load_bypass_list(filepath)
            text = "Список пуст" if not sites else "\n".join(sites)
            send_long_message(message.chat.id, text)
            bot.send_message(message.chat.id, "Меню " + state.selected_file, reply_markup=get_menu_bypass_list().markup)
        elif message.text == "➕ Добавить в список":
            set_menu_and_reply(message.chat.id, get_menu_add_bypass(), "Введите сайт, домен или IP-адресс для добавления")
        elif message.text == "➖ Удалить из списка":
            set_menu_and_reply(message.chat.id, get_menu_remove_bypass(), "Введите сайт, домен или IP-адресс для удаления")

    def handle_add_to_bypass(message):
        filepath = f"{config.paths['unblock_dir']}{state.selected_file}.txt"
        mylist = load_bypass_list(filepath)
        k = len(mylist)
        added_count = 0
        invalid_items = []
        
        if len(message.text) > 1:
            # Добавляем новые элементы с валидацией
            for item in message.text.split('\n'):
                item = item.strip()
                if item and item not in mylist:
                    # Проверяем валидность записи
                    from utils import validate_bypass_entry
                    if validate_bypass_entry(item):
                        mylist.append(item)
                        added_count += 1
                    else:
                        invalid_items.append(item)
        
        save_bypass_list(filepath, mylist)
        
        if added_count > 0:
            bot.send_message(message.chat.id, f"✅ Успешно добавлено: {added_count} шт.\nПрименяю изменения...")
            subprocess.run(config.services["unblock_update"])
        elif invalid_items:
            bot.send_message(message.chat.id, f"❕Все записи уже в списке или невалидны.\n\nНераспознанные записи:\n" + "\n".join(invalid_items[:5]))
        else:
            bot.send_message(message.chat.id, "❕Было добавлено ранее")
        set_menu_and_reply(message.chat.id, get_menu_bypass_list(), "Меню " + state.selected_file)

    def handle_remove_from_bypass(message):
        filepath = f"{config.paths['unblock_dir']}{state.selected_file}.txt"
        mylist = load_bypass_list(filepath)
        k = len(mylist)
        # Удаляем элементы, сохраняя порядок
        to_remove = [item.strip() for item in message.text.split('\n') if item.strip()]
        mylist = [item for item in mylist if item not in to_remove]
        save_bypass_list(filepath, mylist)
        if k != len(mylist):
            bot.send_message(message.chat.id, "✅ Успешно удалено, применяю изменения...")
            subprocess.run(config.services["unblock_update"])
        else:
            bot.send_message(message.chat.id, "❕Не найдено в списке")
        set_menu_and_reply(message.chat.id, get_menu_bypass_list(), "Меню " + state.selected_file)

    def handle_keys_bridges_selection(message):
        if message.text == 'Tor':
            set_menu_and_reply(message.chat.id, get_menu_tor(), "🔑 Вставьте мосты Tor")
        elif message.text == 'Shadowsocks':
            set_menu_and_reply(message.chat.id, get_menu_shadowsocks(), "🔑 Вставьте ключ Shadowsocks")
        elif message.text == 'Vless':
            set_menu_and_reply(message.chat.id, get_menu_vless(), "🔑 Вставьте ключ Vless")
        elif message.text == 'Trojan':
            set_menu_and_reply(message.chat.id, get_menu_trojan(), "🔑 Вставьте ключ Trojan")

    def update_service(chat_id, service_name, config_func, restart_cmd):
        try:
            config_func()
            result = subprocess.run(restart_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                bot.send_message(chat_id, f'✅ Сервис {service_name} успешно перезапущен')
                return True, None
            else:
                error_message = result.stderr.strip() or result.stdout.strip() or "Неизвестная ошибка"
                bot.send_message(chat_id, f'❌ Ошибка при перезапуске {service_name}: {error_message}')
                return False, error_message
        except Exception as e:
            return False, str(e)

    def handle_tor_manually(message):
        success, error = update_service(message.chat.id, "Tor", lambda: tor_config(message.text, bot, message.chat.id), config.services["tor_restart"])
        if success:
            set_menu_and_reply(message.chat.id, get_menu_keys_bridges())
        else:
            bot.send_message(message.chat.id, "❕Попробуйте ввести мосты заново", reply_markup=state.current_menu.markup)

    def handle_shadowsocks(message):
        success, error = update_service(message.chat.id, "Shadowsocks", lambda: shadowsocks_config(message.text, bot, message.chat.id), config.services["shadowsocks_restart"])
        if success:
            set_menu_and_reply(message.chat.id, get_menu_keys_bridges())
        else:
            bot.send_message(message.chat.id, "❕Попробуйте ввести ключ заново", reply_markup=state.current_menu.markup)

    def handle_vless(message):
        success, error = update_service(message.chat.id, "Vless", lambda: vless_config(message.text, bot, message.chat.id), config.services["vless_restart"])
        if success:
            set_menu_and_reply(message.chat.id, get_menu_keys_bridges())
        else:
            bot.send_message(message.chat.id, "❕Попробуйте ввести ключ заново", reply_markup=state.current_menu.markup)

    def handle_trojan(message):
        success, error = update_service(message.chat.id, "Trojan", lambda: trojan_config(message.text, bot, message.chat.id), config.services["trojan_restart"])
        if success:
            set_menu_and_reply(message.chat.id, get_menu_keys_bridges())
        else:
            bot.send_message(message.chat.id, "❕Попробуйте ввести ключ заново", reply_markup=state.current_menu.markup)

    def handle_restart(chat_id):
        bot.send_message(chat_id, "⏳ Бот будет перезапущен!\nЭто займет около 15-30 секунд", reply_markup=get_menu_service().markup)
        with open(config.paths["chat_id_path"], 'w') as f:
            f.write(str(chat_id))
        subprocess.Popen(config.services['service_script'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)

    def handle_backup(chat_id):
        inline_keyboard = create_backup_menu(state.backup_state)
        bot.send_message(chat_id, "Выберите файлы для бэкапа:", reply_markup=inline_keyboard)

    def handle_install_remove(chat_id):
        inline_keyboard = create_install_remove_menu()
        bot.send_message(chat_id, "Выберите действие:", reply_markup=inline_keyboard)

    def handle_dns_override(chat_id):
        inline_keyboard = create_dns_override_menu()
        bot.send_message(chat_id, "Выберите действие:", reply_markup=inline_keyboard)

    def get_local_version():
        version_file = os.path.join(os.path.dirname(__file__), "version.md")
        try:
            with open(version_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            return "N/A"

    def get_remote_version(bot_url):
        import requests
        try:
            # Используем сессию из utils для connection pooling
            from utils import get_http_session
            session = get_http_session()
            # Добавляем заголовки для обхода кеша
            headers = {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
            # Добавляем timestamp для уникальности URL
            response = session.get(
                f"{bot_url}/version.md?t={int(time.time())}",
                headers=headers,
                timeout=10
            )
            return response.text.strip() if response.status_code == 200 else "N/A"
        except requests.exceptions.Timeout:
            return "N/A (timeout)"
        except requests.exceptions.RequestException:
            return "N/A (error)"

    def handle_updates(chat_id):
        # Закрываем предыдущее окно статистики если открыто
        if state.last_stats_message_id:
            try:
                bot.delete_message(chat_id, state.last_stats_message_id)
                state.last_stats_message_id = None
            except:
                pass
        
        bot_new_version = get_remote_version(config.bot_url)
        bot_version = get_local_version()
        service_update_info = f"Установленная версия: {bot_version}\nДоступная версия: {bot_new_version}"
        
        # Всегда показываем кнопку обновления
        need_update = True
        
        if bot_version != "N/A" and bot_new_version != "N/A":
            try:
                if tuple(map(int, bot_version.split("."))) >= tuple(map(int, bot_new_version.split("."))):
                    service_update_info += "\n✅ У вас последняя версия!"
                    # Но всё равно показываем кнопку для принудительного обновления
            except ValueError:
                service_update_info += "\n⚠️ Версии имеют неверный формат"
        else:
            service_update_info += "\n⚠️ Не удалось проверить обновления"
        
        inline_keyboard = create_updates_menu(need_update)
        msg = bot.send_message(chat_id, service_update_info, reply_markup=inline_keyboard)
        state.last_stats_message_id = msg.message_id  # Сохраняем для закрытия

    # Кэш для статусов сервисов (в области setup_handlers)
    _service_status_cache = {
        'tor_status': '❓',
        'vless_status': '❓',
        'trojan_status': '❓',
        'shadowsocks_status': '❓',
        'vpn_status': '➖'
    }

    def get_stats(refresh_services=False):
        """
        Получение статистики.

        Args:
            refresh_services: Если True — проверять статусы сервисов (медленно)
                             Если False — пропустить проверку (быстро)
        """
        nonlocal _service_status_cache

        stats = {
            'bot_ram_mb': 0,
            'system_ram_total_mb': 0,
            'system_ram_free_mb': 0,
            'bot_uptime': 'N/A',
            'restart_count': 0,
            # Используем кэш статусов
            'tor_status': _service_status_cache['tor_status'],
            'vless_status': _service_status_cache['vless_status'],
            'trojan_status': _service_status_cache['trojan_status'],
            'shadowsocks_status': _service_status_cache['shadowsocks_status'],
            'vpn_status': _service_status_cache['vpn_status']
        }

        bot_pid = os.getpid()

        try:
            with open(f'/proc/{bot_pid}/status', 'r') as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        stats['bot_ram_mb'] = int(line.split()[1]) / 1024
                        break
        except Exception:
            pass

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

        try:
            uptime_seconds = float(subprocess.check_output(['cat', '/proc/uptime'], text=True).split()[0])
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            stats['bot_uptime'] = f"{hours}ч {minutes}мин"
        except Exception:
            pass

        stats['restart_count'] = config.MAX_RESTARTS

        # Проверка сервисов только если явно запрошено (медленная операция)
        if refresh_services:
            # Проверка всех сервисов (с уменьшенным таймаутом)
            services = [
                ('Tor', config.services["tor_restart"][0], 'tor_status'),
                ('VLESS', config.services["vless_restart"][0], 'vless_status'),
                ('Trojan', config.services["trojan_restart"][0], 'trojan_status'),
                ('Shadowsocks', config.services["shadowsocks_restart"][0], 'shadowsocks_status')
            ]

            for service_name, init_script, stat_key in services:
                try:
                    # Таймаут 2 секунды вместо 5 для быстродействия
                    result = subprocess.run([init_script, 'status'], capture_output=True, text=True, timeout=2)
                    status = '✅' if result.returncode == 0 else '❌'
                except Exception:
                    status = '❓'
                stats[stat_key] = status
                _service_status_cache[stat_key] = status  # Обновляем кэш

            # Проверка VPN (через ndmc, так как нет init скрипта)
            try:
                # Проверяем наличие vpn-*.txt файлов в unblock_dir
                unblock_dir = config.paths["unblock_dir"]
                vpn_files = [f for f in os.listdir(unblock_dir) if f.startswith('vpn-') and f.endswith('.txt')]

                if vpn_files:
                    # VPN файлы есть — проверяем статус через ndmc (таймаут 2 сек)
                    result = subprocess.run(
                        ['ndmc', '-c', 'show running | include ip-sec|vpn'],
                        capture_output=True, text=True, timeout=2
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        stats['vpn_status'] = '✅'
                        _service_status_cache['vpn_status'] = '✅'
                    else:
                        # Файлы есть, но VPN не активен
                        stats['vpn_status'] = '⚠️'  # Предупреждение
                        _service_status_cache['vpn_status'] = '⚠️'
                else:
                    # VPN файлов нет — показываем статус "не настроен"
                    stats['vpn_status'] = '➖'
                    _service_status_cache['vpn_status'] = '➖'
            except Exception:
                stats['vpn_status'] = '❓'

        return stats

    def format_stats_message(stats):
        return (
            f"📊 Статистика бота\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"🧠 RAM бота: {stats['bot_ram_mb']:.1f} MB\n"
            f"💻 Система: {stats['system_ram_free_mb']:.0f}/{stats['system_ram_total_mb']:.0f} MB свободно\n"
            f"⏱️ Uptime: {stats['bot_uptime']}\n"
            f"🔄 Перезапусков: {stats['restart_count']}"
        )

    def create_stats_keyboard(stats):
        markup = types.InlineKeyboardMarkup(row_width=2)

        # Кнопки управления сервисами
        service_buttons = []

        # Tor кнопки
        if stats['tor_status'] == '✅':
            service_buttons.append(types.InlineKeyboardButton("🔵 Tor: ВКЛ ✅", callback_data="service_tor_off"))
        else:
            service_buttons.append(types.InlineKeyboardButton("🔵 Tor: ВЫКЛ ❌", callback_data="service_tor_on"))

        # VLESS кнопки
        if stats['vless_status'] == '✅':
            service_buttons.append(types.InlineKeyboardButton("🔷 VLESS: ВКЛ ✅", callback_data="service_vless_off"))
        else:
            service_buttons.append(types.InlineKeyboardButton("🔷 VLESS: ВЫКЛ ❌", callback_data="service_vless_on"))

        # Trojan кнопки
        if stats['trojan_status'] == '✅':
            service_buttons.append(types.InlineKeyboardButton("🟡 Trojan: ВКЛ ✅", callback_data="service_trojan_off"))
        else:
            service_buttons.append(types.InlineKeyboardButton("🟡 Trojan: ВЫКЛ ❌", callback_data="service_trojan_on"))

        # Shadowsocks кнопки
        if stats['shadowsocks_status'] == '✅':
            service_buttons.append(types.InlineKeyboardButton("🟢 SS: ВКЛ ✅", callback_data="service_ss_off"))
        else:
            service_buttons.append(types.InlineKeyboardButton("🟢 SS: ВЫКЛ ❌", callback_data="service_ss_on"))

        # VPN кнопка (только статус, без управления)
        vpn_status_emoji = stats['vpn_status']
        if vpn_status_emoji == '✅':
            service_buttons.append(types.InlineKeyboardButton("🔷 VPN: ВКЛ ✅", callback_data="service_vpn_info"))
        elif vpn_status_emoji == '⚠️':
            service_buttons.append(types.InlineKeyboardButton("⚠️ VPN: Файлы есть", callback_data="service_vpn_info"))
        elif vpn_status_emoji == '➖':
            service_buttons.append(types.InlineKeyboardButton("➖ VPN: Не настроен", callback_data="service_vpn_info"))
        else:
            service_buttons.append(types.InlineKeyboardButton("❓ VPN: Неизвестно", callback_data="service_vpn_info"))

        markup.add(*service_buttons)
        markup.add(types.InlineKeyboardButton("🔄 Обновить", callback_data="stats_refresh"))
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="menu_main"))
        return markup

    def handle_stats(chat_id):
        # Закрываем предыдущее окно статистики если открыто
        if state.last_stats_message_id:
            try:
                bot.delete_message(chat_id, state.last_stats_message_id)
            except:
                pass
        
        try:
            # При открытии статистики проверяем статусы сервисов
            stats = get_stats(refresh_services=True)
            msg = bot.send_message(chat_id, format_stats_message(stats), reply_markup=create_stats_keyboard(stats))
            state.last_stats_message_id = msg.message_id  # Сохраняем ID сообщения
        except Exception as e:
            log_error(f"Error opening stats: {e}")
            bot.send_message(chat_id, f"❌ Ошибка открытия статистики: {e}")

    def toggle_dns_override(chat_id, enable: bool):
        command = ["ndmc", "-c", "opkg dns-override"] if enable else ["ndmc", "-c", "no opkg dns-override"]
        status_text = "включен" if enable else "выключен"
        subprocess.run(command)
        time.sleep(2)
        subprocess.run(["ndmc", "-c", "system configuration save"])
        message_text = f'{"✅" if enable else "✖️"} DNS Override {status_text}!\n⏳ Роутер будет перезапущен!\nЭто займет около 2 минут'
        bot.send_message(chat_id, message_text)
        time.sleep(5)
        subprocess.run(["ndmc", "-c", "system reboot"])
    
    # Словарь переходов и действий
    MENU_TRANSITIONS = {
        '🔙 Назад': lambda chat_id: (
        set_menu_and_reply(chat_id, next(
            (m for m in [get_menu_main(), get_menu_service(), get_menu_bypass_files(), get_menu_keys_bridges(),
                         get_menu_tor(), get_menu_shadowsocks(), get_menu_vless(), get_menu_trojan(),
                         get_menu_bypass_list(), get_menu_add_bypass(), get_menu_remove_bypass()]
             if m.level == state.current_menu.back_level), get_menu_main()))
        ),
        '📑 Списки обхода': go_to_bypass_files,
        '🔑 Ключи и мосты': lambda chat_id: set_menu_and_reply(chat_id, get_menu_keys_bridges()),
        '⚙️ Сервис': lambda chat_id: set_menu_and_reply(chat_id, get_menu_service()),
        '🤖 Перезапуск бота': lambda chat_id: handle_restart(chat_id),
        '🔌 Перезапуск роутера': lambda chat_id: (
            bot.send_message(chat_id, "⏳ Роутер будет перезапущен!\nЭто займет около 2 минут", reply_markup=get_menu_service().markup),
            subprocess.run(["ndmc", "-c", "system reboot"])
        ),
        '⁉️ DNS Override': lambda chat_id: handle_dns_override(chat_id),
        '🔁 Перезапуск сервисов': lambda chat_id: (
            bot.send_message(chat_id, '⏳ Сервисы будут перезапущены!\nЭто займет около 10-15 секунд'),
            update_service(chat_id, "Shadowsocks", lambda: None, config.services["shadowsocks_restart"]),
            update_service(chat_id, "Tor", lambda: None, config.services["tor_restart"]),
            update_service(chat_id, "Vless", lambda: None, config.services["vless_restart"]),
            update_service(chat_id, "Trojan", lambda: None, config.services["trojan_restart"]),
            bot.send_message(chat_id, '❕ Перезапуск сервисов завершен', reply_markup=get_menu_main().markup)
        ),
        '🆕 Обновления': lambda chat_id: handle_updates(chat_id),
        '📲 Установка и удаление': lambda chat_id: handle_install_remove(chat_id),
        '💾 Бэкап': lambda chat_id: handle_backup(chat_id),
        '📊 Статистика': lambda chat_id: handle_stats(chat_id)
    }

    LEVEL_HANDLERS = {
        1: handle_bypass_files_selection,
        2: handle_bypass_list_menu,
        3: handle_add_to_bypass,
        4: handle_remove_from_bypass,
        5: handle_keys_bridges_selection,
        8: handle_tor_manually,
        9: handle_shadowsocks,
        10: handle_vless,
        11: handle_trojan,
    }

    @bot.message_handler(commands=['start'])
    def start(message):
        if message.from_user.username not in config.usernames:
            bot.send_message(message.chat.id, '⚠️ Вы не являетесь автором канала!')
            return
        set_menu_and_reply(message.chat.id, get_menu_main())

    @bot.message_handler(commands=['stats'])
    def stats_command(message):
        if message.from_user.username not in config.usernames:
            bot.send_message(message.chat.id, '⚠️ Доступ запрещён!')
            return
        stats = get_stats()
        bot.send_message(message.chat.id, format_stats_message(stats), reply_markup=create_stats_keyboard(stats))

    # Обработчики команд управления сервисами
    @bot.message_handler(commands=['tor_on', 'tor_off', 'vless_on', 'vless_off', 'trojan_on', 'trojan_off', 'ss_on', 'ss_off'])
    def service_command(message):
        if message.from_user.username not in config.usernames:
            bot.send_message(message.chat.id, '⚠️ Доступ запрещён!')
            return
        command = message.text.split()[0]
        parts = command[1:].rsplit('_', 1)
        if len(parts) != 2:
            bot.send_message(message.chat.id, '❌ Неверная команда')
            return
        service_name, action_type = parts
        enable = (action_type == 'on')
        services_map = {
            'tor': ('🔵 Tor', config.services["tor_restart"][0]),
            'vless': ('🔷 VLESS', config.services["vless_restart"][0]),
            'trojan': ('🟡 Trojan', config.services["trojan_restart"][0]),
            'ss': ('🟢 Shadowsocks', config.services["shadowsocks_restart"][0])
        }
        if service_name not in services_map:
            bot.send_message(message.chat.id, '❌ Неизвестный сервис')
            return
        name, init_script = services_map[service_name]
        status = "включение" if enable else "выключение"
        msg = bot.send_message(message.chat.id, f'⏳ {name} {status}...')
        try:
            # Проверяем существование скрипта
            if not os.path.exists(init_script):
                log_error(f"Script not found: {init_script}")
                bot.edit_message_text(f'❌ {name}: скрипт {init_script} не найден', msg.chat.id, msg.message_id)
                return
            
            # Выполняем команду
            cmd = [init_script, 'start' if enable else 'stop']
            log_error(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            log_error(f"Command result: returncode={result.returncode}, stdout={result.stdout}, stderr={result.stderr}")
            
            # Если не сработало, пробуем restart (для некоторых сервисов)
            if result.returncode != 0 and enable:
                log_error(f"Start failed for {name}, trying restart: {result.stderr}")
                cmd = [init_script, 'restart']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                log_error(f"Restart result: returncode={result.returncode}, stdout={result.stdout}, stderr={result.stderr}")
            
            # Проверяем статус после включения (кроме Trojan - у него могут быть проблемы со status)
            if enable and result.returncode == 0 and service_name != 'trojan':
                time.sleep(2)  # Ждём запуска
                status_result = subprocess.run([init_script, 'status'], capture_output=True, text=True, timeout=10)
                log_error(f"Status check: returncode={status_result.returncode}, output={status_result.stdout}")
                if status_result.returncode != 0:
                    log_error(f"{name} started but status check failed")
                    bot.edit_message_text(f'⚠️ {name} запущен, но статус не подтверждён. Проверьте вручную.', msg.chat.id, msg.message_id)
                    return
            
            # После выключения проверяем статус (кроме Trojan)
            if not enable and result.returncode == 0 and service_name != 'trojan':
                time.sleep(1)
                status_result = subprocess.run([init_script, 'status'], capture_output=True, text=True, timeout=10)
                if status_result.returncode == 0:
                    log_error(f"{name} not stopped, status still shows running")
                    result.returncode = 1  # Помечаем как ошибку
                    result.stdout = "Сервис не остановлен"
            
            # Для Trojan показываем предупреждение если статус failed
            if enable and result.returncode == 0 and service_name == 'trojan':
                log_error(f"✅ {name} started successfully (status check skipped)")
            
            if result.returncode == 0:
                bot.edit_message_text(f'✅ {name} {"включён" if enable else "выключен"}', msg.chat.id, msg.message_id)
            else:
                error = result.stderr.strip() or result.stdout.strip() or "Неизвестная ошибка"
                log_error(f"Service control error ({name}): {error}")
                bot.edit_message_text(f'❌ {name}: {error}', msg.chat.id, msg.message_id)
        except subprocess.TimeoutExpired:
            bot.edit_message_text(f'❌ Таймаут операции ({name})', msg.chat.id, msg.message_id)
        except Exception as e:
            log_error(f"Service control exception ({name}): {str(e)}")
            bot.edit_message_text(f'❌ Ошибка: {str(e)}', msg.chat.id, msg.message_id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("service_"))
    def handle_service_control(call):
        action = call.data.replace("service_", "")
        
        # Обработка VPN info
        if action == "vpn_info":
            bot.answer_callback_query(
                call.id,
                "ℹ️ VPN управляется через роутер Keenetic.\n\n"
                "Для использования VPN:\n"
                "1. Создайте файл vpn-<название>.txt\n"
                "2. Добавьте домены/IP для обхода\n"
                "3. Настройте VPN в веб-интерфейсе роутера",
                show_alert=True
            )
            return
        
        parts = action.rsplit('_', 1)
        if len(parts) != 2:
            bot.answer_callback_query(call.id, "❌ Неверная команда", show_alert=True)
            return
        service_name, action_type = parts
        enable = (action_type == "on")
        services_map = {
            'tor': ("🔵 Tor", config.services["tor_restart"][0], 'tor_status'),
            'vless': ("🔷 VLESS", config.services["vless_restart"][0], 'vless_status'),
            'trojan': ("🟡 Trojan", config.services["trojan_restart"][0], 'trojan_status'),
            'ss': ("🟢 Shadowsocks", config.services["shadowsocks_restart"][0], 'shadowsocks_status')
        }
        if service_name not in services_map:
            bot.answer_callback_query(call.id, "❌ Неизвестный сервис", show_alert=True)
            return
        name, init_script, stat_key = services_map[service_name]
        status = "включение" if enable else "выключение"

        # Показываем уведомление в процессе
        bot.answer_callback_query(call.id, f"⏳ {name} {status}...", show_alert=False)

        try:
            cmd = [init_script, 'start' if enable else 'stop']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                # Получаем статистику без проверки сервисов (быстро)
                stats = get_stats(refresh_services=False)
                
                # Проверяем статус только что изменённого сервиса
                try:
                    status_result = subprocess.run([init_script, 'status'], capture_output=True, text=True, timeout=2)
                    new_status = '✅' if status_result.returncode == 0 else '❌'
                    # Обновляем статус только этого сервиса
                    stats[stat_key] = new_status
                except:
                    pass  # Оставляем как есть
                
                bot.edit_message_text(
                    format_stats_message(stats),
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=create_stats_keyboard(stats)
                )
                # Показываем результат после обновления
                bot.answer_callback_query(call.id, f"✅ {name} {'включён' if enable else 'выключен'}", show_alert=False)
            else:
                error = result.stderr.strip() or result.stdout.strip() or "Неизвестная ошибка"
                bot.answer_callback_query(call.id, f"❌ Ошибка: {error}", show_alert=True)
        except subprocess.TimeoutExpired:
            bot.answer_callback_query(call.id, f"❌ Таймаут операции ({name})", show_alert=True)
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ Ошибка: {str(e)}", show_alert=True)

    @bot.message_handler(commands=['update'])
    def update_command(message):
        """Команда для ручного запуска обновления бота"""
        if message.from_user.username not in config.usernames:
            bot.send_message(message.chat.id, '⚠️ Доступ запрещён!')
            return
        
        # Отправляем сообщение и передаём его message_id в handle_update
        msg = bot.send_message(message.chat.id, '⏳ Запуск обновления...')
        # Эмулируем нажатие кнопки обновления с правильным message_id
        call = type('obj', (object,), {
            'message': message,
            'data': 'trigger_update',
            'from_user': message.from_user
        })
        # Создаем фейковый message_id для редактирования
        call.message.message_id = msg.message_id
        handle_update(call)

    @bot.message_handler(content_types=['text'])
    def bot_message(message):
        if message.from_user.username not in config.usernames or message.chat.type != 'private':
            bot.send_message(message.chat.id, '⚠️ Вы не являетесь автором канала или это не приватный чат!')
            return

        if message.text in MENU_TRANSITIONS:
            MENU_TRANSITIONS[message.text](message.chat.id)
        elif state.current_menu.level in LEVEL_HANDLERS:
            LEVEL_HANDLERS[state.current_menu.level](message)

    @bot.callback_query_handler(func=lambda call: call.data == "menu_service")
    def handle_backup_return(call):
        state.current_menu = get_menu_service()
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, state.current_menu.name, reply_markup=state.current_menu.markup)
        state.backup_state.__init__()

    @bot.callback_query_handler(func=lambda call: call.data.startswith("backup_toggle_"))
    def handle_backup_toggle(call):
        backup_type = call.data.replace("backup_toggle_", "")
        if backup_type == "startup":
            state.backup_state.startup_config = not state.backup_state.startup_config
        elif backup_type == "firmware":
            state.backup_state.firmware = not state.backup_state.firmware
        elif backup_type == "entware":
            state.backup_state.entware = not state.backup_state.entware
        elif backup_type == "custom":
            state.backup_state.custom_files = not state.backup_state.custom_files
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_backup_menu(state.backup_state))
            
    @bot.callback_query_handler(func=lambda call: call.data == "backup_create")
    def handle_backup_create(call):
        drives = get_available_drives()
        if not drives:
            bot.answer_callback_query(call.id, "❌ Нет доступных дисков для бэкапа", show_alert=True)
            return
        msg = bot.edit_message_text("Выберите диск для сохранения бэкапа:", call.message.chat.id, call.message.message_id, reply_markup=create_drive_selection_menu(drives))
        state.backup_state.selection_msg_id = msg.message_id

    @bot.callback_query_handler(func=lambda call: call.data.startswith("backup_drive_"))
    def handle_backup_drive_select(call):
        drive_uuid = call.data.replace("backup_drive_", "")
        drives = get_available_drives()
        selected_drive = next((d for d in drives if d['uuid'] == drive_uuid), None)
        if not selected_drive:
            bot.answer_callback_query(call.id, "❌ Выбранный диск недоступен", show_alert=True)
            return
        state.backup_state.selected_drive = selected_drive
        bot.edit_message_text(f"☑️ Выбран диск: {selected_drive['label']}\nУдалить архив с диска после создания бэкапа?", call.message.chat.id, state.backup_state.selection_msg_id, reply_markup=create_delete_archive_menu())

    @bot.callback_query_handler(func=lambda call: call.data in ["backup_delete_yes", "backup_delete_no"])
    def handle_delete_archive_choice(call):
        if call.data == "backup_delete_yes":
            state.backup_state.delete_archive = True
            choice_text = "Да"
        elif call.data == "backup_delete_no":
            state.backup_state.delete_archive = False
            choice_text = "Нет"
        bot.edit_message_text(
            f"☑️ Выбран диск: {state.backup_state.selected_drive['label']}\n☑️ Удалить архив: {choice_text}", call.message.chat.id, state.backup_state.selection_msg_id)
        progress_msg = bot.send_message(call.message.chat.id, "⏳ Начинаем создание бэкапа, подождите!")
        create_backup_with_params(bot, call.message.chat.id, state.backup_state, state.backup_state.selected_drive, progress_msg.message_id)
        state.backup_state.__init__()

    @bot.callback_query_handler(func=lambda call: call.data == "backup_menu")
    def handle_backup_menu_return(call):
        bot.edit_message_text("Выберите файлы для бэкапа:", call.message.chat.id, call.message.message_id, reply_markup=create_backup_menu(state.backup_state))
    
    @bot.callback_query_handler(func=lambda call: call.data == "dns_override_on")
    def handle_dns_override_on(call):
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        toggle_dns_override(call.message.chat.id, True)

    @bot.callback_query_handler(func=lambda call: call.data == "dns_override_off")
    def handle_dns_override_off(call):
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        toggle_dns_override(call.message.chat.id, False)
        
    @bot.callback_query_handler(func=lambda call: call.data == "trigger_update")
    def handle_update(call):
        chat_id = call.message.chat.id
        
        # Пытаемся скрыть кнопку обновления (игнорируем ошибку если нельзя редактировать)
        try:
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
        except Exception as e:
            if "message can't be edited" not in str(e) and "message is not modified" not in str(e):
                log_error(f"Error hiding update button: {e}")
        
        msg = bot.send_message(chat_id, '⏳ Загрузка обновлений...')

        try:
            download_bot_files()
            bot.edit_message_text('⏳ Файлы бота обновлены. Загрузка скрипта...', chat_id, msg.message_id)
            download_script()
            bot.edit_message_text('⏳ Скрипт обновлён. Выполняю установку...', chat_id, msg.message_id)
        except Exception as e:
            bot.edit_message_text(f'❌ Ошибка загрузки: {str(e)}', chat_id, msg.message_id)
            log_error(f"Error downloading updates: {str(e)}")
            return

        with open(config.paths["chat_id_path"], 'w') as f:
            f.write(str(chat_id))
        process = subprocess.Popen([config.paths['script_sh'], '-update'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        try:
            for line in process.stdout:
                bot.edit_message_text(f"⏳ {line.strip()}", chat_id, msg.message_id)
            process.wait(timeout=300)  # 5 минут таймаут
        except subprocess.TimeoutExpired:
            process.kill()
            bot.edit_message_text('❌ Превышен таймаут операции (5 минут)', chat_id, msg.message_id)
            log_error(f"Timeout expired for update script")
            return

        # Перезапуск бота с задержкой
        bot.edit_message_text('✅ Бот обновлён! Перезапуск через 3 секунды...', chat_id, msg.message_id)
        time.sleep(3)
        
        # Читаем текущую версию для отображения
        try:
            with open(config.paths["bot_dir"] + "/version.md", "r") as f:
                current_version = f.read().strip()
        except:
            current_version = "N/A"
        
        # Отправляем финальное сообщение с версией
        bot.send_message(
            chat_id,
            f'✅ Бот перезапущен\n\n📦 Версия: {current_version}\n💾 RAM: ~22-26 MB',
            reply_markup=get_menu_main().markup
        )
        
        # Запускаем новый процесс бота в фоне
        subprocess.Popen(
            ['python3', config.paths["bot_path"]],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=True
        )
        # Завершаем текущий процесс
        import os
        os._exit(0)

    @bot.callback_query_handler(func=lambda call: call.data == "install")
    def handle_install_callback(call):
        chat_id = call.message.chat.id
        download_script()
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
        msg = bot.send_message(chat_id, '⏳ Начинаем установку, подождите!')
        process = subprocess.Popen([config.paths['script_sh'], '-install'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        try:
            for line in process.stdout:
                bot.edit_message_text(f"⏳ {line.strip()}", chat_id, msg.message_id)
            process.wait(timeout=600)  # 10 минут таймаут для установки
        except subprocess.TimeoutExpired:
            process.kill()
            bot.edit_message_text('❌ Превышен таймаут операции (10 минут)', chat_id, msg.message_id)
            log_error(f"Timeout expired for install script")
            return
        if process.returncode == 0:
            bot.send_message(chat_id, '✅ Установка завершена', reply_markup=get_menu_main().markup)
        else:
            bot.send_message(chat_id, '❌ Установка завершилась с ошибкой', reply_markup=get_menu_main().markup)

    @bot.callback_query_handler(func=lambda call: call.data == "remove")
    def handle_remove_callback(call):
        chat_id = call.message.chat.id
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
        download_script()
        msg = bot.send_message(chat_id, '⏳ Начинаем удаление, подождите!')
        process = subprocess.Popen([config.paths['script_sh'], '-remove'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        try:
            for line in process.stdout:
                bot.edit_message_text(f"⏳ {line.strip()}", chat_id, msg.message_id)
            process.wait(timeout=300)  # 5 минут таймаут для удаления
        except subprocess.TimeoutExpired:
            process.kill()
            bot.edit_message_text('❌ Превышен таймаут операции (5 минут)', chat_id, msg.message_id)
            log_error(f"Timeout expired for remove script")
            return
        if process.returncode == 0:
            bot.send_message(chat_id, '✅ Удаление завершено', reply_markup=get_menu_main().markup)
        else:
            bot.send_message(chat_id, '❌ Ошибка при удалении', reply_markup=get_menu_main().markup)

    @bot.callback_query_handler(func=lambda call: call.data == "menu_main")
    def handle_back_to_main(call):
        state.current_menu = get_menu_main()
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, state.current_menu.name, reply_markup=state.current_menu.markup)

    @bot.callback_query_handler(func=lambda call: call.data == "stats_refresh")
    def handle_stats_refresh(call):
        # Быстрое обновление (только RAM и uptime, без проверки сервисов)
        bot.answer_callback_query(call.id, "⏳ Обновление...", show_alert=False)
        
        try:
            # Не проверяем сервисы повторно - они уже актуальны
            stats = get_stats(refresh_services=False)
            bot.edit_message_text(
                format_stats_message(stats),
                call.message.chat.id,
                call.message.message_id,
                reply_markup=create_stats_keyboard(stats)
            )
        except Exception as e:
            # Игнорируем ошибку "message is not modified" (Telegram API error 400)
            if "message is not modified" not in str(e):
                log_error(f"Error refreshing stats: {e}")
                bot.answer_callback_query(call.id, "❌ Ошибка обновления", show_alert=True)
