#!/bin/sh
# =============================================================================
# БЫСТРЫЙ ТЕСТОВЫЙ СКРИПТ IPSET
# =============================================================================

TAG="unblock_ipset_test"

logger -t "$TAG" "🚀 Запуск теста"

# Проверка DNS
echo "=== Проверка DNS ==="
dig +short google.com @localhost -p 40500
if [ $? -ne 0 ]; then
    echo "❌ DNS на порту 40500 НЕ доступен!"
    logger -t "$TAG" "❌ DNS на порту 40500 НЕ доступен"
    exit 1
fi
echo "✅ DNS доступен"

# Проверка ipset
echo ""
echo "=== Проверка ipset ==="
if ! command -v ipset >/dev/null 2>&1; then
    echo "❌ ipset не установлен!"
    exit 1
fi
echo "✅ ipset установлен"

# Создание/очистка test ipset
echo ""
echo "=== Создание test ipset ==="
ipset create test_unblock hash:net -exist 2>/dev/null
ipset flush test_unblock 2>/dev/null
echo "✅ test_unblock создан"

# Добавление тестовых IP
echo ""
echo "=== Добавление тестовых IP ==="
ipset -exist add test_unblock "8.8.8.8"
ipset -exist add test_unblock "1.1.1.1"
ipset -exist add test_unblock "142.250.0.0/16"
echo "✅ Добавлено 3 IP"

# Проверка
echo ""
echo "=== Результат ==="
ipset list test_unblock
echo ""
echo "Количество IP: $(ipset list test_unblock 2>/dev/null | grep -c '^[0-9]' || echo 0)"

logger -t "$TAG" "✅ Тест завершён"
echo ""
echo "✅ Тест завершён успешно!"
