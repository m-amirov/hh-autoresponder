<div align="center">

<svg width="800" height="200" viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0a0f0a"/>
      <stop offset="100%" style="stop-color:#0d1f14"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#22c55e"/>
      <stop offset="100%" style="stop-color:#4ade80"/>
    </linearGradient>
    <linearGradient id="accentV" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#22c55e"/>
      <stop offset="100%" style="stop-color:#15803d"/>
    </linearGradient>
  </defs>
  <rect width="800" height="200" fill="url(#bg)" rx="14"/>
  <rect x="0" y="0" width="5" height="200" fill="url(#accentV)" rx="2"/>
  <rect x="0" y="0" width="800" height="2" fill="url(#accent)" rx="1" opacity="0.4"/>
  <rect x="30" y="26" width="188" height="22" rx="11" fill="#22c55e18" stroke="#22c55e40" stroke-width="1"/>
  <circle cx="46" cy="37" r="4" fill="#22c55e"/>
  <text x="116" y="42" font-family="'Courier New', monospace" font-size="11" fill="#22c55e" text-anchor="middle" letter-spacing="1">TELEGRAM BOT · hh.ru</text>
  <text x="30" y="98" font-family="Georgia, 'Times New Roman', serif" font-size="40" font-weight="bold" fill="#f8f8f8" letter-spacing="-1">hh-autoresponder</text>
  <text x="30" y="128" font-family="'Courier New', monospace" font-size="13" fill="#6b7280" letter-spacing="0.5">Автоотклики на вакансии hh.ru. Бесплатно, open-source.</text>
  <rect x="30" y="152" width="112" height="26" rx="5" fill="#12211a" stroke="#22553a" stroke-width="1"/>
  <text x="86" y="169" font-family="'Courier New', monospace" font-size="11" fill="#7dd3a8" text-anchor="middle">авто-отклики</text>
  <rect x="152" y="152" width="100" height="26" rx="5" fill="#12211a" stroke="#22553a" stroke-width="1"/>
  <text x="202" y="169" font-family="'Courier New', monospace" font-size="11" fill="#7dd3a8" text-anchor="middle">Python 3.12</text>
  <rect x="262" y="152" width="92" height="26" rx="5" fill="#12211a" stroke="#22553a" stroke-width="1"/>
  <text x="308" y="169" font-family="'Courier New', monospace" font-size="11" fill="#7dd3a8" text-anchor="middle">MIT лицензия</text>
  <text x="668" y="120" font-family="Georgia, serif" font-size="72" fill="#ffffff05" font-weight="bold">hh</text>
</svg>

<br/>

