# 📋 Списки обхода для Shadowsocks

**Дата:** 10 марта 2026 г.  
**Версия:** 1.0

---

## 🎯 Назначение

Shadowsocks требует обхода блокировок для стабильной работы. Этот документ анализирует необходимые домены и предоставляет готовые списки.

---

## 📊 Текущая статистика

### Файл: `/opt/etc/unblock/shadowsocks.txt`

```bash
# Проверка на роутере
wc -l /opt/etc/unblock/shadowsocks.txt
grep -vE '^#|^[0-9]|^$' /opt/etc/unblock/shadowsocks.txt | wc -l
```

---

## 🔍 Анализ доменов Shadowsocks

### Типы записей в списке:

1. **Домены** — требуют DNS разрешения
2. **IP адреса** — добавляются напрямую
3. **CIDR блоки** — диапазоны IP
4. **Shadowsocks ключи** — ss:// ссылки (не для ipset)

---

## 📝 Рекомендуемые домены

### Основные сервисы (пример):

```bash
# Мессенджеры
telegram.org
telegram.me
t.me
web.telegram.org

# Социальные сети
twitter.com
www.twitter.com
mobile.twitter.com
abs.twimg.com
pbs.twimg.com

# Поисковики
duckduckgo.com
www.duckduckgo.com

# Облачные сервисы
dropbox.com
www.dropbox.com
dl.dropboxusercontent.com

# Прочие
reddit.com
www.reddit.com
old.reddit.com
```

---

## 🚀 Оптимизация списка

### Проблема:
- Много доменов → медленное обновление
- Динамические IP → частые изменения

### Решение:

#### 1. Удалить дубликаты

```bash
# На роутере
sort -u /opt/etc/unblock/shadowsocks.txt > /tmp/ss_sorted.txt
mv /tmp/ss_sorted.txt /opt/etc/unblock/shadowsocks.txt
```

#### 2. Удалить нерабочие домены

```bash
# Тест доменов
while read -r domain; do
    [ -z "$domain" ] && continue
    [[ "$domain" == \#* ]] && continue
    [[ "$domain" =~ ^[0-9] ]] && continue
    
    result=$(nslookup "$domain" 8.8.8.8 2>/dev/null | grep -i 'address' | grep -v '8.8.8.8' | head -1)
    if [ -z "$result" ]; then
        echo "❌ $domain - не резолвится"
    else
        echo "✅ $domain - OK"
    fi
done < /opt/etc/unblock/shadowsocks.txt
```

#### 3. Заменить домены на IP (для стабильных)

```bash
# Для доменов с постоянными IP
nslookup telegram.org 8.8.8.8 | grep -i 'address' | grep -v '8.8.8.8'
# Вывод: 149.154.167.99
# Добавить в список: 149.154.167.99
```

---

## 📊 Статистика производительности

### Время обновления:

| Доменов | Время (P20) | IP в ipset |
|---------|-------------|------------|
| 50 | ~5-8 сек | 100-150 |
| 100 | ~10-15 сек | 200-300 |
| 150 | ~15-20 сек | 300-450 |
| 200 | ~20-25 сек | 400-600 |

### Использование памяти:

| IP в ipset | Память |
|------------|--------|
| 100 | ~1 MB |
| 500 | ~2-3 MB |
| 1000 | ~4-5 MB |
| 2000 | ~8-10 MB |

---

## 🔧 Управление списками

### Добавление доменов:

```bash
# На роутер
cat >> /opt/etc/unblock/shadowsocks.txt << 'EOF'
new-domain.com
www.new-domain.com
EOF

# Обновление
/opt/bin/unblock_ipset.sh
```

### Удаление доменов:

```bash
# Удалить конкретный домен
grep -v 'old-domain.com' /opt/etc/unblock/shadowsocks.txt > /tmp/ss.tmp
mv /tmp/ss.tmp /opt/etc/unblock/shadowsocks.txt

# Обновление
/opt/bin/unblock_ipset.sh
```

### Проверка актуальности:

```bash
# Тест всех доменов
/opt/bin/router_check.sh

# Детальная проверка
for file in /opt/etc/unblock/*.txt; do
    name=$(basename "$file")
    domains=$(grep -vE '^#|^[0-9]|^$' "$file" | wc -l)
    echo "$name: $domains доменов"
done
```

---

## 📈 Мониторинг эффективности

### Проверка ipset:

```bash
# Количество IP
ipset list unblocksh | grep -c "^[0-9]"

# Просмотр
ipset list unblocksh | head -30

# Статистика
ipset list unblocksh -t
```

