# План исправления проблем бэкапа

**Дата:** 11 марта 2026 г.  
**Статус:** План  
**Версия:** 1.1

---

## 🔴 Проблемы

| # | Проблема | Статус |
|---|----------|--------|
| 1 | Entware архивируется полностью (500MB+) | ❌ |
| 2 | keensnap.sh НЕ загружается автоматически | ❌ |
| 3 | Нет проверки существования keensnap.sh | ❌ |
| 4 | Тихая обработка ошибок | ❌ |

---

## План исправлений

### 🔴 Проблема 1: Entware архивируется полностью (500MB+)

**Решение:** Добавить исключения в `keensnap.sh`

**Файл:** `deploy/backup/keensnap/keensnap.sh`

**Изменения:**
```bash
# Создать файл исключений
cat > "$exclude_file" << EOF
$backup_file
root/KeenSnap/*.tar.gz
var/cache/*
var/log/*.log
tmp/*
EOF

# Использовать исключения
tar czf "$backup_file" -X "$exclude_file" -C /opt .
```

---

### 🔴 Проблема 2: keensnap.sh НЕ загружается автоматически

**Решение:** Добавить проверку и автозагрузку в `core/backup.py`

**Файл:** `src/core/backup.py`

**Изменения:**
```python
# Перед вызовом скрипта
if not os.path.exists(keensnap_path):
    # Автозагрузка
    download_script(keensnap_url, keensnap_path)
```

---

### 🔴 Проблема 3: Нет проверки существования keensnap.sh

**Решение:** Добавить проверку с понятной ошибкой

**Файл:** `src/core/backup.py`

**Изменения:**
```python
if not os.path.exists(keensnap_path):
    raise FileNotFoundError(f"KeenSnap скрипт не найден: {keensnap_path}")
```

---

### 🔴 Проблема 4: Тихая обработка ошибок

**Решение:** Логировать stderr от keensnap.sh

**Файл:** `src/core/backup.py`

**Изменения:**
```python
stderr_output = process.stderr.read()
if stderr_output:
    log_error(f"KeenSync stderr: {stderr_output}")
```

---

## Файлы для изменения

1. `deploy/backup/keensnap/keensnap.sh` — исключения для tar
2. `src/core/backup.py` — проверка keensnap.sh, логирование
3. `src/bot3/utils.py` — автозагрузка keensnap.sh перед бэкапом

---

## Критерии завершения

- ✅ Entware архивируется без кеша, логов и старых бэкапов
- ✅ keensnap.sh загружается автоматически при отсутствии
- ✅ Ошибки логируются и показываются пользователю
- ✅ Размер бэкапа Entware < 100MB

---

**Файл:** `docs/plans/2026-03-11-backup-fixes.md`
