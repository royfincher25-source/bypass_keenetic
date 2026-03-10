#!/bin/sh
# =============================================================================
# ПРОВЕРКА РАБОТОСПОСОБНОСТИ VLESS
# =============================================================================

echo "========================================"
echo "  ПРОВЕРКА VLESS"
echo "========================================"
echo ""

# 1. Процесс Xray
echo "1. Процесс Xray:"
xray_proc=$(ps | grep -E 'xray|vless' | grep -v grep | head -1)
if [ -n "$xray_proc" ]; then
    echo "   ✅ ЗАПУЩЕН"
    echo "   $xray_proc"
else
    echo "   ❌ НЕ ЗАПУЩЕН"
fi
echo ""

# 2. Порт (можно изменить через переменную)
VLESS_PORT="${VLESS_PORT:-10810}"
echo "2. Порт $VLESS_PORT:"
port_check=$(netstat -tlnp 2>/dev/null | grep $VLESS_PORT)
if [ -n "$port_check" ]; then
    echo "   ✅ Слушается"
    echo "   $port_check"
else
    echo "   ❌ НЕ СЛУШАЕТСЯ"
fi
echo ""

# 3. ipset
echo "3. IP в unblockvless:"
ip_count=$(ipset list unblockvless 2>/dev/null | grep -c "^[0-9]" || echo 0)
if [ "$ip_count" -gt 0 ]; then
    echo "   ✅ $ip_count IP"
else
    echo "   ❌ ПУСТО"
fi
echo ""

# 4. Telegram (web)
echo "4. Доступ к Telegram:"
telegram_test=$(curl -I -s --connect-timeout 5 https://web.telegram.org 2>/dev/null | head -1)
if [ -n "$telegram_test" ]; then
    echo "   ✅ ОТКРЫВАЕТСЯ"
    echo "   $telegram_test"
else
    echo "   ❌ НЕ ДОСТУПЕН"
fi
echo ""

# 5. DNS
echo "5. DNS:"
dns_test=$(nslookup youtube.com 8.8.8.8 2>/dev/null | grep -i 'address' | grep -v '8.8.8.8' | head -1)
if [ -n "$dns_test" ]; then
    echo "   ✅ РАБОТАЕТ"
    echo "   $dns_test"
else
    echo "   ❌ НЕ РАБОТАЕТ"
fi
echo ""

# 6. Сервис
echo "6. Сервис Xray:"
if [ -x /opt/etc/init.d/S24xray ]; then
    s24xray_status=$(/opt/etc/init.d/S24xray status 2>&1)
    if echo "$s24xray_status" | grep -q "running\|started\|running\|already"; then
        echo "   ✅ АКТИВЕН"
    else
        echo "   ❌ НЕ АКТИВЕН"
    fi
else
    echo "   ⚠️ СКРИПТ НЕ НАЙДЕН"
fi
echo ""

echo "========================================"
echo "  РЕКОМЕНДАЦИИ"
echo "========================================"
echo ""

if [ -z "$xray_proc" ]; then
    echo "❌ Xray не запущен:"
    echo "   /opt/etc/init.d/S24xray start"
    echo ""
fi

if [ "$ip_count" -eq 0 ]; then
    echo "⚠️  ipset пуст:"
    echo "   /opt/bin/unblock_ipset.sh"
    echo ""
fi

if [ -z "$telegram_test" ]; then
    echo "❌ Telegram не доступен:"
    echo "   1. Проверьте DNS"
    echo "   2. Обновите списки: /opt/bin/unblock_ipset.sh"
    echo "   3. Проверьте конфиг: /opt/etc/xray/config.json"
    echo ""
fi

echo "========================================"
