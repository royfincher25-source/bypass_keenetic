#!/bin/sh
# =============================================================================
# ГЕНЕРАЦИЯ КЛЮЧЕЙ REALITY ДЛЯ XRAY
# =============================================================================
# Использование: ./generate_reality_keys.sh [domain]
# =============================================================================

# Проверка зависимостей
if ! command -v xray >/dev/null 2>&1; then
    echo "❌ Ошибка: xray не найден. Установите Xray-core."
    exit 1
fi

if ! command -v openssl >/dev/null 2>&1; then
    echo "❌ Ошибка: openssl не найден."
    exit 1
fi

DOMAIN=${1:-"www.microsoft.com"}

# Валидация домена
if ! echo "$DOMAIN" | grep -qE '^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z]{2,})+$'; then
    echo "❌ Ошибка: неверный формат домена: $DOMAIN"
    exit 1
fi

echo "=== Генерация ключей REALITY ==="
echo "Domain: $DOMAIN"
echo ""
echo "⚠️ ВНИМАНИЕ: PrivateKey должен храниться в секрете!"
echo "   Не передавайте его никому и не коммитьте в git!"
echo ""

# Генерация ключей через Xray
echo "--- X25519 Key Pair ---"
xray x25519

echo ""
echo "=== Результат ==="
echo "PrivateKey: <сохраните в секрете>"
echo "PublicKey: <добавьте в конфиг клиента>"
echo ""
echo "ShortId (опционально):"
openssl rand -hex 8

echo ""
echo "=== Пример конфигурации сервера ==="
cat << EOF
{
  "inbounds": [{
    "protocol": "vless",
    "settings": {
      "clients": [{
        "id": "$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid)",
        "flow": "xtls-rprx-vision"
      }]
    },
    "streamSettings": {
      "network": "tcp",
      "security": "reality",
      "realitySettings": {
        "show": false,
        "dest": "$DOMAIN:443",
        "xver": 0,
        "serverNames": ["$DOMAIN"],
        "privateKey": "<ваш PrivateKey>",
        "shortIds": ["", "<ваш ShortId>"]
      }
    }
  }]
}
EOF
