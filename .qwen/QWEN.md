## Qwen Added Memories

### Git и синхронизация
- После каждого `git commit` и `git push` нужно проверять, что изменения действительно попали в удалённый репозиторий на GitHub через команду `git status` (должно быть "Your branch is up to date with 'origin/main'") или через веб-интерфейс GitHub.

### Обновление бота на роутере

**Способ 1: Через Telegram бота (рекомендуется)**
```
/update
```

**Способ 2: Через SSH**
```bash
cd /opt/etc/bot
curl -s -o version.md https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/version.md
curl -s -o handlers.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/handlers.py
curl -s -o bot_config.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/bot_config.py
curl -s -o utils.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/utils.py
curl -s -o main.py https://raw.githubusercontent.com/royfincher25-source/bypass_keenetic/main/bot3/main.py
/opt/etc/init.d/S99telegram_bot restart
```

**Проверка после обновления:**
```bash
cat /opt/etc/bot/version.md           # Проверка версии
tail -20 /opt/etc/bot/error.log       # Проверка ошибок
ps aux | grep python3 | grep main.py  # Проверка потребления RAM (~22-24 MB)
```

### Версии и релизы

| Версия | Изменения |
|--------|-----------|
| **3.4.1** | 🔧 fix: экспорт `is_authorized` в `bot_config` |
| **3.4.0** | ⚡ perf: оптимизация памяти и архитектуры (~6-7 MB экономия) |

**Правило:** После каждого значимого изменения увеличивать версию в `bot3/version.md` (semver: MAJOR.MINOR.PATCH)
