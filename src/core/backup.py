# =============================================================================
# CORE BACKUP
# =============================================================================
# Функции для работы с бэкапами в bot3 и botlight
# =============================================================================

import os
import subprocess
import time


def download_script(url, path):
    """
    Загрузка скрипта по URL.
    
    Args:
        url (str): URL для загрузки
        path (str): Путь для сохранения
    """
    import requests
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(response.text)
        os.chmod(path, 0o755)
        return True
    except Exception:
        return False


def ensure_keensnap_exists(keensnap_path, keensnap_url):
    """
    Проверка существования keensnap.sh и автозагрузка при отсутствии.
    
    Args:
        keensnap_path (str): Путь к скрипту
        keensnap_url (str): URL для загрузки
        
    Returns:
        bool: True если скрипт существует или загружен
        
    Raises:
        FileNotFoundError: Если скрипт не найден и не удалось загрузить
    """
    if os.path.exists(keensnap_path):
        return True
    
    # Пытаемся загрузить автоматически
    if download_script(keensnap_url, keensnap_path):
        return True
    
    raise FileNotFoundError(
        f"KeenSnap скрипт не найден: {keensnap_path}\n"
        f"URL: {keensnap_url}\n"
        f"Загрузите скрипт вручную или проверьте подключение к интернету"
    )


