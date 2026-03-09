#!/bin/sh
# =============================================================================
# СКРИПТ АВТОМАТИЧЕСКОЙ ОЧИСТКИ СТАРЫХ БЕКАПОВ
# =============================================================================
# Удаляет бэкапы старше N дней
# Использование: /opt/root/cleanup_backups.sh [days_to_keep]
# =============================================================================

BACKUP_DIR="/opt/root/bypass_backups"
DAYS_TO_KEEP=${1:-7}  # По умолчанию хранить 7 дней

log_info() {
    echo "[INFO] $1"
}

log_warn() {
    echo "[WARN] $1"
}

# Проверка директории
if [ ! -d "$BACKUP_DIR" ]; then
    log_warn "Директория бэкапов не найдена: $BACKUP_DIR"
    exit 0
fi

# Подсчёт до очистки
TOTAL_BEFORE=$(ls -1 "$BACKUP_DIR"/bypass_backup_*.tar.gz 2>/dev/null | wc -l)
SIZE_BEFORE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)

log_info "Бэкапов до очистки: $TOTAL_BEFORE ($SIZE_BEFORE)"
log_info "Удаление бэкапов старше $DAYS_TO_KEEP дней..."

# Удаление старых бэкапов
deleted=0
for archive in "$BACKUP_DIR"/bypass_backup_*.tar.gz; do
    if [ -f "$archive" ]; then
        # Проверка возраста файла
        file_age=$(( ($(date +%s) - $(stat -c %Y "$archive" 2>/dev/null || stat -f %m "$archive" 2>/dev/null)) / 86400 ))
        
        if [ "$file_age" -gt "$DAYS_TO_KEEP" ]; then
            archive_name=$(basename "$archive")
            log_info "Удаление: $archive_name (возраст: $file_age дн.)"
            rm -f "$archive"
            deleted=$((deleted + 1))
        fi
    fi
done

# Подсчёт после очистки
TOTAL_AFTER=$(ls -1 "$BACKUP_DIR"/bypass_backup_*.tar.gz 2>/dev/null | wc -l)
SIZE_AFTER=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)

log_info "Удалено бэкапов: $deleted"
log_info "Бэкапов после очистки: $TOTAL_AFTER ($SIZE_AFTER)"

# Освобождённое место
if [ "$SIZE_BEFORE" != "$SIZE_AFTER" ]; then
    log_info "Освобождено места: $SIZE_BEFORE -> $SIZE_AFTER"
fi

# Предупреждение если мало бэкапов
if [ "$TOTAL_AFTER" -lt 2 ]; then
    log_warn "⚠️ Мало бэкапов! Рекомендуется создать новый."
fi

exit 0
