# ✅ Как проверить что VLESS работает

**Дата:** 10 марта 2026 г.  
**Версия:** 1.0

---

## 🎯 Быстрая проверка (3 команды)

```bash
# 1. Проверка процесса
ps | grep xray

# 2. Проверка порта
netstat -tlnp | grep 31964

# 3. Тест доступа
curl -I https://www.youtube.com
```

**Если всё OK:**
- ✅ Процесс `xray` запущен
- ✅ Порт `31964` слушается
- ✅ YouTube открывается

---

## 📊 Подробная диагностика

### 1. Проверка сервиса Xray

```bash
# Статус сервиса
/opt/etc/init.d/S24xray status

# Перезапуск
/opt/etc/init.d/S24xray restart

# Логи (если есть)
cat /tmp/xray.log 2>/dev/null
```

**Ожидаемый вывод:**
```
xray is running
```

---

### 2. Проверка процесса

```bash
# Процесс
ps | grep -E 'xray|vless' | grep -v grep

# Детали
ps -w | grep xray
```

**Ожидаемый вывод:**
```
12345 root     15.2M S    /opt/bin/xray run -c /opt/etc/xray/config.json
```

---

### 3. Проверка порта

```bash
# Прослушиваемые порты
netstat -tlnp | grep 31964

# Или через ss
ss -tlnp | grep 31964
```

**Ожидаемый вывод:**
```
tcp        0      0 0.0.0.0:31964    0.0.0.0:*    LISTEN  12345/xray
```

**Порт по умолчанию:** `31964` (может отличаться в конфиге)

---

### 4. Проверка ipset (списки обхода)

```bash
# Количество IP в списке
ipset list unblockvless | grep -c "^[0-9]"

# Просмотр первых 20
ipset list unblockvless | head -25

# Проверка конкретного домена
ipset test unblockvless youtube.com
```

**Ожидаемый вывод:**
```
unblockvless: 17 IP
```

---

### 5. Проверка iptables (маршрутизация)

```bash
# Правила для VLESS
iptables -t nat -L PREROUTING -nv | grep 31964

# Или все правила
iptables -t nat -L -nv | grep -E 'unblockvless|31964'
```

**Ожидаемый вывод:**
```
DNAT       tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            tcp match-set unblockvless dst to:31964
```

---

### 6. Проверка DNS

```bash
# Разрешение доменов
nslookup youtube.com 8.8.8.8
nslookup googlevideo.com 8.8.8.8

# Проверка кэша (если есть)
ls -la /tmp/dns_cache/ | head -10
```

**Ожидаемый вывод:**
```
Name:      youtube.com
Address 1: 142.250.180.78
```

---

### 7. Тест доступа к YouTube

```bash
# HTTP запрос
curl -I https://www.youtube.com

# Тест загрузки
curl -o /dev/null -s -w "%{time_total}\n" https://www.youtube.com

# Проверка IP
curl -s https://www.youtube.com | head -1
```

**Ожидаемый вывод:**
```
HTTP/2 200
content-type: text/html; charset=utf-8
```

---

### 8. Проверка конфигурации

```bash
# Конфиг Xray
cat /opt/etc/xray/config.json | grep -A5 "inbounds"

# Ключи VLESS
cat /opt/etc/xray/config.json | grep -i "vless"
```

**Пример конфига:**
```json
{
  "inbounds": [
    {
      "port": 31964,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "uuid-key",
            "flow": "xtls-rprx-vision"
          }
        ]
      }
    }
  ]
}
```

---

## 🔧 Диагностика проблем

### Проблема 1: Xray не запускается

**Проверка:**
```bash
/opt/etc/init.d/S24xray start
```

**Возможные ошибки:**

1. **Нет файла конфигурации:**
   ```bash
   ls -la /opt/etc/xray/config.json
   ```
   **Решение:** Создать конфиг через бота

2. **Ошибка в конфиге:**
   ```bash
   /opt/bin/xray test -c /opt/etc/xray/config.json
   ```
   **Решение:** Исправить синтаксис

3. **Порт занят:**
   ```bash
   netstat -tlnp | grep 31964
   ```
   **Решение:** Сменить порт в конфиге

---

### Проблема 2: YouTube не открывается

**Проверка по шагам:**

```bash
# 1. Проверка DNS
nslookup youtube.com 8.8.8.8

# 2. Проверка ipset
ipset list unblockvless | grep -c "^[0-9]"

# 3. Проверка маршрутизации
iptables -t nat -L PREROUTING -nv | grep 31964

# 4. Тест через proxy
curl -x socks5://localhost:31964 https://www.youtube.com
```

**Возможные причины:**

1. **Пустой ipset:**
   ```bash
   /opt/bin/unblock_ipset.sh
   ```

