# 🚀 Отключение IPv6 на Keenetic

**Дата:** 10 марта 2026 г.

---

## 📋 Установка

### 1. Загрузить скрипт на роутер:

```bash
curl -o /opt/etc/ndm/100-disable-ipv6.sh \
  https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/scripts/fixes/disable_ipv6.sh

chmod +x /opt/etc/ndm/100-disable-ipv6.sh
```

### 2. Запустить:

```bash
/opt/etc/ndm/100-disable-ipv6.sh start
```

### 3. Проверить:

```bash
# Не должно быть inet6
ip -6 addr show | grep inet6

# Должно быть:
# net.ipv6.conf.all.disable_ipv6 = 1
sysctl net.ipv6.conf.all.disable_ipv6
```

### 4. Перезагрузить роутер:

```bash
reboot
```

После перезагрузки скрипт выполнится автоматически!

---

## 🧪 Проверка работы Telegram

```bash
# Тест
curl -4 -I https://web.telegram.org

# Ожидаемый вывод:
# HTTP/1.1 200 OK
```

---

## ⚠️ Если не помогло

### Очистите кэш DNS на ПК:

**Windows:**
```cmd
ipconfig /flushdns
```

**Chrome/Edge:**
```
chrome://net-internals/#dns → Clear host cache
```

**Firefox:**
```
about:networking#dns → Clear DNS Cache
```

---

## 📝 Альтернатива: Веб-интерфейс

Если скрипт не работает, попробуйте через веб-интерфейс Keenetic:

1. Откройте `http://192.168.1.1`
2. **Настройки → Сетевые правила → IPv6**
3. **Отключите IPv6**
4. **Сохраните**
5. **Перезагрузите**

---

**Файл:** `scripts/fixes/disable_ipv6.sh`  
**Версия:** 1.0
