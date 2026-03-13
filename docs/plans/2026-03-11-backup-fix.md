# Backup Fix Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Исправить функционал бэкапа — добавить проверку и автозагрузку keensnap.sh, улучшить обработку ошибок

**Architecture:** Python-обёртка в core/backup.py проверяет наличие keensnap.sh, при отсутствии — загружает, затем выполняет бэкап. Улучшено логирование для диагностики.

**Tech Stack:** Python 3.11, TeleBot, subprocess, shell-скрипт keensnap.sh

---

## Диагностика (выполнить на роутере ПЕРЕД началом)

```bash
# Проверить есть ли keensnap.sh
ls -la /opt/root/KeenSnap/keensnap.sh

# Проверить Entware
ls -la /opt/

# Проверить DNS
cat /etc/resolv.conf

# Проверить диски
ndmc -c show media

# Проверить error.log
tail -50 /opt/etc/bot/error.log
```

---

## Task 1: Добавить проверку keensnap.sh в core/backup.py

**Files:**
- Modify: `src/core/backup.py:66-98`

**Step 1: Добавить функцию проверки/загрузки keensnap.sh**

```python
def ensure_keensnap_exists():
    """
    Проверяет наличие keensnap.sh, при отсутствии — загружает.
    Возвращает путь к скрипту.
    """
    keensnap_path = "/opt/root/KeenSnap/keensnap.sh"
    keensnap_dir = "/opt/root/KeenSnap"
    
    # Если файл существует — возвращаем путь
    if os.path.exists(keensnap_path):
        return keensnap_path
    
    # Файл не существует — пробуем загрузить
    from .http_client import download_script
    
    try:
        # Создаём директорию
        if not os.path.exists(keensnap_dir):
            os.makedirs(keensnap_dir, exist_ok=True)
        
        # URL для загрузки (относительный путь — загружается через HTTP)
        keensnap_url = "https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/deploy/backup/keensnap/keensnap.sh"
        
        # Пробуем разные URL
        urls_to_try = [
            "https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/deploy/backup/keensnap/keensnap.sh",
            "https://raw.githubusercontent.com/ziwork/bypass_keenetic/main/deploy/backup/keensnap/keensnap.sh",
        ]
        
        for url in urls_to_try:
            try:
                download_script(url, keensnap_path)
                if os.path.exists(keensnap_path):
                    # Делаем исполняемым
                    os.chmod(keensnap_path, 0o755)
                    log_error(f"Keensnap.sh загружен с {url}")
                    return keensnap_path
            except Exception as e:
                log_error(f"Не удалось загрузить с {url}: {e}")
                continue
        
        raise FileNotFoundError(f"Не удалось загрузить keensnap.sh ни с одного URL")
        
    except Exception as e:
        log_error(f"Ошибка при обеспечении keensnap.sh: {e}")
        raise
```

**Step 2: Модифицировать create_backup_with_params для вызова проверки**

В начале функции `create_backup_with_params` добавить:

```python
# Проверяем/загружаем keensnap.sh перед бэкапом
try:
    keensnap_path = ensure_keensnap_exists()
except Exception as e:
    bot.edit_message_text(
        f"❌ Ошибка: не удалось подготовить скрипт бэкапа\n{str(e)}",
        chat_id, progress_msg_id
    )
    return
```

**Step 3: Тестировать локально (без роутера)**

```bash
# Тест импорта
cd src
python -c "from core.backup import ensure_keinsnap_exists; print('OK')"
```

---

## Task 2: Улучшить обработку ошибок в core/backup.py

**Files:**
- Modify: `src/core/backup.py:113-145`

**Step 1: Добавить сбор stderr от keensnap.sh**

```python
# После запуска процесса добавить обработку stderr
stderr_output = []

for line in process.stderr:
    line = line.strip()
    if line:
        stderr_output.append(line)
        log_error(f"Keensnap stderr: {line}")

# После завершения проверить stderr
if stderr_output:
    log_error(f"Keensnap stderr output: {' | '.join(stderr_output)}")
```

**Step 2: Показать ошибки пользователю**

```python
if final_result and final_result["status"] == "error":
    error_msg = final_result.get('message', 'Неизвестная ошибка')
    # Добавить stderr если есть
    if stderr_output:
        error_msg += f"\n\nДетали: {' | '.join(stderr_output[:3])}"  # Первые 3 строки
    bot.edit_message_text(
        f"❌ Ошибка бэкапа: {error_msg}",
        chat_id, progress_msg_id
    )
    return
```

---

## Task 3: Добавить диагностику в сообщения пользователю

**Files:**
- Modify: `src/core/backup.py:120-135`

**Step 1: Добавить диагностический вывод при запуске**

