# 📦 Бэкапы - Полный список файлов

**Версия:** 3.5.51  
**Дата:** 13 марта 2026 г.

---

## 📋 Что входит в бэкап

### **Группы файлов:**

| Группа | Файлы | Размер (примерно) |
|--------|-------|-------------------|
| **Startup Config** | Конфигурация роутера | ~100 KB |
| **Firmware** | Прошивка роутера | ~20 MB |
| **Entware** | Пакеты Entware | ~50-500 MB |
| **Custom Files** | Файлы бота и сервисов | ~5-10 MB |

---

## 🔍 Детальный список файлов

### **1. Startup Config** (`BACKUP_STARTUP_CONFIG=true`)

**Файл:** `${DEVICE_ID}_${FW_VERSION}_startup-config.txt`

**Что сохраняется:**
- Конфигурация роутера из `startup-config`
- Все настройки Keenetic (интерфейсы, DNS, маршрутизация)
- Настройки бота и разблокировок

**Команда:**
```bash
ndmc -c "copy startup-config usb:/$date/startup-config.txt"
```

---

### **2. Firmware** (`BACKUP_FIRMWARE=true`)

**Файл:** `${DEVICE_ID}_${FW_VERSION}_firmware.bin`

**Что сохраняется:**
- Текущая прошивка роутера
- Версия: `stable_4.03.C.6.3-9` (или ваша)

**Размер:** ~20 MB

**Команда:**
```bash
ndmc -c "copy flash:/firmware usb:/$date/firmware.bin"
```

---

### **3. Entware** (`BACKUP_ENTWARE=true`)

**Файл:** `${ARCH}-installer.tar.gz` (например, `mipsel-installer.tar.gz`)

**Что сохраняется:**
| Путь | Описание | Размер |
|------|----------|--------|
| `/opt/bin/` | Исполняемые файлы | ~20 MB |
| `/opt/etc/` | Конфигурационные файлы | ~5 MB |
| `/opt/lib/` | Библиотеки | ~100 MB |
| `/opt/sbin/` | Системные утилиты | ~10 MB |
| `/opt/share/` | Данные | ~5 MB |

**Исключения (не сохраняются):**
```
/opt/root/KeenSnap/*.tar.gz  # Старые бэкапы
/opt/var/cache/*             # Кеш пакетов
/opt/var/log/*.log           # Логи
/opt/var/log/*.gz            # Архивы логов
/opt/tmp/*                   # Временные файлы
```

**Проверка валидности:**
- ✅ Архив должен содержать `bin/`, `etc/`, `lib/`
- ✅ Размер > 1 KB

---

### **4. Custom Files** (`BACKUP_CUSTOM_FILES=true`)

**Файл:** `${DEVICE_ID}_backup*_custom-files.tar.gz`

**Что сохраняется (из `bot_config.py`):**

```python
CUSTOM_BACKUP_PATHS = " ".join([
    "/opt/etc/bot",              # Вся папка бота
    "/opt/etc/xray/config.json", # Конфигурация VLESS
    "/opt/etc/tor/torrc",        # Конфигурация Tor
    "/opt/root/script.sh",       # Скрипт установки
    "/opt/root/KeenSnap/keensnap.sh",  # Скрипт бэкапа
])
```

#### **Детальный список:**

| Путь | Файлы | Размер |
|------|-------|--------|
| **`/opt/etc/bot/`** | **Вся папка бота** | **~5-10 MB** |
| ├─ `main.py` | Точка входа | ~50 KB |
| ├─ `handlers.py` | Обработчики команд | ~100 KB |
| ├─ `menu.py` | Меню бота | ~10 KB |
| ├─ `utils.py` | Утилиты | ~50 KB |
| ├─ `bot_config.py` | Конфигурация | ~5 KB |
| ├─ `version.md` | Версия бота | ~1 KB |
| ├─ `.env.example` | Шаблон .env | ~3 KB |
| ├─ `S99telegram_bot` | Init скрипт | ~2 KB |
| ├─ `S99unblock` | Init скрипт | ~2 KB |
| └─ `core/` | **Core модули** | **~100 KB** |
| &nbsp;&nbsp;&nbsp;&nbsp;├─ `config.py` | Конфигурация | ~10 KB |
| &nbsp;&nbsp;&nbsp;&nbsp;├─ `env_parser.py` | Парсер .env | ~5 KB |
| &nbsp;&nbsp;&nbsp;&nbsp;├─ `http_client.py` | HTTP клиент | ~5 KB |
| &nbsp;&nbsp;&nbsp;&nbsp;├─ `logging.py` | Логирование | ~5 KB |
| &nbsp;&nbsp;&nbsp;&nbsp;├─ `logging_async.py` | Async логи | ~5 KB |
| &nbsp;&nbsp;&nbsp;&nbsp;├─ `parsers.py` | Парсеры ключей | ~10 KB |
| &nbsp;&nbsp;&nbsp;&nbsp;├─ `services.py` | Сервисы | ~5 KB |
| &nbsp;&nbsp;&nbsp;&nbsp;├─ `validators.py` | Валидаторы | ~5 KB |
| &nbsp;&nbsp;&nbsp;&nbsp;├─ `backup.py` | Бэкапы | ~10 KB |
| &nbsp;&nbsp;&nbsp;&nbsp;├─ `handlers_shared.py` | Обработчики | ~10 KB |
| &nbsp;&nbsp;&nbsp;&nbsp;└─ `__init__.py` | Экспорт | ~2 KB |
| **`/opt/etc/xray/config.json`** | Конфиг VLESS | ~2 KB |
| **`/opt/etc/tor/torrc`** | Конфиг Tor | ~1 KB |
| **`/opt/root/script.sh`** | Скрипт установки | ~20 KB |
| **`/opt/root/KeenSnap/keensnap.sh`** | Скрипт бэкапа | ~10 KB |

