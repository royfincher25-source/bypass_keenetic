#!/bin/sh

for arg in "$@"; do
    case "$arg" in
        LOG_FILE=*) LOG_FILE="${arg#*=}" ;;
        SELECTED_DRIVE=*) SELECTED_DRIVE="${arg#*=}" ;;
        BACKUP_STARTUP_CONFIG=*) BACKUP_STARTUP_CONFIG="${arg#*=}" ;;
        BACKUP_FIRMWARE=*) BACKUP_FIRMWARE="${arg#*=}" ;;
        BACKUP_ENTWARE=*) BACKUP_ENTWARE="${arg#*=}" ;;
        BACKUP_CUSTOM_FILES=*) BACKUP_CUSTOM_FILES="${arg#*=}" ;;
        CUSTOM_BACKUP_PATHS=*) CUSTOM_BACKUP_PATHS="${arg#*=}" ;;
    esac
done

date="backup$(date +%Y-%m-%d_%H-%M)"

progress() {
    echo "{\"type\": \"progress\", \"message\": \"$*\"}"
}

error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $*" >> "$LOG_FILE"
}

clean_log() {
    local log_file="$1"
    if [ ! -f "$log_file" ]; then
        touch "$log_file"
        return
    fi
	
    local file_size=$(wc -c < "$log_file")
    local max_size=524288
    if [ "$file_size" -gt "$max_size" ]; then
        tail -n 50 "$log_file" >"$log_file.tmp" && mv "$log_file.tmp" "$log_file"
    fi
}

get_device_info() {
    version_output=$(ndmc -c show version 2>/dev/null)
    DEVICE=$(echo "$version_output" | grep "device:" | awk -F": " '{print $2}')
    RELEASE=$(echo "$version_output" | grep "release:" | awk -F": " '{print $2}')
    SANDBOX=$(echo "$version_output" | grep "sandbox:" | awk -F": " '{print $2}')
    DEVICE_ID=$(echo "$version_output" | grep "hw_id:" | awk -F": " '{print $2}')

    [ -z "$DEVICE" ] && DEVICE="unknown"
    [ -z "$RELEASE" ] && RELEASE="unknown"
    [ -z "$SANDBOX" ] && SANDBOX="unknown"
    [ -z "$DEVICE_ID" ] && DEVICE_ID="unknown"

    FW_VERSION="${SANDBOX}_${RELEASE}"
}

get_architecture() {
    arch=$(opkg print-architecture | grep -oE 'mips-3|mipsel-3|aarch64-3|armv7' | head -n 1)
    case "$arch" in
        "mips-3") echo "mips" ;;
        "mipsel-3") echo "mipsel" ;;
        "aarch64-3") echo "aarch64" ;;
        "armv7") echo "armv7" ;;
        *) echo "unknown_arch" ;;
    esac
}

check_free_space() {
    local source_size_kb="$1"
    local backup_name="$2"
    local multiplier="$3"
    local required_size_kb=$((source_size_kb * multiplier))
    local available_size_kb=$(df -k "$SELECTED_DRIVE" | tail -n 1 | awk '{print $4}')
    if [ "$available_size_kb" -lt "$required_size_kb" ]; then
        error "Недостаточно места для $backup_name (нужно $((required_size_kb / 1024)) MB, доступно $((available_size_kb / 1024)) MB)"
        return 1
    fi
    progress "Для $backup_name (нужно $((required_size_kb / 1024)) MB, доступно $((available_size_kb / 1024)) MB)"
    return 0
}

backup_startup_config() {
    local item_name="startup-config"
    local device_uuid=$(echo "$SELECTED_DRIVE" | awk -F'/' '{print $NF}')
    local folder_path="$device_uuid:/$date"
    local backup_file="$folder_path/${DEVICE_ID}_${FW_VERSION}_$item_name.txt"
    progress "Создаю бэкап $item_name в $backup_file"
	
    if ! ndmc -c "copy $item_name $backup_file" >/dev/null 2>>"$LOG_FILE"; then
        error "Ошибка при сохранении $item_name"
        return 1
    fi
    return 0
}

backup_firmware() {
    local item_name="firmware"
    local device_uuid=$(echo "$SELECTED_DRIVE" | awk -F'/' '{print $NF}')
    local folder_path="$device_uuid:/$date"
    local backup_file="$folder_path/${DEVICE_ID}_${FW_VERSION}_$item_name.bin"
    local source_size_kb=20480
    check_free_space "$source_size_kb" "$item_name" 1 || return 1
    progress "Создаю бекап $item_name в $backup_file"

    if ! ndmc -c "copy flash:/$item_name $backup_file" >/dev/null 2>>"$LOG_FILE"; then
        error "Ошибка при сохранении $item_name"
        return 1
    fi
    return 0
}

