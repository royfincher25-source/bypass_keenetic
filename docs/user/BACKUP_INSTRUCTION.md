# 📦 Сохранение и восстановление конфигурации

**Важно:** Перед любыми изменениями сохраняйте текущую конфигурацию!

---

## 🚀 Быстрый старт

### Сохранение конфигурации (на роутере)

```bash
# 1. Загрузите скрипт бэкапа
curl -o /opt/root/backup_config.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/backup_config.sh
chmod 755 /opt/root/backup_config.sh

# 2. Создайте бэкап
/opt/root/backup_config.sh backup

# Или с именем
/opt/root/backup_config.sh backup before_optimize
```

**Бэкап будет сохранён в:** `/opt/root/bypass_backups/`

---

## 📋 Что сохраняется в бэкап

✅ **Конфигурационные файлы:**
- `.env` (токен бота, настройки)
- `bot_config.py`
- Все файлы из `/opt/etc/bot/`
- Core модуль (`/opt/etc/bot/core/`)

✅ **Списки обхода:**
- Все `.txt` файлы из `/opt/etc/unblock/`

✅ **Конфиги сервисов:**
- Tor (`torrc`)
- Shadowsocks (`shadowsocks.json`)
- Xray/VLESS (`xray/config.json`)
- Trojan (`trojan/config.json`)

✅ **Скрипты:**
- `script.sh`
- `keensnap.sh`
- `crontab`

✅ **Информация о системе:**
- Версия Keenetic
- Установленные пакеты
- Свободное место

---

## 📖 Использование

### 1. Создание бэкапа

```bash
# Бэкап с автоматическим именем (дата-время)
/opt/root/backup_config.sh backup

# Бэкап с именем
/opt/root/backup_config.sh backup before_update

# Бэкап перед оптимизацией
/opt/root/backup_config.sh backup before_optimize
```

### 2. Просмотр списка бэкапов

```bash
/opt/root/backup_config.sh list
```

**Пример вывода:**
```
[INFO] Доступные бэкапы:

  1) 2026-03-07_14-30-15             2.3M (Мар 07 14:30)
  2) before_optimize                 2.1M (Мар 07 15:00)

[INFO] Всего бэкапов: 2
```

### 3. Восстановление из бэкапа

```bash
# Восстановление из бэкапа по имени
/opt/root/backup_config.sh restore before_optimize
```

**Важно:**
- Текущая конфигурация будет перезаписана
- Бот будет перезапущен (по желанию)

### 4. Удаление бэкапа

```bash
# Удаление старого бэкапа
/opt/root/backup_config.sh delete 2026-03-07_14-30-15
```

---

## 🔄 Автоматическое сохранение

### Еженедельный бэкап

Добавьте в crontab (`/opt/etc/crontab`):

```bash
# Еженедельный бэкап каждое воскресенье в 3:00
0 3 * * 0 /opt/root/backup_config.sh backup weekly_$(date +\%Y-\%m-\%d)

# Ежедневный бэкап (хранить последние 7 дней)
0 2 * * * /opt/root/backup_config.sh backup daily_$(date +\%Y-\%m-\%d)
```

### Бэкап перед обновлением

Создайте скрипт `/opt/root/update_and_backup.sh`:

```bash
#!/bin/sh
# Автоматическое обновление с бэкапом

# 1. Бэкап перед обновлением
/opt/root/backup_config.sh backup pre_update_$(date +%Y-%m-%d)

# 2. Обновление
cd /opt/etc/bot
curl -o main.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/main.py
curl -o utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/utils.py

# 3. Перезапуск
/opt/etc/init.d/S99telegram_bot restart

echo "✅ Обновление завершено"
```

---

## 💾 Управление местом

### Проверка размера бэкапов

```bash
# Размер всех бэкапов
du -sh /opt/root/bypass_backups/

# Размер каждого бэкапа
ls -lh /opt/root/bypass_backups/*.tar.gz
```

### Очистка старых бэкапов

```bash
# Удалить бэкапы старше 30 дней
find /opt/root/bypass_backups -name "*.tar.gz" -mtime +30 -delete

# Оставить только последние 5 бэкапов
cd /opt/root/bypass_backups
ls -t bypass_backup_*.tar.gz | tail -n +6 | xargs rm
```

### Сжатие бэкапов

Скрипт автоматически использует gzip сжатие.
Типичный размер бэкапа: **2-5 MB**

---

## 🛡️ Безопасность

### Защита бэкапов

```bash
# Установить права доступа (только root)
chmod 700 /opt/root/bypass_backups
chmod 600 /opt/root/bypass_backups/*.tar.gz
```

### Шифрование бэкапов (опционально)