**Итого:** ~5-10 MB

---

## 📊 Итоговый размер бэкапа

| Тип бэкапа | Размер |
|------------|--------|
| **Startup Config** | ~100 KB |
| **Firmware** | ~20 MB |
| **Entware** | ~50-500 MB |
| **Custom Files** | ~5-10 MB |
| **Финальный архив** | **~75-530 MB** |

---

## 🗂️ Структура архива

**Имя файла:** `${DEVICE_ID}_backup2026-03-13_15-30.tar.gz`

**Внутри архива:**
```
backup2026-03-13_15-30/
├── KN-1212_stable_4.03.C.6.3-9_startup-config.txt
├── KN-1212_stable_4.03.C.6.3-9_firmware.bin
├── mipsel-installer.tar.gz
├── config.json              # VLESS
├── torrc                    # Tor
├── script.sh                # Установка
└── keensnap.sh              # Бэкап
```

---

## ⚙️ Настройка бэкапа

### **Изменение списка файлов (bot_config.py):**

```python
backup_settings = {
    "LOG_FILE": "/opt/root/KeenSnap/backup.log",
    "MAX_SIZE_MB": 45,  # Максимальный размер бэкапа
    "CUSTOM_BACKUP_PATHS": " ".join([
        "/opt/etc/bot",              # Весь бот
        "/opt/etc/xray/config.json", # VLESS
        "/opt/etc/tor/torrc",        # Tor
        "/opt/root/script.sh",       # Установка
        "/opt/root/KeenSnap/keensnap.sh",  # Бэкап
        # Добавьте свои пути:
        # "/opt/etc/shadowsocks.json",
        # "/opt/etc/trojan/config.json",
        # "/opt/etc/unblock/",
    ])
}
```

---

## 🚀 Создание бэкапа

### **Через Telegram бота:**

1. Откройте меню: `⚙️ Сервис` → `💾 Бэкап`
2. Выберите типы бэкапов:
   - ✅ Конфигурация (startup-config)
   - ✅ Прошивка (firmware)
   - ✅ Entware
   - ✅ Другие файлы (custom files)
3. Выберите диск
4. Дождитесь создания архива

### **Вручную (SSH):**

```bash
# Запустить бэкап всех компонентов
/opt/root/KeenSnap/keensnap.sh \
  LOG_FILE=/opt/root/KeenSnap/backup.log \
  SELECTED_DRIVE=/tmp/mnt/USB_DISK \
  BACKUP_STARTUP_CONFIG=true \
  BACKUP_FIRMWARE=true \
  BACKUP_ENTWARE=true \
  BACKUP_CUSTOM_FILES=true
```

---

## 📥 Восстановление из бэкапа

### **1. Распаковать архив:**

```bash
# На роутере
cd /tmp
tar -xzf /tmp/mnt/USB_DISK/KN-1212_backup*.tar.gz
```

### **2. Восстановить файлы:**

```bash
# Скрипт установки
cp /tmp/backup*/script.sh /opt/root/
chmod 755 /opt/root/script.sh

# Скрипт бэкапа
mkdir -p /opt/root/KeenSnap
cp /tmp/backup*/keensnap.sh /opt/root/KeenSnap/
chmod 755 /opt/root/KeenSnap/keensnap.sh

# Бот
cp -r /tmp/backup*/* /opt/etc/

# Конфигурации
cp /tmp/backup*/config.json /opt/etc/xray/
cp /tmp/backup*/torrc /opt/etc/tor/
```

### **3. Восстановить Entware:**

```bash
# Распаковать Entware
tar -xzf /tmp/backup*/mipsel-installer.tar.gz -C /
```

### **4. Восстановить конфигурацию роутера:**

```bash
# Через веб-интерфейс:
# Управление → Параметры системы → Загрузить startup-config
```

---

## ⚠️ Важные замечания

1. **Не бэкапьте логи:**
   - `error.log` не нужен для восстановления
   - Логи занимают место и быстро устаревают

2. **Проверяйте архив:**
   ```bash
   # Проверка валидности
   tar -tzf backup.tar.gz | grep -E "^(bin/|etc/|lib/)"
   ```

3. **Храните несколько версий:**
   - Минимум 2-3 последних бэкапа
   - На разных дисках (USB + облако)

4. **Регулярность:**
   - Перед обновлением бота
   - После изменения конфигурации
   - Раз в месяц (планово)

---

## 🔧 Диагностика

### **Проверка места на диске:**

```bash
df -h /tmp/mnt/USB_DISK
```

### **Проверка размера бэкапа:**

```bash
du -sh /tmp/mnt/USB_DISK/KN-1212_backup*
```

### **Проверка валидности архива:**

```bash
# Проверка содержимого
tar -tzf backup.tar.gz | head -20

# Проверка критичных директорий
tar -tzf backup.tar.gz | grep -E "^backup.*/(bin|etc|lib)/" | head -5
```

---

## 📞 Поддержка

**Проблемы с бэкапом:**

1. Проверьте логи:
   ```bash
   tail -50 /opt/root/KeenSnap/backup.log
   ```

2. Проверьте место на диске:
   ```bash
   df -h
   ```

3. Создайте Issue: [GitHub Issues](https://github.com/royfincher25-source/bypass_keenetic/issues)

---

**Последнее обновление:** 13 марта 2026 г.  
**Версия инструкции:** 1.1
