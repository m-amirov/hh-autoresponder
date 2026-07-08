import json

import httpx
import structlog

from app.config import settings
from app.ai.prompts import (
    SYSTEM_REPLY_GENERATOR,
    SYSTEM_SENTIMENT_ANALYZER,
)

log = structlog.get_logger()

MODEL = settings.llm_model
# Модель для прохождения тестов вакансий (ответы на вопросы/тесты работодателя)
TEST_MODEL = settings.llm_model


def _ai_ready() -> bool:
    """AI используется только если включён и задан ключ."""
    return bool(settings.ai_enabled and settings.llm_api_key)


class ClaudeAI:
    """Опциональный LLM-помощник (OpenAI-совместимый эндпоинт, напр. polza.ai).

    Нужен ТОЛЬКО для прохождения тестов/анкет работодателя и ответов рекрутёрам.
    Если AI выключен (AI_ENABLED=false или нет ключа) — методы возвращают
    безопасные заглушки, бот продолжает откликаться без AI.
    """

    def __init__(self):
        self._client = httpx.AsyncClient(
            base_url=settings.llm_base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            timeout=httpx.Timeout(120.0),
        )
        self._floor = settings.llm_max_tokens_floor

    def reset_fallback(self):  # совместимость со старым интерфейсом
        pass

    async def _call(self, system: str, user_message: str, max_tokens: int = 1024, model: str | None = None) -> tuple[str, int, int]:
        if not _ai_ready():
            return "", 0, 0
        # Reasoning-модели тратят часть бюджета max_tokens на «мысли» — держим
        # щедрый нижний порог, иначе видимый ответ приходит пустым.
        if max_tokens < self._floor:
            max_tokens = self._floor
        payload = {
            "model": model or MODEL,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
        }
        try:
            resp = await self._client.post("/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            log.warning("llm_call_error", error=str(e)[:150])
            return "", 0, 0
        choice = (data.get("choices") or [{}])[0]
        text = (choice.get("message") or {}).get("content") or ""
        usage = data.get("usage") or {}
        return text, int(usage.get("prompt_tokens", 0) or 0), int(usage.get("completion_tokens", 0) or 0)

    async def generate_cover_letter(self, vacancy_title: str, vacancy_description: str, company_name: str = "") -> tuple[str, int, int]:
        # Письмо не генерится AI — всем уходит фиксированный текст из настроек.
        return settings.cover_letter, 0, 0

    async def generate_reply(self, recruiter_message: str, vacancy_context: str = "", platform: str = "") -> tuple[str, int, int]:
        if not _ai_ready():
            return "", 0, 0
        system = SYSTEM_REPLY_GENERATOR.format(
            resume=settings.resume_text,
            salary_min=settings.desired_salary_min,
            salary_max=settings.desired_salary_max,
            platform="hh.ru",
        )
        user_msg = f"Сообщение рекрутера:\n{recruiter_message}\n\nКонтекст вакансии:\n{vacancy_context}"
        text, inp_tok, out_tok = await self._call(system, user_msg, max_tokens=512)
        return text.strip(), inp_tok, out_tok

    async def analyze_sentiment(self, message: str) -> dict:
        default = {"sentiment": "neutral", "intent": "info", "urgency": "low", "summary": message[:100]}
        if not _ai_ready():
            return default
        text, _, _ = await self._call(SYSTEM_SENTIMENT_ANALYZER, message, max_tokens=256)
        try:
            clean = text.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(clean)
        except (json.JSONDecodeError, IndexError):
            return default


claude_ai = ClaudeAI()
