#!/usr/bin/env python3
# =============================================================================
# СКРИПТ ПРОВЕРКИ КОНФИГУРАЦИИ
# =============================================================================
# Запустите этот скрипт перед развёртыванием для проверки настроек
# Использование: python check_config.py
# =============================================================================

import os
import sys

def check_file_exists(filepath, description):
    """Проверка существования файла"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} не найден: {filepath}")
        return False

def check_env_variable(name, required=True):
    """Проверка переменной окружения"""
    value = os.environ.get(name)
    if value:
        if name == 'TELEGRAM_BOT_TOKEN':
            # Маскируем токен
            masked = value[:10] + '...' if len(value) > 10 else value
            print(f"✅ {name}: {masked}")
        elif name == 'TELEGRAM_USERNAMES':
            print(f"✅ {name}: {value}")
        else:
            print(f"✅ {name}: {value}")
        return True
    elif required:
        print(f"❌ {name}: не задана")
        return False
    else:
        print(f"⚠️  {name}: не задана (опционально)")
        return True

def validate_token_format(token):
    """Валидация формата токена"""
    if not token:
        return False
    if ':' not in token:
        return False
    if len(token) < 10:
        return False
    parts = token.split(':')
    if len(parts) != 2:
        return False
    if not parts[0].isdigit():
        return False
    return True

def main():
    print("=" * 70)
    print("ПРОВЕРКА КОНФИГУРАЦИИ BYPASS_KEENETIC")
    print("=" * 70)
    print()
    
    errors = 0
    warnings = 0
    
    # ---------------------------------------------------------------------
    # Проверка файлов
    # ---------------------------------------------------------------------
    print("📁 Проверка файлов...")
    print("-" * 70)
    
    if not check_file_exists('.env', '.env файл'):
        print("   → Скопируйте .env.example в .env и заполните значения")
        errors += 1
    
    check_file_exists('requirements.txt', 'requirements.txt')
    check_file_exists('.env.example', '.env.example')
    
    print()
    
    # ---------------------------------------------------------------------
    # Загрузка .env
    # ---------------------------------------------------------------------
    print("📥 Загрузка .env...")
    print("-" * 70)
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env загружен")
    except ImportError:
        print("❌ python-dotenv не установлен")
        print("   → Установите: pip install python-dotenv")
        errors += 1
        print()
        print("=" * 70)
        print("ПРОВЕРКА ПРЕРВАНА")
        print("=" * 70)
        return 1
    except Exception as e:
        print(f"❌ Ошибка при загрузке .env: {e}")
        errors += 1
    
    print()
    
    # ---------------------------------------------------------------------
    # Проверка переменных окружения
    # ---------------------------------------------------------------------
    print("🔐 Проверка переменных окружения...")
    print("-" * 70)
    
    if not check_env_variable('TELEGRAM_BOT_TOKEN', required=True):
        errors += 1
    else:
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not validate_token_format(token):
            print(f"❌ TELEGRAM_BOT_TOKEN: неверный формат")
            print("   → Формат: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
            errors += 1
        else:
            print(f"   ✅ Формат токена корректен")
    
    if not check_env_variable('TELEGRAM_USERNAMES', required=True):
        errors += 1
    else:
        usernames = os.environ.get('TELEGRAM_USERNAMES', '').split(',')
        if usernames == [''] or len(usernames) == 0:
            print(f"⚠️  TELEGRAM_USERNAMES: пустой список")
            warnings += 1
    
    print()
    
    # ---------------------------------------------------------------------
    # Проверка опциональных переменных
    # ---------------------------------------------------------------------
    print("⚙️  Проверка опциональных переменных...")
    print("-" * 70)
    
    optional_vars = [
        'ROUTER_IP',
        'LOCALPORT_SH',
        'DNSPORT_TOR',
        'LOCALPORT_TOR',
        'LOCALPORT_VLESS',
        'LOCALPORT_TROJAN',
        'DNSOVER_TLS_PORT',
        'DNSOVER_HTTPS_PORT',
        'MAX_RESTARTS',
        'RESTART_DELAY',
        'BACKUP_MAX_SIZE_MB'
    ]
    
    for var in optional_vars:
        check_env_variable(var, required=False)
    
    print()
    
    # ---------------------------------------------------------------------
    # Проверка портов
    # ---------------------------------------------------------------------
    print("🔌 Проверка портов...")
    print("-" * 70)
    
    port_vars = {
        'LOCALPORT_SH': 1082,
        'DNSPORT_TOR': 9053,
        'LOCALPORT_TOR': 9141,
        'LOCALPORT_VLESS': 10810,
        'LOCALPORT_TROJAN': 10829,
        'DNSOVER_TLS_PORT': 40500,
        'DNSOVER_HTTPS_PORT': 40508
    }
    
    for var, default in port_vars.items():
        value = os.environ.get(var)
        if value:
            try:
                port = int(value)
                if 1 <= port <= 65535:
                    print(f"✅ {var}: {port}")
                else:
                    print(f"❌ {var}: порт должен быть от 1 до 65535")
                    errors += 1
            except ValueError:
                print(f"❌ {var}: должно быть числом")
                errors += 1
        else:
            print(f"⚠️  {var}: используется значение по умолчанию ({default})")
    
    print()
    
    # ---------------------------------------------------------------------
    # Итоги
    # ---------------------------------------------------------------------
    print("=" * 70)
    print("ИТОГИ ПРОВЕРКИ")
    print("=" * 70)
    print(f"✅ Успешно: {errors}")
    print(f"❌ Ошибки: {errors}")
    print(f"⚠️  Предупреждения: {warnings}")
    print()
    
    if errors > 0:
        print("❌ ПРОВЕРКА НЕ ПРОЙДЕНА")
        print()
        print("Устраните ошибки перед развёртыванием:")
        print("1. Скопируйте .env.example в .env")
        print("2. Заполните TELEGRAM_BOT_TOKEN и TELEGRAM_USERNAMES")
        print("3. Убедитесь, что формат токена корректен")
        return 1
    else:
        print("✅ ПРОВЕРКА ПРОЙДЕНА")
        print()
        print("Конфигурация готова к развёртыванию!")
        return 0

if __name__ == '__main__':
    sys.exit(main())
