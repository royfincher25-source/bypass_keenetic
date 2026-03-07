#!/bin/sh
# =============================================================================
# СКРИПТ СОХРАНЕНИЯ КОНФИГУРАЦИИ BYPASS_KEENETIC
# =============================================================================
# Сохраняет все настройки, конфиги и списки обхода
# Использование: /opt/root/backup_config.sh [backup|restore|list] [имя]
# =============================================================================

BACKUP_DIR="/opt/root/bypass_backups"
DATE_STAMP=$(date +%Y-%m-%d_%H-%M-%S)
CONFIG_DIR="/opt/etc"
BOT_DIR="/opt/etc/bot"
UNBLOCK_DIR="/opt/etc/unblock"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# СОЗДАНИЕ БЕКАПА
# =============================================================================
do_backup() {
    BACKUP_NAME=$1
    
    if [ -z "$BACKUP_NAME" ]; then
        BACKUP_NAME="$DATE_STAMP"
    fi
    
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
    
    log_info "Создание бэкапа конфигурации..."
    log_info "Путь: $BACKUP_PATH"
    
    # Создание директории бэкапа
    mkdir -p "$BACKUP_PATH"
    
    # 1. Сохранение .env файла (самое важное!)
    if [ -f "$BOT_DIR/.env" ]; then
        log_info "Сохранение .env файла..."
        cp "$BOT_DIR/.env" "$BACKUP_PATH/.env"
        chmod 600 "$BACKUP_PATH/.env"
    else
        log_warn ".env файл не найден"
    fi
    
    # 2. Сохранение конфигов бота
    if [ -d "$BOT_DIR" ]; then
        log_info "Сохранение файлов бота..."
        mkdir -p "$BACKUP_PATH/bot"
        cp -r "$BOT_DIR"/* "$BACKUP_PATH/bot/" 2>/dev/null
        # Исключаем большие файлы
        rm -f "$BACKUP_PATH/bot/"*.pyc 2>/dev/null
        rm -rf "$BACKUP_PATH/bot/__pycache__" 2>/dev/null
    fi
    
    # 3. Сохранение core модуля
    if [ -d "$BOT_DIR/core" ]; then
        log_info "Сохранение core модуля..."
        mkdir -p "$BACKUP_PATH/core"
        cp -r "$BOT_DIR/core"/* "$BACKUP_PATH/core/" 2>/dev/null
    fi
    
    # 4. Сохранение списков обхода
    if [ -d "$UNBLOCK_DIR" ]; then
        log_info "Сохранение списков обхода..."
        mkdir -p "$BACKUP_PATH/unblock"
        cp "$UNBLOCK_DIR"/*.txt "$BACKUP_PATH/unblock/" 2>/dev/null
    fi
    
    # 5. Сохранение конфигов сервисов
    for conf in torrc shadowsocks.json xray/config.json trojan/config.json; do
        conf_path="$CONFIG_DIR/$conf"
        if [ -f "$conf_path" ]; then
            log_info "Сохранение $conf..."
            mkdir -p "$BACKUP_PATH/configs/$(dirname $conf)"
            cp "$conf_path" "$BACKUP_PATH/configs/$conf" 2>/dev/null
        fi
    done
    
    # 6. Сохранение скриптов
    for script in /opt/root/script.sh /opt/root/KeenSnap/keensnap.sh; do
        if [ -f "$script" ]; then
            log_info "Сохранение $script..."
            mkdir -p "$BACKUP_PATH/scripts"
            cp "$script" "$BACKUP_PATH/scripts/" 2>/dev/null
        fi
    done
    
    # 7. Сохранение crontab
    if [ -f "$CONFIG_DIR/crontab" ]; then
        log_info "Сохранение crontab..."
        cp "$CONFIG_DIR/crontab" "$BACKUP_PATH/crontab" 2>/dev/null
    fi
    
    # 8. Сохранение информации о версии
    log_info "Сохранение информации о системе..."
    cat > "$BACKUP_PATH/system_info.txt" << EOF
Дата бэкапа: $(date)
Версия Keenetic: $(ndmc -c show version 2>/dev/null | head -5)
Версия Python: $(python3 --version 2>&1)
Установленные пакеты:
$(opkg list-installed 2>/dev/null | grep -E "python|telegram|requests|pyTelegram" || echo "Не удалось получить")
Свободное место:
$(df -h /opt 2>/dev/null | tail -1)
EOF
    
    # 9. Создание архива
    ARCHIVE_NAME="$BACKUP_DIR/bypass_backup_${BACKUP_NAME}.tar.gz"
    log_info "Создание архива $ARCHIVE_NAME..."
    
    cd "$BACKUP_DIR"
    tar -czf "$ARCHIVE_NAME" "$BACKUP_NAME" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        # Удаление временной директории
        rm -rf "$BACKUP_PATH"
        
        ARCHIVE_SIZE=$(ls -lh "$ARCHIVE_NAME" | awk '{print $5}')
        log_info "✅ Бэкап успешно создан!"
        log_info "Архив: $ARCHIVE_NAME"
        log_info "Размер: $ARCHIVE_SIZE"
        
        # Проверка свободного места
        FREE_SPACE=$(df -m /opt | tail -1 | awk '{print $4}')
        if [ "$FREE_SPACE" -lt 50 ]; then
            log_warn "⚠️ Мало свободного места на /opt (< 50 MB)"
        fi
    else
        log_error "❌ Ошибка при создании архива"
        return 1
    fi
    
    return 0
}

# =============================================================================
# ВОССТАНОВЛЕНИЕ ИЗ БЕКАПА
# =============================================================================
do_restore() {
    BACKUP_NAME=$1
    
    if [ -z "$BACKUP_NAME" ]; then
        log_error "Укажите имя бэкапа"
        log_info "Доступные бэкапы:"
        do_list
        return 1
    fi
    
    # Поиск архива
    ARCHIVE="$BACKUP_DIR/bypass_backup_${BACKUP_NAME}.tar.gz"
    
    if [ ! -f "$ARCHIVE" ]; then
        # Поиск по директории
        BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"
        if [ ! -d "$BACKUP_PATH" ]; then
            log_error "Бэкап не найден: $BACKUP_NAME"
            return 1
        fi
    fi
    
    log_info "Восстановление из бэкапа: $BACKUP_NAME"
    
    # Предупреждение
    echo ""
    log_warn "⚠️ ВНИМАНИЕ: Текущая конфигурация будет перезаписана!"
    echo "   Рекомендуется создать бэкап текущей конфигурации перед восстановлением."
    echo ""
    read -p "Продолжить? (y/n): " confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "Отменено"
        return 0
    fi
    
    # Распаковка
    if [ -f "$ARCHIVE" ]; then
        log_info "Распаковка архива..."
        cd "$BACKUP_DIR"
        tar -xzf "$ARCHIVE" 2>/dev/null
        RESTORE_PATH="$BACKUP_DIR/$BACKUP_NAME"
    else
        RESTORE_PATH="$BACKUP_PATH"
    fi
    
    if [ ! -d "$RESTORE_PATH" ]; then
        log_error "Ошибка распаковки"
        return 1
    fi
    
    # 1. Восстановление .env
    if [ -f "$RESTORE_PATH/.env" ]; then
        log_info "Восстановление .env файла..."
        cp "$RESTORE_PATH/.env" "$BOT_DIR/.env"
        chmod 600 "$BOT_DIR/.env"
    fi
    
    # 2. Восстановление файлов бота
    if [ -d "$RESTORE_PATH/bot" ]; then
        log_info "Восстановление файлов бота..."
        cp -r "$RESTORE_PATH/bot"/* "$BOT_DIR/" 2>/dev/null
    fi
    
    # 3. Восстановление core модуля
    if [ -d "$RESTORE_PATH/core" ]; then
        log_info "Восстановление core модуля..."
        mkdir -p "$BOT_DIR/core"
        cp -r "$RESTORE_PATH/core"/* "$BOT_DIR/core/" 2>/dev/null
    fi
    
    # 4. Восстановление списков обхода
    if [ -d "$RESTORE_PATH/unblock" ]; then
        log_info "Восстановление списков обхода..."
        mkdir -p "$UNBLOCK_DIR"
        cp "$RESTORE_PATH/unblock"/*.txt "$UNBLOCK_DIR/" 2>/dev/null
    fi
    
    # 5. Восстановление конфигов
    if [ -d "$RESTORE_PATH/configs" ]; then
        log_info "Восстановление конфигов..."
        cp -r "$RESTORE_PATH/configs"/* "$CONFIG_DIR/" 2>/dev/null
    fi
    
    # 6. Восстановление скриптов
    if [ -d "$RESTORE_PATH/scripts" ]; then
        log_info "Восстановление скриптов..."
        for script in "$RESTORE_PATH/scripts"/*; do
            if [ -f "$script" ]; then
                dest="/opt/root/$(basename $script)"
                cp "$script" "$dest"
                chmod 755 "$dest"
            fi
        done
    fi
    
    # 7. Восстановление crontab
    if [ -f "$RESTORE_PATH/crontab" ]; then
        log_info "Восстановление crontab..."
        cp "$RESTORE_PATH/crontab" "$CONFIG_DIR/crontab"
    fi
    
    # Перезапуск сервисов
    echo ""
    log_info "✅ Восстановление завершено!"
    echo ""
    read -p "Перезапустить бота? (y/n): " restart
    
    if [ "$restart" = "y" ] || [ "$restart" = "Y" ]; then
        log_info "Перезапуск бота..."
        /opt/etc/init.d/S99telegram_bot restart
        log_info "✅ Бот перезапущен"
    fi
    
    return 0
}

# =============================================================================
# СПИСОК БЕКАПОВ
# =============================================================================
do_list() {
    log_info "Доступные бэкапы:"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ]; then
        log_warn "Директория бэкапов не найдена"
        return 0
    fi
    
    count=0
    for archive in "$BACKUP_DIR"/bypass_backup_*.tar.gz; do
        if [ -f "$archive" ]; then
            count=$((count + 1))
            name=$(basename "$archive" | sed 's/bypass_backup_//' | sed 's/.tar.gz//')
            size=$(ls -lh "$archive" | awk '{print $5}')
            date=$(ls -l "$archive" | awk '{print $6, $7, $8}')
            printf "  %d) %-30s %s (%s)\n" "$count" "$name" "$size" "$date"
        fi
    done
    
    if [ $count -eq 0 ]; then
        log_warn "Бэкапы не найдены"
    else
        echo ""
        log_info "Всего бэкапов: $count"
    fi
}

# =============================================================================
# УДАЛЕНИЕ БЕКАПА
# =============================================================================
do_delete() {
    BACKUP_NAME=$1
    
    if [ -z "$BACKUP_NAME" ]; then
        log_error "Укажите имя бэкапа"
        return 1
    fi
    
    ARCHIVE="$BACKUP_DIR/bypass_backup_${BACKUP_NAME}.tar.gz"
    
    if [ ! -f "$ARCHIVE" ]; then
        log_error "Бэкап не найден: $BACKUP_NAME"
        return 1
    fi
    
    read -p "Удалить бэкап $BACKUP_NAME? (y/n): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        rm -f "$ARCHIVE"
        log_info "✅ Бэкап удалён"
    else
        log_info "Отменено"
    fi
}

# =============================================================================
# ОСНОВНОЙ СЦЕНАРИЙ
# =============================================================================

# Создание директории для бэкапов
mkdir -p "$BACKUP_DIR"

case "$1" in
    backup|b)
        do_backup "$2"
        ;;
    restore|r)
        do_restore "$2"
        ;;
    list|l)
        do_list
        ;;
    delete|d)
        do_delete "$2"
        ;;
    *)
        echo "Использование: $0 {backup|restore|list|delete} [имя]"
        echo ""
        echo "Команды:"
        echo "  backup [имя]   - Создать бэкап текущей конфигурации"
        echo "  restore имя    - Восстановить из бэкапа"
        echo "  list           - Показать список бэкапов"
        echo "  delete имя     - Удалить бэкап"
        echo ""
        echo "Примеры:"
        echo "  $0 backup                    # Создать бэкап с текущей датой"
        echo "  $0 backup before_optimize    # Создать бэкап с именем"
        echo "  $0 list                      # Показать все бэкапы"
        echo "  $0 restore before_optimize   # Восстановить из бэкапа"
        ;;
esac
