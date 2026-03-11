# Анализ проблемы бэкапа в bypass_keenetic

## Дата анализа: 2026-03-11

---

## Симптомы проблемы

- При создании бэкапа не сохраняются данные Entware и роутера
- Ошибка DNS при работе бота (после подключения USB с Entware)
- Бот не может подключиться к api.telegram.org

---

## Архитектура бэкапа

Есть **ДВЕ версии** кода бэкапа:

### 1. keensnap.sh (shell-скрипт)
- **Путь:** `deploy/backup/keensnap/keensnap.sh`
- **Назначение:** Реальный бэкап через системные команды
- **Функции:**
  - `backup_startup_config()` — сохранение startup-config через ndmc
  - `backup_firmware()` — сохранение прошивки через ndmc
  - `backup_entware()` — архивирование /opt через tar

### 2. Python обёртка (core/backup.py)
- **Путь:** `src/core/backup.py`
- **Назначение:** Вызывает keensnap.sh с параметрами, парсит JSON-ответ

---

## Обнаруженные проблемы

### 🔴 Проблема 1: keensnap.sh НЕ загружается автоматически

**Код:** `src/bot3/utils.py:295-302`

```python
# Загрузка обновлённого keensnap.sh
keensnap_url = f"{config.base_url}/deploy/backup/keensnap/keensnap.sh"
keensnap_path = config.paths.get("script_bu", "/opt/root/KeenSnap/keensnap.sh")
download_script(keensnap_url, keensnap_path)
```

**Проблема:** keensnap.sh загружается только при **обновлении бота** (`/update`)

**Решение:** Загружать keensnap.sh автоматически при запуске бэкапа, если файл отсутствует

---

### 🔴 Проблема 2: Нет проверки существования keensnap.sh

**Код:** `src/core/backup.py:98`

```python
args = [keensnap_path]  # keensnap_path = "/opt/root/KeenSnap/keensnap.sh"
```

**Проблема:** Если файл не существует — будет непонятная ошибка

**Решение:** Добавить проверку `os.path.exists(keensnap_path)` перед вызовом

---

### 🔴 Проблема 3: Entware архивируется ПОЛНОСТЬЮ

**Код:** `deploy/backup/keensnap/keensnap.sh:118`

```bash
tar czf "$backup_file" -C /opt .
```

**Проблема:** Архивирует ВСЮ папку /opt — может быть 500MB+ и не поместиться на диск!

**Решение:** 
- Добавить исключения для ненужных файлов (кеш, временные файлы)
- Проверять свободное место перед архивацией

---

### 🔴 Проблема 4: Тихая обработка ошибок

**Код:** `src/core/backup.py:133-134`

```python
except (json.JSONDecodeError, ValueError):
    continue
```

**Проблема:** Ошибки от keensnap.sh игнорируются

**Решение:** Логировать ошибки и показывать их пользователю

---

### 🔴 Проблема 5: DNS не работает после подключения USB

**Симптом:** `[Errno -3] Temporary failure in name resolution`

**Причина:** Entware при монтировании перезаписывает `/etc/resolv.conf`

**Решение:** Прописать DNS вручную:
```bash
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 1.1.1.1" >> /etc/resolv.conf
```

---

## Код для диагностики

### Проверить на роутере:

```bash
# 1. Проверить есть ли keensnap.sh
ls -la /opt/root/KeenSnap/keensnap.sh

# 2. Проверить запущен ли бот и работает ли Entware
ls -la /opt/

# 3. Проверить DNS
cat /etc/resolv.conf
ping 8.8.8.8

# 4. Проверить error.log бота
tail -50 /opt/etc/bot/error.log

# 5. Проверить диски
ndmc -c show media
```

---

## План исправлений

### Приоритет 1: Исправление бэкапа

1. **Добавить проверку существования keensnap.sh** перед вызовом
2. **Автоматически загружать** keensnap.sh если отсутствует
3. **Улучшить обработку ошибок** — показывать stderr от keensnap.sh
4. **Добавить диагностику** — показывать какие пути проверяются

### Приоритет 2: Исправление DNS

1. **Добавить автоисправление DNS** при запуске бота
2. **Добавить проверку DNS** в меню диагностики

---

## Файлы для изменения

1. `src/core/backup.py` — добавить проверку keensnap.sh, улучшить логирование
2. `src/bot3/utils.py` — добавить автозагрузку keensnap.sh перед бэкапом
3. Возможно создание нового модуля `dns_fix.sh`

---

## Константы и пути

```python
# bot_config.py
"keensnap_dir": "/opt/root/KeenSnap/"
"script_bu": "/opt/root/KeenSnap/keensnap.sh"
```

---

## Версии ПО

- Роутер: Keenetic KN-1212
- Прошивка: 4.03.C.6.3-9
- Entware: установлен на USB

---

## Ссылки на код

- Парсер VLESS: `src/core/parsers.py:14`
- Генератор VLESS: `src/core/parsers.py:136`
- Шаблон VLESS: `deploy/config/vless_template.json`
- Обработчик VLESS: `src/bot3/handlers.py:180`
- Бэкап (Python): `src/core/backup.py`
- Бэкап (shell): `deploy/backup/keensnap/keensnap.sh`
