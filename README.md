# ThreeFour (DailyFour) - Office Wi-Fi Time Tracker

Automatic office-time tracking on macOS, driven by Wi-Fi SSID detection and persisted in MongoDB.

## Overview

This application starts and pauses tracking automatically based on your office Wi-Fi and network connectivity, stores daily cumulative sessions in MongoDB, and exposes a dashboard + API for live status and analytics.

Recent enhancements include:

- MongoDB-first architecture for daily session tracking
- Restart-safe notification deduplication in `daily_sessions`
- Two-stage email flow: pre-leave reminder and completion email
- Styled HTML emails with plain-text fallback
- Completion notifications on macOS and browser
- Test mode database isolation (`MONGODB_TEST_DATABASE`)

## Core Behavior

### Session Lifecycle

- Session starts when current SSID matches `OFFICE_WIFI_NAME`
- Session enters grace period on SSID disconnect (`GRACE_PERIOD_MINUTES`)
- Timer pauses during captive-portal/re-auth when internet is unavailable
- Session automatically recovers after app restart when possible
- Day rollover and stale active sessions are closed safely

### Timer Target

- Production target: `WORK_DURATION_HOURS * 60 + BUFFER_MINUTES` (default: `4h 10m`)
- Test target: `TEST_DURATION_MINUTES` when `TEST_MODE=true`
- Daily tracking is cumulative: multiple office visits in one day aggregate into one daily total

### Notification Flow

Notification state is persisted in MongoDB per day:

- `pre_leave_email_sent_at`
- `completion_email_sent_at`
- `completion_desktop_sent_at`

Alert rules:

1. Pre-leave email
   - Trigger: `0 < remaining_minutes <= 10`
   - Channel: email only
   - Subject: `WiFi Tracker: 10 minutes to leave`
2. Completion alerts
   - Trigger: `total_minutes >= target_minutes`
   - Channels: macOS desktop + email
   - Subject: `WiFi Tracker: Target completed`

After manual start-time edits (`POST /api/session/edit-start-time`), notification flags are reset so alerts can be recalculated and resent.

## Email Content

Pre-leave email includes:

- Came office at / Start time
- Duration complete
- You can leave in 10 mins with end time

Completion email includes:

- Came office at / Start time
- Duration complete
- Target completed at

All displayed times are formatted in IST for the user-facing message.

## Tech Stack

- Backend: Python, FastAPI, Uvicorn, Pydantic, Motor, PyMongo
- Frontend: Jinja2 templates, vanilla JavaScript, Chart.js
- Storage: MongoDB Atlas (`daily_sessions`, `session_events`)
- Notifications: `osascript` for macOS desktop, SMTP for email
- Runtime: `launchd` (LaunchAgent) for login auto-start and keepalive

## Project Structure

```text
wifi-tracking/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── wifi_detector.py
│   ├── session_manager.py
│   ├── timer_engine.py
│   ├── mongodb_store.py
│   ├── email_notifier.py
│   ├── notifier.py
│   ├── analytics.py
│   └── timezone_utils.py
├── static/
├── templates/
├── tests/
├── scripts/
│   ├── install-autostart.sh
│   └── uninstall-autostart.sh
├── com.officetracker.plist
├── .env.example
└── README.md
```

## Setup

### Prerequisites

- macOS
- Python 3.11+
- MongoDB Atlas connection string

### Install

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment

```bash
cp .env.example .env
```

Set at least:

```env
OFFICE_WIFI_NAME=YourOfficeWiFiName
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=wifi-calculator
MONGODB_TEST_DATABASE=wifi-calculator-test
WORK_DURATION_HOURS=4
BUFFER_MINUTES=10
GRACE_PERIOD_MINUTES=2
TEST_MODE=false
TEST_DURATION_MINUTES=2
```

Optional email settings:

```env
EMAIL_ADDRESS=sender@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=receiver@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

Notes:

- `EMAIL_PASSWORD` should be an app password (not your account login password).
- Keep `TEST_MODE=false` for production tracking.

## Run

### Development

```bash
source venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload
```

### Production (LaunchAgent)

```bash
mkdir -p logs
./scripts/install-autostart.sh
launchctl list | grep officetracker
curl -sS --max-time 8 http://127.0.0.1:8787/health
```

Modern launchctl lifecycle:

```bash
# Stop
launchctl bootout gui/$(id -u)/com.officetracker

# Start
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.officetracker.plist

# Restart
launchctl bootout gui/$(id -u)/com.officetracker 2>/dev/null
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.officetracker.plist
```

Logs:

```bash
tail -f logs/stdout.log
tail -f logs/stderr.log
```

## Test Mode Without Polluting Production Data

Use test mode with a separate DB:

```env
TEST_MODE=true
TEST_DURATION_MINUTES=2
MONGODB_TEST_DATABASE=wifi-calculator-test
```

At startup, the app selects:

- `MONGODB_TEST_DATABASE` when `TEST_MODE=true`
- `MONGODB_DATABASE` when `TEST_MODE=false`

This keeps production and test session data isolated.

## API Endpoints

### `GET /health`

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "office_wifi": "YourOfficeWiFiName",
  "work_duration_hours": 4
}
```

### `GET /api/status`

Live connection, timer, completion, and leave-time status.

### `GET /api/today`

Today’s cumulative total and session row for the day.

### `GET /api/weekly`

Weekly aggregation: `days`, `total_minutes`, `avg_minutes_per_day`, `days_target_met`.

### `GET /api/monthly`

Monthly aggregation: `weeks`, `total_minutes`, `total_days_present`, `avg_daily_minutes`.

### `GET /api/gamification`

Streaks and achievements.

### `POST /api/session/edit-start-time`

Edits start time for a day, recalculates dependent fields, and resets notification sent flags.

## Validation and Tests

Run all tests:

```bash
venv/bin/python -m pytest -v
```

Run notification smoke test:

```bash
venv/bin/python tests/test_email_notification.py
```

Run timer alert tests:

```bash
venv/bin/python -m pytest tests/test_timer_email_alerts.py -v
```

Run notification flag reset test:

```bash
venv/bin/python -m pytest tests/test_edit_start_time_notification_flags.py -v
```

## Troubleshooting

### Service not reachable on `127.0.0.1:8787`

- Confirm LaunchAgent is loaded: `launchctl list | grep officetracker`
- Check service detail: `launchctl print gui/$(id -u)/com.officetracker`
- Check logs: `tail -f logs/stderr.log`
- Restart with `bootout` + `bootstrap` (not deprecated `load`/`unload`)

### No macOS desktop notification

- Ensure app is running on macOS (notifications use `osascript`)
- Verify completion threshold is actually reached
- Check `completion_desktop_sent_at` in `daily_sessions` to confirm send state

### No email received

- Verify `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `EMAIL_TO`, `SMTP_SERVER`, `SMTP_PORT`
- Use app password for Gmail
- Run: `venv/bin/python tests/test_email_notification.py`
- Check logs for SMTP/authentication errors

## Security and Privacy

- API binds to localhost by default (`127.0.0.1`)
- MongoDB TLS is enabled via CA certificates
- Credentials are read from `.env` and should never be committed

## Additional Documentation

- [docs/action-plan.md](docs/action-plan.md)
- [docs/PHASE_6_AUTO_START_GUIDE.md](docs/PHASE_6_AUTO_START_GUIDE.md)
- [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md)
