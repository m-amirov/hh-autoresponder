from pathlib import Path

from pydantic_settings import BaseSettings


def _split(s: str) -> list[str]:
    """Разбить строку 'a, b, c' в список ['a','b','c'] (пустые — выбросить)."""
    return [x.strip() for x in (s or "").split(",") if x.strip()]


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    # ── Telegram ──────────────────────────────────────────────
    tg_bot_token: str = ""            # токен бота из @BotFather
    tg_admin_chat_id: str = ""        # твой numeric id из @userinfobot
    tg_api_server: str = ""
    tg_proxy: str = ""                # socks5://user:pass@host:port (опц.)

    # Безопасный режим личного помощника: никаких действий в аккаунте hh.ru.
    # Бот только ищет вакансии и готовит письма для ручной отправки.
    preview_only: bool = True

    # ── LLM (опционально: только для прохождения тестов работодателя) ──
    ai_enabled: bool = False
    llm_base_url: str = "https://api.polza.ai/api/v1"   # OpenAI-совместимый эндпоинт
    llm_api_key: str = ""
    llm_model: str = "deepseek/deepseek-v4-flash"
    llm_max_tokens_floor: int = 2000

    # ── hh.ru ─────────────────────────────────────────────────
    hh_login: str = ""
    hh_password: str = ""
    hh_resume_id: str = ""            # id резюме (подставится автоматически при первом входе)

    # ── Профиль и цель ────────────────────────────────────────
    desired_position: str = "Делопроизводитель / методист"
    desired_salary_min: int = 0
    desired_salary_max: int = 0
    resume_text_path: str = "configs/resume.txt"

    # ── Поисковые запросы (через запятую) ─────────────────────
    search_queries_raw: str = (
        "делопроизводитель, методист, специалист по документообороту, "
        "специалист учебно-методического отдела"
    )
    search_remote_russia: bool = True
    search_country_area_id: str = "113"  # Россия в справочнике hh.ru
    search_local_area_enabled: bool = True
    search_area_id: str = "72"         # Пермь (город), не весь Пермский край
    search_pages_per_query: int = 1
    min_relevance_score: int = 60

    # ── Скоринг вакансий (всё через запятую) ──────────────────
    # target_keywords — если ХОТЯ БЫ одно слово есть в заголовке, вакансия подходит.
    target_keywords_raw: str = "делопроизвод, методист, документооборот, учебно-методич"
    # negative_keywords — если слово есть в заголовке, вакансия отсеивается сразу.
    negative_keywords_raw: str = ""
    # stack_keywords — каждое совпадение в тексте добавляет баллы (бонус).
    stack_keywords_raw: str = ""
    salary_floor: int = 0             # 0 — не отсеивать по зарплате

    # ── Сопроводительное письмо (одно на всех) ────────────────
    cover_letter: str = (
        "Здравствуйте! Меня заинтересовала ваша вакансия. "
        "Буду рад(а) обсудить требования и рассказать о своём опыте."
    )

    # ── Темп / антибан ────────────────────────────────────────
    check_interval_sec: int = 1800
    browser_headless: bool = True
    proxy_url: str = ""
    min_delay_sec: int = 3
    max_delay_sec: int = 12
    apply_delay_min: int = 40         # пауза между откликами, сек (низ)
    apply_delay_max: int = 68         # пауза между откликами, сек (верх)
    type_delay_min: int = 30
    type_delay_max: int = 120
    max_applies_per_day_hh: int = 5   # дополнительная защита вне preview_only

    # ── База ──────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///data/jobhunter.db"

    # ── Уведомления (тихие часы, МСК) ─────────────────────────
    notify_hour_start: int = 9
    notify_hour_end: int = 22

    # ── Производные значения ──────────────────────────────────
    @property
    def search_queries(self) -> list[str]:
        return _split(self.search_queries_raw) or ([self.desired_position] if self.desired_position.strip() else [])

    @property
    def search_scopes(self) -> list[dict[str, str | bool]]:
        """OR: remote vacancies nationwide + all formats in the configured city."""
        scopes: list[dict[str, str | bool]] = []
        if self.search_remote_russia and self.search_country_area_id.strip():
            scopes.append({"remote": True, "area": self.search_country_area_id.strip()})
        if self.search_local_area_enabled and self.search_area_id.strip():
            scopes.append({"remote": False, "area": self.search_area_id.strip()})
        return scopes

    @property
    def target_keywords(self) -> list[str]:
        return _split(self.target_keywords_raw)

    @property
    def negative_keywords(self) -> list[str]:
        return _split(self.negative_keywords_raw)

    @property
    def stack_keywords(self) -> list[str]:
        return _split(self.stack_keywords_raw)

    @property
    def max_applies_per_day(self) -> int:
        return self.max_applies_per_day_hh

    @property
    def resume_text(self) -> str:
        p = Path(self.resume_text_path)
        if p.exists():
            return p.read_text(encoding="utf-8")
        return ""


settings = Settings()
