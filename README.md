# ThreeFour (TF) - Office Time Tracker

**Automatic WiFi-Based Office Attendance & Time Tracking**

ThreeFour is a production-ready macOS application that automatically tracks your office hours by detecting when you connect to your office WiFi network. It runs as a background service via launchd with a beautiful web dashboard for monitoring your time, viewing analytics, and managing work sessions.

---

## 📋 Current Status

**✅ Production Ready - All Core Features Implemented**

The application is fully functional with **584 passing tests** and runs automatically on macOS login via launchd.

### Key Features Implemented:
- ✅ **Automatic WiFi Detection** - Triple-fallback detection system (airport → networksetup → system_profiler)
- ✅ **Smart Session Management** - State machine with 2-minute grace period for brief disconnects
- ✅ **MongoDB Atlas Storage** - Reliable cloud storage with atomic operations
- ✅ **IST Timezone Support** - Full timezone awareness for India Standard Time (Asia/Kolkata)
- ✅ **Timer Engine** - Configurable work hours + buffer time with live countdown
- ✅ **Network Connectivity Monitoring** - Detects captive portals and pauses timer during re-authentication
- ✅ **Professional Web Dashboard** - Live status, progress visualization, session history
- ✅ **Analytics** - Daily, weekly, and monthly time tracking with interactive charts
- ✅ **Dark Mode** - System-aware theme switching with manual toggle
- ✅ **Accessibility** - WCAG AA compliant with keyboard navigation and screen reader support
- ✅ **Notifications** - Browser and macOS native notifications
- ✅ **Auto-Start on Login** - Runs on login via macOS LaunchAgent with auto-restart
- ✅ **Gamification** - Streaks, achievements, and progress tracking

**Test Coverage:** 584 tests passing, 0 failures, 0 warnings  
**Documentation:** Comprehensive design system, phase guides, and API docs

For detailed implementation status, see [`docs/action-plan.md`](docs/action-plan.md).

---

## 🎯 Core Features

### 📡 Automatic Tracking
- Detects office WiFi connection automatically
- Starts timer when connected to configured office network
- Pauses during network re-authentication (captive portals)
- 2-minute grace period for brief disconnections
- Survives laptop sleep, restarts, and app crashes
- Session recovery on app restart

### ⏱️ Time Management
- Configurable work hour target (default: 4 hours)
- Configurable buffer time (default: 10 minutes)
- Test mode for quick validation (2-minute sessions)
- Real-time progress visualization with circular timer
- Target completion time display ("Free At")
- Personal leave time calculation
- Cumulative daily tracking (multiple sessions = one daily total)

### 📊 Analytics & Insights
- **Today View**: Current session status and all sessions for the day
- **Weekly View**: Day-by-day breakdown with interactive bar charts
- **Monthly View**: Week-by-week aggregation with trends
- Target achievement tracking (did you meet your 4-hour goal?)
- Average time calculations
- Session history with start/end times
- Interactive Chart.js visualizations

### 🎨 Professional UI
- Clean, emoji-free professional interface
- Responsive design (desktop optimized)
- System-aware dark mode with manual toggle
- Real-time updates every 30 seconds
- Smooth animations and transitions
- Status cards showing key metrics
- Progress ring with percentage display

### 💾 Data Storage
- **MongoDB Atlas** - Cloud-based, reliable, automatically backed up
- Cumulative daily tracking (multiple visits = one daily total)
- Atomic operations prevent race conditions
- Session event logging for audit trail
- Efficient indexing for fast queries
- Secure connection with SSL/TLS

---

## 🚀 Tech Stack

### Backend
- **Python 3.11+** - Modern async/await
- **FastAPI** - High-performance web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation and settings
- **Motor** - Async MongoDB driver
- **APScheduler** - Background task scheduling

### Frontend
- **Vanilla JavaScript** - No build tools required
- **Chart.js** - Interactive data visualizations
- **CSS Variables** - Themeable design system
- **Jinja2** - Server-side templating

### Storage & Infrastructure
- **MongoDB Atlas** - Cloud database
- **File-based fallback** - JSON Lines for legacy compatibility
- **macOS LaunchAgent** - Background service management

### Testing
- **Pytest** - Test framework
- **pytest-asyncio** - Async test support
- **httpx** - HTTP testing client

---

