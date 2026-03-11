# Исправление бекапа прошивки на Keenetic KN-1212

**Goal:** Исправить бекап прошивки на KN-1212 — ndmc не поддерживает запись в /tmp, нужно использовать путь `uuid:/path`

**Root Cause:** В коде используется путь `/tmp/backup{timestamp}/...`, но ndmc на KN-1212 не поддерживает запись в /tmp!

**Рабочий формат (из keensnap.sh):**
```
ndmc -c "copy startup-config $device_uuid:/$date/filename"
```

---

## Task 1: Исправить пути для startup-config

**Files:**
- Modify: `src/bot3/utils.py:1136`

Изменить:
```python
# Было:
sys_destination = f"/tmp/backup{timestamp}/{device_id}_{fw_version}_startup-config.txt"

# Стало:
disk_uuid = selected_drive.get('uuid', '')
sys_destination = f"{disk_uuid}:/backup{timestamp}/{device_id}_{fw_version}_startup-config.txt"
```

Удалить код копирования из /tmp на диск (строки 1151-1163).

---

## Task 2: Исправить пути для firmware

**Files:**
- Modify: `src/bot3/utils.py:1200`

Изменить:
```python
# Было:
sys_destination = f"/tmp/backup{timestamp}/{device_id}_{fw_version}_firmware.bin"

# Стало:
disk_uuid = selected_drive.get('uuid', '')
sys_destination = f"{disk_uuid}:/backup{timestamp}/{device_id}_{fw_version}_firmware.bin"
```

Удалить код копирования из /tmp на диск (строки 1215-1227).

---

## Task 3: Удалить жёстко закодированные значения

**Files:**
- Modify: `src/bot3/utils.py:1180-1181`

Удалить:
```python
device_id = "KN-1212"
fw_version = "stable_4.03.C.6.3-9"
```

---

## Тестирование

```bash
# На роутере:
/opt/etc/init.d/S99telegram_bot restart

# Через бота: Меню → Сервис → Бэкап → выбрать всё → Создать
```
