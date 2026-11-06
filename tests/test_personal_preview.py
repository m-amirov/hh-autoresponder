"""Regression tests for the fail-closed personal preview mode.

No test sends requests to hh.ru, Telegram or an LLM provider.
"""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.config import Settings, settings
from app.ai.rule_analyzer import analyze_vacancy
from app.models.vacancy import Vacancy
from app.models.vacancy import VacancyStatus
from app.parsers.hh_oauth import hh_oauth
from app.workers.apply_worker import run_auto_apply
from app.workers.scheduler import WorkerScheduler


def test_personal_profile_defaults_to_selected_roles_and_scopes():
    cfg = Settings(_env_file=None)
    assert cfg.preview_only is True
    assert "делопроизводитель" in cfg.search_queries
    assert "методист" in cfg.search_queries
    assert cfg.search_scopes == [
        {"remote": True, "area": "113"},
        {"remote": False, "area": "72"},
    ]
    assert cfg.salary_floor == 0
    assert cfg.check_interval_sec == 1800
    assert cfg.search_pages_per_query == 1
    assert cfg.max_applies_per_day_hh < 200


def test_disabling_both_scopes_never_falls_back_to_whole_country():
    cfg = Settings(_env_file=None, search_remote_russia=False, search_local_area_enabled=False)
    assert cfg.search_scopes == []


@pytest.mark.parametrize("title,expected", [
    ("Делопроизводитель", True),
    ("Методист образовательного центра", True),
    ("Специалист по документообороту", True),
    ("Специалист учебно-методического отдела", True),
    ("Руководитель отдела продаж", False),
])
def test_target_roles_are_recognized(title, expected, monkeypatch):
    monkeypatch.setattr(settings, "target_keywords_raw", Settings(_env_file=None).target_keywords_raw)
    monkeypatch.setattr(settings, "negative_keywords_raw", "")
    monkeypatch.setattr(settings, "salary_floor", 0)
    result = analyze_vacancy(title, desired_salary_min=0)
    assert result["is_relevant"] is expected


def test_rule_analyzer_rejects_wrong_title_and_low_salary(monkeypatch):
    monkeypatch.setattr(settings, "target_keywords_raw", "аналитик")
    monkeypatch.setattr(settings, "negative_keywords_raw", "стажёр")
    monkeypatch.setattr(settings, "salary_floor", 100000)

    assert analyze_vacancy("Маркетолог")["score"] == 0
    assert analyze_vacancy("Аналитик-стажёр")["score"] == 0
    assert analyze_vacancy("Системный аналитик", salary_from=40000, salary_to=80000, salary_currency="RUR")["score"] == 0


def test_matching_title_is_relevant_without_optional_stack(monkeypatch):
    monkeypatch.setattr(settings, "target_keywords_raw", "аналитик")
    monkeypatch.setattr(settings, "negative_keywords_raw", "")
    monkeypatch.setattr(settings, "stack_keywords_raw", "")
    monkeypatch.setattr(settings, "salary_floor", 0)
    result = analyze_vacancy("Системный аналитик", desired_salary_min=0)
    assert result["score"] >= settings.min_relevance_score
    assert result["is_relevant"] is True


@pytest.mark.asyncio
async def test_auto_apply_is_disabled_before_any_network_or_db(monkeypatch):
    monkeypatch.setattr(settings, "preview_only", True)
    assert await run_auto_apply(auto_mode=True, min_score=0) == 0


@pytest.mark.asyncio
async def test_oauth_apply_is_disabled_before_getting_credentials(monkeypatch):
    monkeypatch.setattr(settings, "preview_only", True)
    monkeypatch.setattr(hh_oauth, "get_token", AsyncMock(side_effect=AssertionError("network/auth must not run")))
    result, info = await hh_oauth.apply("12345", "hello")
    assert result is False
    assert info == {"error": "preview_only"}


@pytest.mark.asyncio
async def test_other_oauth_mutations_are_blocked(monkeypatch):
    monkeypatch.setattr(settings, "preview_only", True)
    monkeypatch.setattr(hh_oauth, "get_token", AsyncMock(side_effect=AssertionError("network/auth must not run")))
    assert (await hh_oauth.bump_resumes())["error"] == "preview_only"
    assert (await hh_oauth.clear_negotiations())["error"] == "preview_only"


@pytest.mark.asyncio
async def test_playwright_apply_is_disabled_before_opening_browser(monkeypatch):
    from app.parsers.hh_playwright import HHPlaywright

    monkeypatch.setattr(settings, "preview_only", True)
    pw = HHPlaywright()
    monkeypatch.setattr(pw, "_get_page", AsyncMock(side_effect=AssertionError("browser must not open")))
    assert await pw.apply_to_vacancy("https://hh.ru/vacancy/123", "text") is False


def test_scheduler_ignores_unsafe_persisted_flags(monkeypatch, tmp_path):
    import json
    from app.workers import scheduler as sched_module

    state_file = tmp_path / "scheduler_state.json"
    state_file.write_text(json.dumps({
        "auto_apply": True, "pass_tests": True, "notify_messages": True,
        "thank_rejections": True, "bump_resume": True,
    }))
    monkeypatch.setattr(sched_module, "STATE_FILE", state_file)
    monkeypatch.setattr(settings, "preview_only", True)
    scheduler = WorkerScheduler()
    assert all(value is False for value in scheduler.get_flags().values())
    scheduler.set_auto_apply(True)
    scheduler.set_flag("bump_resume", True)
    assert scheduler.auto_apply is False
    assert scheduler.bump_resume is False
    saved = json.loads(state_file.read_text())
    assert saved["auto_apply"] is False
    assert saved["pass_tests"] is False


