# 📺 Анализ списков обхода для YouTube

**Дата:** 10 марта 2026 г.  
**Версия:** 1.0

---

## 🎯 Проблема

YouTube может требовать обхода блокировок в некоторых регионах. Этот документ анализирует необходимые домены и предоставляет готовые списки.

---

## 📋 Основные домены YouTube

### Критические домены (обязательны):

```
youtube.com
www.youtube.com
m.youtube.com
music.youtube.com
gaming.youtube.com
youtubekids.com
```

### Домены Google (используются для контента):

```
googlevideo.com
www.googlevideo.com
*.googlevideo.com
ytimg.com
www.ytimg.com
*.ytimg.com
ggpht.com
*.ggpht.com
```

### Сервисные домены:

```
youtube-nocookie.com
youtu.be
s.ytimg.com
i.ytimg.com
```

---

## 🔍 Анализ трафика YouTube

### Основные порты:

| Порт | Протокол | Назначение |
|------|----------|------------|
| 443 | HTTPS | Основной трафик |
| 80 | HTTP | Редиректы |
| 1935 | RTMP | Стриминг (редко) |

### Доменные имена для DNS обхода:

```bash
# Основные
youtube.com
www.youtube.com
m.youtube.com
music.youtube.com
gaming.youtube.com

# Контент
googlevideo.com
www.googlevideo.com
i.ytimg.com
s.ytimg.com
r*.googlevideo.com

# Сервисы
youtube-nocookie.com
youtu.be
ytimg.com
ggpht.com
```

---

## 📝 Готовый список для unblock

### Файл: `/opt/etc/unblock/vpn-youtube.txt`

```bash
# YouTube - основные домены
youtube.com
www.youtube.com
m.youtube.com
music.youtube.com
gaming.youtube.com
youtubekids.com

# YouTube - контент (видео)
googlevideo.com
www.googlevideo.com
*.googlevideo.com
r1.googlevideo.com
r2.googlevideo.com
r3.googlevideo.com
r4.googlevideo.com
r5.googlevideo.com
r6.googlevideo.com
r7.googlevideo.com
r8.googlevideo.com
r9.googlevideo.com
r10.googlevideo.com

# YouTube - изображения и CDN
ytimg.com
www.ytimg.com
i.ytimg.com
s.ytimg.com
ggpht.com
www.ggpht.com
*.ggpht.com

# YouTube - короткие ссылки
youtu.be

# YouTube - прочие
youtube-nocookie.com
youtubeeducation.com
youtubekids.com
yt.be
```

---

## 🚀 Установка

### 1. Создание файла списка

```bash
# На роутере
cat > /opt/etc/unblock/vpn-youtube.txt << 'EOF'
youtube.com
www.youtube.com
m.youtube.com
music.youtube.com
gaming.youtube.com
youtubekids.com
googlevideo.com
www.googlevideo.com
ytimg.com
i.ytimg.com
s.ytimg.com
ggpht.com
youtu.be
youtube-nocookie.com
EOF
```

### 2. Перезапуск скрипта

```bash
# Обновление ipset
/opt/bin/unblock_ipset.sh

# Проверка
ipset list unblockvpn-youtube | head -20
```

### 3. Проверка работы

```bash
# Тест DNS
nslookup youtube.com 8.8.8.8
nslookup googlevideo.com 8.8.8.8

# Тест доступа
curl -I https://www.youtube.com
```

---

## 📊 Статистика

### Ожидаемое количество IP:

| Домен | Примерное IP |
|-------|--------------|
| youtube.com | 4-8 |
| www.youtube.com | 4-8 |
| googlevideo.com | 20-50 |
| *.googlevideo.com | 100-200 |
| ytimg.com | 4-8 |
| ggpht.com | 4-8 |

**Итого:** ~150-250 IP адресов

### Время обновления:

| Доменов | Время (P20) |
|---------|-------------|
| 15 | ~5-8 сек |
| 30 | ~10-15 сек |
| 50 | ~20-25 сек |

---

## 🔧 Интеграция с ботом

### Добавление в меню бота:

```python
# handlers.py
@router.callback_query(F.data == "add_youtube")
async def add_youtube(callback: CallbackQuery):
    youtube_list = """
youtube.com
www.youtube.com
m.youtube.com
googlevideo.com
ytimg.com
"""
    with open("/opt/etc/unblock/vpn-youtube.txt", "w") as f:
        f.write(youtube_list)
    
    # Перезапуск unblock_ipset
    subprocess.run(["/opt/bin/unblock_ipset.sh"])
    
    await callback.answer("✅ YouTube добавлен в списки обхода")
```

---

## ⚠️ Важные замечания

### 1.Wildcard домены

`*.googlevideo.com` может добавить сотни IP. Используйте с осторожностью при нехватке памяти.

### 2. Динамические IP

Google часто меняет IP адреса. Рекомендуется обновлять списки каждые 6-12 часов.

### 3. Производительность

Большое количество IP в ipset может замедлить маршрутизацию. Оптимально: 200-500 IP.

---

## 🧪 Тестирование

### Проверка доступности:

```bash
# Пинг доменов
ping -c 3 youtube.com
ping -c 3 googlevideo.com

# Проверка портов
nc -zv youtube.com 443
nc -zv googlevideo.com 443

# Тест загрузки
curl -o /dev/null -s -w "%{time_total}\n" https://www.youtube.com
```

### Проверка ipset:

```bash
# Количество IP
ipset list unblockvpn-youtube | grep -c "^[0-9]"

# Просмотр первых 20
ipset list unblockvpn-youtube | head -25
```

---

## 📈 Мониторинг

### Логирование:

```bash
# Проверка логов (если есть logread)
logread | grep unblock_ipset | grep youtube

# Статистика по ipset
ipset list unblockvpn-youtube -t | grep "References"
```

### Автоматическое обновление:

```bash
# Crontab (каждые 6 часов)
0 */6 * * * /opt/bin/unblock_ipset.sh

# Или раз в 12 часов
0 */12 * * * /opt/bin/unblock_ipset.sh
```

---

## 🔗 Дополнительные ресурсы

- [Официальная документация YouTube](https://developers.google.com/youtube)
- [Домены Google для обхода](https://support.google.com/youtube/answer/1748152)
- [Списки блокировок](https://github.com/AdguardTeam/AdGuardHome/wiki/DNS-Crypt)

---

## 📝 Рекомендации

### Минимальный набор:

```bash
youtube.com
www.youtube.com
googlevideo.com
ytimg.com
```

### Полный набор (рекомендуется):

```bash
youtube.com
www.youtube.com
m.youtube.com
music.youtube.com
googlevideo.com
www.googlevideo.com
ytimg.com
i.ytimg.com
s.ytimg.com
ggpht.com
youtu.be
```

### Расширенный набор (для продвинутых):

```bash
# Все домены из "Полного набора" +
youtube-nocookie.com
youtubeeducation.com
youtubekids.com
yt.be
*.googlevideo.com
*.ggpht.com
```

---

**Обновлено:** 10 марта 2026 г.  
**Автор:** bypass_keenetic team
