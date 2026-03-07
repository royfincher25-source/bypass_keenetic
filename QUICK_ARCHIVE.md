# 📦 Быстрое создание архива конфигурации

## 🚀 Инструкция (3 команды)

### 1. Подключитесь к роутеру

```bash
ssh root@192.168.1.1
```

### 2. Загрузите скрипт

```bash

# 1. Удалите старый файл
rm -f /opt/root/create_archive.sh
       
# 2. Проверьте что удалён
ls -la /opt/root/create_archive.sh

curl -o /opt/root/create_archive.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/create_archive.sh && chmod 755 /opt/root/create_archive.sh
```

### 3. Запустите

```bash
sh /opt/root/create_archive.sh
```

---

## 📋 Что делает скрипт

✅ Сохраняет **.env** файл (токен бота)  
✅ Сохраняет все файлы бота  
✅ Сохраняет core модуль  
✅ Сохраняет списки обхода  
✅ Сохраняет конфиги сервисов (Tor, Xray, Shadowsocks, Trojan)  
✅ Сохраняет скрипты  
✅ Добавляет информацию о системе  

**На выходе:** Готовый `.tar.gz` архив в `/opt/root/`

---

## 📤 Копирование архива на компьютер

### Windows (PowerShell)

```powershell
scp root@192.168.1.1:/opt/root/backup_*.tar.gz H:\disk_e\dell\bypass_keenetic-main\
```

### Linux/Mac

```bash
scp root@192.168.1.1:/opt/root/backup_*.tar.gz ~/bypass_keenetic/
```

## 🌐 GitHub репозиторий

Проект доступен на GitHub:
**https://github.com/royfincher25-source/bypass_keenetic**

---

## 🎯 Результат

После выполнения вы получите:

```
/opt/root/backup_2026-03-07_15-30-45.tar.gz
Размер: 2.3M
```

**Внутри архива:**
```
backup_2026-03-07_15-30-45/
├── .env              # Токен и настройки
├── bot/              # Файлы бота
├── core/             # Core модуль
├── unblock/          # Списки обхода
├── configs/          # Конфиги сервисов
├── scripts/          # Скрипты
└── system_info.txt   # Информация о системе
```

---

## ⚡ Одна команда (для опытных)

```bash
ssh root@192.168.1.1 "curl -o /opt/root/create_archive.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/create_archive.sh && chmod 755 /opt/root/create_archive.sh && sh /opt/root/create_archive.sh"
```

---

## 🆘 Если что-то не работает

### Ошибка "curl: not found"

```bash
# Установите curl
opkg update
opkg install curl

# Или используйте wget
wget -O /opt/root/create_archive.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/create_archive.sh
```

### Ошибка "Permission denied"

```bash
# Проверьте права
chmod 755 /opt/root/create_archive.sh

# Запустите от root
sh /opt/root/create_archive.sh
```

### Ошибка "No space left on device"

```bash
# Проверьте место
df -h /opt

# Очистите место
rm /opt/root/old_backup_*.tar.gz
```

---

📞 Если понадобится восстановить:

1 # На роутере
     2 cd /opt/root
     3 tar -xzf backup_2026-03-07_21-05.tar.gz
     4 cp -r backup_tmp/bot/* /opt/etc/bot/
     5 cp -r backup_tmp/configs/* /opt/etc/
     6 /opt/etc/init.d/S99telegram_bot restart

**Всё готово! Просто выполните 3 команды выше.** 🎯