## 📁 Project Structure

```text
wifi-tracking/
├── app/                          # Application source code
│   ├── main.py                   # FastAPI app and API endpoints
│   ├── config.py                 # Environment-based configuration
│   ├── wifi_detector.py          # WiFi SSID detection (3 fallback methods)
│   ├── session_manager.py        # Session state machine with grace period
│   ├── timer_engine.py           # Timer calculations and polling
│   ├── mongodb_store.py          # MongoDB operations and queries
│   ├── network_checker.py        # Internet connectivity detection
│   ├── timezone_utils.py         # IST timezone conversions
│   ├── analytics.py              # Weekly/monthly aggregations
│   ├── gamification.py           # Streaks and achievements
│   ├── notifier.py               # macOS notification integration
│   ├── cache.py                  # In-memory session cache
│   └── file_store.py             # Legacy JSON Lines storage
│
├── templates/
│   └── index.html                # Main dashboard template
│
├── static/
│   ├── app.js                    # Dashboard client-side logic
│   ├── style.css                 # Main styles with CSS variables
│   └── images/                   # Logo and assets
│
├── tests/                        # Comprehensive test suite
│   ├── conftest.py               # Pytest fixtures and setup
│   ├── test_phase_*.py           # Phase-driven feature tests
│   └── test_*.py                 # Specific feature tests
│
├── docs/                         # Documentation
│   ├── requirements.md           # Original product requirements
│   ├── action-plan.md            # Phased development plan
│   ├── DESIGN_SYSTEM.md          # UI design tokens and guidelines
│   ├── PERFORMANCE_OPTIMIZATION.md
│   ├── PHASE_6_AUTO_START_GUIDE.md
│   └── ...                       # Additional docs
│
├── scripts/
│   ├── install-autostart.sh      # Install launchd service
│   └── uninstall-autostart.sh    # Remove launchd service
│
├── data/                         # Session data (gitignored)
│   ├── gamification.json         # Streaks and achievements
│   └── archive/                  # Rotated old files
│
├── logs/                         # Application logs (gitignored)
│   ├── app.log                   # Application logs (optional)
│   ├── stdout.log                # LaunchAgent stdout
│   └── stderr.log                # LaunchAgent stderr
│
├── com.officetracker.plist       # LaunchAgent configuration
├── requirements.txt              # Python dependencies
├── .env                          # Environment configuration (gitignored)
├── .env.example                  # Example configuration
└── README.md                     # This file
```

---

## ⚡️ Quick Start

### Prerequisites
- macOS 10.14 or later
- Python 3.11 or later
- MongoDB Atlas account (free tier works great)

### 1. Clone and Setup Virtual Environment

```bash
cd /Users/rahulmishra/Desktop/Personal/wifi-tracking
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. MongoDB Setup

1. Create a free MongoDB Atlas account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a cluster (M0 free tier is sufficient)
3. Create a database named `wifi-calculator`
4. Add your IP address to the IP whitelist
5. Create a database user with read/write permissions
6. Copy your connection string

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

**Required configuration:**

```env
# Office WiFi name (must match exactly)
OFFICE_WIFI_NAME=YourActualOfficeWiFiName

# MongoDB Configuration (REQUIRED)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=wifi-calculator

# Work Duration Settings
WORK_DURATION_HOURS=4
BUFFER_MINUTES=10

# Grace Period (minutes - reconnection window before ending session)
GRACE_PERIOD_MINUTES=2

# Timezone (for accurate time display)
USER_TIMEZONE=Asia/Kolkata

# Server Configuration
SERVER_HOST=127.0.0.1
SERVER_PORT=8787

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=false
LOG_FILE_PATH=logs/app.log

# Check Intervals (seconds)
WIFI_CHECK_INTERVAL_SECONDS=30
TIMER_CHECK_INTERVAL_SECONDS=60
CONNECTIVITY_CHECK_INTERVAL_SECONDS=30

# Testing Mode
TEST_MODE=false
TEST_DURATION_MINUTES=2

# Data Directory (legacy file storage fallback)
DATA_DIR=data
ARCHIVE_DIR=data/archive
```

### 4. Run Manually (Development Mode)

```bash
source venv/bin/activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8787 --reload
```

**Access the dashboard:**
- Dashboard: http://127.0.0.1:8787/
- Health Check: http://127.0.0.1:8787/health

### 5. Install Auto-Start (Production Mode)

**The application is designed to run continuously as a background service.**

```bash
# Install LaunchAgent (runs on login)
./scripts/install-autostart.sh