### Логирование (если доступно):

```bash
# Проверка логов
logread | grep unblock_ipset | tail -20

# Фильтрация по shadowsocks
logread | grep unblocksh | tail -10
```

---

## ⚠️ Частые проблемы

### 1. Мало IP в ipset

**Причина:** Домены не резолвятся

**Решение:**
```bash
# Проверка DNS
nslookup domain.com 8.8.8.8

# Если не работает — заменить домен или добавить IP
```

### 2. Слишком много IP

**Причина:** Много wildcard доменов

**Решение:**
```bash
# Удалить wildcard
grep -v '^\*' /opt/etc/unblock/shadowsocks.txt > /tmp/ss.tmp
mv /tmp/ss.tmp /opt/etc/unblock/shadowsocks.txt
```

### 3. Медленное обновление

**Причина:** Много доменов, медленный DNS

**Решение:**
- Уменьшить список до 100-150 доменов
- Использовать быстрый DNS (8.8.8.8)
- Увеличить MAX_PARALLEL (если есть память)

---

## 🎯 Рекомендации

### Оптимальный размер списка:

| Сценарий | Доменов | IP | Время |
|----------|---------|-----|-------|
| Минимальный | 30-50 | 60-100 | 3-5 сек |
| **Оптимальный** | **100-150** | **200-400** | **10-15 сек** |
| Расширенный | 200-300 | 400-800 | 20-30 сек |

### Приоритеты:

1. **Критичные** — мессенджеры, почта
2. **Важные** — социальные сети, новости
3. **Дополнительные** — развлекательные сервисы

### Формат файла:

```bash
# Комментарии (начинаются с #)
# Мессенджеры
telegram.org
t.me

# Социальные сети
twitter.com

# IP адреса (добавляются напрямую)
149.154.167.99

# CIDR блоки
149.154.160.0/20
```

---

## 📝 Примеры списков

### Минимальный (30 доменов):

```bash
# Мессенджеры
telegram.org
telegram.me
t.me
web.telegram.org

# Поисковики
duckduckgo.com
www.duckduckgo.com

# Социальные сети
twitter.com
www.twitter.com
mobile.twitter.com

# Облачные сервисы
dropbox.com
dl.dropboxusercontent.com

# Новости
reuters.com
www.reuters.com
bloomberg.com

# Прочие
reddit.com
www.reddit.com
medium.com
```

### Оптимальный (100 доменов):

```bash
# Включает все домены из "Минимального" +

# Дополнительные мессенджеры
whatsapp.com
www.whatsapp.com
web.whatsapp.com

# Видео сервисы
vimeo.com
www.vimeo.com
player.vimeo.com

# Файлообменники
mega.nz
mega.io
www.mega.nz

# Почтовые сервисы
protonmail.com
www.protonmail.com
mail.protonmail.com

# И т.д.
```

---

## 🔄 Автоматическое обновление

### Crontab:

```bash
# Обновление каждые 6 часов
0 */6 * * * /opt/bin/unblock_ipset.sh

# Обновление раз в сутки
0 3 * * * /opt/bin/unblock_ipset.sh
```

### Скрипт проверки:

```bash
#!/bin/sh
# /opt/bin/check_shadowsocks.sh

echo "=== Проверка Shadowsocks списков ==="

# Статистика
total=$(wc -l < /opt/etc/unblock/shadowsocks.txt)
domains=$(grep -vE '^#|^[0-9]|^$' /opt/etc/unblock/shadowsocks.txt | wc -l)
ips=$(grep -E '^[0-9]' /opt/etc/unblock/shadowsocks.txt | wc -l)

echo "Всего строк: $total"
echo "Доменов: $domains"
echo "IP адрес: $ips"

# Проверка ipset
ipset_count=$(ipset list unblocksh 2>/dev/null | grep -c "^[0-9]" || echo 0)
echo "IP в ipset: $ipset_count"

# Тест DNS
test_result=$(nslookup google.com 8.8.8.8 2>/dev/null | grep -i 'address' | head -1)
if [ -n "$test_result" ]; then
    echo "DNS: ✅ OK"
else
    echo "DNS: ❌ FAIL"
fi
```

---

## 📚 Дополнительные ресурсы

- [Официальная документация Shadowsocks](https://shadowsocks.org/)
- [Списки блокировок](https://github.com/AdguardTeam/AdGuardHome/wiki/DNS-Crypt)
- [Документация проекта](../README.md)

---

**Обновлено:** 10 марта 2026 г.  
**Автор:** bypass_keenetic team