def get_available_drives():
    """
    Получение списка доступных дисков для бэкапа.
    
    Returns:
        list: Список словарей с информацией о дисках
              [{'uuid': str, 'path': str, 'label': str, 'fstype': str}, ...]
    """
    drives = []
    current_drive = None
    current_manufacturer = None
    
    try:
        media_output = subprocess.check_output(
            ["ndmc", "-c", "show media"],
            text=True,
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError:
        return []
    except Exception:
        return []
    
    for raw_line in media_output.splitlines():
        stripped = raw_line.strip()
        
        if stripped.startswith("manufacturer:"):
            current_manufacturer = stripped.split(":", 1)[1].strip()
        
        elif stripped.startswith("uuid:"):
            if current_drive:
                drives.append(current_drive)
            uuid = stripped.split(":", 1)[1].strip()
            current_drive = {
                'uuid': uuid,
                'path': f"/tmp/mnt/{uuid}"
            }
        
        elif stripped.startswith("label:") and current_drive is not None:
            current_drive['label'] = stripped.split(":", 1)[1].strip()
        
        elif stripped.startswith("fstype:") and current_drive is not None:
            fstype = stripped.split(":", 1)[1].strip()
            if fstype == "swap":
                current_drive = None
            else:
                current_drive['fstype'] = fstype
    
    if current_drive:
        drives.append(current_drive)
    
    return drives


def create_backup_with_params(bot, chat_id, backup_state, selected_drive, progress_msg_id,
                               keensnap_path="/opt/root/KeenSnap/keensnap.sh",
                               keensnap_url=None,
                               max_size_mb=45):
    """
    Создание бэкапа с параметрами.

    Args:
        bot: TeleBot объект
        chat_id (int): ID чата для уведомлений
        backup_state: Объект состояния бэкапа
        selected_drive (dict): Информация о выбранном диске
        progress_msg_id (int): ID сообщения с прогрессом
        keensnap_path (str): Путь к скрипту KeenSnap
        keensnap_url (str): URL для загрузки скрипта (если нужен)
        max_size_mb (int): Максимальный размер бэкапа в MB

    Returns:
        None
    """
    from .logging import log_error

    archive_path = None
    max_size = max_size_mb * 1024 * 1024
    
    # URL по умолчанию для автозагрузки
    if keensnap_url is None:
        keensnap_url = "https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/deploy/backup/keensnap/keensnap.sh"

    # Проверяем существование keensnap.sh и загружаем при необходимости
    try:
        ensure_keensnap_exists(keensnap_path, keensnap_url)
    except FileNotFoundError as e:
        bot.edit_message_text(
            f"❌ {str(e)}",
            chat_id,
            progress_msg_id
        )
        log_error(str(e))
        return

    params = {
        "LOG_FILE": "/opt/root/KeenSnap/backup.log",
        "SELECTED_DRIVE": selected_drive["path"],
        "BACKUP_STARTUP_CONFIG": str(getattr(backup_state, 'startup_config', False)).lower(),
        "BACKUP_FIRMWARE": str(getattr(backup_state, 'firmware', False)).lower(),
        "BACKUP_ENTWARE": str(getattr(backup_state, 'entware', False)).lower(),
        "BACKUP_CUSTOM_FILES": str(getattr(backup_state, 'custom_files', False)).lower()
    }

    args = [keensnap_path]
    args.extend([f"{k}={v}" for k, v in params.items()])

    if getattr(backup_state, 'custom_files', False) and hasattr(backup_state, 'custom_backup_paths'):
        args.append(f"CUSTOM_BACKUP_PATHS={backup_state.custom_backup_paths}")

    try:
        process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        final_result = None
        stderr_output = []

        for line in process.stdout:
            line = line.strip()
            if not line:
                continue

            try:
                import json
                data = json.loads(line)

                if data.get("type") == "progress":
                    bot.edit_message_text(
                        f"⏳ {data['message']}",
                        chat_id,
                        progress_msg_id
                    )
                elif "status" in data:
                    final_result = data

            except (json.JSONDecodeError, ValueError):
                continue

        # Читаем stderr и логируем ошибки
        stderr_output = process.stderr.read()
        if stderr_output:
            for error_line in stderr_output.strip().split('\n'):
                if error_line:
                    log_error(f"KeenSnap stderr: {error_line}")

        process.wait(timeout=900)  # 15 минут таймаут
        
        if final_result and final_result["status"] == "success":
            archive_path = final_result["archive_path"]
            
            if not os.path.exists(archive_path):
                bot.edit_message_text(
                    "❌ Ошибка: архив не найден после создания",
                    chat_id,
                    progress_msg_id
                )
                return
            
            archive_size = os.path.getsize(archive_path)
            
            if archive_size <= max_size:
                bot.edit_message_text(
                    "✅ Бэкап создан, отправляю файл...",
                    chat_id,
                    progress_msg_id
                )
                
                caption = f"✅ Бэкап создан:\n{', '.join(getattr(backup_state, 'get_selected_types', lambda: ['бэкап'])())}"
                
                with open(archive_path, 'rb') as f:
                    bot.send_document(chat_id, f, caption=caption)
                
                bot.edit_message_text(
                    f"✅ Бэкап успешно завершен",
                    chat_id,
                    progress_msg_id
                )
            else:
                bot.edit_message_text(
                    f"❕ Бэкап создан, файл слишком большой ({archive_size // 1024 // 1024} MB)",
                    chat_id,
                    progress_msg_id
                )
                # Здесь можно добавить разбиение на части (из botlight)
        
        elif final_result:
            bot.edit_message_text(
                f"❌ Ошибка при создании бэкапа: {final_result.get('message', 'Неизвестная ошибка')}",
                chat_id,
                progress_msg_id
            )
        else:
            bot.edit_message_text(
                "❌ Ошибка: скрипт завершился без результата",
                chat_id,
                progress_msg_id
            )
    
    except subprocess.TimeoutExpired:
        process.kill()
        bot.edit_message_text(
            '❌ Превышен таймаут операции (15 минут)',
            chat_id,
            progress_msg_id
        )
        log_error("Timeout expired for backup script")
    
    except Exception as e:
        bot.edit_message_text(
            f"❌ Ошибка: {str(e)}",
            chat_id,
            progress_msg_id
        )
        log_error(f"Backup error: {e}")
    
    finally:
        # Очистка архива если нужно
        delete_archive = getattr(backup_state, 'delete_archive', False)
        if archive_path and os.path.exists(archive_path) and delete_archive:
            try:
                os.remove(archive_path)
            except Exception as e:
                log_error(f"Ошибка при удалении архива {archive_path}: {str(e)}")
