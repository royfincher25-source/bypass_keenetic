# Bot Memory Optimization Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Снизить потребление памяти ботом bot3 с 30.2 MB до ~22 MB через быстрые оптимизации (Фазы 1-2).

**Architecture:** Оптимизация кэширования, lazy инициализация, уменьшение memory footprint через __slots__ и LRU eviction.

**Tech Stack:** Python 3, telebot, requests, urllib3.

---

## Фаза 1: Быстрые победы (30 минут)

### Task 1: Ограничить размер Cache (LRU eviction)

**Files:**
- Modify: `bot3/utils.py:41-80` (класс Cache)

**Step 1: Добавить MAX_SIZE и LRU eviction**

```python
class Cache:
    """Простой кэш с TTL и LRU eviction для экономии памяти"""

    _cache = {}
    _timestamps = {}
    MAX_SIZE = 100  # Ограничение размера кэша

    @classmethod
    def get(cls, key, default=None):
        """Получение из кэша с LRU обновлением"""
        if key in cls._cache:
            # Поднимаем элемент вверх (LRU)
            value = cls._cache.pop(key)
            cls._cache[key] = value
            return value
        return default

    @classmethod
    def set(cls, key, value, ttl=300):
        """Установка в кэш с TTL и LRU eviction"""
        # LRU eviction при превышении размера
        if len(cls._cache) >= cls.MAX_SIZE and key not in cls._cache:
            # Удаляем oldest entry (первый в словаре)
            oldest_key = next(iter(cls._cache))
            cls._cache.pop(oldest_key, None)
            cls._timestamps.pop(oldest_key, None)
        
        cls._cache[key] = value
        cls._timestamps[key] = time.time() + ttl

    @classmethod
    def is_valid(cls, key):
        """Проверка валидности кэша"""
        if key not in cls._timestamps:
            return False
        return time.time() < cls._timestamps[key]

    @classmethod
    def cleanup(cls):
        """Очистка просроченного кэша + LRU"""
        now = time.time()
        expired = [k for k, t in cls._timestamps.items() if now >= t]
        for key in expired:
            cls._cache.pop(key, None)
            cls._timestamps.pop(key, None)
        
        # Дополнительно: оставляем только MAX_SIZE последних
        while len(cls._cache) > cls.MAX_SIZE:
            oldest_key = next(iter(cls._cache))
            cls._cache.pop(oldest_key, None)
            cls._timestamps.pop(oldest_key, None)

    @classmethod
    def clear(cls):
        """Полная очистка кэша"""
        cls._cache.clear()
        cls._timestamps.clear()
```

**Step 2: Run syntax check**

```bash
python3 -m py_compile bot3/utils.py
```
Expected: PASS (no output)

**Step 3: Commit**

```bash
git add bot3/utils.py
git commit -m "perf: добавить LRU eviction в Cache (MAX_SIZE=100)"
```

---

### Task 2: Удалить неиспользуемые глобальные переменные

**Files:**
- Modify: `bot3/utils.py:155-165`

**Step 1: Найти и удалить дубликаты кэшей**

Прочитать строки 155-165, найти:
```python
# ❌ УДАЛИТЬ:
_script_cache = {}
_bypass_cache = {}
_key_cache = {}
```

**Step 2: Оставить только _http_session**

```python
# Connection pooling для HTTP запросов (экономия памяти и времени)
_http_session = None
```

**Step 3: Проверить использование _key_cache**

```bash
grep -n "_key_cache" bot3/utils.py
```
Если есть использования — заменить на `Cache`.

**Step 4: Run syntax check**

```bash
python3 -m py_compile bot3/utils.py
```
Expected: PASS

**Step 5: Commit**

```bash
git add bot3/utils.py
git commit -m "perf: удалить неиспользуемые глобальные кэши"
```

---

### Task 3: Уменьшить HTTP connection pool

**Files:**
- Modify: `bot3/utils.py:166-187` (функция get_http_session)