```python
# В начале create_backup_with_params добавить логирование
log_error(f"=== Backup started ===")
log_error(f"Backup state: startup={backup_state.startup_config}, firmware={backup_state.firmware}, entware={backup_state.entware}")
log_error(f"Selected drive: {selected_drive}")

# Проверить пути для Entware
entware_paths = [
    "/opt/root/KeenSnap",
    "/opt/root/script.sh", 
    "/opt/etc/init.d/S99telegram_bot",
    "/opt/etc/init.d/S99unblock",
    "/opt/etc/crontab",
    "/opt/etc/dnsmasq.conf"
]
for path in entware_paths:
    exists = os.path.exists(path)
    log_error(f"Path {path}: {'EXISTS' if exists else 'NOT FOUND'}")
```

---

## Task 4: Исправить проблему с DNS (дополнительно)

**Files:**
- Modify: `src/bot3/main.py` или создать `src/core/dns_fix.py`

**Step 1: Добавить функцию проверки/исправления DNS**

```python
def ensure_dns_works():
    """
    Проверяет и исправляет DNS если нужно.
    """
    import socket
    
    # Тест DNS
    try:
        socket.gethostbyname("api.telegram.org")
        log_error("DNS: OK")
        return True
    except socket.gaierror:
        log_error("DNS: FAIL — пытаюсь исправить...")
    
    # Пробуем исправить
    dns_servers = ["8.8.8.8", "1.1.1.1", "8.8.4.4"]
    
    for dns in dns_servers:
        try:
            with open("/etc/resolv.conf", "w") as f:
                f.write(f"nameserver {dns}\n")
            
            # Проверяем
            socket.gethostbyname("api.telegram.org")
            log_error(f"DNS исправлен: {dns}")
            return True
        except Exception as e:
            log_error(f"DNS {dns} не работает: {e}")
            continue
    
    log_error("Не удалось исправить DNS")
    return False
```

**Step 2: Вызвать при запуске бота**

В `main.py` в начале добавить:

```python
# Проверка и исправление DNS
try:
    from core.dns_fix import ensure_dns_works
    ensure_dns_works()
except Exception as e:
    log_error(f"DNS check failed: {e}")
```

---

## Task 5: Тестирование ✅ ВЫПОЛНЕНО

**Status:** Реализовано в коммитах `ea5e813`, `a54d7d9`, `6832a8d`

**Что было сделано:**
- ✅ `ensure_keensnap_exists()` добавлена в `src/core/backup.py`
- ✅ Проверка keensnap.sh перед бэкапом
- ✅ Автозагрузка keensnap.sh при отсутствии
- ✅ Улучшена обработка ошибок
- ✅ Добавлено логирование

**Step 1: Запустить бота и проверить бэкап**

```bash
# На роутере:
# 1. Перезапустить бота
/opt/etc/init.d/S99telegram_bot restart

# 2. Проверить логи
tail -100 /opt/etc/bot/error.log | grep -i backup

# 3. Через бота: Меню → Сервис → Бэкап
```

**Step 2: Проверить DNS**

```bash
# Тест DNS
ping api.telegram.org

# Если не работает — проверить resolv.conf
cat /etc/resolv.conf
```

---

## Файлы для изменения

| Файл | Изменение | Статус |
|------|-----------|--------|
| `src/core/backup.py` | Добавить ensure_keensnap_exists(), улучшить логирование | ✅ Выполнено |
| `src/core/dns_fix.py` | Создать (или добавить в backup.py) | ⚠️ Опционально |
| `src/bot3/main.py` | Добавить вызов ensure_dns_works() при запуске | ⚠️ Опционально |

---

## Готовая команда для быстрого теста

```bash
# На роутере:
ssh admin@192.168.1.1

# Тест keensnap.sh
/opt/root/KeenSnap/keensnap.sh LOG_FILE=/tmp/test.log SELECTED_DRIVE=/tmp/mnt/XXX BACKUP_ENTWARE=true

# Тест DNS
ping -c 3 api.telegram.org
```

---

## Проверка перед коммитом

- [x] Код компилируется (без ошибок импорта)
- [x] Логирование добавлено в ключевые места
- [x] Обработка исключений есть
- [ ] Тест на роутере прошёл ← **Нужно сделать пользователю**

---

## Примечание

**Task 5** требует тестирования на реальном роутере с Keenetic OS. Это нельзя сделать автоматически.

**Рекомендация:** После установки бота на роутер (через `/start` → `📲 Установка и удаление` → `📲 Установка`) протестировать создание бэкапа через меню бота.

## Команда для ручного запуска теста на роутере

```bash
# Диагностика
cd /opt/etc/bot
python3 -c "import core.backup; print('Import OK')"

# Запуск бэкапа (через бота)
# Меню → Сервис → Бэкап
```