backup_entware() {
    local item_name="Entware"
    local backup_file="$SELECTED_DRIVE/${DEVICE_ID}_${date}_entware.tar.gz"
    local source_size_kb=$(du -s /opt | awk '{print $1}')
    check_free_space "$source_size_kb" "$item_name" 1 || return 1
    progress "Создаю бэкап $item_name в $backup_file"
    local exclude_file=$(mktemp)
    trap "rm -f '$exclude_file'" EXIT
    echo "$backup_file" > "$exclude_file"
    if ! tar czf "$backup_file" -X "$exclude_file" -C /opt . 2>>"$LOG_FILE"; then
        error "Ошибка при сохранении $item_name"
        return 1
    fi
    progress "Бэкап $item_name завершён"
    return 0
}

backup_custom_files() {
    local item_name="custom-files"
    local archive_path="$SELECTED_DRIVE/${DEVICE_ID}_${date}_custom-files.tar.gz"
    
    if [ -z "$CUSTOM_BACKUP_PATHS" ]; then
        error "Переменная CUSTOM_BACKUP_PATHS не задана в bot_config.py"
        return 1
    fi
    
    # Проверка существования файлов
    local existing_paths=""
    for path in $CUSTOM_BACKUP_PATHS; do
        if [ -e "$path" ]; then
            existing_paths="$existing_paths $path"
        else
            error "Путь не найден: $path"
        fi
    done
    
    if [ -z "$existing_paths" ]; then
        error "Не найдено файлов для бэкапа"
        return 1
    fi
    
    local source_size_kb=0
    for path in $existing_paths; do
        source_size_kb=$((source_size_kb + $(du -s "$path" | awk '{print $1}')))
    done
    
    check_free_space "$source_size_kb" "$item_name" 1 || return 1
    progress "Архивирование пользовательских файлов..."
    
    for path in $existing_paths; do
        progress "  - $(basename "$path")"
    done
    
    if ! tar -czf "$archive_path" $existing_paths 2>>"$LOG_FILE"; then
        error "Ошибка при создании архива"
        return 1
    fi
    
    progress "Архив создан: $archive_path"
    return 0
}

create_backup() {
    if [ -z "$SELECTED_DRIVE" ]; then
        echo "{\"status\": \"error\", \"message\": \"Не указан путь к диску для бэкапа\"}"
        return 1
    fi

    if [ ! -d "$SELECTED_DRIVE" ]; then
        echo "{\"status\": \"error\", \"message\": \"Указанный путь недоступен: $SELECTED_DRIVE\"}"
        return 1
    fi

    # Единая проверка места для всех бэкапов
    local total_required_kb=0
    [ "$BACKUP_STARTUP_CONFIG" = "true" ] && total_required_kb=$((total_required_kb + 100))
    [ "$BACKUP_FIRMWARE" = "true" ] && total_required_kb=$((total_required_kb + 20480))
    [ "$BACKUP_ENTWARE" = "true" ] && total_required_kb=$((total_required_kb + $(du -s /opt | awk '{print $1}')))
    [ "$BACKUP_CUSTOM_FILES" = "true" ] && {
        for path in $CUSTOM_BACKUP_PATHS; do
            [ -e "$path" ] && total_required_kb=$((total_required_kb + $(du -s "$path" | awk '{print $1}')))
        done
    }
    check_free_space "$total_required_kb" "всех бэкапов" 2 || return 1

    progress "Выбран диск: $SELECTED_DRIVE"
    local backup_performed=0
    local backup_failed=0

    [ "$BACKUP_STARTUP_CONFIG" = "true" ] && { backup_startup_config && backup_performed=1 || backup_failed=1; }
    [ "$BACKUP_FIRMWARE" = "true" ] && { backup_firmware && backup_performed=1 || backup_failed=1; }
    [ "$BACKUP_ENTWARE" = "true" ] && { backup_entware && backup_performed=1 || backup_failed=1; }
    [ "$BACKUP_CUSTOM_FILES" = "true" ] && { backup_custom_files && backup_performed=1 || backup_failed=1; }

    if [ "$backup_failed" -eq 1 ]; then
        error "Один или несколько бэкапов завершились с ошибкой"
        echo "{\"status\": \"error\", \"message\": \"Один или несколько бэкапов завершились с ошибкой, см. $LOG_FILE\"}"
        return 1
    fi

    progress "Все бэкапы завершены"
    echo "{\"status\": \"success\", \"archive_path\": \"$SELECTED_DRIVE/${DEVICE_ID}_$date\"}"
}

main() {
    clean_log "$LOG_FILE"
    get_device_info
    create_backup
}

main