**Step 1: Уменьшить pool_maxsize с 5 до 2**

```python
def get_http_session():
    """Получение HTTP сессии с connection pooling"""
    global _http_session
    if _http_session is None:
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        _http_session = requests.Session()

        # Настройка retry logic
        retry = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=1,
            pool_maxsize=2  # Было 5, уменьшено для embedded
        )
        _http_session.mount("http://", adapter)
        _http_session.mount("https://", adapter)

    return _http_session
```

**Step 2: Run syntax check**

```bash
python3 -m py_compile bot3/utils.py
```
Expected: PASS

**Step 3: Commit**

```bash
git add bot3/utils.py
git commit -m "perf: уменьшить HTTP pool_maxsize с 5 до 2"
```

---

### Task 4: Добавить функцию cleanup_memory

**Files:**
- Modify: `bot3/utils.py` (добавить в конец модуля)
- Modify: `bot3/main.py` (добавить вызов в главный цикл)

**Step 1: Добавить функцию cleanup_memory в utils.py**

```python
def cleanup_memory():
    """Периодическая очистка памяти"""
    import gc
    Cache.cleanup()
    gc.collect()
```

**Step 2: Добавить вызов в main.py**

```python
# В начале файла добавить импорт
from utils import log_error, clean_log, check_restart, signal_handler, cleanup_memory

# В главном цикле добавить счётчик
restart_count = 0
cleanup_counter = 0
while restart_count < config.MAX_RESTARTS:
    try:
        # Очистка каждые 100 итераций
        cleanup_counter += 1
        if cleanup_counter >= 100:
            cleanup_memory()
            cleanup_counter = 0
        
        bot.infinity_polling(long_polling_timeout=30, timeout=35, interval=1)
    except ...
```

**Step 3: Run syntax check**

```bash
python3 -m py_compile bot3/utils.py bot3/main.py
```
Expected: PASS

**Step 4: Commit**

```bash
git add bot3/utils.py bot3/main.py
git commit -m "perf: добавить периодическую очистку памяти"
```

---

## Фаза 2: Структурные изменения (1-2 часа)

### Task 5: Добавить __slots__ в классы

**Files:**
- Modify: `bot3/menu.py:5-30` (классы Menu и BackupState)

**Step 1: Добавить __slots__ в Menu**

```python
class Menu:
    __slots__ = ['name', 'markup', 'level', 'back_level']
    
    def __init__(self, name, markup, level, back_level=None):
        self.name = name
        self.markup = markup
        self.level = level
        self.back_level = back_level
```

**Step 2: Добавить __slots__ в BackupState**

```python
class BackupState:
    __slots__ = ['startup_config', 'firmware', 'entware', 'custom_files', 
                 'selected_drive', 'delete_archive', 'selection_msg_id']
    
    def __init__(self):
        self.startup_config = False
        self.firmware = False
        self.entware = False
        self.custom_files = False
        self.selected_drive = None
        self.delete_archive = False
        self.selection_msg_id = None

    def get_selected_count(self):
        return sum([self.startup_config, self.firmware, self.entware, self.custom_files])

    def get_selected_types(self):
        types = []
        if self.startup_config: types.append("Конфигурация")
        if self.firmware: types.append("Прошивка")
        if self.entware: types.append("Entware")
        if self.custom_files: types.append("Другие файлы")
        return types
```

**Step 3: Run syntax check**

```bash
python3 -m py_compile bot3/menu.py
```
Expected: PASS

**Step 4: Commit**

```bash
git add bot3/menu.py
git commit -m "perf: добавить __slots__ в Menu и BackupState"
```

---

### Task 6: Добавить __slots__ в BotState

**Files:**
- Modify: `bot3/handlers.py:18-22` (класс BotState)

**Step 1: Добавить __slots__ в BotState**

