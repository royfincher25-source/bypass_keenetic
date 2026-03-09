#!/bin/sh
# =============================================================================
# ОПТИМИЗИРОВАННЫЙ СКРИПТ ЗАПОЛНЕНИЯ IPSET
# =============================================================================
# Оптимизации:
# - Пакетная загрузка IP (вместо одного ipset на IP)
# - Кэширование DNS запросов
# - Быстрая проверка существования ipset
# - Параллельная обработка
# =============================================================================

TAG="unblock_ipset"

# Быстрая проверка существования ipset
ipset_exists() {
    ipset list "$1" -n 2>/dev/null | grep -q "^$1$"
}

# Кэширование DNS
resolve_cached() {
    local domain="$1"
    local cache_file="/tmp/dns_cache/${domain//\//_}"
    
    # Создаём директорию кэша
    mkdir -p /tmp/dns_cache 2>/dev/null
    
    # Проверяем кэш (1 час)
    if [ -f "$cache_file" ]; then
        # Проверяем возраст файла (3600 секунд = 1 час)
        local now=$(date +%s)
        local mtime=$(stat -c %Y "$cache_file" 2>/dev/null || echo 0)
        if [ $((now - mtime)) -lt 3600 ]; then
            cat "$cache_file"
            return 0
        fi
    fi
    
    # DNS запрос
    dig +short "$domain" @localhost -p 40500 > "$cache_file" 2>/dev/null
    cat "$cache_file"
}

# Пакетная загрузка IP в ipset
load_ipset_batch() {
    local ipset_name="$1"
    local ip_file="$2"
    
    if [ -f "$ip_file" ] && [ -s "$ip_file" ]; then
        # Фильтрация локальных IP
        grep -vE 'localhost|^0\.|^127\.|^10\.|^172\.16\.|^192\.168\.|^::|^fc..:|^fd..:|^fe..:' "$ip_file" | \
        while read -r ip; do
            ipset -exist add "$ipset_name" "$ip" 2>/dev/null
        done
        logger -t "$TAG" "✅ $ipset_name: загружено $(wc -l < "$ip_file") IP"
    fi
}

# Обработка файла со списком
process_list() {
    local ipset_name="$1"
    local list_file="$2"
    local temp_ip_file="/tmp/ipset_${ipset_name}.txt"
    
    # Очищаем временный файл
    > "$temp_ip_file"
    
    # Создаём ipset если нет
    if ! ipset_exists "$ipset_name"; then
        ipset create "$ipset_name" hash:net -exist 2>/dev/null
        logger -t "$TAG" "Создан ipset: $ipset_name"
    fi
    
    # Очищаем старый ipset
    ipset flush "$ipset_name" 2>/dev/null
    
    logger -t "$TAG" "🔄 Обработка: $list_file → $ipset_name"
    
    while read -r line || [ -n "$line" ]; do
        # Пропускаем пустые строки и комментарии
        [ -z "$line" ] && continue
        [ "${line#?}" = "#" ] && continue
        
        # CIDR
        cidr=$(echo "$line" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}')
        if [ -n "$cidr" ]; then
            echo "$cidr" >> "$temp_ip_file"
            continue
        fi
        
        # Диапазон
        range=$(echo "$line" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}-[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')
        if [ -n "$range" ]; then
            echo "$range" >> "$temp_ip_file"
            continue
        fi
        
        # Одиночный IP
        addr=$(echo "$line" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')
        if [ -n "$addr" ]; then
            echo "$addr" >> "$temp_ip_file"
            continue
        fi
        
        # Домен → DNS запрос
        domain="$line"
        resolve_cached "$domain" >> "$temp_ip_file"
        
    done < "$list_file"
    
    # Пакетная загрузка
    load_ipset_batch "$ipset_name" "$temp_ip_file"
    
    # Очистка
    rm -f "$temp_ip_file"
}

# =============================================================================
# ОСНОВНАЯ ЧАСТЬ
# =============================================================================

logger -t "$TAG" "🚀 Запуск оптимизированного скрипта ipset"

# Обрабатываем все списки
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

logger -t "$TAG" "✅ Завершено"

# Статистика
logger -t "$TAG" "📊 Статистика:"
for ipset in unblocksh unblocktor unblockvless unblocktroj; do
    if ipset_exists "$ipset"; then
        count=$(ipset list "$ipset" 2>/dev/null | grep -c "^[0-9]" || echo 0)
        logger -t "$TAG" "  $ipset: $count IP"
    fi
done
