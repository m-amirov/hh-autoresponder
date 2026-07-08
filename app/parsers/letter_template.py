"""
Сопроводительное письмо для откликов.

Текст письма задаётся в .env (COVER_LETTER) — одно и то же уходит всем
работодателям. AI на письма не тратится.
"""
from __future__ import annotations

from app.config import settings


def render_letter(vacancy_name: str = "", template: str | None = None) -> str:
    """Единое письмо для всех откликов (из настройки COVER_LETTER)."""
    return settings.cover_letter
