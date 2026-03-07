#!/bin/sh
# =============================================================================
# АВТОМАТИЧЕСКОЕ СОЗДАНИЕ АРХИВА КОНФИГУРАЦИИ
# =============================================================================
# Просто запустите: sh /opt/root/create_archive.sh
# =============================================================================

set -e

DATE=$(date +%Y-%m-%d_%H-%M)
BACKUP_DIR="/opt/root/backup_tmp"
ARCHIVE="/opt/root/backup_${DATE}.tar.gz"

echo "=============================================="
echo "  Создание архива конфигурации"
echo "=============================================="
echo ""

# Очистка и создание директорий
echo "[INFO] Подготовка..."
rm -rf "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR/bot"
mkdir -p "$BACKUP_DIR/configs"
mkdir -p "$BACKUP_DIR/scripts"
mkdir -p "$BACKUP_DIR/unblock"

# Сохранение .env
echo "[1/6] Сохранение .env..."
if [ -f "/opt/etc/bot/.env" ]; then
    cp /opt/etc/bot/.env "$BACKUP_DIR/.env"
    chmod 600 "$BACKUP_DIR/.env"
    echo "      OK"
else
    echo "      .env не найден"
fi

# Сохранение файлов бота
echo "[2/6] Сохранение файлов бота..."
if [ -d "/opt/etc/bot" ]; then
    cp -r /opt/etc/bot/* "$BACKUP_DIR/bot/" 2>/dev/null || true
    rm -rf "$BACKUP_DIR/bot/__pycache__" 2>/dev/null || true
    echo "      OK"
else
    echo "      Директория бота не найдена"
fi

# Сохранение списков обхода
echo "[3/6] Сохранение списков обхода..."
if [ -d "/opt/etc/unblock" ]; then
    cp /opt/etc/unblock/*.txt "$BACKUP_DIR/unblock/" 2>/dev/null || true
    echo "      OK"
else
    echo "      Списки обхода не найдены"
fi

# Сохранение конфигов сервисов
echo "[4/6] Сохранение конфигов сервисов..."
if [ -f "/opt/etc/tor/torrc" ]; then
    cp /opt/etc/tor/torrc "$BACKUP_DIR/configs/" 2>/dev/null && echo "      Tor: OK" || true
fi
if [ -f "/opt/etc/shadowsocks.json" ]; then
    cp /opt/etc/shadowsocks.json "$BACKUP_DIR/configs/" 2>/dev/null && echo "      Shadowsocks: OK" || true
fi
if [ -f "/opt/etc/xray/config.json" ]; then
    cp /opt/etc/xray/config.json "$BACKUP_DIR/configs/" 2>/dev/null && echo "      Xray: OK" || true
fi
if [ -f "/opt/etc/trojan/config.json" ]; then
    cp /opt/etc/trojan/config.json "$BACKUP_DIR/configs/" 2>/dev/null && echo "      Trojan: OK" || true
fi

# Сохранение скриптов
echo "[5/6] Сохранение скриптов..."
if [ -f "/opt/root/script.sh" ]; then
    cp /opt/root/script.sh "$BACKUP_DIR/scripts/" 2>/dev/null && echo "      script.sh: OK" || true
fi
if [ -f "/opt/root/KeenSnap/keensnap.sh" ]; then
    cp /opt/root/KeenSnap/keensnap.sh "$BACKUP_DIR/scripts/" 2>/dev/null && echo "      keensnap.sh: OK" || true
fi

# Создание архива
echo ""
echo "[6/6] Создание архива..."
cd /opt/root
tar -czf "$ARCHIVE" backup_tmp 2>/dev/null

# Очистка
rm -rf "$BACKUP_DIR"

# Результат
echo ""
echo "=============================================="
echo "  Архив успешно создан!"
echo "=============================================="
echo ""
echo "  Путь: $ARCHIVE"
echo "  Размер:"
ls -lh "$ARCHIVE"
echo ""
echo "  Для копирования на компьютер:"
echo "  scp root@192.168.1.1:$ARCHIVE /путь/на/компьютере/"
echo ""
echo "=============================================="

exit 0
