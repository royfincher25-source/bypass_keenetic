# Code Review Отчёт: bypass_keenetic

**Дата:** 8 марта 2026 г.  
**Ревизия:** 35839a1  
**Файлы:** bot3/*, core/*

---

## 1. Краткое резюме

Проект представляет собой Telegram-бота для управления обходом блокировок на роутерах Keenetic. Код демонстрирует осознанную оптимизацию для embedded-устройств с ограниченной памятью. Реализовано кэширование, обработка ошибок и базовая модульность. Однако выявлены **критические проблемы безопасности** (отсутствие валидации входных данных, потенциальные command injection), **проблемы надёжности** (недостаточная обработка ошибок в subprocess вызовах) и **архитектурные недочёты** (глобальное состояние, tight coupling).

---

## 2. Критические проблемы (блокирующие)

### 2.1 Command Injection в `handlers.py`

**Файл:** `bot3/handlers.py`  
**Строки:** 74-87

**Проблема:** Пользовательский ввод напрямую передаётся в subprocess без санитизации.

```python
# ⚠️ ПРОБЛЕМА
def handle_add_to_bypass(message):
    filepath = f"{config.paths['unblock_dir']}{state.selected_file}.txt"
    mylist = load_bypass_list(filepath)
    if len(message.text) > 1:
        mylist.update(message.text.split('\n'))  # Нет валидации!
    save_bypass_list(filepath, mylist)
    subprocess.run(config.services["unblock_update"])  # Инъекция!
```

**Риск:** Злоумышленник может ввести `; rm -rf /opt` или другие инъекции.

**Исправление:**
```python
# ✅ РЕШЕНИЕ
def sanitize_input(text: str, max_length: int = 256) -> str:
    """Санитизация пользовательского ввода"""
    if not text or len(text) > max_length:
        raise ValueError("Некорректный ввод")
    # Разрешаем только буквы, цифры, точки, дефисы
    if not re.match(r'^[a-zA-Z0-9.\-_]+$', text):
        raise ValueError("Ввод содержит недопустимые символы")
    return text

def handle_add_to_bypass(message):
    try:
        for site in message.text.split('\n'):
            site = sanitize_input(site.strip())
            if site:
                mylist.add(site)
    except ValueError as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")
        return
```

---

### 2.2 Path Traversal в `menu.py`

**Файл:** `bot3/menu.py`  
**Строки:** 33-38

**Проблема:** Имена файлов формируются из пользовательского ввода без проверки.

```python
# ⚠️ ПРОБЛЕМА
file_buttons = [fln.replace(".txt", "") for fln in os.listdir(dirname)]
```

**Исправление:**
```python
# ✅ РЕШЕНИЕ
def is_safe_filename(filename: str) -> bool:
    """Проверка безопасности имени файла"""
    if '..' in filename or filename.startswith('.'):
        return False
    if not re.match(r'^[a-zA-Z0-9_\-.]+$', filename):
        return False
    return True

file_buttons = [fln.replace(".txt", "") for fln in os.listdir(dirname) if is_safe_filename(fln)]
```

---

### 2.3 Отсутствие таймаутов в subprocess

**Файл:** `bot3/handlers.py`  
**Строки:** 159-162, 203-206, 221-224

**Проблема:** Многие subprocess вызовы не имеют таймаутов.

```python
# ⚠️ ПРОБЛЕМА
subprocess.run(command)  # Нет таймаута!
```

**Исправление:**
```python
# ✅ РЕШЕНИЕ
try:
    subprocess.run(command, timeout=30)  # 30 секунд таймаут
except subprocess.TimeoutExpired:
    bot.send_message(chat_id, "❌ Таймаут операции")
    log_error("Operation timeout")
```

---

### 2.4 Утечка file handle в `utils.py`

**Файл:** `bot3/utils.py`  
**Строки:** 47-62

**Проблема:** Глобальный file handle может привести к утечке ресурсов.

```python
# ⚠️ ПРОБЛЕМА
_log_file_handle = open(log_file, "a")  # Никогда не закрывается
```

**Исправление:**
```python
# ✅ РЕШЕНИЕ
def log_error(message):
    log_file = config.paths["error_log"]
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(f"{timestamp} - {message}\n")
    except IOError:
        pass  # Логирование не должно ломать приложение
```

---

## 3. Важные замечания (рекомендуется исправить)

### 3.1 Отсутствие retry logic для HTTP

**Файл:** `bot3/utils.py`  
**Строки:** 122-137

**Проблема:** Нет повторных попыток при временных ошибках сети.

**Исправление:** Использовать `requests.Session` с `Retry`:

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=2,
    status_forcelist=[429, 500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)
session.mount("https://", adapter)
```

---

### 3.2 Глобальное состояние в `handlers.py`

**Файл:** `bot3/handlers.py`  
**Строки:** 24-27

**Проблема:** `BotState` создаёт глобальное состояние, затрудняя тестирование.

**Рекомендация:** Использовать dependency injection или контекст.

---

### 3.3 Race condition в кэше

**Файл:** `bot3/utils.py`  
**Строки:** 24-48

**Проблема:** Класс `Cache` не потокобезопасен.

**Исправление:**
```python
import threading

class Cache:
    _lock = threading.Lock()
    
    @classmethod
    def set(cls, key, value, ttl=300):
        with cls._lock:
            cls._cache[key] = value
            cls._timestamps[key] = time.time() + ttl
```

---

### 3.4 Недостаточная валидация в парсерах

**Файл:** `bot3/utils.py`  
**Строки:** 239-267, 381-410, 441-468

**Проблема:** Парсеры не проверяют все поля конфигурации.

**Исправление:**
```python
VALID_SECURITY = {'none', 'tls', 'reality'}
VALID_ENCRYPTION = {'none', 'aes-128-gcm', 'chacha20-poly1305'}

def parse_vless_key(key):
    security = params.get('security', ['none'])[0]
    if security not in VALID_SECURITY:
        raise ValueError(f"Недопустимый security: {security}")
```

---

### 3.5 Отсутствие лимита размера файлов

**Файл:** `bot3/utils.py`  
**Строки:** 122-140

**Проблема:** Нет ограничения на размер файла при загрузке.

**Исправление:**
```python
MAX_SCRIPT_SIZE = 10 * 1024 * 1024  # 10MB

def download_script():
    total_size = 0
    for chunk in response.iter_content(chunk_size=8192):
        total_size += len(chunk)
        if total_size > MAX_SCRIPT_SIZE:
            raise ValueError("Превышен размер")
```

---

## 4. Минорные замечания

### 4.1 Магические числа

**Файл:** `bot3/utils.py`  
**Строка:** 75

```python
max_size = 524288  # ⚠️ Вынести в константу
```

**Исправление:**
```python
MAX_LOG_SIZE = 512 * 1024  # 512KB
```

---

### 4.2 Отсутствие type hints

Большинство функций не имеют аннотаций типов.

**Рекомендация:** Добавить type hints ко всем функциям.

---

### 4.3 Дублирование кода

**Файл:** `bot3/handlers.py`

Функции `handle_install_callback`, `handle_remove_callback`, `handle_update` имеют идентичную структуру.

**Рекомендация:** Создать общую функцию `run_script_with_progress()`.

---

## 5. Положительные моменты

1. ✅ **Кэширование:** Эффективный кэш с TTL
2. ✅ **Оптимизация памяти:** `stream=True`, chunked reading
3. ✅ **Обработка ошибок:** Базовый retry loop в main.py
4. ✅ **Singleton pattern:** Правильная реализация в core/config.py
5. ✅ **Lazy loading:** Отложенная загрузка usernames
6. ✅ **Модульность:** Разделение на handlers, utils, menu, config

---

## 6. Рекомендации по улучшению

### Приоритет 1 (Критично)

- [ ] Добавить санитизацию всего пользовательского ввода
- [ ] Добавить таймауты ко всем subprocess вызовам
- [ ] Исправить утечку file handle в `log_error()`
- [ ] Добавить проверку прав доступа при старте

### Приоритет 2 (Важно)

- [ ] Добавить retry logic для HTTP запросов
- [ ] Сделать кэш потокобезопасным
- [ ] Добавить валидацию всех полей в парсерах ключей
- [ ] Ограничить максимальный размер загружаемых файлов

### Приоритет 3 (Желательно)

- [ ] Добавить type hints ко всем функциям
- [ ] Покрыть тестами критические функции
- [ ] Вынести магические числа в константы
- [ ] Устранить дублирование кода в обработчиках
- [ ] Добавить структурированное логирование

---

## Итоговая оценка

| Критерий | Оценка | Статус |
|----------|--------|--------|
| Безопасность | 3/10 | ⚠️ Критично |
| Надёжность | 5/10 | ⚠️ Требует исправлений |
| Производительность | 8/10 | ✅ Хорошо |
| Качество кода | 5/10 | ⚠️ Требует улучшений |
| Тестируемость | 4/10 | ⚠️ Требует улучшений |

**Общая оценка:** 5/10 — Требуются критические исправления перед production использованием.

---

## Приложения

### A. Список файлов для исправления

1. `bot3/handlers.py` — Command Injection, таймауты
2. `bot3/menu.py` — Path Traversal
3. `bot3/utils.py` — Утечка file handle, кэш, валидация
4. `bot3/main.py` — Проверка прав доступа

### B. Рекомендуемые тесты

```python
# tests/test_security.py
def test_sanitize_input():
    assert sanitize_input("example.com") == "example.com"
    with pytest.raises(ValueError):
        sanitize_input("; rm -rf /")
    with pytest.raises(ValueError):
        sanitize_input("../etc/passwd")

# tests/test_parsers.py
def test_parse_vless_key_invalid_security():
    with pytest.raises(ValueError):
        parse_vless_key("vless://...security=invalid...")
```

### C. Чек-лист для PR

- [ ] Исправлены все критические уязвимости
- [ ] Добавлены таймауты к subprocess
- [ ] Добавлена санитизация ввода
- [ ] Исправлена утечка file handle
- [ ] Добавлены type hints
- [ ] Написаны тесты на критические функции
- [ ] Пройден линтинг (flake8, pylint)

---

**Ревьювер:** AI Assistant  
**Дата:** 8 марта 2026 г.  
**Статус:** ⚠️ Требуются критические исправления
