#!/bin/sh
# =============================================================================
# ОПТИМИЗИРОВАННЫЙ СКРИПТ ЗАПОЛНЕНИЯ IPSET (v3.4.3)
# =============================================================================
# Оптимизации:
# - Параллельная обработка доменов (xargs -P)
# - Кэширование DNS запросов (1 час)
# - Пакетная загрузка в ipset через ipset restore
# - Пропуск уже обработанных доменов
# - Проверка доступности DNS перед запуском
# =============================================================================

TAG="unblock_ipset"
DNS_SERVER="8.8.8.8"
DNS_PORT="53"
DNS_CACHE_DIR="/tmp/dns_cache"
DNS_CACHE_TTL=3600  # 1 час в секундах
MAX_PARALLEL=8      # Максимум параллельных DNS запросов

# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

# Фильтрация локальных IP
cut_local() {
    grep -vE 'localhost|^0\.|^127\.|^10\.|^172\.16\.|^192\.168\.|^::|^fc..:|^fd..:|^fe..:'
}

# Создание директории кэша
mkdir -p "$DNS_CACHE_DIR" 2>/dev/null

# DNS запрос с кэшированием
dns_resolve() {
    local domain="$1"
    local cache_file="$DNS_CACHE_DIR/${domain//\//_}.cache"
    local now=$(date +%s 2>/dev/null || echo 0)
    
    # Проверяем кэш
    if [ -f "$cache_file" ]; then
        local mtime=$(stat -c %Y "$cache_file" 2>/dev/null || echo 0)
        if [ $((now - mtime)) -lt $DNS_CACHE_TTL ]; then
            cat "$cache_file"
            return 0
        fi
    fi
    
    # DNS запрос
    dig +short "$domain" @"$DNS_SERVER" -p "$DNS_PORT" +time=2 +tries=1 +nocookie 2>/dev/null > "$cache_file"
    cat "$cache_file"
}

# Проверка доступности DNS
check_dns() {
    local test_result=$(dig +short "google.com" @"$DNS_SERVER" -p "$DNS_PORT" +time=2 +tries=1 2>/dev/null)
    if [ -z "$test_result" ]; then
        logger -t "$TAG" "❌ DNS НЕ доступен: $DNS_SERVER:$DNS_PORT"
        echo "❌ DNS НЕ доступен: $DNS_SERVER:$DNS_PORT" >&2
        return 1
    fi
    logger -t "$TAG" "✅ DNS доступен: $DNS_SERVER:$DNS_PORT"
    return 0
}

# =============================================================================
# ОБРАБОТКА СПИСКА
# =============================================================================

process_list() {
    local ipset_name="$1"
    local list_file="$2"
    local temp_ips="/tmp/ipset_${ipset_name}_$$.txt"
    local temp_domains="/tmp/domains_${ipset_name}_$$.txt"
    local count_total=0
    local count_domains=0
    local count_ips=0
    local count_cached=0
    
    if [ ! -f "$list_file" ]; then
        logger -t "$TAG" "⚠️ Файл не найден: $list_file"
        return 1
    fi
    
    # Создаём/сбрасываем ipset
    ipset create "$ipset_name" hash:net family inet hashsize 4096 maxelem 65536 -exist 2>/dev/null
    ipset flush "$ipset_name" 2>/dev/null
    
    : > "$temp_ips"
    : > "$temp_domains"
    
    logger -t "$TAG" "🔄 Обработка: $list_file → $ipset_name"
    
    # Первый проход: разделяем IP и домены
    while read -r line || [ -n "$line" ]; do
        [ -z "$line" ] && continue
        case "$line" in
            \#*|"") continue ;;
        esac
        
        count_total=$((count_total + 1))
        
        # CIDR
        cidr=$(echo "$line" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}')
        if [ -n "$cidr" ]; then
            echo "$cidr" >> "$temp_ips"
            continue
        fi
        
        # Диапазон
        range=$(echo "$line" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}-[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')
        if [ -n "$range" ]; then
            echo "$range" >> "$temp_ips"
            continue
        fi
        
        # Одиночный IP
        addr=$(echo "$line" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')
        if [ -n "$addr" ]; then
            echo "$addr" >> "$temp_ips"
            continue
        fi
        
        # Домен
        echo "$line" >> "$temp_domains"
        count_domains=$((count_domains + 1))
        
    done < "$list_file"
    
    # Второй проход: резолвим домены параллельно
    if [ -s "$temp_domains" ]; then
        logger -t "$TAG" "🔍 DNS запросов: $count_domains (параллельно: $MAX_PARALLEL)"
        
        cat "$temp_domains" | xargs -P$MAX_PARALLEL -I{} sh -c '
            domain="{}"
            cache_dir="'"$DNS_CACHE_DIR"'"
            cache_file="$cache_dir/${domain//\//_}.cache"
            now=$(date +%s 2>/dev/null || echo 0)
            
            # Проверяем кэш
            if [ -f "$cache_file" ]; then
                mtime=$(stat -c %Y "$cache_file" 2>/dev/null || echo 0)
                if [ $((now - mtime)) -lt '"$DNS_CACHE_TTL"' ]; then
                    cat "$cache_file"
                    exit 0
                fi
            fi
            
            # DNS запрос
            dig +short "$domain" @'"$DNS_SERVER"' -p '"$DNS_PORT"' +time=2 +tries=1 +nocookie 2>/dev/null > "$cache_file"
            cat "$cache_file"
        ' | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut_local >> "$temp_ips"
    fi
    
    # Третий проход: загружаем в ipset пакетно
    if [ -s "$temp_ips" ]; then
        count_ips=$(sort -u "$temp_ips" | cut_local | wc -l)
        sort -u "$temp_ips" | cut_local | sed "s/^/add $ipset_name /" | ipset restore -! 2>/dev/null
    fi
    
    # Очистка
    rm -f "$temp_ips" "$temp_domains"
    
    # Статистика
    local final_count=$(ipset list "$ipset_name" 2>/dev/null | grep -c "^[0-9]" || echo 0)
    logger -t "$TAG" "✅ $ipset_name: всего=$count_total, доменов=$count_domains, IP=$final_count"
}

# =============================================================================
# ОСНОВНАЯ ЧАСТЬ
# =============================================================================

START_TIME=$(date +%s)
logger -t "$TAG" "🚀 Запуск (DNS: $DNS_SERVER:$DNS_PORT, параллельно: $MAX_PARALLEL)"

# Проверка DNS
check_dns || exit 1

# Обработка основных списков
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

# Итоговая статистика
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

logger -t "$TAG" "📊 Итог (время: ${DURATION}c):"
for ipset in unblocksh unblocktor unblockvless unblocktroj; do
    if ipset list "$ipset" -n 2>/dev/null | grep -q "^$ipset$"; then
        count=$(ipset list "$ipset" 2>/dev/null | grep -c "^[0-9]" || echo 0)
        logger -t "$TAG" "  $ipset: $count IP"
    fi
done

# Вывод в консоль
echo "✅ Завершено за ${DURATION}c"
echo "📊 Статистика:"
for ipset in unblocksh unblocktor unblockvless unblocktroj; do
    if ipset list "$ipset" -n 2>/dev/null | grep -q "^$ipset$"; then
        count=$(ipset list "$ipset" 2>/dev/null | grep -c "^[0-9]" || echo 0)
        echo "  $ipset: $count IP"
    fi
done
