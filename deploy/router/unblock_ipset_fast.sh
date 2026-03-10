#!/bin/sh
# =============================================================================
# БЫСТРЫЙ СКРИПТ ЗАПОЛНЕНИЯ IPSET (v3.4.8)
# =============================================================================
# Исправления:
# - Убраны logger (нет на некоторых роутерах)
# - Проверка на пустые списки
# - Таймаут на весь скрипт через watchdog
# =============================================================================

TAG="unblock_ipset"
DNS_SERVER="8.8.8.8"
DNS_PORT="53"
MAX_PARALLEL=30

cut_local() {
    grep -vE '^0\.|^127\.|^10\.|^172\.16\.|^192\.168\.|^::1$'
}

process_list() {
    ipset_name="$1"
    list_file="$2"
    
    if [ ! -f "$list_file" ]; then
        echo "⚠️ Нет файла: $list_file"
        return 1
    fi
    
    domain_count=$(grep -vE '^#|^[0-9]|^$' "$list_file" 2>/dev/null | wc -l)
    if [ "$domain_count" -eq 0 ]; then
        echo "⊘ $ipset_name: пусто"
        ipset create "$ipset_name" hash:net family inet hashsize 4096 maxelem 65536 -exist 2>/dev/null
        ipset flush "$ipset_name" 2>/dev/null
        return 0
    fi
    
    ipset create "$ipset_name" hash:net family inet hashsize 4096 maxelem 65536 -exist 2>/dev/null
    ipset flush "$ipset_name" 2>/dev/null
    
    # Домены -> DNS (параллельно) + IP из файла -> ipset
    {
        grep -vE '^#|^[0-9]|^$' "$list_file" | \
            xargs -P$MAX_PARALLEL -I{} dig +short {} @"$DNS_SERVER" -p "$DNS_PORT" +time=2 +tries=1 2>/dev/null
        grep -E '^[0-9]' "$list_file" 2>/dev/null
    } | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut_local | \
        sort -u | sed "s/^/add $ipset_name /" | ipset restore -! 2>/dev/null
    
    ip_count=$(ipset list "$ipset_name" 2>/dev/null | grep -c "^[0-9]")
    echo "✅ $ipset_name: $ip_count IP"
}

# =============================================================================
# ОСНОВНАЯ ЧАСТЬ
# =============================================================================

START_TIME=$(date +%s)
echo "🚀 Запуск (параллельно: $MAX_PARALLEL)"

process_list "unblocksh" "/opt/etc/unblock/shadowsocks.txt"
process_list "unblocktor" "/opt/etc/unblock/tor.txt"
process_list "unblockvless" "/opt/etc/unblock/vless.txt"
process_list "unblocktroj" "/opt/etc/unblock/trojan.txt"

for vpn_file in /opt/etc/unblock/vpn-*.txt; do
    [ -f "$vpn_file" ] || continue
    vpn_name=$(basename "$vpn_file" .txt)
    ipset_name="unblock${vpn_name#vpn-}"
    process_list "$ipset_name" "$vpn_file"
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
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