# Verify it's running
launchctl list | grep officetracker
curl http://127.0.0.1:8787/health
```

**The service will:**
- ✅ Start automatically when you log in
- ✅ Restart automatically if it crashes (KeepAlive enabled)
- ✅ Log output to `logs/stdout.log` and `logs/stderr.log`
- ✅ Track your office time in the background
- ✅ Survive laptop restarts

**To stop/restart:**

```bash
# Stop the service
launchctl bootout gui/$(id -u)/com.officetracker

# Start the service
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.officetracker.plist

# Or use the provided scripts
./scripts/uninstall-autostart.sh  # Completely remove
./scripts/install-autostart.sh    # Reinstall
```

**Full documentation:** See [`docs/PHASE_6_AUTO_START_GUIDE.md`](docs/PHASE_6_AUTO_START_GUIDE.md)

---

## 🔧 Configuration Reference

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `OFFICE_WIFI_NAME` | `YourOfficeWiFiName` | **Required.** Exact name of your office WiFi network |
| `MONGODB_URI` | `""` | **Required.** MongoDB Atlas connection string |
| `MONGODB_DATABASE` | `wifi-calculator` | MongoDB database name |
| `WORK_DURATION_HOURS` | `4` | Target work hours per day |
| `BUFFER_MINUTES` | `10` | Extra minutes added to target (e.g., 4h 10m) |
| `USER_TIMEZONE` | `Asia/Kolkata` | Timezone for time display (IST) |

### Intervals

| Variable | Default | Description |
|----------|---------|-------------|
| `WIFI_CHECK_INTERVAL_SECONDS` | `30` | How often to check WiFi connection |
| `TIMER_CHECK_INTERVAL_SECONDS` | `60` | How often to update the timer |
| `CONNECTIVITY_CHECK_INTERVAL_SECONDS` | `30` | How often to check internet connectivity |
| `GRACE_PERIOD_MINUTES` | `2` | Reconnection window before ending session |

### Server

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_HOST` | `127.0.0.1` | Server bind address (localhost only) |
| `SERVER_PORT` | `8787` | Web server port |

### Testing

| Variable | Default | Description |
|----------|---------|-------------|
| `TEST_MODE` | `false` | Use short duration for testing |
| `TEST_DURATION_MINUTES` | `2` | Target duration in test mode |

### Logging

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Log verbosity (DEBUG, INFO, WARNING, ERROR) |
| `LOG_TO_FILE` | `false` | Enable file logging |
| `LOG_FILE_PATH` | `logs/app.log` | Log file location |

---

## 🌐 API Endpoints

### Health Check
```
GET /health
```
Returns service health status and version info.

**Response:**
```json
{
  "status": "healthy",
  "mongodb": "connected",
  "timestamp": "2026-03-06T10:30:00Z"
}
```

### Live Status
```
GET /api/status
```
Returns current connection status, session state, and timer information.

**Response:**
```json
{
  "connected": true,
  "ssid": "OfficeWifi",
  "session_active": true,
  "start_time": "09:30:00 AM",
  "elapsed_seconds": 7200,
  "elapsed_display": "02:00:00",
  "remaining_seconds": 7800,
  "remaining_display": "02:10:00",
  "completed_4h": false,
  "progress_percent": 48.0,
  "target_display": "4h 10m",
  "target_completion_time_ist": "01:40:00 PM",
  "personal_leave_time_ist": "01:40:00 PM"
}
```

### Today's Sessions
```
GET /api/today
```
Returns all sessions for today and cumulative total.

**Response:**
```json
{
  "date": "06-03-2026",
  "sessions": [
    {
      "start_time": "09:30:00 AM",
      "end_time": null,
      "duration_minutes": 120,
      "completed_4h": false
    }
  ],
  "total_minutes": 120,
  "total_display": "2h 00m",
  "personal_leave_time_ist": "01:40:00 PM"
}
```

### Weekly Aggregation
```
GET /api/weekly?week=2026-W10
```
Returns day-by-day breakdown for the specified week (defaults to current week).

