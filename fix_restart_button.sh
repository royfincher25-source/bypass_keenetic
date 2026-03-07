#!/bin/sh
# =============================================================================
# ИСПРАВЛЕНИЕ КНОПКИ ПЕРЕЗАПУСКА БОТА
# =============================================================================
# Этот скрипт исправляет ошибку кнопки "Перезапуск бота" в Telegram меню
# =============================================================================

echo "=============================================="
echo "  Исправление кнопки перезапуска"
echo "=============================================="
echo ""

cd /opt/etc/bot

# 1. Проверка текущего кода
echo "[1/4] Проверка текущего кода..."
echo ""
echo "Текущая строка:"
grep "subprocess.Popen(config.services" handlers.py
echo ""

# 2. Исправление через Python
echo "[2/4] Исправление кода..."

python3 << 'EOF'
# Читаем файл
with open('/opt/etc/bot/handlers.py', 'r') as f:
    content = f.read()

# Заменяем
old = "subprocess.Popen(config.services['service_script'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)"
new = "subprocess.Popen(['/opt/etc/bot/S99telegram_bot', 'restart'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)"

if old in content:
    content = content.replace(old, new)
    
    # Пишем обратно
    with open('/opt/etc/bot/handlers.py', 'w') as f:
        f.write(content)
    
    print("✅ Исправлено!")
else:
    print("⚠️ Строка не найдена (возможно уже исправлена)")
EOF

# 3. Проверка исправления
echo ""
echo "[3/4] Проверка исправления..."
echo ""
echo "Новая строка:"
grep "subprocess.Popen" handlers.py | grep restart
echo ""

# 4. Очистка и перезапуск
echo "[4/4] Очистка кэша и перезапуск..."
rm -rf /opt/etc/bot/__pycache__
/opt/etc/bot/S99telegram_bot restart
sleep 3

# Результат
echo ""
echo "=============================================="
echo "  Результат"
echo "=============================================="
echo ""

echo "Процессы Python:"
ps | grep python | grep -v grep

echo ""
echo "Теперь кнопка '🤖 Перезапуск бота' будет работать!"
echo ""
echo "=============================================="
