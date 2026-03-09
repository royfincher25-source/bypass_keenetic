#!/bin/sh
# =============================================================================
# СКРИПТ ЗАПОЛНЕНИЯ IPSET (ИСПРАВЛЕННЫЙ)
# =============================================================================
# Исправления:
# - Собственный таймаут для DNS запросов (без команды timeout)
# - Обработка ошибок DNS
# - Логирование процесса
# =============================================================================

TAG="unblock_ipset"

# Функция для фильтрации локальных IP
cut_local() {
    grep -vE 'localhost|^0\.|^127\.|^10\.|^172\.16\.|^192\.168\.|^::|^fc..:|^fd..:|^fe..:'
}

# DNS запрос с собственным таймаутом (3 секунды)
dig_with_timeout() {
    local domain="$1"
    local result=""
    
    # Запускаем dig в фоне
    (dig +short "$domain" @localhost -p 40500 2>/dev/null) > /tmp/dns_result_$$ &
    local PID=$!
    
    # Ждём максимум 3 секунды
    local count=0
    while [ $count -lt 3 ]; do
        sleep 1
        count=$((count + 1))
        
        # Проверяем, завершился ли процесс
        if ! kill -0 $PID 2>/dev/null; then
            wait $PID
            result=$(cat /tmp/dns_result_$$ 2>/dev/null)
            rm -f /tmp/dns_result_$$
            echo "$result"
            return 0
        fi
    done
    
    # Убиваем процесс если ещё работает
    kill $PID 2>/dev/null
    wait $PID 2>/dev/null
    rm -f /tmp/dns_result_$$
    
    # Возвращаем пустоту (таймаут)
    echo ""
    return 1
}

# Обработка одного файла со списком
process_list() {
    local ipset_name="$1"
    local list_file="$2"
    local count=0
    local dns_count=0
    local error_count=0
    
    if [ ! -f "$list_file" ]; then
        logger -t "$TAG" "⚠️ Файл не найден: $list_file"
        return 1
    fi
    
    # Создаём/очищаем ipset
    ipset create "$ipset_name" hash:net -exist 2>/dev/null
    ipset flush "$ipset_name" 2>/dev/null
    logger -t "$TAG" "🔄 Начало: $list_file → $ipset_name"
    
    while read -r line || [ -n "$line" ]; do
        # Пропускаем пустые строки и комментарии
        [ -z "$line" ] && continue
        [ "${line#?}" = "#" ] && continue
        
        count=$((count + 1))
        
        # CIDR
        cidr=$(echo "$line" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}' | cut_local)
        if [ -n "$cidr" ]; then
            ipset -exist add "$ipset_name" "$cidr" 2>/dev/null
            continue
        fi
        
        # Диапазон
        range=$(echo "$line" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}-[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut_local)
        if [ -n "$range" ]; then
            ipset -exist add "$ipset_name" "$range" 2>/dev/null
            continue
        fi
        
        # Одиночный IP
        addr=$(echo "$line" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut_local)
        if [ -n "$addr" ]; then
            ipset -exist add "$ipset_name" "$addr" 2>/dev/null
            continue
        fi
        
        # Домен → DNS запрос с таймаутом
        dns_count=$((dns_count + 1))
        ips=$(dig_with_timeout "$line")
        
        if [ -n "$ips" ]; then
            echo "$ips" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | while read -r ip; do
                ipset -exist add "$ipset_name" "$ip" 2>/dev/null
            done
        else
            error_count=$((error_count + 1))
            logger -t "$TAG" "⚠️ DNS таймаут: $line"
        fi
        
    done < "$list_file"
    
    # Статистика
    local final_count=$(ipset list "$ipset_name" 2>/dev/null | grep -c "^[0-9]" || echo 0)
    logger -t "$TAG" "✅ Завершено: $ipset_name (строк: $count, DNS: $dns_count, ошибок: $error_count, IP: $final_count)"
}

# =============================================================================
# ОСНОВНАЯ ЧАСТЬ
# =============================================================================

logger -t "$TAG" "🚀 Запуск скрипта ipset"

# Проверка DNS перед запуском
logger -t "$TAG" "Проверка DNS..."
test_dns=$(dig_with_timeout "google.com")
if [ -z "$test_dns" ]; then
    logger -t "$TAG" "❌ DNS НЕ доступен на порту 40500!"
    echo "❌ DNS НЕ доступен на порту 40500!"
    exit 1
fi
logger -t "$TAG" "✅ DNS доступен"

# Обработка всех списков
process_list "unblocksh" "/opt/etc/unblock/shadowsocks.txt"
process_list "unblocktor" "/opt/etc/unblock/tor.txt"
process_list "unblockvless" "/opt/etc/unblock/vless.txt"
process_list "unblocktroj" "/opt/etc/unblock/trojan.txt"

# VPN списки
if ls -d /opt/etc/unblock/vpn-*.txt >/dev/null 2>&1; then
    for vpn_file in /opt/etc/unblock/vpn-*.txt; do
        vpn_name=$(basename "$vpn_file" .txt)
        ipset_name="unblock${vpn_name#vpn-}"
        process_list "$ipset_name" "$vpn_file"
    done
fi

logger -t "$TAG" "✅ Все списки обработаны"

# Итоговая статистика
logger -t "$TAG" "📊 Итоговая статистика:"
for ipset in unblocksh unblocktor unblockvless unblocktroj; do
    if ipset list "$ipset" -n 2>/dev/null | grep -q "^$ipset$"; then
        count=$(ipset list "$ipset" 2>/dev/null | grep -c "^[0-9]" || echo 0)
        logger -t "$TAG" "  $ipset: $count IP"
    fi
done

echo "✅ Скрипт завершён успешно!"
echo "📊 Статистика:"
for ipset in unblocksh unblocktor unblockvless unblocktroj; do
    if ipset list "$ipset" -n 2>/dev/null | grep -q "^$ipset$"; then
        count=$(ipset list "$ipset" 2>/dev/null | grep -c "^[0-9]" || echo 0)
        echo "  $ipset: $count IP"
    fi
done
