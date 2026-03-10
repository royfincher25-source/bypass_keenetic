#!/bin/sh
# =============================================================================
# ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ IPSET
# =============================================================================
# Совместимо с sh (Almquist shell)
# =============================================================================

echo "========================================"
echo "  ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ IPSET"
echo "========================================"
echo ""

# Проверка списков
echo "Статистика списков:"
total_domains=0
for file in /opt/etc/unblock/*.txt; do
    [ -f "$file" ] || continue
    name=$(basename "$file")
    domains=$(grep -vE '^#|^[0-9]|^$' "$file" 2>/dev/null | wc -l)
    total_domains=$((total_domains + domains))
    echo "  $name: $domains доменов"
done
echo "  ВСЕГО: $total_domains доменов"
echo ""

# Проверка DNS
echo "Проверка DNS:"

echo -n "  Google DNS (8.8.8.8): "
test_google=$(nslookup google.com 8.8.8.8 2>/dev/null | grep -i 'address' | grep -v '8\.8\.8\.8' | head -1)
if [ -n "$test_google" ]; then
    echo "OK"
else
    echo "FAIL"
fi
echo ""

# Тест: Замер времени
echo "Замер времени выполнения:"
start_time=$(date +%s)

if [ -x /opt/bin/unblock_ipset.sh ]; then
    /opt/bin/unblock_ipset.sh
    exit_code=$?
else
    echo "  Скрипт не найден или не исполняемый"
    exit_code=1
fi

end_time=$(date +%s)
duration=$((end_time - start_time))

echo ""
echo "========================================"
if [ $exit_code -eq 0 ]; then
    echo "ТЕСТ ЗАВЕРШЁН: ${duration} секунд"
else
    echo "ТЕСТ ПРЕРВАН: код ошибки $exit_code"
fi
echo "========================================"

# Статистика ipset
echo ""
echo "Статистика ipset:"
for ipset in unblocksh unblocktor unblockvless unblocktroj; do
    if ipset list "$ipset" -n 2>/dev/null | grep -q "^$ipset$"; then
        count=$(ipset list "$ipset" 2>/dev/null | grep -c "^[0-9]")
        echo "  $ipset: $count IP"
    else
        echo "  $ipset: не создан"
    fi
done

echo ""
echo "Рекомендации:"
if [ $duration -gt 120 ]; then
    echo "  Время > 2 минут - уменьшите MAX_PARALLEL до 10"
elif [ $duration -gt 60 ]; then
    echo "  Время > 1 минуты - проверьте DNS"
else
    echo "  Время в норме"
fi

if [ $total_domains -gt 1000 ]; then
    echo "  Много доменов (>1000) - рассмотрите фильтрацию"
fi

echo ""