[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)]()
[![Telegram](https://img.shields.io/badge/Telegram-Digital--трафик-2CA5E0?style=flat-square&logo=telegram&logoColor=white)](https://t.me/trafficisobar)
[![Version](https://img.shields.io/badge/version-1.0.0-e63946?style=flat-square)]()

</div>

<br/>

# hh-autoresponder — бот автооткликов на вакансии hh.ru (хх ру)

**Автоотклики на hh.ru на автопилоте.** Телеграм-бот сам ищет вакансии на
**hh.ru** по твоим запросам, отбирает подходящие и **автоматически откликается**
за тебя — ровным, человеческим темпом. Бесплатный, с открытым кодом
(open-source), запускается на твоём компьютере. Всё управление и подробный лог —
в Telegram.

Проще говоря: ставишь **автоотклик на вакансии hh** один раз — и бот сам
рассылает отклики, пока ты занимаешься другими делами. Аналог платных сервисов
автооткликов, только бесплатно и под твоим контролем.

> 📖 **Пошаговая инструкция с картинками:** [Автоотклик на вакансии hh.ru — как настроить за вечер](https://pawetta.com/blog/avtootklik-hh/)

> ⚠️ **Дисклеймер.** Автоматические отклики на вакансии нарушают правила hh.ru —
> аккаунт могут ограничить. Держи разумные лимиты и используй на свой риск.
> Проект — для личного использования.

---

## Возможности

- 🔍 Каждые 5 минут ищет вакансии на **hh.ru (хх ру)** по твоим поисковым запросам (с пагинацией)
- 🎯 Оценивает каждую вакансию по правилам (заголовок, зарплата, стек, уровень) — без трат токенов
- 📨 Делает **автоотклик через официальный API hh** — ровным человеческим темпом (антибан)
- ✉️ Отправляет твоё сопроводительное письмо (задаётся в конфиге, одно на всех)
- 🧠 Опционально: если у вакансии тест/анкета — на вопросы отвечает ИИ (нужен LLM-ключ)
- 💬 Ловит сообщения рекрутёров и присылает тебе в Telegram
- 📊 Тянет статусы откликов: приглашения / отказы / без ответа
- ⬆️ Поднимает резюме в поиске hh
- 📱 Управление через меню бота: пауза, вкл/выкл автооткликов, статистика, логи

---

## Требования

- **Python 3.12+**
- Аккаунт на **hh.ru** с опубликованным резюме
- Телеграм-бот (токен из [@BotFather](https://t.me/BotFather))
- (опционально) ключ LLM-провайдера — только если нужно, чтобы ИИ проходил тесты работодателя

База — SQLite (файл). Ни Postgres, ни Redis, ни Docker ставить не нужно.

---

## Установка

```bash
git clone https://github.com/YAMAKAYAMACO/hh-autoresponder.git
cd hh-autoresponder

python -m venv .venv
# Windows:
.venv\Scripts\pip install -e .
.venv\Scripts\playwright install chromium
# macOS/Linux:
# .venv/bin/pip install -e .
# .venv/bin/playwright install chromium

cp .env.example .env      # затем открой .env и заполни
```

---

## Как настроить и включить автоотклики на hh.ru

Вся настройка — в файле `.env`, код трогать не нужно. Подробный разбор по шагам
с картинками — в статье-инструкции: **[как настроить автоотклик на hh.ru за вечер](https://pawetta.com/blog/avtootklik-hh/)**.

Обязательный минимум:

| Поле | Что это |
|---|---|
| `TG_BOT_TOKEN` | токен бота из [@BotFather](https://t.me/BotFather) |
| `TG_ADMIN_CHAT_ID` | твой числовой id из [@userinfobot](https://t.me/userinfobot) |
| `HH_LOGIN` / `HH_PASSWORD` | почта/телефон и пароль от hh.ru |

Дальше подгони под себя (уже с адекватными дефолтами):

- `SEARCH_QUERIES_RAW` — поисковые запросы через запятую (по каким вакансиям делать автоотклик)
- `COVER_LETTER` — текст сопроводительного письма (уходит всем)
- `TARGET_KEYWORDS_RAW` / `NEGATIVE_KEYWORDS_RAW` / `STACK_KEYWORDS_RAW` — правила отбора вакансий
- `DESIRED_SALARY_MIN` / `MAX`, `SALARY_FLOOR` — зарплатные ориентиры
- `APPLY_DELAY_MIN` / `MAX`, `MAX_APPLIES_PER_DAY_HH` — темп и дневной лимит откликов

Чтобы **включить автоотклики**, после запуска открой меню бота в Telegram и
переключи «Авто-отклики» в положение ВКЛ.

### ИИ — по желанию

По умолчанию `AI_ENABLED=false` — бот делает автоотклики без всякого ИИ. Если
хочешь, чтобы ИИ отвечал на анкеты/тесты работодателя, поставь `AI_ENABLED=true`
и укажи `LLM_API_KEY` (любой OpenAI-совместимый провайдер).

---

## Первый вход на hh (один раз)

```bash
.venv\Scripts\python manual_login.py     # Windows
# .venv/bin/python manual_login.py       # macOS/Linux
```

Откроется окно браузера — залогинься на hh руками (телефон/почта + пароль, при
необходимости SMS). Скрипт сам поймает вход и сохранит сессию. После этого
автоотклики работают сами.

---

## Запуск

```bash
.venv\Scripts\python -m app.main     # Windows
# .venv/bin/python -m app.main       # macOS/Linux
```

Дальше всё — через меню твоего бота в Telegram. Пока процесс запущен, бот делает
автоотклики. Автозапуск при старте системы настраивается штатными средствами ОС
(Планировщик задач / автозагрузка / systemd).

---

## Как это работает

```
поиск вакансий на hh.ru (каждые 5 мин)
        │
        ▼
отбор по правилам (rule-based скоринг, без токенов)
        │
        ▼
автоотклик через официальный API hh + сопроводительное письмо
        │
        ├─ если у вакансии тест/анкета → Playwright (+ ИИ, если включён)
        ▼
лог в Telegram + сводка по откликам
```

---

## FAQ

**Это бесплатно?** Да. Проект с открытым кодом (open-source), лицензия MIT.
Никаких подписок — в отличие от платных сервисов автооткликов.

**На какой площадке работает?** Только **hh.ru (хх ру)**. Отклики идут через
официальный API hh.

**Нужен ли ИИ / нейросеть?** Нет. Базовые автоотклики на вакансии работают без
всякого ИИ и без API-ключей. ИИ подключается только по желанию — чтобы отвечать
на тесты и анкеты работодателя.

**Не забанят ли аккаунт hh?** Автоматические отклики нарушают правила hh.ru, так
что риск есть. Бот шлёт отклики со случайными паузами и дневным лимитом, но
держи темп разумным и используй на свой риск.

**Чем отличается от онлайн-сервисов автооткликов?** Работает локально у тебя,
код открыт, данные никуда не уходят, настройки — полностью твои, платить не надо.

**Python нужен?** Да, Python 3.12+. Всё остальное ставится одной командой.

---

## См. также

- [digitaltraffic-detectai](https://github.com/YAMAKAYAMACO/digitaltraffic-detectai) — гуманизатор текста для Claude: очеловечить текст и убрать признаки ИИ из русского текста (бесплатно).
- Другие проекты автора: [github.com/YAMAKAYAMACO](https://github.com/YAMAKAYAMACO)

---

## Лицензия

[MIT](LICENSE) © Nikita Vikhrov

Полезное про digital-маркетинг, трафик и SEO — в моём Telegram-канале:
https://t.me/trafficisobar