```python
class BotState:
    __slots__ = ['current_menu', 'selected_file']
    
    def __init__(self):
        self.current_menu = MENU_MAIN
        self.selected_file = ""
```

**Step 2: Run syntax check**

```bash
python3 -m py_compile bot3/handlers.py
```
Expected: PASS

**Step 3: Commit**

```bash
git add bot3/handlers.py
git commit -m "perf: добавить __slots__ в BotState"
```

---

### Task 7: Lazy инициализация Menu объектов

**Files:**
- Modify: `bot3/menu.py` (заменить глобальные объекты на функции)
- Modify: `bot3/handlers.py` (обновить ссылки на меню)

**Step 1: Прочитать все глобальные Menu объекты в menu.py**

```bash
grep -n "^MENU_" bot3/menu.py
```

**Step 2: Заменить на фабричные функции**

Было:
```python
MENU_MAIN = Menu("🤎...", create_menu([
    ["🔑 Ключи и мосты", "📑 Списки обхода"],
    ["📲 Установка и удаление", "📊 Статистика", "⚙️ Сервис"]
]), 0)
```

Стало:
```python
def get_menu_main():
    return Menu("🤎...", create_menu([
        ["🔑 Ключи и мосты", "📑 Списки обхода"],
        ["📲 Установка и удаление", "📊 Статистика", "⚙️ Сервис"]
    ]), 0)
```

**Step 3: Обновить handlers.py**

Заменить все `MENU_MAIN` на `get_menu_main()` и т.д.

**Step 4: Run syntax check**

```bash
python3 -m py_compile bot3/menu.py bot3/handlers.py
```
Expected: PASS

**Step 5: Commit**

```bash
git add bot3/menu.py bot3/handlers.py
git commit -m "perf: lazy инициализация Menu объектов"
```

---

### Task 8: Оптимизировать замыкания в handlers.py

**Files:**
- Modify: `bot3/handlers.py:24-30` (функция setup_handlers)

**Step 1: Создать HandlerState класс**

```python
class HandlerState:
    __slots__ = ['current_menu', 'selected_file', 'backup_state']
    
    def __init__(self):
        self.current_menu = None
        self.selected_file = ""
        self.backup_state = BackupState()
```

**Step 2: Обновить setup_handlers**

```python
def setup_handlers(bot):
    state = HandlerState()

    def set_menu_and_reply(chat_id, new_menu, text=None, markup=None):
        state.current_menu = new_menu
        if not text:
            text = new_menu.name
        bot.send_message(chat_id, text, reply_markup=markup if markup else new_menu.markup)
    # ...
```

**Step 3: Run syntax check**

```bash
python3 -m py_compile bot3/handlers.py
```
Expected: PASS

**Step 4: Commit**

```bash
git add bot3/handlers.py
git commit -m "refactor: оптимизировать замыкания через HandlerState"
```

---

## Testing Plan

### Task 9: Проверка работы бота

**Files:**
- Test: ручной запуск бота

**Step 1: Запустить бота**

```bash
cd bot3
python3 main.py
```

**Step 2: Проверить базовые команды**

- `/start` — главное меню отображается
- `🔑 Ключи и мосты` — переход в меню ключей
- `📑 Списки обхода` — переход в меню списков
- Проверить кэширование ключей (вставить ключ 2 раза)

**Step 3: Проверить память**

```bash
# В другом терминале
ps aux | grep python3 | grep bot3
```

Ожидаемое потребление: ~22-24 MB (было 30.2 MB)

---

## Rollback Plan

Если что-то пошло не так:

```bash
git log --oneline -5
git revert HEAD~4..HEAD  # Откатить все коммиты оптимизации
```

---

## Success Criteria

1. ✅ Потребление памяти: < 25 MB (целевое 22-24 MB)
2. ✅ Все меню работают корректно
3. ✅ Кэширование ключей работает
4. ✅ Нет утечек памяти (проверка через 1 час работы)
5. ✅ Все тесты проходят
