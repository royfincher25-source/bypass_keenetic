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
curl -o main.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/main.py
curl -o handlers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/handlers.py
curl -o menu.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/menu.py
curl -o utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/utils.py
curl -o bot_config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/bot_config.py

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

### Шаг 4: Запуск бота

```bash
# Загрузите скрипт установки
curl -o /opt/root/script.sh https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/script.sh
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
