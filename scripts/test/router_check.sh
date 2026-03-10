#!/bin/sh
# =============================================================================
# ДИАГНОСТИКА РОУТЕРА ПЕРЕД ЗАПУСКОМ
# =============================================================================
# Совместимо с sh (Almquist shell)
# =============================================================================

echo "========================================"
echo "  ДИАГНОСТИКА РОУТЕРА"
echo "========================================"
echo ""

# 1. Проверка timeout
echo "1. Проверка команды timeout:"
if timeout --help >/dev/null 2>&1; then
    echo "   ✅ timeout доступен"
else
    echo "   ❌ timeout НЕ доступен"
fi
echo ""

# 2. Проверка DNS на порту 40500
echo "2. Проверка DNS порт 40500:"
test_dns_40500=$(dig +short google.com @localhost -p 40500 2>/dev/null | head -1)
if [ -n "$test_dns_40500" ]; then
    echo "   ✅ DNS 40500: $test_dns_40500"
else
    echo "   ❌ DNS 40500: НЕ доступен"
fi
echo ""

# 3. Проверка DNS Google
echo "3. Проверка DNS 8.8.8.8:"
test_dns_google=$(dig +short google.com @8.8.8.8 +time=2 +tries=1 2>/dev/null | head -1)
if [ -n "$test_dns_google" ]; then
    echo "   ✅ DNS 8.8.8.8: $test_dns_google"
else
    echo "   ❌ DNS 8.8.8.8: НЕ доступен"
fi
echo ""

# 4. Количество доменов в списках
echo "4. Статистика списков:"
if [ -d /opt/etc/unblock ]; then
    for file in /opt/etc/unblock/*.txt; do
        [ -f "$file" ] || continue
        name=$(basename "$file")
        total=$(wc -l < "$file" 2>/dev/null)
        domains=$(grep -vE '^#|^[0-9]|^$' "$file" 2>/dev/null | wc -l)
        echo "   $name: всего=$total, доменов=$domains"
    done
else
    echo "   ⚠️ Директория /opt/etc/unblock не найдена"
fi
echo ""

# 5. Проверка памяти
echo "5. Доступная память:"
if free -m >/dev/null 2>&1; then
    free -m | grep -E '^Mem:'
else
    echo "   ⚠️ Команда free недоступна"
fi
echo ""

# 6. Проверка ipset
echo "6. Версия ipset:"
if ipset --version >/dev/null 2>&1; then
    ipset --version | head -1
else
    echo "   ❌ ipset НЕ доступен"
fi
echo ""

echo "========================================"
echo "  БЫСТРЫЙ ТЕСТ"
echo "========================================"
echo ""
echo "Команды для запуска:"
echo "  rm -rf /tmp/dns_cache/*"
echo "  time /opt/bin/unblock_ipset.sh"
echo "  logread | grep unblock_ipset | tail -10"
echo ""
