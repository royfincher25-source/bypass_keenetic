# Bot Memory Optimization Plan for Keenetic (MT7628N, 128MB RAM)

> **For implementation:** Use executing-plans skill to implement task-by-task.

**Goal:** Снизить потребление памяти ботом с ~50-60 MB до ~35-45 MB.

**Target Router:** MT7628N, 575MHz, 1 ядро, 128MB DDR2 RAM

**Current estimated usage:** 50-60 MB  
**Target usage:** 35-45 MB  
**Expected savings:** ~15 MB

---

## Целевое потребление

| Компонент | Текущее | После оптимизации |
|-----------|---------|------------------|
| Python интерpreter | ~15-20 MB | ~15 MB |
| telebot | ~8-15 MB | ~8 MB |
| requests + urllib3 | ~3-5 MB | ~2 MB |
| Код бота | ~5-10 MB | ~4 MB |
| Системные | ~10-15 MB | ~10 MB |
| **ИТОГО** | **~50-60 MB** | **~35-45 MB** |

---

## Фаза 1: Критические оптимизации (без изменения функциональности)

### Task 1: Уменьшить MAX_SIZE в Cache (100 → 20)

**Files:**
- `bot3/utils.py:46` — изменить `MAX_SIZE = 100` на `MAX_SIZE = 20`

**Impact:** -2 MB RAM

---

### Task 2: Упростить Cache класс (убрать LRU логику)

**Files:**
- `bot3/utils.py:41-97` — упростить класс Cache

**Changes:**
```python
class Cache:
    """Простой кэш с TTL для embedded-устройств"""
    _cache = {}
    _timestamps = {}
    MAX_SIZE = 20

    @classmethod
    def get(cls, key, default=None):
        return cls._cache.get(key, default)

    @classmethod
    def set(cls, key, value, ttl=300):
        if len(cls._cache) >= cls.MAX_SIZE:
            # Просто очищаем всё при переполнении
            cls._cache.clear()
            cls._timestamps.clear()
        cls._cache[key] = value
        cls._timestamps[key] = time.time() + ttl

    @classmethod
    def is_valid(cls, key):
        if key not in cls._timestamps:
            return False
        return time.time() < cls._timestamps[key]

    @classmethod
    def cleanup(cls):
        now = time.time()
        expired = [k for k, t in cls._timestamps.items() if now >= t]
        for key in expired:
            cls._cache.pop(key, None)
            cls._timestamps.pop(key, None)

    @classmethod
    def clear(cls):
        cls._cache.clear()
        cls._timestamps.clear()
```

**Impact:** -1 MB RAM, +CPU (менее сложная логика)

---

### Task 3: Уменьшить HTTP connection pool (5 → 2)

**Files:**
- `bot3/utils.py:197` — `pool_maxsize=2`
- `core/http_client.py:42` — `pool_maxsize=2`

**Impact:** -1 MB RAM

---

### Task 4: Убрать неиспользуемые глобальные переменные

**Files:**
- `bot3/utils.py:177-180` — удалить `_http_session` (уже импортируется из core)

**Impact:**微量 (чистота кода)

---

## Фаза 2: Структурные оптимизации

### Task 5: Добавить __slots__ в классы

**Files:**
- `bot3/menu.py:5-37` — Menu и BackupState (уже есть)
- `bot3/handlers.py:33-41` — HandlerState (уже есть)

**Status:** ✅ Уже реализовано

---

### Task 6: Lazy инициализация Menu

**Files:**
- `bot3/menu.py:125-193` — фабричные функции (уже есть)

**Status:** ✅ Уже реализовано

---

### Task 7: Убрать дублирование botlight → core

**Problem:** ~50% кода дублируется между bot3 и botlight

**Solution:** Создать общие модули в core/

**Files to create:**
- `core/handlers_shared.py` — общие обработчики (stats, backup, updates)

**Files to modify:**
- `botlight/handlers.py` — импортировать из core вместо локальных функций
- `botlight/menu.py` — импортировать из bot3/menu.py или создать общий

**Impact:** -5 MB RAM (меньше загруженного кода), проще поддержка

---

### Task 8: Оптимизация импортов

**Files:**
- `bot3/utils.py` — убрать тяжёлые импорты из стартового импорта

**Changes:**
- Переместить `import json` внутрь функций где используется
- Переместить `import re` внутрь функций где используется
- Переместить `import gc` внутрь функций

**Impact:** -1 MB RAM при старте

---

### Task 9: Периодическая очистка памяти

**Files:**
- `bot3/main.py:54-61` — cleanup каждые 100 итераций (уже есть)

**Status:** ✅ Уже реализовано

---

## Фаза 3: Дополнительные микро-оптимизации

### Task 10: Кэширование чтения /proc

**Files:**
- `bot3/handlers.py:277-414` — функция get_stats()

**Changes:**
```python
# Добавить кэш для системных метрик
_system_stats_cache = {
    'uptime': None,
    'meminfo': None,
    'timestamp': 0
}
CACHE_TTL = 5  # 5 секунд

def get_stats(refresh_services=False):
    global _system_stats_cache
    
    # Использовать кэш если валиден
    if time.time() - _system_stats_cache['timestamp'] < CACHE_TTL:
        # Вернуть закэшированные значения RAM/uptime
        pass
    
    # ... существующий код ...
```

**Impact:** -I/O операции, +CPU экономия

---

### Task 11: Упростить regex валидацию

**Files:**
- `bot3/utils.py:271-301` — validate_bypass_entry()

**Changes:** Использовать простые проверки вместо полных regex:

```python
def validate_bypass_entry(entry):
    entry = entry.strip()
    if not entry:
        return False
    if entry.startswith('#'):
        return True
    # Простая проверка домена
    if '.' in entry and len(entry) < 253:
        return True
    # Простая проверка IP
    parts = entry.split('.')
    if len(parts) == 4:
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except ValueError:
            pass
    return False
```

**Impact:** -0.5 MB (меньше regex объектов), +CPU

---

## Итоговая оценка экономии

| Оптимизация | Экономия RAM |
|-------------|---------------|
| MAX_SIZE 100 → 20 | -2 MB |
| Упрощённый Cache | -1 MB |
| HTTP pool 5 → 2 | -1 MB |
| Убранное дублирование | -5 MB |
| Оптимизация импортов | -1 MB |
| Regex упрощение | -0.5 MB |
| **ИТОГО** | **~10.5 MB** |

---

## Тестирование

### Ручное тестирование

```bash
# Запустить бота
cd bot3 && python3 main.py

# В другом терминале проверить память
ps aux | grep python3 | grep bot3
# Ожидаемое: VmRSS ~35-45 MB
```

### Функциональное тестирование

1. `/start` — главное меню
2. `🔑 Ключи и мосты` — вставить VLESS ключ
3. `📑 Списки обхода` — добавить домен
4. `📊 Статистика` — проверить отображение
5. `🆕 Обновления` — проверить кнопку

---

## Rollback Plan

```bash
# Откатить все изменения
git log --oneline -20
git revert HEAD~10..HEAD
```

---

## Success Criteria

1. ✅ Потребление RAM: < 45 MB (целевое 35-45 MB)
2. ✅ Все функции работают корректно
3. ✅ Нет утечек памяти (проверка через 1 час работы)
4. ✅ CPU usage не увеличился значительно
