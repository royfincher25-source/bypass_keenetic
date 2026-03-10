# 📋 Диагностика роутера перед запуском

## Быстрая проверка (выполнить команды по очереди)

### 1. Проверка команды `timeout`

```bash
timeout --help 2>&1 | head -1
```

**Результат:**
- ✅ Есть: `timeout (GNU coreutils) ...`
- ❌ Нет: `command not found`

---

### 2. Проверка DNS на порту 40500 (dnsmasq)

```bash
dig +short google.com @localhost -p 40500
```

**Результат:**
- ✅ Работает: `142.250.180.78` (или другие IP Google)
- ❌ Не работает: пусто или ошибка

**Альтернативная проверка:**

```bash
nslookup google.com localhost 40500
```

---

### 3. Проверка DNS через Google DNS (резервный вариант)

```bash
dig +short google.com @8.8.8.8
```

**Результат:**
- ✅ Работает: `142.250.180.78` (или другие IP Google)
- ❌ Не работает: пусто или ошибка

---

### 4. Количество доменов в списках обхода

```bash
# Подсчёт доменов (без IP и комментариев)
echo "=== Shadowsocks ==="
grep -vE '^#|^[0-9]|^$' /opt/etc/unblock/shadowsocks.txt 2>/dev/null | wc -l

echo "=== Tor ==="
grep -vE '^#|^[0-9]|^$' /opt/etc/unblock/tor.txt 2>/dev/null | wc -l

echo "=== VLESS ==="
grep -vE '^#|^[0-9]|^$' /opt/etc/unblock/vless.txt 2>/dev/null | wc -l

echo "=== Trojan ==="
grep -vE '^#|^[0-9]|^$' /opt/etc/unblock/trojan.txt 2>/dev/null | wc -l

echo "=== VPN списки ==="
ls -la /opt/etc/unblock/vpn-*.txt 2>/dev/null
```

---

### 5. Общая статистика по спискам

```bash
echo "=== ОБЩАЯ СТАТИСТИКА ==="
for file in /opt/etc/unblock/*.txt; do
    [ -f "$file" ] || continue
    name=$(basename "$file")
    total=$(wc -l < "$file")
    domains=$(grep -vE '^#|^[0-9]|^$' "$file" | wc -l)
    ips=$((total - domains))
    echo "$name: всего=$total, доменов=$domains, IP=$ips"
done
```

---

### 6. Проверка доступной памяти

```bash
free -m
```

**Важно:** Если свободно < 20 MB, возможна нестабильная работа при параллельной обработке

---

### 7. Проверка версии ipset

```bash
ipset --version
```

**Важно:** Должно быть `ipset v6.x` или выше для поддержки `-exist` и `restore -!`

---

## 📊 Сводная таблица результатов

| Параметр | Команда | Ожидаемый результат |
|----------|---------|---------------------|
| **timeout** | `timeout --help` | GNU coreutils |
| **DNS 40500** | `dig @localhost -p 40500` | IP адреса |
| **DNS 8.8.8.8** | `dig @8.8.8.8` | IP адреса |
| **Доменов всего** | `grep -vE '^#|^[0-9]'` | < 1000 (оптимально) |
| **Свободно RAM** | `free -m` | > 20 MB |
| **ipset версия** | `ipset --version` | v6.x+ |

---

## 🔧 Быстрый тест скрипта

```bash
# Очистка кэша
rm -rf /tmp/dns_cache/*

# Запуск с замером времени
time /opt/bin/unblock_ipset.sh

# Проверка логов
logread | grep unblock_ipset | tail -20
```

---

## ⚡ Если скрипт работает медленно

### Вариант 1: Уменьшить параллельность

В файле `/opt/bin/unblock_ipset.sh` изменить:

```bash
MAX_PARALLEL=4  # было 8
```

### Вариант 2: Использовать только Google DNS

В файле `/opt/bin/unblock_ipset.sh` изменить:

```bash
DNS_SERVER="8.8.8.8"
DNS_PORT="53"
```

### Вариант 3: Отключить кэширование (для теста)

```bash
rm -rf /tmp/dns_cache/*
```

---

## 📝 Пример вывода успешной проверки

```
=== ОБЩАЯ СТАТИСТИКА ===
shadowsocks.txt: всего=150, доменов=120, IP=30
tor.txt: всего=500, доменов=500, IP=0
vless.txt: всего=200, доменов=180, IP=20
trojan.txt: всего=100, доменов=80, IP=20

✅ Завершено за 45c
📊 Статистика:
  unblocksh: 150 IP
  unblocktor: 500 IP
  unblockvless: 200 IP
  unblocktroj: 100 IP
```
