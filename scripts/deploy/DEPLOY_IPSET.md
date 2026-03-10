# 🚀 Развёртывание оптимизированного скрипта unblock_ipset.sh

## 📦 Шаг 1: Копирование файлов на роутер

```bash
# Основной скрипт
scp deploy/router/unblock_ipset.sh admin@192.168.1.1:/opt/bin/unblock_ipset.sh

# Скрипт диагностики (опционально)
scp scripts/test/router_check.sh admin@192.168.1.1:/opt/bin/router_check.sh

# Скрипт бенчмарка (опционально)
scp scripts/test/ipset_benchmark.sh admin@192.168.1.1:/opt/bin/ipset_benchmark.sh

# Сделать исполняемыми
ssh admin@192.168.1.1 "chmod +x /opt/bin/*.sh"
```

---

## 🔍 Шаг 2: Диагностика (первое подключение)

```bash
# Подключение к роутеру
ssh admin@192.168.1.1

# Запуск диагностики
/opt/bin/router_check.sh
```

**Запишите результаты:**
- [ ] DNS на порту 40500: ✅ / ❌
- [ ] DNS Google (8.8.8.8): ✅ / ❌
- [ ] Количество доменов: _____
- [ ] Свободно RAM: _____ MB

---

## ⚙️ Шаг 3: Настройка скрипта (при необходимости)

### Если DNS на порту 40500 НЕ работает

Откройте файл для редактирования:

```bash
nano /opt/bin/unblock_ipset.sh
```

Измените параметры (строки 17-18):

```bash
DNS_SERVER="8.8.8.8"    # было 8.8.8.8
DNS_PORT="53"           # было 53
```

### Если мало памяти (< 20 MB)

Измените параметр (строка 19):

```bash
MAX_PARALLEL=4          # было 8
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 🧪 Шаг 4: Тестирование

### Вариант A: Быстрый тест

```bash
# Очистка кэша
rm -rf /tmp/dns_cache/*

# Запуск с замером времени
time /opt/bin/unblock_ipset.sh
```

### Вариант B: Полный бенчмарк

```bash
/opt/bin/ipset_benchmark.sh
```

### Проверка результатов

```bash
# Статистика ipset
ipset list unblockvless | head -5
ipset list unblocktor | head -5

# Логи
logread | grep unblock_ipset | tail -10

# Размер кэша
du -sh /tmp/dns_cache/
ls -1 /tmp/dns_cache/*.cache | wc -l
```

---

## 📊 Шаг 5: Настройка автоматического обновления

### Добавление в crontab

```bash
# Редактирование crontab
crontab -l > /tmp/mycron
echo "0 3 * * * /opt/bin/unblock_ipset.sh" >> /tmp/mycron
crontab /tmp/mycron
rm /tmp/mycron

# Проверка
crontab -l
```

**Расписание:**
- `0 3 * * *` — ежедневно в 03:00
- `0 */6 * * *` — каждые 6 часов
- `*/30 * * * *` — каждые 30 минут (не рекомендуется!)

---

## 🔧 Шаг 6: Интеграция с системой

### Обновление через unblock_update.sh

Если используете скрипт обновлений:

```bash
# Проверка наличия
ls -la /opt/bin/unblock_update.sh

# Обновление скриптов
/opt/bin/unblock_update.sh
```

### Добавление в автозагрузку

```bash
# Копирование в ndm
cp /opt/bin/unblock_ipset.sh /opt/etc/ndm/

# Создание скрипта инициализации
cat > /opt/etc/ndm/100-ipset-restore.sh << 'EOF'
#!/bin/sh
[ "$1" != "start" ] && exit 0
sleep 10
/opt/bin/unblock_ipset.sh &
EOF

chmod +x /opt/etc/ndm/100-ipset-restore.sh
```

---

## 📈 Шаг 7: Мониторинг производительности

### Быстрая проверка статуса

```bash
# Текущее количество IP в ipset
echo "unblocksh:  $(ipset list unblocksh 2>/dev/null | grep -c '^[0-9]')"
echo "unblocktor: $(ipset list unblocktor 2>/dev/null | grep -c '^[0-9]')"
echo "unblockvless: $(ipset list unblockvless 2>/dev/null | grep -c '^[0-9]')"
echo "unblocktroj: $(ipset list unblocktroj 2>/dev/null | grep -c '^[0-9]')"
```

### Логирование

```bash
# Последние 20 записей
logread | grep unblock_ipset | tail -20

# Сохранение в файл
logread | grep unblock_ipset > /tmp/ipset_log.txt
```

---

## ⚠️ Решение проблем

### Скрипт зависает

**Причина 1:** DNS недоступен
```bash
# Проверка
dig +short google.com @8.8.8.8

# Решение: изменить DNS_SERVER в скрипте
```

**Причина 2:** Нехватка памяти
```bash
# Проверка
free -m

# Решение: уменьшить MAX_PARALLEL до 4 или 2
```

**Причина 3:** Слишком много доменов
```bash
# Проверка
wc -l /opt/etc/unblock/*.txt

# Решение: почистить списки от ненужных доменов
```

### Кэш разрастается

```bash
# Очистка кэша
rm -rf /tmp/dns_cache/*

# Автоматическая очистка (добавить в crontab)
echo "0 2 * * 0 rm -rf /tmp/dns_cache/*" >> /tmp/mycron
crontab /tmp/mycron
```

### IPset не создаётся

```bash
# Проверка версии ipset
ipset --version

# Перезагрузка ipset
ipset destroy unblocksh
ipset destroy unblocktor
ipset destroy unblockvless
ipset destroy unblocktroj

# Запуск заново
/opt/bin/unblock_ipset.sh
```

---

## 📝 Чек-лист успешного развёртывания

- [ ] Скрипт скопирован: `/opt/bin/unblock_ipset.sh`
- [ ] Права установлены: `chmod +x`
- [ ] Диагностика пройдена
- [ ] DNS работает (40500 или 8.8.8.8)
- [ ] Тестовый запуск успешен
- [ ] Время выполнения < 60 секунд
- [ ] Все ipset созданы
- [ ] Логи записываются
- [ ] Настроен crontab (опционально)

---

## 🎯 Ожидаемые результаты

| Количество доменов | Время выполнения | RAM |
|--------------------|------------------|-----|
| < 200 | 15-30 сек | ~10 MB |
| 200-500 | 30-60 сек | ~15 MB |
| 500-1000 | 60-120 сек | ~20 MB |
| > 1000 | > 120 сек | ~25 MB |

---

**Поддержка:** Создайте issue с результатами диагностики при проблемах
