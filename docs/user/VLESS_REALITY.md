# VLESS + REALITY — Полная инструкция

**Версия:** 1.0
**Дата:** 14 марта 2026 г.

---

## 🎯 Что такое REALITY?

**REALITY** — это современный протокол обхода блокировок от Xray Project (2023).

### Преимущества:

✅ **Полная невидимость** — маскировка под legitimate HTTPS
✅ **Не нужен свой домен** — используется чужой сертификат (microsoft.com, apple.com)
✅ **Автоматическая ротация** — динамическая смена параметров
✅ **Высокая скорость** — до 300+ Mbps на KN-1212
✅ **Устойчивость к DPI** — обход глубокой инспекции трафика

---

## 📋 Требования

### Сервер (VPS):

- **OS:** Linux (Debian 11+, Ubuntu 20.04+)
- **CPU:** 1 ядро
- **RAM:** 256 MB
- **Xray:** версии 1.8.0+

### Клиент (Роутер):

- **Keenetic:** KN-1212 Giga или новее
- **Xray:** версии 1.8.0+
- **Бот:** версии 3.5.51+

---

## 🔧 Настройка сервера

### Шаг 1: Установка Xray

```bash
# На VPS
bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
```

### Шаг 2: Генерация ключей

```bash
# Сгенерировать ключи
cd /usr/local/etc/xray
xray x25519

# Результат:
# PrivateKey: <сохраните в секрете>
# PublicKey: <добавьте в конфиг клиента>
```

### Шаг 3: Генерация ShortId (опционально)

```bash
openssl rand -hex 8
# Результат: 1234567890abcdef
```

### Шаг 4: Конфигурация сервера

```json
{
  "inbounds": [{
    "port": 443,
    "protocol": "vless",
    "settings": {
      "clients": [{
        "id": "UUID-CLIENTA",
        "flow": "xtls-rprx-vision"
      }]
    },
    "streamSettings": {
      "network": "tcp",
      "security": "reality",
      "realitySettings": {
        "show": false,
        "dest": "www.microsoft.com:443",
        "xver": 0,
        "serverNames": ["www.microsoft.com"],
        "privateKey": "PRIVATE_KEY_ОТ_ШАГА_2",
        "shortIds": ["", "1234567890abcdef"]
      }
    }
  }],
  "outbounds": [{
    "protocol": "freedom"
  }]
}
```

### Шаг 5: Перезапуск Xray

```bash
systemctl restart xray
systemctl status xray
```

---

## 📱 Настройка клиента (бот)

### Шаг 1: Получение ключа

Ключ REALITY имеет формат:

```
vless://UUID@SERVER_IP:443?security=reality&pbk=PUBLIC_KEY&sid=SHORT_ID&fp=chrome&sni=www.microsoft.com
```

**Параметры:**
- `UUID` — идентификатор клиента (из конфига сервера)
- `SERVER_IP` — IP вашего VPS
- `pbk` — PublicKey (из шага 2)
- `sid` — ShortId (из шага 3, опционально)
- `fp` — fingerprint (chrome, firefox, safari)
- `sni` — домен для маскировки

### Шаг 2: Отправка боту

1. Откройте бота в Telegram
2. Перейдите: `⚙️ Сервис` → `🔑 Ключи и мосты` → `VLESS`
3. Отправьте ключ в формате `vless://...`

### Шаг 3: Проверка

```bash
# На роутере
ps | grep xray
curl -I https://youtube.com

# Должно работать!
```

---

## 🔍 Диагностика

### Проверка подключения к серверу

```bash
# На роутере
ping SERVER_IP

# Проверка порта
telnet SERVER_IP 443
```

### Проверка Xray

```bash
# Статус
ps | grep xray

# Логи
tail -50 /opt/etc/xray/error.log
```

### Тест скорости

```bash
# Speedtest
curl -o /dev/null http://ipv4.download.thinkbroadband.com/10MB.zip

# YouTube
curl -I https://youtube.com
```

---

## ⚠️ Возможные проблемы

### Ошибка: "Invalid publicKey"

**Причина:** Неверный формат ключа

**Решение:**
```bash
# Проверить ключ
echo "PUBLIC_KEY" | base64 -d | wc -c
# Должно быть 32 байта
```

### Ошибка: "Connection refused"

**Причина:** Xray не запущен на сервере

**Решение:**
```bash
systemctl start xray
systemctl enable xray
```

### Ошибка: "TLS handshake failed"

**Причина:** Неправильный SNI или dest

**Решение:**
- Проверьте `serverNames` в конфиге сервера
- Убедитесь что `dest` указывает на работающий HTTPS сайт

---

## 📊 Производительность

### Keenetic KN-1212:

| Метрика | Значение |
|---------|----------|
| **Скорость** | 200-300 Mbps |
| **CPU** | 30-40% |
| **RAM** | 80-100 MB |
| **Пинг** | +10-15 ms |

### YouTube:

- ✅ 4K HDR — стабильно
- ✅ 8K — работает
- ✅ Live — без задержек

---

## 🔗 Ссылки

- [Xray Project](https://github.com/XTLS/Xray-core)
- [REALITY Documentation](https://www.xrayui.com/)
- [Генерация ключей](../scripts/reality/README.md)
