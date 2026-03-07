"""
Focused tests for timer email/notification alert behavior.
"""

import asyncio
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock

import pytest

import app.timer_engine as timer_engine
import app.timezone_utils as timezone_utils
import app.wifi_detector as wifi_detector


def _build_active_doc(
    *,
    total_minutes: int,
    completed_4h: bool,
    pre_leave_email_sent_at=None,
    completion_email_sent_at=None,
    completion_desktop_sent_at=None,
    start_utc: datetime | None = None,
) -> dict:
    return {
        "date": "07-03-2026",
        "is_active": True,
        "has_network_access": True,
        "completed_4h": completed_4h,
        "total_minutes": total_minutes,
        "current_session_start": None,
        "first_session_start_utc": start_utc,
        "pre_leave_email_sent_at": pre_leave_email_sent_at,
        "completion_email_sent_at": completion_email_sent_at,
        "completion_desktop_sent_at": completion_desktop_sent_at,
    }


async def _run_timer_for_iterations(
    monkeypatch: pytest.MonkeyPatch,
    *,
    store: object,
    docs: list[dict],
    target_minutes: int,
    email_sender: MagicMock,
    desktop_sender: MagicMock,
) -> None:
    get_active_session = AsyncMock(side_effect=docs)
    setattr(store, "get_active_session", get_active_session)

    monkeypatch.setattr(timer_engine, "get_mongo_store", lambda: store)
    monkeypatch.setattr(timer_engine, "_resolve_target_minutes", lambda: target_minutes)
    monkeypatch.setattr(timer_engine, "send_email_notification", email_sender)
    monkeypatch.setattr(timer_engine, "send_notification", desktop_sender)
    monkeypatch.setattr(timezone_utils, "get_today_date_ist", lambda: "07-03-2026")
    monkeypatch.setattr(wifi_detector, "get_current_ssid", lambda use_cache=True: "OfficeWiFi")
    monkeypatch.setattr(wifi_detector, "is_office_ssid", lambda ssid: True)

    async def _fake_to_thread(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    monkeypatch.setattr(timer_engine.asyncio, "to_thread", _fake_to_thread)

    iterations = len(docs)
    sleep_effects = [None] * iterations + [asyncio.CancelledError()]
    monkeypatch.setattr(
        timer_engine.asyncio,
        "sleep",
        AsyncMock(side_effect=sleep_effects),
    )

    with pytest.raises(asyncio.CancelledError):
        await timer_engine.timer_polling_loop()


@pytest.mark.asyncio
async def test_pre_alert_email_sent_once_when_remaining_is_10(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sends exactly one pre-leave email inside the <=10 minute window."""
    start_utc = datetime(2026, 3, 7, 4, 0, 0, tzinfo=UTC)
    store = MagicMock()
    store.update_elapsed_time = AsyncMock(return_value=False)
    store.end_session = AsyncMock()
    store.mark_completed = AsyncMock()
    store.mark_pre_leave_email_sent = AsyncMock(return_value=True)
    store.mark_completion_email_sent = AsyncMock(return_value=True)
    store.mark_completion_desktop_sent = AsyncMock(return_value=True)

    docs = [
        _build_active_doc(
            total_minutes=240,
            completed_4h=False,
            start_utc=start_utc,
        )
    ]
    email_sender = MagicMock(return_value=True)
    desktop_sender = MagicMock(return_value=True)

    await _run_timer_for_iterations(
        monkeypatch,
        store=store,
        docs=docs,
        target_minutes=250,
        email_sender=email_sender,
        desktop_sender=desktop_sender,
    )

    assert email_sender.call_count == 1
    subject, message, html_message = email_sender.call_args.args
    assert subject == "WiFi Tracker: 10 minutes to leave"
    assert "Came office at / Start time:" in message
    assert "Duration complete:" in message
    assert "You can leave in 10 mins with end time:" in message
    assert "<html" in html_message.lower()
    assert "10 minutes to leave" in html_message.lower()
    desktop_sender.assert_not_called()
    store.mark_pre_leave_email_sent.assert_awaited_once()
    store.mark_completion_email_sent.assert_not_awaited()
    store.mark_completion_desktop_sent.assert_not_awaited()


@pytest.mark.asyncio
async def test_pre_alert_not_sent_outside_window(monkeypatch: pytest.MonkeyPatch) -> None:
    """Does not send pre-alert when remaining time is above 10 minutes."""
    store = MagicMock()
    store.update_elapsed_time = AsyncMock(return_value=False)
    store.end_session = AsyncMock()
    store.mark_completed = AsyncMock()
    store.mark_pre_leave_email_sent = AsyncMock(return_value=True)
    store.mark_completion_email_sent = AsyncMock(return_value=True)
    store.mark_completion_desktop_sent = AsyncMock(return_value=True)

    docs = [_build_active_doc(total_minutes=239, completed_4h=False)]
    email_sender = MagicMock(return_value=True)
    desktop_sender = MagicMock(return_value=True)

    await _run_timer_for_iterations(
        monkeypatch,
        store=store,
        docs=docs,
        target_minutes=250,
        email_sender=email_sender,
        desktop_sender=desktop_sender,
    )

    email_sender.assert_not_called()
    desktop_sender.assert_not_called()
    store.mark_pre_leave_email_sent.assert_not_awaited()


@pytest.mark.asyncio
async def test_completion_sends_email_and_desktop(monkeypatch: pytest.MonkeyPatch) -> None:
    """At completion threshold, send completion email + desktop and persist sent flags."""
    store = MagicMock()
    store.update_elapsed_time = AsyncMock(return_value=False)
    store.end_session = AsyncMock()
    store.mark_completed = AsyncMock()
    store.mark_pre_leave_email_sent = AsyncMock(return_value=True)
    store.mark_completion_email_sent = AsyncMock(return_value=True)
    store.mark_completion_desktop_sent = AsyncMock(return_value=True)

    docs = [_build_active_doc(total_minutes=250, completed_4h=False)]
    email_sender = MagicMock(return_value=True)
    desktop_sender = MagicMock(return_value=True)

    await _run_timer_for_iterations(
        monkeypatch,
        store=store,
        docs=docs,
        target_minutes=250,
        email_sender=email_sender,
        desktop_sender=desktop_sender,
    )

    store.mark_completed.assert_awaited_once_with("07-03-2026")
    desktop_sender.assert_called_once()
    email_sender.assert_called_once()
    completion_subject, completion_message, completion_html = email_sender.call_args.args
    assert completion_subject == "WiFi Tracker: Target completed"
    assert "Came office at / Start time:" in completion_message
    assert "Duration complete:" in completion_message
    assert "Target completed at:" in completion_message
    assert "<html" in completion_html.lower()
    assert "target completed" in completion_html.lower()
    store.mark_completion_desktop_sent.assert_awaited_once()
    store.mark_completion_email_sent.assert_awaited_once()


@pytest.mark.asyncio
async def test_completion_not_resent_when_sent_flags_exist(monkeypatch: pytest.MonkeyPatch) -> None:
    """Restart-safe: when sent flags exist, no duplicate completion alerts are sent."""
    sent_at = datetime(2026, 3, 7, 10, 0, 0, tzinfo=UTC)
    store = MagicMock()
    store.update_elapsed_time = AsyncMock(return_value=False)
    store.end_session = AsyncMock()
    store.mark_completed = AsyncMock()
    store.mark_pre_leave_email_sent = AsyncMock(return_value=True)
    store.mark_completion_email_sent = AsyncMock(return_value=True)
    store.mark_completion_desktop_sent = AsyncMock(return_value=True)

    docs = [
        _build_active_doc(
            total_minutes=260,
            completed_4h=True,
            completion_email_sent_at=sent_at,
            completion_desktop_sent_at=sent_at,
        )
    ]
    email_sender = MagicMock(return_value=True)
    desktop_sender = MagicMock(return_value=True)

    await _run_timer_for_iterations(
        monkeypatch,
        store=store,
        docs=docs,
        target_minutes=250,
        email_sender=email_sender,
        desktop_sender=desktop_sender,
    )

    email_sender.assert_not_called()
    desktop_sender.assert_not_called()
    store.mark_completion_email_sent.assert_not_awaited()
    store.mark_completion_desktop_sent.assert_not_awaited()


@pytest.mark.asyncio
async def test_completion_retries_only_unsent_channel(monkeypatch: pytest.MonkeyPatch) -> None:
    """If one completion channel already sent, retry only the unsent channel."""
    sent_at = datetime(2026, 3, 7, 10, 0, 0, tzinfo=UTC)
    store = MagicMock()
    store.update_elapsed_time = AsyncMock(return_value=False)
    store.end_session = AsyncMock()
    store.mark_completed = AsyncMock()
    store.mark_pre_leave_email_sent = AsyncMock(return_value=True)
    store.mark_completion_email_sent = AsyncMock(return_value=True)
    store.mark_completion_desktop_sent = AsyncMock(return_value=True)

    docs = [
        _build_active_doc(total_minutes=260, completed_4h=True),
        _build_active_doc(
            total_minutes=261,
            completed_4h=True,
            completion_desktop_sent_at=sent_at,
        ),
    ]
    email_sender = MagicMock(side_effect=[False, True])
    desktop_sender = MagicMock(return_value=True)

    await _run_timer_for_iterations(
        monkeypatch,
        store=store,
        docs=docs,
        target_minutes=250,
        email_sender=email_sender,
        desktop_sender=desktop_sender,
    )

    # Desktop is sent in first cycle only, then skipped because second doc has sent marker.
    assert desktop_sender.call_count == 1
    # Email failed first cycle and retried on second cycle.
    assert email_sender.call_count == 2
    store.mark_completion_desktop_sent.assert_awaited_once()
    store.mark_completion_email_sent.assert_awaited_once()