**Response:**
```json
{
  "week": "2026-W10",
  "days": [
    {
      "date": "02-03-2026",
      "day": "Monday",
      "total_minutes": 270,
      "session_count": 2,
      "target_met": true
    }
  ],
  "total_minutes": 1350,
  "avg_minutes_per_day": 270,
  "days_target_met": 5
}
```

### Monthly Aggregation
```
GET /api/monthly?month=2026-03
```
Returns week-by-week breakdown for the specified month.

**Response:**
```json
{
  "month": "2026-03",
  "weeks": [
    {
      "week": "2026-W10",
      "start_date": "02-03-2026",
      "end_date": "08-03-2026",
      "total_minutes": 1350,
      "days_present": 5,
      "avg_daily_minutes": 270
    }
  ],
  "total_minutes": 5400,
  "total_days": 20,
  "avg_daily_minutes": 270
}
```

### Gamification
```
GET /api/gamification
```
Returns streaks and achievements.

**Response:**
```json
{
  "current_streak": 5,
  "longest_streak": 12,
  "achievements": [
    {
      "id": "early_bird",
      "name": "Early Bird",
      "description": "Started work before 9 AM",
      "icon": "⏰",
      "condition_met": true
    }
  ]
}
```

---

## 🧪 Testing

### Run All Tests

```bash
source venv/bin/activate
pytest tests/ -v
```

**Expected output:** `584 passed`

### Run Specific Test Suites

```bash
# WiFi detection tests
pytest tests/test_phase_1_*.py -v

# Session management tests
pytest tests/test_phase_2_*.py -v

# Timer engine tests
pytest tests/test_phase_3_*.py -v

# Analytics tests
pytest tests/test_phase_5_*.py -v

# MongoDB implementation tests
pytest tests/test_mongodb_*.py -v

# Timezone tests
pytest tests/test_timezone_utils.py -v
```

### Test Mode

For quick validation, enable test mode:

```env
TEST_MODE=true
TEST_DURATION_MINUTES=2
```

This changes the target from 4 hours to 2 minutes, allowing rapid testing of timer completion and notifications.

---

## 📖 Documentation

- **[Requirements](docs/requirements.md)** - Original product specification
- **[Action Plan](docs/action-plan.md)** - Phased development plan with completion status
- **[Design System](docs/DESIGN_SYSTEM.md)** - UI tokens, colors, typography
- **[Auto-Start Guide](docs/PHASE_6_AUTO_START_GUIDE.md)** - LaunchAgent setup
- **[Performance Optimization](docs/PERFORMANCE_OPTIMIZATION.md)** - Caching and efficiency
- **[QA Reports](docs/PRE_PUSH_QA_REPORT.md)** - Quality assurance audits

---

## 🐛 Known Issues & Limitations

### Current Limitations
1. **macOS Only** - WiFi detection uses macOS-specific commands
2. **Single User** - Designed for personal use, not multi-user
3. **No Authentication** - API is open but binds to localhost only
4. **WiFi Only** - Cannot track wired (Ethernet) connections

### Minor Issues
1. Debug print statements in `app/main.py` (lines 806-809) should use logger
2. Gamification uses file storage while rest uses MongoDB
3. Cache module may be unnecessary given MongoDB's built-in caching

### Upcoming Fixes
See [Bug Tracking List](#bug-tracking-list) in the code review section above.

---

## 🔒 Privacy & Security

- **All data stays local or in your private MongoDB database**
- No third-party analytics or tracking
- No data sharing with external services
- Web dashboard binds to localhost only (127.0.0.1)
- MongoDB connection uses SSL/TLS encryption
- Logs contain no sensitive information

---

## 🤝 Contributing

This is a personal productivity tool, but contributions are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Please ensure:**
- All tests pass (`pytest tests/ -v`)
- Code follows existing style conventions
- Documentation is updated if needed

---

## 📝 License

This project is licensed for personal use. See LICENSE file for details.

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Charts powered by [Chart.js](https://www.chartjs.org/)
- Database by [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- Design inspired by modern dashboard UIs

---

## 📞 Support

For issues, questions, or feature requests:
1. Check the [documentation](docs/)
2. Review the [action plan](docs/action-plan.md) for implementation details
3. Check logs in `logs/` directory
4. File an issue in the repository

---

**Made with ☕ in Bangalore, India (IST)**
