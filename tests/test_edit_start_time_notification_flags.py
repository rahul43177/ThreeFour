"""
Regression tests for edit-start-time notification flag reset behavior.
"""

from datetime import datetime, UTC
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

import app.main as main


@pytest.mark.asyncio
async def test_edit_start_time_resets_notification_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    """Successful start-time edit must reset daily notification sent flags."""
    mock_store = AsyncMock()
    mock_store.get_daily_status.return_value = {
        "date": "07-03-2026",
        "total_minutes": 180,
        "completed_4h": False,
        "session_start_total_minutes": 180,
        "current_session_start": datetime(2026, 3, 7, 4, 0, 0, tzinfo=UTC),
        "first_session_start_utc": datetime(2026, 3, 7, 4, 0, 0, tzinfo=UTC),
    }
    mock_store.update_first_session_start.return_value = True
    mock_store.reset_notification_flags.return_value = True
    monkeypatch.setattr(main, "_mongo_store", mock_store)

    payload = {
        "date": "07-03-2026",
        "new_start_time_ist": "10:00 AM",
    }

    async with AsyncClient(
        transport=ASGITransport(app=main.app),
        base_url="http://test",
    ) as client:
        response = await client.post("/api/session/edit-start-time", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    mock_store.reset_notification_flags.assert_awaited_once_with("07-03-2026")