2. **Нет правил iptables:**
   ```bash
   # Перезапуск скриптов
   /opt/etc/ndm/100-redirect.sh
   ```

3. **Неверный порт:**
   Проверить в `/opt/etc/xray/config.json`

---

### Проблема 3: Медленная скорость

**Проверка:**
```bash
# Тест скорости
curl -o /dev/null -s -w "%{speed_download}\n" https://www.youtube.com

# Проверка нагрузки
top | grep xray
```

**Возможные решения:**

1. **Увеличить MAX_PARALLEL:**
   ```bash
   # В unblock_ipset.sh
   MAX_PARALLEL=30  # было 20
   ```

2. **Проверить DNS:**
   ```bash
   # Использовать быстрый DNS
   DNS_SERVER="8.8.8.8"
   ```

3. **Обновить списки:**
   ```bash
   /opt/bin/unblock_ipset.sh
   ```

---

## 📝 Чек-лист проверки

### Быстрая проверка (30 сек):

- [ ] `ps | grep xray` — процесс запущен
- [ ] `netstat -tlnp | grep 31964` — порт слушается
- [ ] `curl -I https://www.youtube.com` — YouTube открывается

### Подробная проверка (2 мин):

- [ ] `ipset list unblockvless | grep -c "^[0-9]"` — IP в списке
- [ ] `iptables -t nat -L PREROUTING -nv` — правила есть
- [ ] `nslookup youtube.com 8.8.8.8` — DNS работает
- [ ] `/opt/etc/init.d/S24xray status` — сервис активен

---

## 🧪 Автоматическая диагностика

### Скрипт проверки:

```bash
#!/bin/sh
# /opt/bin/check_vless.sh

echo "=== Проверка VLESS ==="
echo ""

# 1. Процесс
echo "1. Процесс Xray:"
ps | grep -E 'xray|vless' | grep -v grep | head -1
if [ $? -eq 0 ]; then
    echo "   ✅ OK"
else
    echo "   ❌ НЕ ЗАПУЩЕН"
fi
echo ""

# 2. Порт
echo "2. Порт 31964:"
netstat -tlnp | grep 31964 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Слушается"
else
    echo "   ❌ НЕ СЛУШАЕТСЯ"
fi
echo ""

# 3. ipset
echo "3. IP в unblockvless:"
count=$(ipset list unblockvless 2>/dev/null | grep -c "^[0-9]" || echo 0)
if [ "$count" -gt 0 ]; then
    echo "   ✅ $count IP"
else
    echo "   ❌ ПУСТО"
fi
echo ""

# 4. YouTube
echo "4. Доступ к YouTube:"
curl -I -s --connect-timeout 5 https://www.youtube.com | grep "HTTP" > /dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ ОТКРЫВАЕТСЯ"
else
    echo "   ❌ НЕ ДОСТУПЕН"
fi
echo ""

# 5. DNS
echo "5. DNS:"
nslookup youtube.com 8.8.8.8 2>/dev/null | grep "Address" > /dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ РАБОТАЕТ"
else
    echo "   ❌ НЕ РАБОТАЕТ"
fi
echo ""

echo "=== Готово ==="
```

**Запуск:**
```bash
chmod +x /opt/bin/check_vless.sh
/opt/bin/check_vless.sh
```

---

## 📊 Интерпретация результатов

### Всё работает ✅

```
✅ Процесс запущен
✅ Порт слушается
✅ 17 IP в unblockvless
✅ YouTube открывается
✅ DNS работает
```

**Действия:** Никаких, всё работает!

---

### Частично работает ⚠️

```
✅ Процесс запущен
✅ Порт слушается
❌ ПУСТО (ipset)
✅ YouTube открывается
✅ DNS работает
```

**Действия:**
```bash
/opt/bin/unblock_ipset.sh
```

---

### Не работает ❌

```
❌ НЕ ЗАПУЩЕН
❌ НЕ СЛУШАЕТСЯ
❌ ПУСТО
❌ НЕ ДОСТУПЕН
❌ НЕ РАБОТАЕТ
```

**Действия:**
```bash
# 1. Проверка конфига
cat /opt/etc/xray/config.json

# 2. Запуск Xray
/opt/etc/init.d/S24xray start

# 3. Обновление списков
/opt/bin/unblock_ipset.sh

# 4. Проверка логов
logread | grep xray | tail -20
```

---

## 🔗 Дополнительные ресурсы

- [Официальная документация Xray](https://xtls.github.io/)
- [VLESS протокол](https://github.com/XTLS/Xray-core/discussions)
- [Диагностика в боте](#сервисное-меню)

---

**Обновлено:** 10 марта 2026 г.  
**Автор:** bypass_keenetic team
