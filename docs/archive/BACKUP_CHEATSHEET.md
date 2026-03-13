# ⚡ Шпаргалка по бэкапам

## Быстрые команды

```bash
# Создать бэкап
/opt/root/backup_config.sh backup

# Создать бэкап с именем
/opt/root/backup_config.sh backup before_change

# Показать список бэкапов
/opt/root/backup_config.sh list

# Восстановить из бэкапа
/opt/root/backup_config.sh restore before_change

# Удалить бэкап
/opt/root/backup_config.sh delete before_change
```

---

## Перед изменениями

```bash
# 1. Создать бэкап
/opt/root/backup_config.sh backup $(date +%Y-%m-%d_%H-%M)

# 2. Проверить
/opt/root/backup_config.sh list

# 3. Внести изменения
# ...

# 4. Если что-то не так - восстановить
/opt/root/backup_config.sh restore 2026-03-07_15-30
```

---

## После установки

```bash
# 1. Загрузить скрипт бэкапа
curl -o /opt/root/backup_config.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/backup_config.sh
chmod 755 /opt/root/backup_config.sh

# 2. Создать первый бэкап
/opt/root/backup_config.sh backup initial

# 3. Проверить
/opt/root/backup_config.sh list
```

---

## Автоматизация

### В crontab (`/opt/etc/crontab`)

```bash
# Еженедельный бэкап (воскресенье 3:00)
0 3 * * 0 /opt/root/backup_config.sh backup weekly

# Ежедневный бэкап (2:00)
0 2 * * * /opt/root/backup_config.sh backup daily_$(date +\%Y-\%m-\%d)
```

---

## Проверка

```bash
# Размер бэкапов
du -sh /opt/root/bypass_backups/

# Список файлов
ls -lh /opt/root/bypass_backups/

# Свободное место
df -h /opt
```

---

## Расположение

- **Скрипт:** `/opt/root/backup_config.sh`
- **Бэкапы:** `/opt/root/bypass_backups/`
- **Конфиги:** `/opt/etc/bot/`

---

## Важно!

✅ **Всегда создавайте бэкап перед:**
- Обновлением бота
- Изменением `.env`
- Установкой пакетов

✅ **Храните минимум 3 бэкапа:**
- Последний рабочий
- Перед последними изменениями
- Недельной давности

✅ **Проверяйте бэкапы:**
```bash
/opt/root/backup_config.sh list
```
