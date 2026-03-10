#!/bin/sh

TAG="unblock_ipset"
DNS_PORT=40500
DNS_TIMEOUT=3
DNS_CACHE_DIR="/tmp/dns_cache"
DNS_CACHE_TTL=3600

cut_local() {
    grep -vE 'localhost|^0\.|^127\.|^10\.|^172\.16\.|^192\.168\.|^::|^fc..:|^fd..:|^fe..:'
}

mkdir -p "$DNS_CACHE_DIR" 2>/dev/null

dns_resolve() {
    local domain="$1"
    local cache_file="$DNS_CACHE_DIR/${domain//\//_}"
    local now age

    if [ -f "$cache_file" ]; then
        now=$(date +%s 2>/dev/null || echo 0)
        age=$((now - $(stat -c %Y "$cache_file" 2>/dev/null || echo 0)))
        if [ "$age" -lt "$DNS_CACHE_TTL" ]; then
            cat "$cache_file"
            return 0
        fi
    fi

    (dig +short "$domain" @localhost -p $DNS_PORT 2>/dev/null > "$cache_file" &
     local pid=$!
     sleep $DNS_TIMEOUT
     kill $pid 2>/dev/null
     wait $pid 2>/dev/null) &
    wait $! 2>/dev/null

    cat "$cache_file" 2>/dev/null
}

process_list() {
    local ipset_name="$1"
    local list_file="$2"
    local restore_file="/tmp/ipset_restore_$$.txt"
    local line count=0 dns_count=0

    [ ! -f "$list_file" ] && return 1

    ipset create "$ipset_name" hash:net family inet hashsize 4096 maxelem 65536 -exist 2>/dev/null
    ipset flush "$ipset_name" 2>/dev/null

    : > "$restore_file"

    while read -r line || [ -n "$line" ]; do
        [ -z "$line" ] && continue
        [ "${line#?}" = "#" ] && continue

        count=$((count + 1))

        cidr=$(echo "$line" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}' | cut_local)
        if [ -n "$cidr" ]; then
            echo "add $ipset_name $cidr" >> "$restore_file"
            continue
        fi

        range=$(echo "$line" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}-[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut_local)
        if [ -n "$range" ]; then
            echo "add $ipset_name $range" >> "$restore_file"
            continue
        fi

        addr=$(echo "$line" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut_local)
        if [ -n "$addr" ]; then
            echo "add $ipset_name $addr" >> "$restore_file"
            continue
        fi

        dns_count=$((dns_count + 1))
        ips=$(dns_resolve "$line")
        if [ -n "$ips" ]; then
            echo "$ips" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | cut_local | while read -r ip; do
                echo "add $ipset_name $ip" >> "$restore_file"
            done
        fi
    done < "$list_file"

    if [ -s "$restore_file" ]; then
        ipset restore -! < "$restore_file" 2>/dev/null
    fi

    rm -f "$restore_file"

    final_count=$(ipset list "$ipset_name" 2>/dev/null | grep -c "^[0-9]" || echo 0)
    logger -t "$TAG" "✅ $ipset_name: $final_count IP (строк: $count, DNS: $dns_count)"
}

until dns_resolve "google.com" | grep -q .; do
    sleep 5
done

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

logger -t "$TAG" "📊 Итог:"
for ipset in unblocksh unblocktor unblockvless unblocktroj; do
    if ipset list "$ipset" -n 2>/dev/null | grep -q "^$ipset$"; then
        c=$(ipset list "$ipset" 2>/dev/null | grep -c "^[0-9]" || echo 0)
        logger -t "$TAG" "  $ipset: $c"
    fi
done
