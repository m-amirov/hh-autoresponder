"""
Оценка вакансии по правилам, без трат AI-токенов.

Балл складывается из явных сигналов: совпадение по заголовку, стек, зарплата,
удалёнка, уровень. Все ключевые слова задаются в .env:
  TARGET_KEYWORDS_RAW   — хотя бы одно в заголовке → вакансия подходит
  NEGATIVE_KEYWORDS_RAW — есть в заголовке → дисквалификация
  STACK_KEYWORDS_RAW    — каждое совпадение в тексте даёт бонус к баллу
  SALARY_FLOOR          — вакансии с указанной ЗП ниже отсеиваются
"""
from __future__ import annotations

import re

from app.config import settings

# Сигналы уровня (для небольшого бонуса)
LEVEL_MIDDLE = [r"\bmiddle\b", r"\bmid\b", r"\bсредн"]
LEVEL_SENIOR = [
    r"\bsenior\b", r"\bстарш", r"\bлид\b", r"\blead\b", r"\bhead\b",
    r"руководител", r"директор", r"начальник", r"глава",
]


def _match_any_re(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def _contains_any(text: str, words: list[str]) -> bool:
    return any(w.lower() in text for w in words)


def analyze_vacancy(
    title: str,
    description: str = "",
    skills: str = "",
    salary_from: int | None = None,
    salary_to: int | None = None,
    is_remote: bool = False,
    salary_currency: str = "",
    desired_salary_min: int = 150000,
    desired_salary_max: int = 400000,
) -> dict:
    t = (title or "").lower()
    d = (description or "").lower()
    s_skills = (skills or "").lower()
    full = f"{t}\n{d}\n{s_skills}"

    red_flags: list[str] = []

    # 1. Заголовок должен содержать хотя бы одно целевое слово
    if not _contains_any(t, settings.target_keywords):
        return {
            "score": 0, "reason": "Заголовок не соответствует целевым словам",
            "is_relevant": False, "seniority": "unknown",
            "red_flags": ["title_mismatch"], "stack_match": 0,
        }

    # 2. Стоп-слова в заголовке — дисквалификация
    if _contains_any(t, settings.negative_keywords):
        return {
            "score": 0, "reason": "Дисквалифицировано стоп-словом",
            "is_relevant": False, "seniority": "unknown",
            "red_flags": ["negative_keyword"], "stack_match": 0,
        }

    # 3. Зарплата ниже порога (если указана и в рублях) — отсеиваем
    cur = (salary_currency or "").upper()
    if (salary_from or salary_to) and cur in ("", "RUR", "RUB", "РУБ"):
        best = max(salary_from or 0, salary_to or 0)
        if 0 < best < settings.salary_floor:
            return {
                "score": 0, "reason": f"Зарплата {best} ниже порога {settings.salary_floor}",
                "is_relevant": False, "seniority": "unknown",
                "red_flags": ["salary_below_floor"], "stack_match": 0,
            }

    # 4. Считаем балл
    score = 30  # совпал заголовок
    stack_hits = sum(1 for kw in settings.stack_keywords if kw.lower() in full)
    stack_score = min(stack_hits * 5, 40)
    score += stack_score

    # Зарплата
    if salary_from or salary_to:
        if salary_from and salary_to:
            sal_mid = (salary_from + salary_to) // 2
        else:
            sal_mid = salary_from or salary_to or 0
        if sal_mid >= desired_salary_min:
            score += 15
        elif sal_mid >= desired_salary_min * 0.7:
            score += 5
        else:
            red_flags.append("low_salary")

    # Удалёнка
    if is_remote or "удалён" in d or "удален" in d or "remote" in d:
        score += 5

    # Уровень
    seniority = "middle"
    is_senior = _match_any_re(full, LEVEL_SENIOR)
    is_middle = _match_any_re(full, LEVEL_MIDDLE)
    if is_senior and not is_middle:
        seniority = "senior"
        score += 5
    elif is_middle:
        score += 10

    score = max(0, min(score, 100))

    return {
        "score": score,
        "reason": f"title=ok, stack={stack_hits}({stack_score}p), level={seniority}",
        "is_relevant": score >= 60,
        "seniority": seniority,
        "red_flags": red_flags,
        "stack_match": stack_score * 100 // 40 if stack_score else 0,
    }
