#!/bin/sh

# Путь к конфигу
BOT_CONFIG="/opt/etc/bot/bot_config.py"
if [ ! -f "$BOT_CONFIG" ]; then
    echo "❌ Ошибка: Файл конфигурации $BOT_CONFIG не найден!" >&2
    exit 1
fi

# Чтение переменных
MT_URL=$(grep "^MT_url" "$BOT_CONFIG" | awk -F'"' '{print $2}')
BASE_URL=$(grep "^base_url" "$BOT_CONFIG" | awk -F'"' '{print $2}')
BOT_URL="$BASE_URL/src/botlight"
PROXY0PORT=$(grep "proxy0port" "$BOT_CONFIG" | awk -F'=' '{print $2}' | awk '{print $1}')
PROXY1PORT=$(grep "proxy1port" "$BOT_CONFIG" | awk -F'=' '{print $2}' | awk '{print $1}')
PROXY2PORT=$(grep "proxy2port" "$BOT_CONFIG" | awk -F'=' '{print $2}' | awk '{print $1}')
PROXY0INTERFACE=$(grep "proxy0interface" "$BOT_CONFIG" | awk -F'=' '{print $2}' | awk '{gsub(/["'\'']/, ""); print $1}')
PROXY1INTERFACE=$(grep "proxy1interface" "$BOT_CONFIG" | awk -F'=' '{print $2}' | awk '{gsub(/["'\'']/, ""); print $1}')
PROXY1INTERFACE=$(grep "proxy2interface" "$BOT_CONFIG" | awk -F'=' '{print $2}' | awk '{gsub(/["'\'']/, ""); print $1}')
VLESS_CLIENT=$(grep "vless_client" "$BOT_CONFIG" | awk -F'=' '{print $2}' | awk '{gsub(/["'\'']/, ""); print $1}')
CLIENT_MODE=$(grep "client_mode" "$BOT_CONFIG" | awk -F'=' '{print $2}' | awk '{gsub(/["'\'']/, ""); print $1}')

# Чтение версии прошивки
if [ -f /proc/version ]; then
    keen_os_full=$(cat /proc/version | awk '{print $3}')
else
    echo "❌ Ошибка: файл /proc/version не найден. Не удалось получить версию ОС"
fi

# Функция для чтения путей из конфига
read_path() {
    sed -n "/\"$1\":/s/.*\": *\"\([^\"]*\)\".*/\1/p" "$BOT_CONFIG"
}

# Чтение путей из paths
TOR_CONFIG=$(read_path "tor_config")
SINGBOX_CONFIG=$(read_path "singbox_config")
XRAY_CONFIG=$(read_path "xray_config")
TEMPLATES_DIR=$(read_path "templates_dir")
KEENSNAP_DIR=$(read_path "keensnap_dir")
SCRIPT_BU=$(read_path "keensnap")
BOT_DIR=$(read_path "bot_dir")
TOR_DIR=$(read_path "tor_dir")
SINGBOX_DIR=$(read_path "singbox_dir")
XRAY_DIR=$(read_path "xray_dir")
INIT_SINGBOX=$(read_path "init_singbox")
INIT_XRAY=$(read_path "init_xray")
INIT_TOR=$(read_path "init_tor")
INIT_BOT=$(read_path "init_bot")
INIT_MT=$(read_path "init_MT")

