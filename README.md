# Help Desk Service

Система технической поддержки с Telegram и MAX ботами и веб-интерфейсом для работы с заявками.

Пользователи создают заявки через бота (Telegram или MAX), прикладывая текст, изображения или голосовые сообщения. Сотрудники поддержки обрабатывают заявки через веб-панель, а ответы автоматически отправляются обратно пользователю через того же бота.

## Архитектура

```
Пользователь ──► Telegram Bot (bot_telebot.py)  ──►┐
                                                     ├──► PostgreSQL
Пользователь ──► MAX Bot (bot_max.py)            ──►┘        │
                                                              │
Сотрудник    ──► Flask Web App (webapp.py)       ◄────────────┘
                                                              │
                 Scheduler Telegram (sheduler_for_response_bot.py) ◄─┤
                 Scheduler MAX (sheduler_for_response_max.py)      ◄─┘
```

## Компоненты

| Файл | Описание |
|---|---|
| `bot_telebot.py` | Telegram-бот для создания заявок (pyTelegramBotAPI) |
| `bot_max.py` | MAX-бот для создания заявок (maxapi, asyncio) |
| `webapp.py` | Flask веб-приложение для сотрудников поддержки |
| `sheduler_for_response_bot.py` | Планировщик отправки ответов в Telegram |
| `sheduler_for_response_max.py` | Планировщик отправки ответов в MAX |
| `db_working.py` | Слой работы с базой данных (psycopg2) |
| `config.py` | Чтение конфигурации из `config.ini` |
| `forms.py` | WTForms формы для веб-приложения |
| `models.py` | SQLAlchemy модели |

## Требования

- Python 3.9+
- PostgreSQL 14+

## Установка

1. Клонировать репозиторий:

```bash
git clone git@github.com:ecoli79/help_desk_service.git
cd help_desk_service
```

2. Установить зависимости:

```bash
pip install psycopg2 pyTelegramBotAPI flask flask-login flask-sqlalchemy flask-wtf requests APScheduler maxapi aiohttp
```

3. Создать базу данных PostgreSQL и применить схему:

```bash
createdb -U admin bot_support
psql -U admin -d bot_support -f bot_support.sql
```

4. Создать файл конфигурации `config.ini` в корне проекта:

Все настройки для подключения к БД и токены ботов хранятся в этом файле.
Он добавлен в `.gitignore` и **не попадает в репозиторий** -- каждый разработчик создает его локально.

```ini
[postgresql]
host = localhost
database = bot_support
user = admin
password = your_password

[telegram_bot]
token = YOUR_TELEGRAM_BOT_TOKEN

[max_bot]
token = YOUR_MAX_BOT_TOKEN
```

| Секция | Параметры | Используется в |
|---|---|---|
| `postgresql` | `host`, `database`, `user`, `password` | `db_working.py`, `webapp.py` |
| `telegram_bot` | `token` | `bot_telebot.py`, `sheduler_for_response_bot.py` |
| `max_bot` | `token` | `bot_max.py`, `sheduler_for_response_max.py` |

## Запуск

Для полноценной работы сервиса необходимо запустить 5 процессов:

```bash
# 1. Telegram-бот
python bot_telebot.py

# 2. MAX-бот
python bot_max.py

# 3. Веб-панель для сотрудников (http://0.0.0.0:5000)
python webapp.py

# 4. Планировщик ответов Telegram
python sheduler_for_response_bot.py

# 5. Планировщик ответов MAX
python sheduler_for_response_max.py
```

## Структура БД

- `users` -- пользователи Telegram/MAX
- `employee` -- сотрудники поддержки (авторизация в веб-панели)
- `tickets` -- заявки
- `ticket_types` -- типы заявок. При создании базы скрипт добавляет типы по умолчанию: Подписание, Оборудование, Доступ к системам, Другое. Если нужны другие типы -- измените список `INSERT` в `bot_support.sql` перед применением скрипта, либо добавьте/измените записи в таблице `ticket_types` после создания базы. Боты и веб-панель подхватывают типы из этой таблицы автоматически
- `images` -- изображения, прикрепленные к заявкам
- `voices` -- голосовые сообщения, прикрепленные к заявкам
