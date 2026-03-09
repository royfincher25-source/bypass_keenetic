#!/usr/bin/python3
import os
import sys
import signal
import time
import telebot
import subprocess
import requests.exceptions

# СНАЧАЛА загружаем .env перед импортом bot_config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.env_parser import load_env
load_env('/opt/etc/bot/.env')

# ТЕПЕРЬ импортируем остальное
from handlers import setup_handlers
from utils import log_error, clean_log, check_restart, signal_handler, cleanup_memory
import bot_config as config

if not config.token or config.token.strip() == "" or ":" not in config.token or len(config.token) < 10:
    log_error("Ошибка: Токен не указан или имеет неверный формат в bot_config.py")
    sys.exit(1)
    
current_pid = str(os.getpid())
pids_output = subprocess.run(['pgrep', '-f', f'python3 {config.paths["bot_path"]}'], capture_output=True, text=True).stdout.strip()
running_pids = [pid for pid in pids_output.splitlines() if pid and pid != current_pid]
if running_pids:
    log_error(f"Бот уже запущен с PID: {', '.join(running_pids)}")
    sys.exit(1)

bot = telebot.TeleBot(config.token)
restart_count = 0
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Сохранение restart_count в файл для статистики
def save_restart_count(count):
    try:
        with open('/opt/etc/bot/restart_count.txt', 'w') as f:
            f.write(str(count))
    except (IOError, OSError):
        pass

if __name__ == "__main__":
    clean_log(config.paths["error_log"])

    # Запуск бота и обработчиков
    setup_handlers(bot)
    check_restart(bot)

    # Параметры polling: long_polling_timeout=30 (ожидание от Telegram),
    # timeout=35 (общий HTTP таймаут), interval=1 (задержка при ошибке)
    restart_count = 0
    cleanup_counter = 0
    while restart_count < config.MAX_RESTARTS:
        try:
            # Очистка памяти каждые 50 итераций (~50 секунд)
            cleanup_counter += 1
            if cleanup_counter >= 50:
                cleanup_memory()
                cleanup_counter = 0

            bot.infinity_polling(long_polling_timeout=30, timeout=35, interval=1)
        except (telebot.apihelper.ApiException, requests.exceptions.RequestException) as err:
            log_error(f"Ошибка соединения или Telegram API: {str(err)}")
            restart_count += 1
            save_restart_count(restart_count)
            time.sleep(config.RESTART_DELAY)
        except Exception as err:
            log_error(f"Неизвестная ошибка: {str(err)}")
            restart_count += 1
            save_restart_count(restart_count)
            time.sleep(config.RESTART_DELAY)
    log_error("Бот остановлен после достижения максимального количества попыток перезапуска")
