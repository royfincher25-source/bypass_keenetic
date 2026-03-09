# 📋 План оптимизации алгоритма архивации

**Дата:** 9 марта 2026 г.  
**Версия:** 3.5.3  
**Файл:** `deploy/backup/keensnap/keensnap.sh`

---

## 🎯 Цель

Оптимизировать алгоритм создания бэкапов для снижения нагрузки на диск и ускорения процесса.

---

## 🔴 Выявленные проблемы

### 1. Двойная запись на диск (КРИТИЧНО)

**Проблема:**
```bash
# Копирование файлов во временную папку
cp -r "$path" "$SELECTED_DRIVE/$date/"  # Запись ~50 MB

# Создание архива
tar -czf "$archive_path" -C "$SELECTED_DRIVE" "$date"  # Чтение + Сжатие

# Удаление временной папки
rm -rf "$SELECTED_DRIVE/$date"  # Очистка ~50 MB
```

**Итого:** 150 MB операций ввода-вывода

**Решение:** Прямое архивирование без копирования
```bash
tar -czf "$archive_path" $CUSTOM_BACKUP_PATHS 2>>"$LOG_FILE"
```

**Итого:** 50 MB операций (в 3 раза меньше!)

---

### 2. Множественная проверка места

**Проблема:**
```bash
check_free_space "$source_size_kb" "$item_name" 1  # Вызов 1
check_free_space "$source_size_kb" "$item_name" 1  # Вызов 2
check_free_space "$source_size_kb" "$item_name" 1  # Вызов 3
check_free_space "$total_size_kb" "финального архива" 2  # Вызов 4
```

**Решение:** Единая проверка в начале
```bash
total_required_kb=0
[ "$BACKUP_STARTUP_CONFIG" = "true" ] && total_required_kb=$((total_required_kb + 100))
[ "$BACKUP_FIRMWARE" = "true" ] && total_required_kb=$((total_required_kb + 20480))
[ "$BACKUP_ENTWARE" = "true" ] && total_required_kb=$((total_required_kb + $(du -s /opt | awk '{print $1}')))
[ "$BACKUP_CUSTOM_FILES" = "true" ] && {
    for path in $CUSTOM_BACKUP_PATHS; do
        total_required_kb=$((total_required_kb + $(du -s "$path" | awk '{print $1}')))
    done
}
check_free_space "$total_required_kb" "всех бэкапов" 2
```

---

### 3. Утечка temp файлов

**Проблема:**
```bash
local exclude_file=$(mktemp)
echo "$backup_file" > "$exclude_file"
if ! tar czf "$backup_file" -X "$exclude_file" -C /opt . 2>>"$LOG_FILE"; then
    error "Ошибка..."
    return 1  # ← exclude_file не удалён!
fi
rm -f "$exclude_file"  # ← Не выполнится при ошибке
```

**Решение:**
```bash
local exclude_file=$(mktemp)
trap "rm -f '$exclude_file'" EXIT
echo "$backup_file" > "$exclude_file"
if ! tar czf "$backup_file" -X "$exclude_file" -C /opt . 2>>"$LOG_FILE"; then
    error "Ошибка..."
    return 1
fi
```

---

### 4. Нет прогресса по файлам

**Проблема:**
```bash
backup_custom_files && backup_performed=1 || backup_failed=1
```

**Решение:**
```bash
progress "Архивирование пользовательских файлов..."
for path in $CUSTOM_BACKUP_PATHS; do
    if [ -e "$path" ]; then
        progress "  - $(basename "$path")"
    fi
done
tar -czf "$archive_path" $CUSTOM_BACKUP_PATHS 2>>"$LOG_FILE"
```

---

### 5. Нет сжатия firmware (опционально)

**Проблема:**
```bash
ndmc -c "copy flash:/$item_name $backup_file"  # 20 MB без сжатия
```

**Решение:**
```bash
if [ "$COMPRESS_FIRMWARE" = "true" ]; then
    ndmc -c "copy flash:/$item_name /tmp/$item_name.bin"
    gzip -c /tmp/$item_name.bin > "$backup_file.gz"
    rm -f /tmp/$item_name.bin
else
    ndmc -c "copy flash:/$item_name $backup_file"
fi
```

---

## 📈 Ожидаемые улучшения

| Метрика | До | После | Улучшение |
|---------|-----|-------|-----------|
| **Операции I/O** | 150 MB | 50 MB | **3x меньше** |
| **Время бэкапа** | ~60 сек | ~25 сек | **2.4x быстрее** |
| **Временные файлы** | ~50 MB | 0 MB | **100% меньше** |
| **Проверка места** | 4 вызова df | 1 вызов | **4x меньше** |
| **Temp файлы** | Утечка | Гарантированная очистка | **Без утечек** |

---

## 🔧 Изменения в коде

### Функция `backup_custom_files`

**До:**
```bash
backup_custom_files() {
    local item_name="custom-files"
    local device_uuid=$(echo "$SELECTED_DRIVE" | awk -F'/' '{print $NF}')
    local folder_path="$device_uuid:/$date"

    if [ -z "$CUSTOM_BACKUP_PATHS" ]; then
        error "Переменная CUSTOM_BACKUP_PATHS не задана в bot_config.py"
        return 1
    fi

    local source_size_kb=0

    for path in $CUSTOM_BACKUP_PATHS; do
        if [ -e "$path" ]; then
            local path_size_kb=$(du -s "$path" | awk '{print $1}')
            source_size_kb=$((source_size_kb + path_size_kb))
        fi
    done

    check_free_space "$source_size_kb" "$item_name" 1 || return 1
    progress "Создаю бекап: $CUSTOM_BACKUP_PATHS в $folder_pah"

    for path in $CUSTOM_BACKUP_PATHS; do
        if ! cp -r "$path" "$SELECTED_DRIVE/$date/" 2>>"$LOG_FILE"; then
            error "Ошибка при копировании $path"
            return 1
        fi
    done
    return 0
}
```

