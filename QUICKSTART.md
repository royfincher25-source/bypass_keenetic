# ⚡ Быстрый старт

## 3 шага для начала работы

### 1️⃣ Создайте .env файл

```bash
cp .env.example .env
```

### 2️⃣ Заполните токен и логин

Откройте `.env` и заполните:

```ini
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_USERNAMES=ваш_логин
```

### 3️⃣ Проверьте конфигурацию

```bash
python check_config.py
```

**Если всё ✅ — готово к развёртыванию!**

---

## 📚 Документация

- **Полная инструкция:** [SETUP.md](SETUP.md)
- **Развёртывание:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **Отчёт о тестировании:** [TEST_REPORT.md](TEST_REPORT.md)

---

## 🆘 Помощь

Если что-то не работает:

1. Проверьте `.env` файл
2. Запустите `python check_config.py`
3. Посмотрите логи: `tail -f error.log`
