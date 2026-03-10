# Анализ недостатков кода маршрутизации

**Дата:** 2026-03-10  
**Проект:** bypass_keenetic  

---

## Обзор файлов маршрутизации

| Файл | Назначение | Строк |
|------|------------|-------|
| `deploy/router/100-unblock-vpn.sh` | Обработка VPN-подключений | 74 |
| `deploy/router/100-unblock-vpn-v4.sh` | Упрощенная версия VPN v4 | 81 |
| `deploy/router/100-redirect.sh` | iptables правила NAT/REDIRECT | 138 |
| `deploy/router/100-ipset.sh` | Создание ipsets при старте | 17 |
| `deploy/router/unblock_ipset.sh` | Заполнение ipsets из списков | 162 |
| `deploy/router/unblock_dnsmasq.sh` | Генерация dnsmasq конфига | 62 |
| `deploy/router/unblock_ipset_fixed.sh` | Исправленная версия | 168 |
| `deploy/router/unblock_ipset_optimized.sh` | Оптимизированная версия | 147 |

---

## Критические недостатки (CRITICAL)

### 1. Дублирование кода в unblock_ipset.sh
**Строки:** 9-37, 40-68, 71-99, 102-130

**Проблема:** Блок обработки списка (while read + if/continue + regex + ipset add) повторяется 4 раза практически без изменений для:
- shadowsocks.txt → unblocksh
- tor.txt → unblocktor
- vless.txt → unblockvless
- trojan.txt → unblocktroj

**Влияние:** Трудно поддерживать, легко допустить ошибку при изменении логики.

---

### 2. Медленная загрузка IP (O(n) вместо O(1))
**Строки:** 35,66,97,128

**Проблема:** Каждый IP добавляется отдельным вызовом `ipset -exist add`:
```bash
dig +short "$line" @localhost -p 40500 | grep -Eo '[0-9.]+' | awk '{system("ipset -exist add unblocksh "$1)}'
```

**Влияние:**
- 10,000 IP ≈ ~30 секунд
- 100,000 IP ≈ ~5 минут

**Решение:** Использовать `ipset restore -! < file` для пакетной загрузки.

---

### 3. Shell injection уязвимость
**Строки:** 35,66,97,128

**Проблема:** Использование `awk '{system(...)}'` без экранирования:
```bash
awk '{system("ipset -exist add unblocksh "$1)}'
```

**Влияние:** Если `$1` содержит специальные символы, возможно выполнение произвольных команд.

---

### 4. Нет таймаута для DNS запросов
**Строки:** 7,35,66,97,128

**Проблема:** `dig +short` без таймаута. При недоступности DNS (порт 40500) скрипт зависает.

**Влияние:** Полная блокировка обновления списков при проблемах с DNS.

---

### 5. Многократные вызовы iptables-save
**Строки:** 15,20,44,58,72,106 (100-redirect.sh)

**Проблема:** `iptables-save` - тяжелая операция, вызывается 5+ раз:
```bash
if [ -z "$(iptables-save 2>/dev/null | grep "$protocol --dport 53 -j DNAT")" ]; then
if [ -z "$(iptables-save 2>/dev/null | grep unblocksh)" ]; then
if [ -z "$(iptables-save 2>/dev/null | grep unblocktor)" ]; then
# ... и т.д.
```

**Влияние:** Задержка при каждом запуске скрипта, нагрузка на CPU.

---

### 6. Race conditions в 100-unblock-vpn.sh
**Строки:** 14,34-70

**Проблема:** Переменные `$change`, `$id`, `$connected` используются без проверки инициализации:
```bash
if [ "$1" = "hook" ] && [ "$change" = "link" ] && [ "$id" = "$vpn" ]; then
```

**Влияние:** При одновременном подключении нескольких VPN возможно некорректное поведение.

---

## Средние недостатки (MEDIUM)

### 7. Нет дедупликации в unblock_dnsmasq.sh
**Строка:** 3

**Проблема:** Файл полностью перезаписывается при каждом запуске, нет дедупликации доменов.

---

### 8. Неполная обработка wildcards для Tor
**Строки:** 24-30 (unblock_dnsmasq.sh)

**Проблема:** Для tor.txt не обрабатываются wildcards (`*.domain.com`), хотя для shadowsocks.txt они есть.

---

### 9. Скрытие ошибок
**Все скрипты**

**Проблема:** `2>/dev/null` скрывает ошибки, затрудняя диагностику.

---

### 10. Мусорный код
**Строки:** 27-55 (100-redirect.sh)

**Проблема:** 50+ закомментированных строк затрудняют чтение и поддержку.

---

## Рекомендации по приоритету исправлений

| Приоритет | Задача | Файл |
|-----------|--------|------|
| 1 | Рефакторинг + batch load | unblock_ipset.sh |
| 2 | Кеширование iptables-save | 100-redirect.sh |
| 3 | Исправление race conditions | 100-unblock-vpn.sh |
| 4 | Дедупликация + проверка DNS | unblock_dnsmasq.sh |

---

## Источники

- Анализ файлов: `deploy/router/*.sh`
- Конфигурация: `deploy/config/dnsmasq.conf`
- Интеграция: `src/bot3/script.sh`
