# 📚 Документация проекта

**Версия:** 3.4.1  
**Дата:** 9 марта 2026 г.

---

## 📁 Структура документации

```
docs/
├── user/                           # Пользовательская документация
│   ├── BACKUP_CHEATSHEET.md       # Шпаргалка по бэкапам
│   ├── BACKUP_FILES_LIST.md       # Полный список файлов бэкапа
│   ├── BACKUP_INSTRUCTION.md      # Полная инструкция по бэкапам
│   ├── CREATE_ENV.md              # Настройка .env
│   ├── MIGRATION.md               # Переход на этот форк (Ziwork/tas-unn)
│   └── LOGS_INSTRUCTION.md        # Работа с логами
│
├── developer/                      # Документация разработчика
│   ├── LOGGING_OPTIMIZATION.md    # Оптимизация логирования
│   └── REFACTORING_INSTRUCTION.md # Рефакторинг кода
│
├── analysis/                       # Аналитика
│   ├── ASYNCIO_ANALYSIS.md        # Анализ asyncio
│   └── DEDUPLICATION_ANALYSIS.md  # Анализ дублирования кода
│
├── plans/archive/                  # Архив планов
│   ├── 2026-03-08-bot-memory-optimization.md
│   └── 2026-03-09-router-optimization.md
│
└── archive/                        # Исторические документы
    ├── AUDIT_CHANGES.md
    ├── AUDIT_COMPLETE.md
    ├── IMPLEMENTATION_REPORT.md
    ├── OPTIMIZATION_REPORT.md
    ├── PUSH_TO_GITHUB.md
    ├── QUICK_ARCHIVE.md
    └── SAVE_CONFIG_GUIDE.md
```

---

## 📄 Файлы в корне проекта

В корне проекта оставлены **только основные файлы** для пользователей:

| Файл | Описание |
|------|----------|
| **README.md** | Главный файл проекта с описанием и скриншотами |
| **CHANGELOG.md** | История изменений (v3.4.1) |
| **SETUP.md** | Полная инструкция по установке |
| **QUICKSTART.md** | Быстрый старт для новых пользователей |
| **DEPLOYMENT.md** | Инструкция по развёртыванию изменений |
| **UPDATE_INSTRUCTION.md** | Обновление бота на роутере |
| **.env.example** | Шаблон конфигурации |

---

## 🔗 Навигация

### Для пользователей

1. **Новичкам:** Начните с [QUICKSTART.md](QUICKSTART.md)
2. **Установка:** Подробно в [SETUP.md](SETUP.md)
3. **Обновление:** [UPDATE_INSTRUCTION.md](UPDATE_INSTRUCTION.md)
4. **Бэкапы:** [docs/user/BACKUP_INSTRUCTION.md](docs/user/BACKUP_INSTRUCTION.md)
5. **Логи:** [docs/user/LOGS_INSTRUCTION.md](docs/user/LOGS_INSTRUCTION.md)

### Для разработчиков

1. **Развёртывание:** [DEPLOYMENT.md](DEPLOYMENT.md)
2. **Логирование:** [docs/developer/LOGGING_OPTIMIZATION.md](docs/developer/LOGGING_OPTIMIZATION.md)
3. **Рефакторинг:** [docs/developer/REFACTORING_INSTRUCTION.md](docs/developer/REFACTORING_INSTRUCTION.md)
4. **Анализ кода:** [docs/analysis/](docs/analysis/)

---

## 📊 Статистика документации

| Категория | Файлов | Описание |
|-----------|--------|----------|
| 📖 Пользовательская | 7 | Инструкции для пользователей |
| 🔧 Разработчик | 3 | Документация для разработчиков |
| 📈 Аналитика | 2 | Анализ и отчёты |
| 🗄️ Архив | 9 | Исторические документы |
| **ИТОГО** | **21** | **Вся документация проекта** |

---

## 🎯 Принципы организации

1. **В корне** — только основные файлы для пользователей
2. **docs/user/** — инструкции по использованию
3. **docs/developer/** — техническая документация
4. **docs/analysis/** — аналитика и исследования
5. **docs/archive/** — устаревшие/исторические документы
6. **.qwen/** — конфигурация Qwen Code (не документация)

---

## 📝 Обновление документации

При добавлении новой документации:

1. **Инструкции для пользователей** → `docs/user/`
2. **Техническая документация** → `docs/developer/`
3. **Аналитика/отчёты** → `docs/analysis/`
4. **Устаревшие файлы** → `docs/archive/`
5. **Планы (реализованные)** → `docs/plans/archive/`

---

**Поддержка:** Создайте issue в [GitHub репозитории](https://github.com/royfincher25-source/bypass_keenetic/issues)
