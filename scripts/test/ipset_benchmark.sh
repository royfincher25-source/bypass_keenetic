#!/bin/sh
# =============================================================================
# ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ IPSET
# =============================================================================
# Замеряет время выполнения для разных конфигураций
# =============================================================================

TAG="ipset_benchmark"
DNS_CACHE_DIR="/tmp/dns_cache"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ IPSET                           ║"
echo "╚══════════════════════════════════════════════════════════╝"

# Проверка списков
echo ""
echo "📊 Статистика списков:"
total_domains=0
for file in /opt/etc/unblock/*.txt; do
    [ -f "$file" ] || continue
    name=$(basename "$file")
    domains=$(grep -vE '^#|^[0-9]|^$' "$file" 2>/dev/null | wc -l)
    total_domains=$((total_domains + domains))
    echo "  $name: $domains доменов"
done
echo "  ВСЕГО: $total_domains доменов"

# Проверка DNS
echo ""
echo "🔍 Проверка DNS:"

echo -n "  Google DNS (8.8.8.8): "
test_google=$(dig +short google.com @8.8.8.8 +time=2 +tries=1 2>/dev/null | head -1)
if [ -n "$test_google" ]; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

echo -n "  Local DNS (40500): "
test_local=$(dig +short google.com @localhost -p 40500 +time=2 +tries=1 2>/dev/null | head -1)
if [ -n "$test_local" ]; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

# Тест 1: Очистка кэша
echo ""
echo "🧹 Очистка кэша DNS..."
rm -rf "$DNS_CACHE_DIR"/*
echo "  ✅ Кэш очищен"

# Тест 2: Замер времени
echo ""
echo "⏱️  Замер времени выполнения:"
start_time=$(date +%s)

if [ -x /opt/bin/unblock_ipset.sh ]; then
    /opt/bin/unblock_ipset.sh
    exit_code=$?
else
    echo "  ❌ Скрипт не найден или не исполняемый"
    exit_code=1
fi

end_time=$(date +%s)
duration=$((end_time - start_time))

echo ""
echo "══════════════════════════════════════════════════════════"
if [ $exit_code -eq 0 ]; then
    echo "✅ ТЕСТ ЗАВЕРШЁН: ${duration} секунд"
else
    echo "❌ ТЕСТ ПРЕРВАН: код ошибки $exit_code"
fi
echo "══════════════════════════════════════════════════════════"

# Статистика по кэшу
if [ -d "$DNS_CACHE_DIR" ]; then
    cache_count=$(ls -1 "$DNS_CACHE_DIR"/*.cache 2>/dev/null | wc -l)
    cache_size=$(du -sh "$DNS_CACHE_DIR" 2>/dev/null | cut -f1)
    echo ""
    echo "📦 Кэш DNS: $cache_count файлов, $cache_size"
fi

# Логи
echo ""
echo "📝 Последние логи:"
logread | grep unblock_ipset | tail -5

echo ""
echo "💡 Рекомендации:"
if [ $duration -gt 120 ]; then
    echo "  ⚠️  Время > 2 минут - уменьшите MAX_PARALLEL до 4"
elif [ $duration -gt 60 ]; then
    echo "  ⚠️  Время > 1 минуты - проверьте скорость DNS"
else
    echo "  ✅  Время в норме"
fi

if [ $total_domains -gt 1000 ]; then
    echo "  ⚠️  Много доменов (>1000) - рассмотрите фильтрацию"
fi

echo ""
