# 🚀 Production файлы для развёртывания

**Версия:** 3.5.51
**Дата:** 13 марта 2026 г.

---

## 📁 Структура папки deploy/

```
deploy/
├── router/              # Скрипты для роутера
│   ├── 100-ipset.sh
│   ├── 100-redirect.sh
│   ├── 100-unblock-vpn-v4.sh
│   ├── 100-unblock-vpn.sh
│   ├── unblock_dnsmasq.sh
│   ├── unblock_ipset.sh
│   └── unblock_update.sh
│
├── backup/              # Скрипты бэкапа
│   └── keensnap/
│       └── keensnap.sh
│
├── config/              # Конфигурационные файлы
│   ├── crontab
│   ├── dnsmasq.conf
│   ├── shadowsocks_template.json
│   ├── tor_template.torrc
│   ├── trojan_template.json
│   └── vless_template.json
│
├── lists/               # Списки обхода
│   ├── unblock-shadowsocks-optimal.txt
│   ├── unblock-shadowsocks-template.txt
│   ├── unblock-youtube.txt
│   ├── unblocktor.txt
│   └── unblockvless.txt
│
└── archive/             # Архив (устаревшие скрипты)
    ├── backup_config.sh
    └── cleanup_backups.sh
```

---

## 📋 Описание компонентов

### 🔧 router/ - Скрипты инициализации и обновления

Эти скрипты **копируются на роутер** и загружаются при старте системы.

| Скрипт | Назначение | Куда копируется |
|--------|------------|-----------------|
| **100-ipset.sh** | Создание ipset множеств | `/opt/etc/ndm/fs.d/` |
| **100-redirect.sh** | Настройка iptables правил | `/opt/etc/ndm/netfilter.d/` |
| **100-unblock-vpn.sh** | Обработка VPN (KeenOS 3) | `/opt/etc/ndm/ifstatechanged.d/` |
| **100-unblock-vpn-v4.sh** | Обработка VPN (KeenOS 4+) | `/opt/etc/ndm/ifstatechanged.d/` |
| **unblock_dnsmasq.sh** | Генерация dnsmasq.conf | `/opt/bin/` |
| **unblock_ipset.sh** | Заполнение ipset IP | `/opt/bin/` |
| **unblock_update.sh** | Принудительное обновление | `/opt/bin/` |

**Установка:**
```bash
# Скопировать скрипты на роутер
scp deploy/router/100-*.sh admin@192.168.1.1:/opt/etc/ndm/
scp deploy/router/unblock_*.sh admin@192.168.1.1:/opt/bin/

# Установить права на выполнение
ssh admin@192.168.1.1 "chmod +x /opt/bin/unblock_*.sh"
```

---

### 💾 backup/ - Скрипты бэкапирования

| Скрипт | Назначение | Использование |
|--------|------------|---------------|
| **keensnap/keensnap.sh** | Бэкап через Telegram бота | Через меню бота `💾 Бэкап` |

**Использование:**
```bash
# Создать бэкап через Telegram бота
# Меню: ⚙️ Сервис → 💾 Бэкап

# Или вручную на роутере:
/opt/root/KeenSnap/keensnap.sh LOG_FILE=/opt/root/KeenSnap/backup.log SELECTED_DRIVE=/tmp/mnt/USB_DISK BACKUP_STARTUP_CONFIG=true BACKUP_ENTWARE=true
```

**Архивные скрипты** (не используются, перемещены в `archive/`):
- `backup_config.sh` — альтернативное бэкапирование
- `cleanup_backups.sh` — альтернативная очистка

---

### ⚙️ config/ - Шаблоны конфигурации

Эти файлы **копируются в соответствующие директории** на роутере.

| Файл | Назначение | Куда копируется |
|------|------------|-----------------|
| **crontab** | Расписание задач | `/opt/etc/crontab` |
| **dnsmasq.conf** | Конфигурация DNS | `/opt/etc/dnsmasq.conf` |
| **shadowsocks_template.json** | Шаблон Shadowsocks | Используется ботом |
| **tor_template.torrc** | Шаблон Tor | Используется ботом |
| **trojan_template.json** | Шаблон Trojan | Используется ботом |
| **vless_template.json** | Шаблон VLESS | Используется ботом |

**Установка:**
```bash
# Скопировать конфигурацию
scp deploy/config/dnsmasq.conf admin@192.168.1.1:/opt/etc/
scp deploy/config/crontab admin@192.168.1.1:/opt/etc/

# Перезапустить службы
ssh admin@192.168.1.1 "/opt/etc/init.d/S56dnsmasq restart"
ssh admin@192.168.1.1 "crontab /opt/etc/crontab"
```

