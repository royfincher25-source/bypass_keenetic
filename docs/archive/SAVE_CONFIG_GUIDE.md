# 📦 Сохранение конфигурации на Keenetic

**Критически важно:** Перед любыми изменениями сохраняйте текущую конфигурацию!

---

## 🚀 Установка скриптов бэкапа

### 1. Загрузка скриптов

```bash
# Перейдите в директорию для скриптов
cd /opt/root

# Загрузите скрипт бэкапа
curl -o backup_config.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/backup_config.sh

# Загрузите скрипт очистки
curl -o cleanup_backups.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/cleanup_backups.sh

# Установите права доступа
chmod 755 backup_config.sh cleanup_backups.sh
```

### 2. Проверка

```bash
# Проверка скрипта бэкапа
./backup_config.sh

# Проверка скрипта очистки
./cleanup_backups.sh 7
```

---

## 📋 Быстрое использование

### Создать бэкап

```bash
# Бэкап с автоматическим именем
/opt/root/backup_config.sh backup

# Бэкап с именем (рекомендуется!)
/opt/root/backup_config.sh backup before_optimize
```

### Показать список бэкапов

```bash
/opt/root/backup_config.sh list
```

### Восстановить из бэкапа

```bash
/opt/root/backup_config.sh restore before_optimize
```

---

## 📖 Что сохраняется

✅ **Сохраняется:**
- `.env` файл (токен бота, все настройки)
- Все файлы бота (`/opt/etc/bot/`)
- Core модуль (оптимизации)
- Списки обхода (`/opt/etc/unblock/*.txt`)
- Конфиги сервисов (Tor, Xray, Shadowsocks, Trojan)
- Скрипты (`script.sh`, `keensnap.sh`)
- Crontab
- Информация о системе

✅ **Не сохраняется:**
- Логи (`error.log`)
- Временные файлы
- Кэш Python

---

## 🎯 Сценарии использования

### Сценарий 1: Перед оптимизацией

```bash
# 1. Создать бэкап
/opt/root/backup_config.sh backup before_optimize

# 2. Провести оптимизацию
# ... (изменения конфигов, обновление и т.д.)

# 3. Проверить работу
ps | grep python
tail -f /opt/etc/bot/error.log

# 4. Если проблемы - откатиться
/opt/root/backup_config.sh restore before_optimize
```

### Сценарий 2: Перед обновлением

```bash
# 1. Бэкап
/opt/root/backup_config.sh backup before_update_$(date +%Y-%m-%d)

# 2. Обновление
cd /opt/etc/bot
curl -O https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/main.py
# ... другие файлы

# 3. Перезапуск
/opt/etc/init.d/S99telegram_bot restart

# 4. Проверка
ps | grep python

# 5. Если не работает - откат
/opt/root/backup_config.sh restore before_update_2026-03-07
```

### Сценарий 3: Регулярное обслуживание

```bash
# 1. Еженедельный бэкап
/opt/root/backup_config.sh backup weekly_$(date +%Y-%m-%d)

# 2. Очистка старых бэкапов (старше 7 дней)
/opt/root/cleanup_backups.sh 7

# 3. Проверка места
df -h /opt
du -sh /opt/root/bypass_backups/
```

---

## ⚙️ Автоматизация

### В crontab (`/opt/etc/crontab`)

```bash
# Еженедельный бэкап (воскресенье 3:00)
0 3 * * 0 /opt/root/backup_config.sh backup weekly_$(date +\%Y-\%m-\%d)

# Ежедневная очистка (2:30, хранить 7 дней)
30 2 * * * /opt/root/cleanup_backups.sh 7

# Ежемесячная полная проверка (1-е число 4:00)
0 4 1 * * /opt/root/backup_config.sh list > /opt/root/bypass_backups/list_monthly.txt
```

---

## 💾 Управление местом

### Проверка размера

```bash
# Размер всех бэкапов
du -sh /opt/root/bypass_backups/

# Размер каждого бэкапа
ls -lh /opt/root/bypass_backups/*.tar.gz
```

### Очистка вручную

```bash
# Удалить конкретный бэкап
/opt/root/backup_config.sh delete old_backup_name

# Удалить все бэкапы старше 30 дней
find /opt/root/bypass_backups -name "*.tar.gz" -mtime +30 -delete

# Оставить только последние 5
cd /opt/root/bypass_backups
ls -t bypass_backup_*.tar.gz | tail -n +6 | xargs rm
```

### Рекомендуемые лимиты

- **Хранить:** 7-14 дней
- **Минимум бэкапов:** 3 штуки
- **Максимальный размер:** 50 MB

---

## 🔧 Восстановление

### Проблема: Бот не запускается

```bash
# 1. Проверить логи
tail -f /opt/etc/bot/error.log

# 2. Посмотреть доступные бэкапы
/opt/root/backup_config.sh list

# 3. Восстановить
/opt/root/backup_config.sh restore before_optimize

# 4. Перезапустить
/opt/etc/init.d/S99telegram_bot restart
```

### Проблема: Потерян .env файл

```bash
# 1. Найти бэкап
/opt/root/backup_config.sh list

# 2. Распаковать только .env
cd /opt/root/bypass_backups
tar -xzf bypass_backup_*.tar.gz */.env --to-stdout > /opt/etc/bot/.env

# 3. Проверить
cat /opt/etc/bot/.env

# 4. Перезапустить бота
/opt/etc/init.d/S99telegram_bot restart
```

### Проблема: Полная потеря конфигурации

```bash
# 1. Остановить бота
/opt/etc/init.d/S99telegram_bot stop

# 2. Восстановить всё
/opt/root/backup_config.sh restore working_backup

# 3. Запустить
/opt/etc/init.d/S99telegram_bot start
```

---

## 📊 Типичные размеры бэкапов

| Компонент | Размер |
|-----------|--------|
| **.env + bot_config** | < 10 KB |
| **Все файлы бота** | 100-200 KB |
| **Списки обхода** | 10-50 KB |
| **Конфиги сервисов** | 5-10 KB |
| **Итого (сжато):** | **200-500 KB** |

---

## ✅ Чек-лист перед изменениями

- [ ] Создан бэкап с понятным именем
- [ ] Бэкап проверен (`list`)
- [ ] Достаточно места на `/opt`
- [ ] Запомнили имя бэкапа

---

## 📞 Команды для запоминания

```bash
# Бэкап
backup_config.sh backup [имя]

# Список
backup_config.sh list

# Восстановление
backup_config.sh restore [имя]

# Очистка
cleanup_backups.sh [дни]
```

---

## 📍 Расположение

| Файл | Путь |
|------|------|
| **Скрипт бэкапа** | `/opt/root/backup_config.sh` |
| **Скрипт очистки** | `/opt/root/cleanup_backups.sh` |
| **Директория бэкапов** | `/opt/root/bypass_backups/` |
| **Конфиги бота** | `/opt/etc/bot/` |
| **Списки обхода** | `/opt/etc/unblock/` |

---

## ⚠️ Важно!

1. **Всегда создавайте бэкап перед изменениями**
2. **Давайте понятные имена бэкапам** (before_update, before_optimize)
3. **Храните минимум 3 бэкапа**
4. **Регулярно очищайте старые бэкапы**
5. **Проверяйте свободное место**

---

**Скрипты готовы к использованию!**

Для установки выполните:
```bash
curl -o /opt/root/backup_config.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/backup_config.sh
curl -o /opt/root/cleanup_backups.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/cleanup_backups.sh
chmod 755 /opt/root/backup_config.sh /opt/root/cleanup_backups.sh
```

**Последнее обновление:** 7 марта 2026 г.