```bash
# Установка GPG
opkg install gnupg

# Создание ключа
gpg --gen-key

# Шифрование бэкапа
gpg -c /opt/root/bypass_backups/bypass_backup_*.tar.gz

# Расшифровка
gpg /opt/root/bypass_backups/bypass_backup_*.tar.gz.gpg
```

---

## 📍 Расположение файлов

| Файл | Путь |
|------|------|
| **Скрипт бэкапа** | `/opt/root/backup_config.sh` |
| **Директория бэкапов** | `/opt/root/bypass_backups/` |
| **Конфиги бота** | `/opt/etc/bot/` |
| **Списки обхода** | `/opt/etc/unblock/` |
| **Конфиги сервисов** | `/opt/etc/*.json`, `/opt/etc/tor/torrc` |

---

## ⚠️ Важные замечания

### 1. Перед обновлением

**Всегда создавайте бэкап перед:**
- Обновлением бота
- Изменением `.env` файла
- Установкой новых пакетов
- Изменением конфигов

### 2. После создания бэкапа

**Проверьте:**
```bash
# 1. Список бэкапов
/opt/root/backup_config.sh list

# 2. Размер бэкапа
ls -lh /opt/root/bypass_backups/

# 3. Свободное место
df -h /opt
```

### 3. Регулярность бэкапов

**Рекомендуется:**
- **Еженедельно** - плановый бэкап
- **Перед изменениями** - обязательный бэкап
- **После настройки** - бэкап рабочей конфигурации

---

## 🔧 Восстановление после сбоя

### Сценарий 1: Бот не запускается

```bash
# 1. Посмотреть логи
tail -f /opt/etc/bot/error.log

# 2. Если проблема в конфиге - восстановить из бэкапа
/opt/root/backup_config.sh restore before_update

# 3. Перезапустить бота
/opt/etc/init.d/S99telegram_bot restart
```

### Сценарий 2: Потеря .env файла

```bash
# 1. Найти последний бэкап
/opt/root/backup_config.sh list

# 2. Восстановить только .env
cd /opt/root/bypass_backups
tar -xzf bypass_backup_before_optimize.tar.gz */.env
cp .env /opt/etc/bot/.env

# 3. Перезапустить бота
/opt/etc/init.d/S99telegram_bot restart
```

### Сценарий 3: Полный откат

```bash
# 1. Остановить бота
/opt/etc/init.d/S99telegram_bot stop

# 2. Восстановить полную конфигурацию
/opt/root/backup_config.sh restore before_optimize

# 3. Запустить бота
/opt/etc/init.d/S99telegram_bot start
```

---

## 📊 Примеры использования

### Пример 1: Бэкап перед оптимизацией

```bash
# 1. Создать бэкап
/opt/root/backup_config.sh backup before_optimize

# 2. Провести оптимизацию
# ... (изменение конфигов, обновление и т.д.)

# 3. Проверить работу
ps | grep python

# 4. Если что-то не так - откатиться
/opt/root/backup_config.sh restore before_optimize
```

### Пример 2: Перенос на другой роутер

```bash
# 1. Создать бэкап на старом роутере
/opt/root/backup_config.sh backup for_migration

# 2. Скопировать архив на новый роутер
scp /opt/root/bypass_backups/bypass_backup_for_migration.tar.gz root@new-router:/opt/root/

# 3. Восстановить на новом роутере
/opt/root/backup_config.sh restore for_migration
```

### Пример 3: Тестирование новой версии

```bash
# 1. Бэкап рабочей версии
/opt/root/backup_config.sh backup stable

# 2. Обновить до новой версии
# ... (установка новых файлов)

# 3. Тестировать

# 4. Если не работает - откат
/opt/root/backup_config.sh restore stable
```

---

## 📞 Решение проблем

### Проблема: "Бэкап не найден"

**Решение:**
```bash
# Проверить наличие бэкапов
ls -la /opt/root/bypass_backups/

# Проверить имя
/opt/root/backup_config.sh list
```

### Проблема: "Недостаточно места"

**Решение:**
```bash
# Проверить место
df -h /opt

# Удалить старые бэкапы
/opt/root/backup_config.sh delete old_backup_name

# Или очистить все старые
find /opt/root/bypass_backups -name "*.tar.gz" -mtime +30 -delete
```

### Проблема: "Ошибка при восстановлении"

**Решение:**
```bash
# Проверить целостность архива
tar -tzf /opt/root/bypass_backups/bypass_backup_*.tar.gz

# Если архив повреждён - использовать другой бэкап
/opt/root/backup_config.sh list
```

---

**Последнее обновление:** 7 марта 2026 г.  
**Версия скрипта:** 1.0
