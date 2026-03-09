# Version Bump Skill

## Назначение
Автоматическое обновление версии бота после каждого значимого изменения кода.

---

## Когда использовать

**После каждого коммита, который:**
- ✅ Добавляет новую функциональность
- ✅ Исправляет ошибки
- ✅ Меняет существующее поведение
- ✅ Добавляет команды или кнопки

**Не использовать для:**
- ❌ Изменений документации (README, docs/)
- ❌ Изменений .gitignore
- ❌ Орфографических исправлений в комментариях

---

## Процесс

### Шаг 1: Прочитать текущую версию
```bash
cat bot3/version.md
# Пример: 3.3.17
```

### Шаг 2: Увеличить версию
**Формат:** `MAJOR.MINOR.PATCH`

- **MAJOR** — крупные изменения (новая архитектура, breaking changes)
- **MINOR** — новые функции (команды, кнопки, сервисы)
- **PATCH** — исправления ошибок, мелкие улучшения

**Правило:** Увеличивать PATCH на 1 после каждого коммита.

```bash
# Было: 3.3.17
# Стало: 3.3.18
```

### Шаг 3: Обновить файл версии
```bash
echo "3.3.18" > bot3/version.md
```

### Шаг 4: Закоммитить версию
```bash
git add bot3/version.md
git commit -m "chore: обновить версию бота до 3.3.18"
```

### Шаг 5: Запушить и проверить
```bash
git push origin main
git status
# Должно быть: "Your branch is up to date with 'origin/main'"
```

---

## Примеры

### Пример 1: Добавлена новая команда
```bash
# После коммита с новой командой /ping
git add bot3/handlers.py
git commit -m "feat: добавить команду /ping"

# Обновить версию:
echo "3.3.18" > bot3/version.md
git add bot3/version.md
git commit -m "chore: обновить версию бота до 3.3.18"
git push origin main
git status  # Проверка
```

### Пример 2: Исправлена ошибка
```bash
# После коммита с исправлением
git add bot3/handlers.py
git commit -m "fix: исправить ошибку в /stats"

# Обновить версию:
echo "3.3.18" > bot3/version.md
git add bot3/version.md
git commit -m "chore: обновить версию бота до 3.3.18"
git push origin main
git status  # Проверка
```

---

## Автоматизация (опционально)

### Скрипт version-bump.sh
```bash
#!/bin/bash
# version-bump.sh - автоматическое увеличение версии

CURRENT=$(cat bot3/version.md)
MAJOR=$(echo $CURRENT | cut -d. -f1)
MINOR=$(echo $CURRENT | cut -d. -f2)
PATCH=$(echo $CURRENT | cut -d. -f3)

NEW_PATCH=$((PATCH + 1))
NEW_VERSION="${MAJOR}.${MINOR}.${NEW_PATCH}"

echo $NEW_VERSION > bot3/version.md
echo "Version bumped: $CURRENT → $NEW_VERSION"

git add bot3/version.md
git commit -m "chore: обновить версию бота до $NEW_VERSION"
git push origin main
git status
```

**Использование:**
```bash
chmod +x scripts/version-bump.sh
./scripts/version-bump.sh
```

---

## Чек-лист

- [ ] Прочитана текущая версия из `bot3/version.md`
- [ ] Увеличен PATCH на 1 (или MINOR/MAJOR при крупных изменениях)
- [ ] Обновлён файл `bot3/version.md`
- [ ] Закоммичено с сообщением `chore: обновить версию бота до X.X.X`
- [ ] Запушено в GitHub
- [ ] Проверено через `git status` (branch is up to date)

---

## Связанные файлы

- `bot3/version.md` — файл версии
- `bot3/handlers.py` — функция `get_local_version()`
- `bot3/handlers.py` — меню "🆕 Обновления"

---

## История версий

| Версия | Изменения |
|--------|-----------|
| 3.3.17 | Управление сервисами (Tor, VLESS, Trojan, SS) |
| 3.3.16 | Цветные эмодзи в статистике |
| 3.3.15 | Вывод версии после обновления |
| 3.3.14 | Исправление ошибок Telegram API |
| 3.3.13 | Оптимизация памяти (30→22-26 MB) |