# Чтение пакетов
installed_packages=$(opkg list-installed | awk '{print $1}')
PACKAGES=$(awk -v client="$VLESS_CLIENT" '
/^packages = \[/,/\]/ {
    if ($0 ~ /".*"/) {
        gsub(/^[[:space:]]*"|".*$/, "")
        package = $0
        if (package == "xray" && client != "xray") next
        if (package == "sing-box-go" && client != "singbox") next
        printf "%s ", package
    }
}' "$BOT_CONFIG")


if [ "$1" = "-remove" ]; then

    # Удаление пакетов
    for pkg in $PACKAGES; do
        if echo "$installed_packages" | grep -q "^$pkg$"; then
            echo "Удаляем пакет: $pkg"
            opkg remove "$pkg" --force-removal-of-dependent-packages
        else
            echo "❕Пакет $pkg не был установлен, пропускаем..."
        fi
    done
    echo "Все пакеты удалены. Продолжаем удаление"

    # Удаления того, что не удаляется через remove
    for file in \
        "$TOR_DIR" \
        "$SINGBOX_DIR" \
        "$XRAY_DIR" \
        "$TEMPLATES_DIR"
    do
        [ -e "$file" ] && rm -rf "$file" && echo "Удалён файл или директория: \"$file\""
    done
    echo "Созданные папки, файлы и настройки удалены"
    exit 0

elif [ "$1" = "-install" ]; then
    # echo "ℹ️ Ваша версия KeenOS" "${keen_os_full}"
    
    wget -qO- "$MT_URL"  | sh && echo "Репозиторий MagiTrickle добавлен в пакетный менеджер"
    
    # Установка пакетов
    opkg update > /dev/null 2>&1 && echo "Пакеты обновлены"
    for pkg in $PACKAGES; do
        if echo "$installed_packages" | grep -q "^$pkg$"; then
            echo "❕Пакет $pkg уже установлен, пропускаем..."
        else
            echo "Устанавливаем пакет: $pkg"
            if ! opkg install "$pkg"; then
                echo "❌ Ошибка при установке $pkg" >&2
                exit 1
            fi
        fi
    done
    sleep 3
    echo "Установка пакетов завершена. Продолжаем установку"
    
    # Создадим прокси-подключение для Xray или Sing-box в режиме socks5
    if [ "$VLESS_CLIENT" = "singbox" ] && [ "$CLIENT_MODE" = "tun" ]; then
        echo "Прокси-подключение не будет создано так как выбран Sing-box в режиме tun"
    else
        if [ "$VLESS_CLIENT" = "xray" ]; then
            INTERFACE="$PROXY1INTERFACE"
            PORT="$PROXY1PORT"
        elif [ "$VLESS_CLIENT" = "singbox" ] && [ "$CLIENT_MODE" = "socks5" ]; then
            INTERFACE="$PROXY2INTERFACE"
            PORT="$PROXY2PORT"
        fi
    
        ndmc -c interface "$INTERFACE" && \
        ndmc -c interface "$INTERFACE" proxy protocol socks5 && \
        ndmc -c interface "$INTERFACE" proxy socks5-udp && \
        ndmc -c interface "$INTERFACE" proxy upstream 127.0.0.1 "$PORT" && \
        ndmc -c interface "$INTERFACE" up && \
        ndmc -c system configuration save
    
        echo "Прокси-подключение для $VLESS_CLIENT создано"
    fi

    # Создадим прокси-подключение для Tor
    ndmc -c interface "$PROXY0INTERFACE" && \
    ndmc -c interface "$PROXY0INTERFACE" proxy protocol socks5 && \
    ndmc -c interface "$PROXY0INTERFACE" proxy socks5-udp && \
    ndmc -c interface "$PROXY0INTERFACE" proxy upstream 127.0.0.1 "$PROXY0PORT" && \
    ndmc -c interface "$PROXY0INTERFACE" up && \
    ndmc -c system configuration save
    echo "Прокси-подключение для Tor создано"

    # Создание шаблонов
    mkdir -p "$TEMPLATES_DIR"
    for template in tor_template.torrc xray_template.json singbox1_template.json singbox2_template.json; do
        curl -s -o "$TEMPLATES_DIR/$template" "$BOT_URL/$template" || exit 1
    done
    echo "Загружены шаблоны конфигураций для Tor, Xray и Sing-box"

    # Создание базовых конфигураций из шаблонов
    cp "$TEMPLATES_DIR/tor_template.torrc" "$TOR_CONFIG" && \
    echo "Установлены базовые настройки Tor"

    if [ "$VLESS_CLIENT" = "xray" ]; then
        cp "$TEMPLATES_DIR/xray_template.json" "$XRAY_CONFIG" && \
        echo "Установлены базовые настройки Xray"
    else
        case "$CLIENT_MODE" in
        "tun")
            cp "$TEMPLATES_DIR/singbox2_template.json" "$SINGBOX_CONFIG" && \
            echo "Установлены базовые настройки Sing-box (Tun режим)"
            ;;
        "socks5")
            cp "$TEMPLATES_DIR/singbox1_template.json" "$SINGBOX_CONFIG" && \
            echo "Установлены базовые настройки Sing-box (SOCKS5 режим)"
            ;;
        *)
            echo "Ошибка: неизвестный режим Sing-box $CLIENT_MODE"
            ;;
        esac
    fi

    curl -s -o "$INIT_BOT" "$BOT_URL/S99telegram_bot" || exit 1
    chmod 755 "$INIT_BOT" || chmod +x "$INIT_BOT"
    echo "Установлен cкрипт автоматического запуска бота при загрузке маршрутизатора"

    # Установка скрипта для создания бекапов через telegram
    mkdir -p "$KEENSNAP_DIR"
    curl -s -o "$SCRIPT_BU" "$BASE_URL/KeenSnap/keensnap.sh" || exit 1
    chmod 755 "$SCRIPT_BU"
    echo "Установлен скрипт для создания бекапов через telegram"
    
    "$INIT_MT" start > /dev/null 2>&1 || echo "❕❌ Ошибка! MagiTrickle не запущен"
    
    echo "Выполнена основная настройка бота"
    curl -s "$BOT_URL/version.md" > "$BOT_DIR/version.md"
    echo "Через меню \"🔑 Ключи и мосты\" добавьте ваши мосты Tor, ключ Vless"
    echo "Через MagiTrickle (:8080) настройте маршрутизацию через нужные интерфейсы"
    
    exit 0

