# 🛠️ Инструменты разработчика

**Версия:** 3.4.2  
**Дата:** 9 марта 2026 г.

---

## 📁 Структура папки tools/

```
tools/
├── check_config.py        # Проверка конфигурации
└── push_to_github.bat     # Быстрый пуш на GitHub
```

---

## 🔧 Описание инструментов

### check_config.py - Проверка конфигурации

**Назначение:** Проверка корректности загрузки и валидации конфигурации.

**Использование:**
```bash
# Запустить проверку
python3 tools/check_config.py

# С флагом отладки
python3 tools/check_config.py --debug
```

**Проверяет:**
- Наличие файла `.env`
- Корректность формата `TELEGRAM_BOT_TOKEN`
- Наличие `TELEGRAM_USERNAMES` или `TELEGRAM_USER_IDS`
- Корректность путей к файлам
- Доступность портов

**Пример вывода:**
```
✅ .env файл найден
✅ TELEGRAM_BOT_TOKEN валиден
✅ TELEGRAM_USERNAMES указан
✅ TELEGRAM_USER_IDS указан
✅ Все пути существуют
✅ Конфигурация корректна
```

---

### push_to_github.bat - Быстрый пуш на GitHub

**Назначение:** Автоматизация процесса коммита и пуша изменений.

**Использование (Windows):**
```cmd
tools\push_to_github.bat "Описание изменений"
```

**Что делает:**
1. `git add -A` — добавляет все изменения
2. `git commit -m "Описание"` — коммитит с сообщением
3. `git push` — пушит на GitHub
4. `git status` — показывает финальный статус

**Пример:**
```cmd
tools\push_to_github.bat "docs: обновить инструкцию"
```

**Вывод:**
```
[main 1234567] docs: обновить инструкцию
 1 file changed, 10 insertions(+)
 To https://github.com/.../bypass_keenetic.git
    abc1234..1234567  main -> main
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

---

## 📋 Другие инструменты (в scripts/)

### Отладка (scripts/debug/)

| Скрипт | Назначение |
|--------|------------|
| **check_config_load.sh** | Проверка загрузки конфигурации на роутере |
| **clean_restart.sh** | Полная очистка и перезапуск бота |
| **debug_import.sh** | Отладка импорта функций |
| **debug_import_detail.sh** | Детальная отладка импорта |
| **final_check.sh** | Финальная проверка после установки |

### Тестирование (scripts/test/)

| Скрипт | Назначение |
|--------|------------|
| **test_priority_3.sh** | Тестирование HTTP Connection Pooling |

---

## 🔗 Ссылки

- [Документация по скриптам](../scripts/README.md)
- [Документация по развёртыванию](../deploy/README.md)

---

**Поддержка:** Создайте issue в [GitHub репозитории](https://github.com/royfincher25-source/bypass_keenetic/issues)
