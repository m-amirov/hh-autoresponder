"""
Ручной вход на hh.ru под Windows (без Xvfb/VNC).

Открывает обычное окно Chromium, ты логинишься руками (телефон + пароль,
при необходимости — SMS/капча). Скрипт сам замечает успешный вход и
сохраняет сессию в data/browser_sessions/hh_state.json — оттуда её берёт бот.

Запуск:
    .venv\\Scripts\\python.exe manual_login_win.py
"""
import asyncio
import json
from pathlib import Path


async def main():
    from playwright.async_api import async_playwright

    storage_path = Path("data/browser_sessions/hh_state.json")

    pw = await async_playwright().start()

    launch_args = [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
    ]

    # headless=False — окно браузера появится у тебя на экране
    browser = await pw.chromium.launch(headless=False, args=launch_args)

    ctx_opts = {
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "viewport": {"width": 1200, "height": 680},
        "locale": "ru-RU",
        "timezone_id": "Europe/Moscow",
    }
    if storage_path.exists():
        ctx_opts["storage_state"] = str(storage_path)
        print(f"Загрузил прежние cookies из {storage_path}")

    ctx = await browser.new_context(**ctx_opts)
    await ctx.add_init_script(
        """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        window.chrome = {runtime: {}};
        """
    )

    page = await ctx.new_page()
    await page.goto("https://hh.ru/account/login", wait_until="domcontentloaded")

    print("\n" + "=" * 55)
    print("Открылось окно браузера на странице входа hh.ru.")
    print("Залогинься руками (телефон + пароль, при необходимости SMS).")
    print("Скрипт сам поймает вход и сохранит сессию. Не закрывай окно.")
    print("=" * 55 + "\n")

    while True:
        await asyncio.sleep(5)
        try:
            check_url = page.url
            if "/account/login" in check_url:
                continue
            login_btn = await page.query_selector('[data-qa="login"]')
            if login_btn:
                continue
            avatar = await page.query_selector('[data-qa="mainmenu-user"], button[data-qa*="user"]')
            resumes_link = await page.query_selector('[data-qa="mainmenu_myResumes"]')
            applicant_profile = await page.query_selector('[data-qa="mainmenu_applicantProfile"]')
            if avatar or resumes_link or applicant_profile:
                print("\nВход обнаружен! Сохраняю cookies...")
                state = await ctx.storage_state()
                storage_path.parent.mkdir(parents=True, exist_ok=True)
                storage_path.write_text(json.dumps(state), encoding="utf-8")
                print(f"Сессия сохранена: {storage_path}")
                await page.goto("https://hh.ru", wait_until="domcontentloaded")
                await asyncio.sleep(3)
                state = await ctx.storage_state()
                storage_path.write_text(json.dumps(state), encoding="utf-8")
                print("Финальное сохранение готово.")
                break
        except Exception:
            pass

    await asyncio.sleep(2)
    await browser.close()
    await pw.stop()

    print("\nГотово! Теперь запускай бота:  .venv\\Scripts\\python.exe -m app.main")


if __name__ == "__main__":
    asyncio.run(main())