elif [ "$1" = "-update" ]; then
    # echo "ℹ️ Ваша версия KeenOS" "${keen_os_full}"
    # opkg update > /dev/null 2>&1 && echo "Пакеты обновлены"
    # opkg install magitrickle && echo "MagiTrickle обновлен"
    
    # Что нужно обновить
    curl -s -o "$BOT_DIR/main.py" "$BOT_URL/main.py" || exit 1
    curl -s -o "$BOT_DIR/menu.py" "$BOT_URL/menu.py" || exit 1
    curl -s -o "$BOT_DIR/utils.py" "$BOT_URL/utils.py" || exit 1
    curl -s -o "$BOT_DIR/handlers.py" "$BOT_URL/handlers.py" || exit 1
    curl -s -o "$INIT_BOT" "$BOT_URL/S99telegram_bot" || exit 1
    # curl -s -o "$SCRIPT_BU" "$BASE_URL/KeenSnap/keensnap.sh" || exit 1
    # curl -s -o "$TEMPLATES_DIR/tor_template.torrc" "$BOT_URL/tor_template.torrc" || exit 1
    # cp "$TEMPLATES_DIR/tor_template.torrc" "$TOR_CONFIG" && echo "Базовые настройки Tor обновлены"
    
    echo "Обновления для бота загружены, применяем права"
    chmod 755 "$BOT_DIR"
    chmod 644 "$BOT_DIR"/*.py
    chmod 755 "$INIT_BOT" || chmod +x "$INIT_BOT"
    # chmod 755 "$SCRIPT_BU"

    # "$INIT_SINGBOX" restart > /dev/null 2>&1 || echo "❕Sing-box не запустился, проверьте конфигурацию"
    # "$INIT_XRAY" restart > /dev/null 2>&1 || echo "❕Xray не запустился, проверьте конфигурацию"
    # "$INIT_TOR" restart > /dev/null 2>&1 || echo "❕Tor не запуcтился, проверьте конфигурацию"
    # "$INIT_MT" restart > /dev/null 2>&1 || echo "❕MagiTrickle не запустился, проверьте конфигурацию"

    bot_old_version=$(cat "$BOT_DIR/version.md")
    curl -s "$BOT_URL/version.md" > "$BOT_DIR/version.md"
    bot_new_version=$(cat "$BOT_DIR/version.md")
    echo "Версия бота \"${bot_old_version}\" обновлена до \"${bot_new_version}\""
    sleep 2
    echo "✅ Обновление выполнено. Бот будет перезапущен"
    # echo "Бот будет перезапущен, после запуска введите ключи Tor! Теперь поддерживаются obfs4 и webtunnel ключи!"
    sleep 2
    "$INIT_BOT" restart

    exit 0

elif [ "$1" = "-var" ]; then
    echo -e "\n=== Место расположения файла конфигурации ==="
    echo "BOT_CONFIG: $BOT_CONFIG"
    echo -e "\n=== URL-адреса для скачиваемых файлов ==="
    echo "BASE_URL: $BASE_URL"
    echo "BOT_URL: $BOT_URL"
    echo "MT_URL: $MT_URL"
    echo -e "\n=== Версия прошивки ==="
    echo "Ваша версия KeenOS" "${keen_os_full}"
    echo -e "\n=== Настройки прокси ==="
    echo "PROXY0PORT: $PROXY0PORT"
    echo "PROXY0INTERFACE: $PROXY0INTERFACE"
    echo "PROXY1PORT: $PROXY1PORT"
    echo "PROXY1INTERFACE: $PROXY1INTERFACE"
    echo "PROXY2PORT: $PROXY2PORT"
    echo "PROXY2INTERFACE: $PROXY2INTERFACE"
    echo -e "\n=== Настройки vless клиента ==="
    echo "VLESS_CLIENT: $VLESS_CLIENT"
    echo "CLIENT_MODE: $CLIENT_MODE"
    echo -e "\n=== Пути из paths ==="
    echo "TOR_CONFIG: $TOR_CONFIG"
    echo "SINGBOX_CONFIG: $SINGBOX_CONFIG"
    echo "XRAY_CONFIG: $XRAY_CONFIG"
    echo "TEMPLATES_DIR: $TEMPLATES_DIR"
    echo "KEENSNAP_DIR: $KEENSNAP_DIR"
    echo "SCRIPT_BU: $SCRIPT_BU"
    echo "BOT_DIR: $BOT_DIR"
    echo "TOR_DIR: $TOR_DIR"
    echo "SINGBOX_DIR: $SINGBOX_DIR"
    echo "XRAY_DIR: $XRAY_DIR"
    echo "INIT_SINGBOX: $INIT_SINGBOX"
    echo "INIT_XRAY: $INIT_XRAY"
    echo "INIT_TOR: $INIT_TOR"
    echo "INIT_BOT: $INIT_BOT"
    echo "INIT_MT: $INIT_MT"
    echo -e "\n=== Пакеты ==="
    echo "PACKAGES: $PACKAGES"
    exit 0

elif [ "$1" = "-help" ]; then
    echo "-install для установки"
    echo "-remove для удаления"
    echo "-update для обновления"
    echo "-var для проверки чтения переменных"
    exit 0

else
    echo "-help посмотреть список доступных аргументов"
    exit 0
fi
