# Генерация ключей REALITY

## На сервере (VPS):

```bash
# 1. Сгенерировать ключи
./generate_reality_keys.sh www.microsoft.com

# 2. Скопировать PrivateKey и PublicKey
# 3. Настроить Xray сервер
```

## Настройка сервера (пример):

```json
{
  "inbounds": [{
    "protocol": "vless",
    "settings": {
      "clients": [{"id": "UUID", "flow": "xtls-rprx-vision"}]
    },
    "streamSettings": {
      "network": "tcp",
      "security": "reality",
      "realitySettings": {
        "dest": "www.microsoft.com:443",
        "serverNames": ["www.microsoft.com"],
        "privateKey": "PRIVATE_KEY",
        "shortIds": ["", "SHORT_ID"]
      }
    }
  }]
}
```

## Клиент получает:
- PublicKey
- ShortId (опционально)
- Server IP и порт
- UUID клиента
