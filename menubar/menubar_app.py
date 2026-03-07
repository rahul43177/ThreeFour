import webbrowser

import rumps

from status_client import get_status

DASHBOARD_URL = "http://127.0.0.1:8787"


def _fmt_time(raw: str | None) -> str:
    """Convert '09:41:00 AM IST' → '09:41 AM', or return '--' if empty."""
    if not raw:
        return "--"
    raw = raw.replace(" IST", "").strip()
    parts = raw.split(":")
    if len(parts) == 3:
        # parts = ["09", "41", "00 AM"] or ["09", "41", "00"]
        last = parts[2].strip()
        if " " in last:
            _, ampm = last.rsplit(" ", 1)
            return f"{parts[0]}:{parts[1]} {ampm}"
        return f"{parts[0]}:{parts[1]}"
    return raw


def _fmt_remaining(remaining_seconds: int) -> str:
    """Convert seconds to 'Xh Ym' or 'Ym' string."""
    if remaining_seconds <= 0:
        return "0m"
    h = remaining_seconds // 3600
    m = (remaining_seconds % 3600) // 60
    if h > 0:
        return f"{h}h {m}m"
    return f"{m}m"


class ThreeFourMenuApp(rumps.App):

    def __init__(self):
        super().__init__("⏱ --")

        self.start_item = rumps.MenuItem("Start: --")
        self.leave_item = rumps.MenuItem("Leave At: --")
        self.remaining_item = rumps.MenuItem("Remaining: --")
        self.status_item = rumps.MenuItem("Status: --")

        self.menu = [
            rumps.MenuItem("ThreeFour"),
            None,
            self.start_item,
            self.leave_item,
            self.remaining_item,
            self.status_item,
            None,
            rumps.MenuItem("Open Dashboard", callback=self.open_dashboard),
        ]

        # Disable the title item (purely informational)
        self.menu["ThreeFour"].set_callback(None)

        self._timer = rumps.Timer(self.update_status, 5)
        self._timer.start()

    def update_status(self, _):
        data = get_status()

        if data is None:
            self.title = "⚠ No WiFi"
            self._set_menu_unavailable()
            return

        connected = data.get("connected", False)
        session_active = data.get("session_active", False)

        if not connected or not session_active:
            self.title = "🏠 Off"
            self._set_menu_unavailable()
            return

        elapsed = data.get("elapsed_seconds", 0)
        remaining = data.get("remaining_seconds", 0)
        completed = data.get("completed_4h", False)

        h = elapsed // 3600
        m = (elapsed % 3600) // 60
        self.title = "✅ Done" if completed else f"⏱ {h}h {m}m"

        self.start_item.title = f"Start: {_fmt_time(data.get('start_time'))}"
        self.leave_item.title = f"Leave At: {_fmt_time(data.get('personal_leave_time_ist'))}"
        self.remaining_item.title = f"Remaining: {_fmt_remaining(remaining)}"

        ssid = data.get("ssid") or "Unknown"
        self.status_item.title = f"Status: {ssid}"

    def _set_menu_unavailable(self):
        self.start_item.title = "Start: --"
        self.leave_item.title = "Leave At: --"
        self.remaining_item.title = "Remaining: --"
        self.status_item.title = "Status: --"

    def open_dashboard(self, _):
        webbrowser.open(DASHBOARD_URL)


if __name__ == "__main__":
    ThreeFourMenuApp().run()
