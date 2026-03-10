#!/bin/sh
# =============================================================================
# БЫСТРЫЙ СКРИПТ ЗАПОЛНЕНИЯ IPSET (v3.4.4)
# =============================================================================
# Упрощён для Entware:
# - Прямая параллельная обработка через xargs -P
# - Без кэширования (домены часто меняются)
# - Минимум накладных расходов
# =============================================================================

TAG="unblock_ipset"
DNS_SERVER="8.8.8.8"
DNS_PORT="53"
MAX_PARALLEL=20

# Фильтрация локальных IP
cut_local() {
    grep -vE '^0\.|^127\.|^10\.|^172\.16\.|^192\.168\.|^::1$'
}

# Проверка DNS
check_dns() {
    test_dns=$(dig +short google.com @"$DNS_SERVER" -p "$DNS_PORT" +time=2 +tries=1 2>/dev/null | head -1)
    if [ -z "$test_dns" ]; then
        logger -t "$TAG" "❌ DNS НЕ доступен"
        echo "❌ DNS НЕ доступен" >&2
        return 1
    fi
    return 0
}

# Обработка списка
process_list() {
    ipset_name="$1"
    list_file="$2"
    temp_file="/tmp/ipset_${ipset_name}_$$.txt"
    
    if [ ! -f "$list_file" ]; then
        logger -t "$TAG" "⚠️ Нет файла: $list_file"
        return 1
    fi
    
    # Создаём/очищаем ipset
    ipset create "$ipset_name" hash:net family inet hashsize 4096 maxelem 65536 -exist 2>/dev/null
    ipset flush "$ipset_name" 2>/dev/null
    
    # Извлекаем домены (не IP)
    grep -vE '^#|^[0-9]|^$' "$list_file" > "$temp_file.domains" 2>/dev/null
    domain_count=$(wc -l < "$temp_file.domains")
    
    if [ "$domain_count" -eq 0 ]; then
        logger -t "$TAG" "⊘ $ipset_name: нет доменов"
        rm -f "$temp_file.domains" "$temp_file.ips"
        return 0
    fi
    
    # Параллельный DNS
    xargs -P$MAX_PARALLEL -I{} sh -c 'dig +short {} @'"$DNS_SERVER"' -p '"$DNS_PORT"' +time=2 +tries=1 2>/dev/null' < "$temp_file.domains" | \
        grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut_local > "$temp_file.ips"
    
    # Добавляем IP из файла (CIDR, диапазоны)
    grep -E '^[0-9]' "$list_file" | cut_local >> "$temp_file.ips" 2>/dev/null
    
    # Загрузка в ipset
    ip_count=$(sort -u "$temp_file.ips" | wc -l)
    sort -u "$temp_file.ips" | sed "s/^/add $ipset_name /" | ipset restore -! 2>/dev/null
    
    logger -t "$TAG" "✅ $ipset_name: доменов=$domain_count, IP=$ip_count"
    
    rm -f "$temp_file.domains" "$temp_file.ips"
}

# =============================================================================
# ОСНОВНАЯ ЧАСТЬ
# =============================================================================

START_TIME=$(date +%s)
logger -t "$TAG" "🚀 Запуск (параллельно: $MAX_PARALLEL)"

check_dns || exit 1

process_list "unblocksh" "/opt/etc/unblock/shadowsocks.txt"
process_list "unblocktor" "/opt/etc/unblock/tor.txt"
process_list "unblockvless" "/opt/etc/unblock/vless.txt"
process_list "unblocktroj" "/opt/etc/unblock/trojan.txt"

# VPN списки
for vpn_file in /opt/etc/unblock/vpn-*.txt; do
    [ -f "$vpn_file" ] || continue
    vpn_name=$(basename "$vpn_file" .txt)
    ipset_name="unblock${vpn_name#vpn-}"
    process_list "$ipset_name" "$vpn_file"
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "✅ Завершено за ${DURATION}c"
echo "📊 Статистика:"
for ipset in unblocksh unblocktor unblockvless unblocktroj; do
    if ipset list "$ipset" -n 2>/dev/null | grep -q "^$ipset$"; then
        count=$(ipset list "$ipset" 2>/dev/null | grep -c "^[0-9]")
        echo "  $ipset: $count IP"
    else
        echo "  $ipset: 0 IP"
    fi
done

logger -t "$TAG" "📊 Итог: ${DURATION}c"
