#!/bin/sh
# =============================================================================
# АВТОМАТИЧЕСКОЕ СОЗДАНИЕ АРХИВА КОНФИГУРАЦИИ
# =============================================================================
# Просто запустите: sh /opt/root/create_archive.sh
# =============================================================================

set -e  # Выход при ошибке

BACKUP_NAME="backup_$(date +%Y-%m-%d_%H-%M-%S)"
BACKUP_DIR="/opt/root/$BACKUP_NAME"
ARCHIVE_PATH="/opt/root/$BACKUP_NAME.tar.gz"

echo "=============================================="
echo "  Создание архива конфигурации"
echo "=============================================="
echo ""

# 1. Создание временной директории
echo "[1/8] Создание временной директории..."
mkdir -p "$BACKUP_DIR"

# 2. Сохранение .env файла
echo "[2/8] Сохранение .env файла..."
if [ -f "/opt/etc/bot/.env" ]; then
    cp /opt/etc/bot/.env "$BACKUP_DIR/.env"
    chmod 600 "$BACKUP_DIR/.env"
    echo "      ✅ .env сохранён"
else
    echo "      ⚠️ .env не найден"
fi

# 3. Сохранение файлов бота
echo "[3/8] Сохранение файлов бота..."
if [ -d "/opt/etc/bot" ]; then
    mkdir -p "$BACKUP_DIR/bot"
    cp -r /opt/etc/bot/* "$BACKUP_DIR/bot/" 2>/dev/null || true
    # Удаление кэша
    rm -rf "$BACKUP_DIR/bot/__pycache__" 2>/dev/null || true
    rm -f "$BACKUP_DIR/bot/"*.pyc 2>/dev/null || true
    echo "      ✅ Файлы бота сохранены"
else
    echo "      ⚠️ Директория бота не найдена"
fi

# 4. Сохранение core модуля
echo "[4/8] Сохранение core модуля..."
if [ -d "/opt/etc/bot/core" ]; then
    mkdir -p "$BACKUP_DIR/core"
    cp -r /opt/etc/bot/core/* "$BACKUP_DIR/core/" 2>/dev/null || true
    echo "      ✅ Core модуль сохранён"
else
    echo "      ℹ️ Core модуль отсутствует (нормально для старой версии)"
fi

# 5. Сохранение списков обхода
echo "[5/8] Сохранение списков обхода..."
if [ -d "/opt/etc/unblock" ]; then
    mkdir -p "$BACKUP_DIR/unblock"
    cp /opt/etc/unblock/*.txt "$BACKUP_DIR/unblock/" 2>/dev/null || true
    echo "      ✅ Списки обхода сохранены"
else
    echo "      ℹ️ Списки обхода пусты"
fi

# 6. Сохранение конфигов сервисов
echo "[6/8] Сохранение конфигов сервисов..."
mkdir -p "$BACKUP_DIR/configs"

if [ -f "/opt/etc/tor/torrc" ]; then
    cp /opt/etc/tor/torrc "$BACKUP_DIR/configs/" 2>/dev/null && echo "      ✅ Tor конфиг"
fi

if [ -f "/opt/etc/shadowsocks.json" ]; then
    cp /opt/etc/shadowsocks.json "$BACKUP_DIR/configs/" 2>/dev/null && echo "      ✅ Shadowsocks конфиг"
fi

if [ -f "/opt/etc/xray/config.json" ]; then
    cp /opt/etc/xray/config.json "$BACKUP_DIR/configs/" 2>/dev/null && echo "      ✅ Xray/VLESS конфиг"
fi

if [ -f "/opt/etc/trojan/config.json" ]; then
    cp /opt/etc/trojan/config.json "$BACKUP_DIR/configs/" 2>/dev/null && echo "      ✅ Trojan конфиг"
fi

# 7. Сохранение скриптов
echo "[7/8] Сохранение скриптов..."
mkdir -p "$BACKUP_DIR/scripts"

if [ -f "/opt/root/script.sh" ]; then
    cp /opt/root/script.sh "$BACKUP_DIR/scripts/" 2>/dev/null && echo "      ✅ script.sh"
fi

if [ -f "/opt/root/KeenSnap/keensnap.sh" ]; then
    cp /opt/root/KeenSnap/keensnap.sh "$BACKUP_DIR/scripts/" 2>/dev/null && echo "      ✅ keensnap.sh"
fi

# 8. Информация о системе
echo "[8/8] Сохранение информации о системе..."
cat > "$BACKUP_DIR/system_info.txt" << EOF
Дата создания бэкапа: $(date)
Хост: $(hostname)
Версия Keenetic OS: $(ndmc -c show version 2>/dev/null | grep "release:" | awk '{print $2}' || echo "неизвестно")
Версия Python: $(python3 --version 2>&1 || echo "неизвестно")

Установленные пакеты:
$(opkg list-installed 2>/dev/null | grep -E "python|telegram|requests|pyTelegram" | head -20 || echo "не удалось получить")

Свободное место на /opt:
$(df -h /opt 2>/dev/null | tail -1)

Запущенные процессы:
$(ps 2>/dev/null | grep -E "python|telegram" || echo "не удалось получить")
EOF

# Создание архива
echo ""
echo "Создание архива..."
cd /opt/root
tar -czf "$ARCHIVE_PATH" "$BACKUP_NAME" 2>/dev/null

if [ $? -eq 0 ]; then
    # Удаление временной директории
    rm -rf "$BACKUP_DIR"
    
    # Информация об архиве
    ARCHIVE_SIZE=$(ls -lh "$ARCHIVE_PATH" | awk '{print $5}')
    
    echo ""
    echo "=============================================="
    echo "  ✅ Архив успешно создан!"
    echo "=============================================="
    echo ""
    echo "  Путь: $ARCHIVE_PATH"
    echo "  Размер: $ARCHIVE_SIZE"
    echo ""
    echo "  Для копирования на компьютер:"
    echo "  scp root@192.168.1.1:$ARCHIVE_PATH /путь/на/компьютере/"
    echo ""
    echo "=============================================="
else
    echo ""
    echo "=============================================="
    echo "  ❌ Ошибка при создании архива!"
    echo "=============================================="
    exit 1
fi

exit 0
