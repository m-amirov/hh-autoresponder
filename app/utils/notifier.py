"""Глобальный нотификатор в Telegram для подробного лога действий бота.

Воркеры (поиск/анализ/отклики) вызывают notifier.vlog(...) в ключевых точках.
Колбэк, реально отправляющий сообщение в TG, настраивается один раз в main.py.
"""
import structlog

log = structlog.get_logger()

_callback = None      # async fn(text) -> отправляет в Telegram
_verbose = True       # подробный лог включён


def configure(callback, verbose: bool = True):
    global _callback, _verbose
    _callback = callback
    _verbose = verbose


def set_verbose(value: bool):
    global _verbose
    _verbose = value


def is_verbose() -> bool:
    return _verbose


async def send(text: str):
    """Безусловно отправить сообщение (если колбэк настроен)."""
    if _callback is None:
        return
    try:
        await _callback(text)
    except Exception as e:
        log.warning("notifier_send_error", error=str(e)[:120])


async def vlog(text: str):
    """Детальный лог действия — отправляется только в verbose-режиме."""
    if _verbose:
        await send(text)