---

### 📄 lists/ - Списки обхода

Пользовательские файлы со списками доменов/IP для обхода блокировок.

| Файл | Описание |
|------|----------|
| **unblocktor.txt** | Список для Tor (используется ботом) |
| **unblockvless.txt** | Список для VLESS (используется ботом) |

**Формат:**
```
# Комментарии начинаются с #
example.com
1.2.3.4
subdomain.example.org
```

**Использование:**
```bash
# Копировать списки на роутер
scp deploy/lists/unblocktor.txt admin@192.168.1.1:/opt/etc/unblock/
scp deploy/lists/unblockvless.txt admin@192.168.1.1:/opt/etc/unblock/

# Или отредактировать напрямую на роутере
ssh admin@192.168.1.1 "vi /opt/etc/unblock/unblocktor.txt"
```

---

## 🔄 Процесс развёртывания

### Шаг 1: Подготовка

```bash
# 1. Проверить наличие всех файлов
ls -la deploy/router/
ls -la deploy/backup/
ls -la deploy/config/
ls -la deploy/lists/
```

### Шаг 2: Копирование на роутер

```bash
# Скрипты инициализации
scp deploy/router/100-ipset.sh admin@192.168.1.1:/opt/etc/ndm/fs.d/
scp deploy/router/100-redirect.sh admin@192.168.1.1:/opt/etc/ndm/netfilter.d/
scp deploy/router/100-unblock-vpn.sh admin@192.168.1.1:/opt/etc/ndm/ifstatechanged.d/
scp deploy/router/100-unblock-vpn-v4.sh admin@192.168.1.1:/opt/etc/ndm/ifstatechanged.d/

# Утилиты
scp deploy/router/unblock_dnsmasq.sh admin@192.168.1.1:/opt/bin/
scp deploy/router/unblock_ipset.sh admin@192.168.1.1:/opt/bin/
scp deploy/router/unblock_update.sh admin@192.168.1.1:/opt/bin/

# Конфигурация
scp deploy/config/dnsmasq.conf admin@192.168.1.1:/opt/etc/
scp deploy/config/crontab admin@192.168.1.1:/opt/etc/

# Бэкап
scp -r deploy/backup/ admin@192.168.1.1:/opt/root/
```

### Шаг 3: Установка прав

```bash
ssh admin@192.168.1.1 << 'EOF'
chmod +x /opt/bin/unblock_*.sh
chmod +x /opt/root/KeenSnap/keensnap.sh
chmod +x /opt/root/backup_config.sh
chmod +x /opt/root/cleanup_backups.sh
EOF
```

### Шаг 4: Перезапуск служб

```bash
ssh admin@192.168.1.1 << 'EOF'
/opt/etc/init.d/S56dnsmasq restart
crontab /opt/etc/crontab
/opt/etc/init.d/S99telegram_bot restart
EOF
```

---

## ✅ Проверка развёртывания

```bash
# 1. Проверить наличие скриптов
ssh admin@192.168.1.1 "ls -la /opt/bin/unblock_*.sh"
ssh admin@192.168.1.1 "ls -la /opt/etc/ndm/*100*"

# 2. Проверить конфигурацию
ssh admin@192.168.1.1 "cat /opt/etc/dnsmasq.conf | head -20"
ssh admin@192.168.1.1 "crontab -l"

# 3. Проверить бота
ssh admin@192.168.1.1 "ps aux | grep python3 | grep main.py"

# 4. Проверить логи
ssh admin@192.168.1.1 "tail -20 /opt/etc/bot/error.log"
```

---

## 📊 Статистика

| Компонент | Файлов | Размер | Назначение |
|-----------|--------|--------|------------|
| **router/** | 7 | ~50 KB | Скрипты инициализации |
| **backup/** | 3 | ~30 KB | Скрипты бэкапа |
| **config/** | 6 | ~10 KB | Шаблоны конфигурации |
| **lists/** | 2 | ~5 KB | Списки обхода |
| **ИТОГО** | **18** | **~95 KB** | **Production файлы** |

---

## ⚠️ Важные замечания

1. **Не редактируйте файлы в deploy/** напрямую на роутере
2. **Вносите изменения в локальные файлы** и копируйте через `scp`
3. **Делайте бэкап** перед обновлением production файлов
4. **Проверяйте права на выполнение** после копирования

---

## 🔗 Ссылки

- [Инструкция по установке](../SETUP.md)
- [Обновление через Telegram бота](../README.md#Обновление-бота)
- [Документация по скриптам](../scripts/README.md)

---

**Поддержка:** Создайте issue в [GitHub репозитории](https://github.com/royfincher25-source/bypass_keenetic/issues)