@pytest.mark.asyncio
async def test_search_forwards_user_region_and_remote_filter(monkeypatch):
    from app.workers import vacancy_worker

    monkeypatch.setattr(settings, "target_keywords_raw", "аналитик")
    monkeypatch.setattr(settings, "search_area_id", "72")
    monkeypatch.setattr(settings, "search_remote_russia", True)
    monkeypatch.setattr(settings, "search_local_area_enabled", True)
    monkeypatch.setattr(vacancy_worker, "SEARCH_QUERIES", ["аналитик"])
    parser = SimpleNamespace(login=AsyncMock(return_value=True), search_vacancies=AsyncMock(return_value=[]))
    monkeypatch.setattr(vacancy_worker, "PARSERS", {"hh": parser})
    monkeypatch.setattr(vacancy_worker, "_save_vacancies", AsyncMock(return_value=0))
    monkeypatch.setattr(vacancy_worker, "random_delay", AsyncMock())

    assert await vacancy_worker.run_vacancy_search() == 0
    assert parser.search_vacancies.await_count == 2
    assert [c.kwargs for c in parser.search_vacancies.await_args_list] == [
        {"remote": True, "area": "113", "pages": 1},
        {"remote": False, "area": "72", "pages": 1},
    ]


@pytest.mark.asyncio
async def test_analysis_rejects_nonmatching_vacancies(monkeypatch):
    from app.workers import vacancy_worker
    from app.utils import notifier

    monkeypatch.setattr(settings, "target_keywords_raw", "аналитик")
    monkeypatch.setattr(settings, "negative_keywords_raw", "")
    monkeypatch.setattr(settings, "stack_keywords_raw", "")
    monkeypatch.setattr(settings, "salary_floor", 0)
    monkeypatch.setattr(settings, "min_relevance_score", 60)

    valid = Vacancy(id=1, title="Системный аналитик", status=VacancyStatus.NEW, url="https://hh.ru/vacancy/1")
    invalid = Vacancy(id=2, title="Менеджер продаж", status=VacancyStatus.NEW, url="https://hh.ru/vacancy/2")
    vacancies = {1: valid, 2: invalid}

    class FakeResult:
        def scalars(self):
            return self
        def all(self):
            return list(vacancies.values())

    class FakeSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *_):
            return False
        async def execute(self, *_):
            return FakeResult()
        async def get(self, _, vacancy_id):
            return vacancies[vacancy_id]
        async def commit(self):
            pass

    monkeypatch.setattr(vacancy_worker, "async_session", lambda: FakeSession())
    monkeypatch.setattr(notifier, "vlog", AsyncMock())
    assert await vacancy_worker.run_vacancy_analysis() == 2
    assert valid.status == VacancyStatus.APPROVED
    assert invalid.status == VacancyStatus.REJECTED


@pytest.mark.asyncio
async def test_telegram_preview_never_calls_apply_or_ai(monkeypatch):
    from app.bot import handlers

    monkeypatch.setattr(settings, "preview_only", True)
    monkeypatch.setattr(handlers.claude_ai, "generate_cover_letter", AsyncMock(side_effect=AssertionError("AI must not run")))
    vacancy = Vacancy(id=1, title="Аналитик", url="https://hh.ru/vacancy/12345", description="")

    class FakeSession:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *_):
            return False
        async def get(self, *_):
            return vacancy

    monkeypatch.setattr(handlers, "async_session", lambda: FakeSession())
    sent = []

    async def message_answer(text, **kwargs):
        sent.append((text, kwargs))

    callback = SimpleNamespace(
        data="apply:1", answer=AsyncMock(),
        message=SimpleNamespace(answer=message_answer),
    )
    await handlers.cb_apply.__wrapped__(callback)
    assert len(sent) == 1
    assert "Отклик не отправлен" in sent[0][0]
    assert sent[0][1]["reply_markup"].inline_keyboard[0][0].url == vacancy.url


@pytest.mark.asyncio
async def test_stale_telegram_confirm_callback_cannot_send(monkeypatch):
    from app.bot import handlers

    monkeypatch.setattr(settings, "preview_only", True)
    callback = SimpleNamespace(data="confirm_apply:1", answer=AsyncMock(), message=None)
    await handlers.cb_confirm_apply.__wrapped__(callback)
    callback.answer.assert_awaited_once()


def test_preview_keyboard_hides_mutations(monkeypatch):
    from app.bot.keyboards import settings_keyboard, vacancy_keyboard

    monkeypatch.setattr(settings, "preview_only", True)
    buttons = [button for row in settings_keyboard().inline_keyboard for button in row]
    assert {button.callback_data for button in buttons} == {"toggle_pause", "force_search"}
    vacancy_buttons = [button for row in vacancy_keyboard(1).inline_keyboard for button in row]
    assert any("Письмо" in button.text for button in vacancy_buttons)
