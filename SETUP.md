# Руководство по установке и настройке для разработчиков

Этот документ описывает процесс настройки проекта для разработки и развёртывания.

## 📋 Оглавление

- [Быстрый старт](#быстрый-старт)
- [Настройка окружения](#настройка-окружения)
- [Конфигурация](#конфигурация)
- [Установка на роутер](#установка-на-роутер)
- [Разработка](#разработка)
- [Тестирование](#тестирование)
- [Развёртывание](#развёртывание)

---

## 🚀 Быстрый старт

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/royfincher25-source/bypass_keenetic.git
cd bypass_keenetic

# 2. Создайте виртуальное окружение
make setup-venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# 3. Установите зависимости
make install-dev

# 4. Настройте конфигурацию
cp .env.example .env
# Отредактируйте .env и заполните TELEGRAM_BOT_TOKEN и TELEGRAM_USERNAMES

# 5. Проверьте установку
make validate
```

---

## ⚙️ Настройка окружения

### Требования

- Python 3.9+
- pip 21.0+
- GNU Make (опционально, для использования Makefile)

### Создание виртуального окружения

**С использованием Make:**
```bash
make setup-venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

**Вручную:**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Установка зависимостей

**Основные зависимости:**
```bash
make install
# или
pip install -r requirements.txt
```

**Зависимости для разработки:**
```bash
make install-dev
# или
pip install -r requirements-dev.txt
```

**Зависимости для тестирования:**
```bash
make install-test
# или
pip install -r requirements-test.txt
```

---

## 🔐 Конфигурация

### Настройка .env файла

1. Скопируйте шаблон:
   ```bash
   cp .env.example .env
   ```

2. Откройте `.env` и заполните обязательные поля:

   ```ini
   # Telegram Bot (ОБЯЗАТЕЛЬНО)
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   TELEGRAM_USERNAMES=your_username

   # Router Settings
   ROUTER_IP=192.168.1.1

   # Ports (можно оставить по умолчанию)
   LOCALPORT_SH=1082
   DNSPORT_TOR=9053
   LOCALPORT_TOR=9141
   LOCALPORT_VLESS=10810
   LOCALPORT_TROJAN=10829
   DNSOVER_TLS_PORT=40500
   DNSOVER_HTTPS_PORT=40508

   # Bot Settings
   MAX_RESTARTS=5
   RESTART_DELAY=60

   # Backup Settings
   BACKUP_MAX_SIZE_MB=45
   ```

3. Проверьте конфигурацию:
   ```bash
   make validate
   ```

### Получение токена бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен в `.env`

### Настройка имён пользователей

Укажите ваш логин Telegram без `@` в поле `TELEGRAM_USERNAMES`:

```ini
TELEGRAM_USERNAMES=your_username
```

Для нескольких пользователей:
```ini
TELEGRAM_USERNAMES=user1,user2,user3
```

---

## 📦 Установка на роутер

### Предварительные требования

1. USB-накопитель (рекомендуется HDD, а не флешка)
2. Подготовленный USB по [инструкции Keenetic](https://help.keenetic.com/hc/ru/articles/360000184259)
3. Установленный Entware по [инструкции](https://help.keenetic.com/hc/ru/articles/360021214160)

### Шаг 1: Установка компонентов

Подключитесь к роутеру по SSH и выполните:

```bash
opkg update
opkg install curl python3 python3-pip
pip3 install --upgrade pip
pip3 install pyTelegramBotAPI==4.27.0
```

### Шаг 2: Загрузка файлов бота

```bash
mkdir -p /opt/etc/bot
cd /opt/etc/bot

# Загрузка файлов (замените VERSION на нужную версию)
curl -o main.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/main.py
curl -o handlers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/handlers.py
curl -o menu.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/menu.py
curl -o utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/utils.py
curl -o bot_config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/bot_config.py

# Установка прав
chmod 755 /opt/etc/bot
chmod 644 /opt/etc/bot/*.py
```

### Шаг 3: Настройка конфигурации

```bash
# Создайте .env файл
nano /opt/etc/bot/.env
```

Заполните `.env` (см. раздел [Конфигурация](#конфигурация)).

---

### ⚠️ Важно: Проверка bot_config.py

**После загрузки bot_config.py обязательно проверьте правильность URL!**

```bash
# Открыть bot_config.py
nano /opt/etc/bot/bot_config.py
```

**Найдите строки (примерно строки 15-20):**

```python
# Базовый URL для загрузки файлов
base_url = "https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main"
bot_url = base_url + "/src/bot3"
```

**✅ ПРАВИЛЬНО:**

```python
base_url = "https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main"
bot_url = base_url + "/src/bot3"
```

**❌ НЕПРАВИЛЬНО (так быть не должно):**

```python
# Ошибка 1: Используется github.com вместо raw.githubusercontent.com
base_url = "https://github.com/royfincher25-source/bypass_keenetic/blob/main"

# Ошибка 2: URL другого форка
base_url = "https://raw.githubusercontent.com/Ziwork/bypass_keenetic/main"

# Ошибка 3: Неправильный путь
bot_url = base_url + "/bot3"  # Должно быть /src/bot3
```

**Если нашли ошибку — исправьте:**

1. Замените неправильный URL на правильный
2. Сохраните: `Ctrl+O` → `Enter` → `Ctrl+X`
3. Перезапустите бота:

```bash
# Очистить кэш
rm -rf /opt/etc/bot/__pycache__
rm -rf /opt/etc/bot/core/__pycache__

# Перезапустить
/opt/etc/init.d/S99telegram_bot restart
```

**Проверка:**

```bash
# Проверить base_url
grep base_url /opt/etc/bot/bot_config.py

# Проверить version.md
curl -L https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/version.md
# Должно вернуть: 3.5.51
```

---

### ⚠️ Важно: Проверка пути к сервисному скрипту

**Если при перезапуске бота возникает ошибка:**

```
FileNotFoundError: [Errno 2] No such file or directory: '/opt/etc/bot/S99telegram_bot'
```

**Это означает, что в config.py отсутствует секция `services`!**

**✅ В актуальной версии (3.5.51) эта проблема уже исправлена!**

**Если у вас старая версия — обновите бота или исправьте вручную:**

**Проверка и исправление:**

```bash
# 1. Проверить текущий путь
grep service_script /opt/etc/bot/core/config.py

# Если видите:
# 'service_script': '/opt/etc/bot/S99telegram_bot'  ❌ НЕПРАВИЛЬНО!
# или секция services отсутствует
```

**Исправить (выберите один из вариантов):**

**Вариант A: Обновить бота (рекомендуется)**

```bash
# Использовать меню бота в Telegram:
# ⚙️ Сервис → 🆕 Обновления → 🔄 Обновить
```

**Вариант B: Добавить секцию вручную (nano):**

```bash
nano /opt/etc/bot/core/config.py
```

**Найти (примерно строка 60-70):**

```python
# Backup
self.backup_max_size_mb = get_env_int('BACKUP_MAX_SIZE_MB', 45)

Config._initialized = True
```

**Добавить ПОСЛЕ backup_max_size_mb:**

```python
# Services
self.services = {
    'service_script': '/opt/etc/init.d/S99telegram_bot',
}
```

**Сохранить:** `Ctrl+O` → `Enter` → `Ctrl+X`

**Проверка:**

```bash
# Проверить путь
grep service_script /opt/etc/bot/core/config.py

# Должно быть:
# 'service_script': '/opt/etc/init.d/S99telegram_bot'

# Проверить существование скрипта
ls -la /opt/etc/init.d/S99telegram_bot

# Перезапустить бота
rm -rf /opt/etc/bot/__pycache__ /opt/etc/bot/core/__pycache__
/opt/etc/init.d/S99telegram_bot restart
tail -20 /opt/etc/bot/error.log
```

---

### Шаг 4: Запуск бота

```bash
# Загрузите скрипт установки
curl -o /opt/root/script.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/src/bot3/script.sh
chmod 755 /opt/root/script.sh

# Запустите установку
/opt/root/script.sh -install
```

### Шаг 5: Проверка статуса

```bash
/opt/etc/init.d/S99telegram_bot status
```

---

## 💻 Разработка

### Структура проекта

```
bypass_keenetic/
├── bot3/                 # Полная версия бота
│   ├── main.py          # Точка входа
│   ├── handlers.py      # Обработчики сообщений
│   ├── menu.py          # Меню и клавиатуры
│   ├── utils.py         # Утилиты и функции
│   └── bot_config.py    # Конфигурация
├── botlight/            # Облегчённая версия
│   └── ...
├── .env.example         # Шаблон конфигурации
├── requirements.txt     # Зависимости
└── Makefile            # Автоматизация
```

### Команды разработки

**Проверка кода:**
```bash
make lint          # Запустить все линтеры
make format        # Форматировать код
make validate      # Валидировать конфигурацию
```

**Тестирование:**
```bash
make test          # Запустить тесты
make test-cov      # Тесты с покрытием
```

**Очистка:**
```bash
make clean         # Удалить временные файлы
```

### Использование pre-commit

```bash
# Установка pre-commit хуков
make pre-commit-install

# Запуск вручную
make pre-commit-run
```

---

## 🧪 Тестирование

### Запуск тестов

```bash
# Простой запуск
make test

# С покрытием
make test-cov

# Прямой вызов pytest
pytest tests/ -v
pytest tests/ -v --cov=bot3 --cov=botlight
```

### Написание тестов

Создайте файл `tests/test_example.py`:

```python
import pytest
from bot3.utils import parse_vless_key

def test_parse_vless_key():
    key = "vless://uuid@192.168.1.1:443?security=reality&pbk=..."
    result = parse_vless_key(key)
    assert result['address'] == '192.168.1.1'
    assert result['port'] == 443
```

---

## 🚀 Развёртывание

### Обновление бота

**Через Telegram бота:**
1. Откройте меню бота
2. Перейдите в `⚙️ Сервис` → `🆕 Обновления`
3. Нажмите `🆕 Обновить`

**Вручную через SSH:**
```bash
/opt/root/script.sh -update
```

### Откат к предыдущей версии

```bash
# Остановите бота
/opt/etc/init.d/S99telegram_bot stop

# Восстановите файлы из бэкапа
# (путь зависит от вашей конфигурации бэкапа)

# Запустите бота
/opt/etc/init.d/S99telegram_bot start
```

### Мониторинг

**Проверка статуса:**
```bash
/opt/etc/init.d/S99telegram_bot status
```

**Просмотр логов:**
```bash
tail -f /opt/etc/bot/error.log
```

**Проверка процесса:**
```bash
pgrep -f "python3 /opt/etc/bot/main.py"
```

---

## ❓ Решение проблем

### Бот не запускается

1. Проверьте токен в `.env`:
   ```bash
   cat /opt/etc/bot/.env | grep TELEGRAM_BOT_TOKEN
   ```

2. Проверьте логи:
   ```bash
   cat /opt/etc/bot/error.log
   ```

3. Проверьте права доступа:
   ```bash
   ls -la /opt/etc/bot/
   ```

### Ошибка таймаута

- Проверьте подключение к интернету
- Увеличьте таймауты в `.env` (если применимо)
- Проверьте доступность GitHub с роутера

### Проблемы с зависимостями

```bash
# Переустановите зависимости
pip3 uninstall -y pyTelegramBotAPI
pip3 install pyTelegramBotAPI==4.27.0
```

---

## 📞 Поддержка

- **Issues:** [GitHub Issues](https://github.com/royfincher25-source/bypass_keenetic/issues)
- **Discussions:** [GitHub Discussions](https://github.com/royfincher25-source/bypass_keenetic/discussions)
- **Wiki:** [GitHub Wiki](https://github.com/royfincher25-source/bypass_keenetic/wiki)

---

## 📝 Чек-лист перед развёртыванием

- [ ] Скопирован `.env.example` в `.env`
- [ ] Заполнен `TELEGRAM_BOT_TOKEN`
- [ ] Заполнен `TELEGRAM_USERNAMES`
- [ ] Проверено командой `make validate`
- [ ] Установлены зависимости (`make install`)
- [ ] Пройдены тесты (`make test`)
- [ ] Проверены линтеры (`make lint`)

---

**Последнее обновление:** 7 марта 2026 г.