**После:**
```bash
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
```

---

### Функция `create_backup`

**До:**
```bash
create_backup() {
    # ... проверки ...
    
    progress "Выбран диск: $SELECTED_DRIVE"
    progress "Создаю временную папку: $SELECTED_DRIVE/$date"
    mkdir -p "$SELECTED_DRIVE/$date"
    local backup_performed=0
    local backup_failed=0

    [ "$BACKUP_STARTUP_CONFIG" = "true" ] && { backup_startup_config && backup_performed=1 || backup_failed=1; }
    [ "$BACKUP_FIRMWARE" = "true" ] && { backup_firmware && backup_performed=1 || backup_failed=1; }
    [ "$BACKUP_ENTWARE" = "true" ] && { backup_entware && backup_performed=1 || backup_failed=1; }
    [ "$BACKUP_CUSTOM_FILES" = "true" ] && { backup_custom_files && backup_performed=1 || backup_failed=1; }

    if [ "$backup_failed" -eq 1 ]; then
        error "Один или несколько бэкапов завершились с ошибкой"
        echo "{\"status\": \"error\", \"message\": \"...\"}"
        rm -rf "$SELECTED_DRIVE/$date"
        return 1
    fi

    progress "Все бэкапы завершены"
    local total_size_kb=$(du -s "$SELECTED_DRIVE/$date" | awk '{print $1}')
    check_free_space "$total_size_kb" "финального архива" 2 || {
        rm -rf "$SELECTED_DRIVE/$date"
        echo "{\"status\": \"error\", \"message\": \"...\"}"
        return 1
    }
    local archive_path="$SELECTED_DRIVE/${DEVICE_ID}_$date.tar.gz"
    progress "Создаю финальный архив в $archive_path"

    if tar -czf "$archive_path" -C "$SELECTED_DRIVE" "$date" 2>>"$LOG_FILE"; then
        progress "Архив успешно создан: $archive_path"
        echo "{\"status\": \"success\", \"archive_path\": \"$archive_path\"}"
    else
        error "Ошибка при создании архива"
        echo "{\"status\": \"error\", \"message\": \"...\"}"
        rm -rf "$SELECTED_DRIVE/$date"
        return 1
    fi
    progress "Удаляю временную папку $SELECTED_DRIVE/$date"
    rm -rf "$SELECTED_DRIVE/$date"
}
```

**После:**
```bash
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
    local archive_files=""

    [ "$BACKUP_STARTUP_CONFIG" = "true" ] && { backup_startup_config && archive_files="$archive_files startup.txt" && backup_performed=1 || backup_failed=1; }
    [ "$BACKUP_FIRMWARE" = "true" ] && { backup_firmware && archive_files="$archive_files firmware.bin" && backup_performed=1 || backup_failed=1; }
    [ "$BACKUP_ENTWARE" = "true" ] && { backup_entware && archive_files="$archive_files entware.tar.gz" && backup_performed=1 || backup_failed=1; }
    [ "$BACKUP_CUSTOM_FILES" = "true" ] && { backup_custom_files && archive_files="$archive_files custom.tar.gz" && backup_performed=1 || backup_failed=1; }

    if [ "$backup_failed" -eq 1 ]; then
        error "Один или несколько бэкапов завершились с ошибкой"
        echo "{\"status\": \"error\", \"message\": \"...\"}"
        # Очистка созданных файлов
        for file in $archive_files; do
            rm -f "$SELECTED_DRIVE/$file"
        done
        return 1
    fi

    progress "Все бэкапы завершены"
    echo "{\"status\": \"success\", \"archive_path\": \"$SELECTED_DRIVE/${DEVICE_ID}_$date\"}"
}
```

---

### Функция `backup_entware`

**До:**
```bash
backup_entware() {
    local item_name="Entware"
    local backup_file="$SELECTED_DRIVE/$date/$(get_architecture)-installer.tar.gz"
    local source_size_kb=$(du -s /opt | awk '{print $1}')
    check_free_space "$source_size_kb" "$item_name" 1 || return 1
    progress "Создаю бекап $item_name в $backup_file"
    local exclude_file=$(mktemp)
    echo "$backup_file" > "$exclude_file"
    if ! tar czf "$backup_file" -X "$exclude_file" -C /opt . 2>>"$LOG_FILE"; then
        error "Ошибка при сохранении $item_name"
        return 1
    fi
    rm -f "$exclude_file"
    return 0
}
```

**После:**
```bash
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
    return 0
}
```

---

## ✅ Критерии приёмки

- [ ] Удалена временная папка `$SELECTED_DRIVE/$date`
- [ ] Прямое архивирование без копирования
- [ ] Единая проверка места в начале
- [ ] Гарантированная очистка temp файлов
- [ ] Прогресс по каждому файлу
- [ ] Тесты пройдены
- [ ] Документация обновлена

---

## 📝 Примечания

1. **Обратная совместимость:** Формат архивов изменится (отдельные .tar.gz файлы вместо одного)
2. **Миграция:** Старые бэкапы останутся совместимы
3. **Тестирование:** Обязательно протестировать на роутере перед публикацией
