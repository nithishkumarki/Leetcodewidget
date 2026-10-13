import sys
import os
import json
import threading
import requests
from datetime import datetime, timedelta, timezone, date

from PyQt6.QtCore import Qt, QPoint, QTimer, QRectF, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPixmap, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame,
    QGraphicsDropShadowEffect, QSizeGrip, QMenu
)

# ----------------------------- SETTINGS ------------------------------------
LEETCODE_USERNAME = "nithishkumarki"
REFRESH_INTERVAL = 30 * 60 * 1000  # 30 minutes
IMAGE_PATH = r"C:\Users\Nithish\Downloads\grayscale-image.png"
STAY_ON_TOP = False       # True = stays visible above other windows (also survives Win+D)
SHOW_IN_TASKBAR = True   # True = shows as an app in the taskbar so you can always bring it back
RESIZE_EDGE = 8          # thickness (px) of the invisible resize border on all 4 sides
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leetcode_widget_config.json")
# ---------------------------------------------------------------------------


class CalendarGridWidget(QWidget):
    """Paints a GitHub-style activity heatmap that scales with the widget size."""
    WEEKS = 53
    ROWS = 7
    SPACING = 2.5

    def __init__(self, parent=None):
        super().__init__(parent)
        self.submission_calendar = {}
        self.setMinimumHeight(120)

    def set_calendar_data(self, calendar_data):
        if isinstance(calendar_data, str):
            try:
                self.submission_calendar = json.loads(calendar_data)
            except Exception:
                self.submission_calendar = {}
        else:
            self.submission_calendar = calendar_data or {}
        self.update()

    @staticmethod
    def _color_for(count):
        if count == 0:
            return QColor(255, 255, 255, 32)
        if count == 1:
            return QColor(14, 110, 60, 255)
        if count <= 3:
            return QColor(0, 150, 60, 255)
        if count <= 5:
            return QColor(38, 190, 75, 255)
        return QColor(80, 235, 110, 255)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Dark glass panel so the heatmap stays readable over any photo
        panel = QPainterPath()
        panel.addRoundedRect(QRectF(self.rect()), 10, 10)
        painter.fillPath(panel, QColor(10, 10, 14, 175))

        weeks, rows, spacing = self.WEEKS, self.ROWS, self.SPACING
        pad = 12
        label_h = 18  # space under the grid for month names

        cell_w = (self.width() - 2 * pad - (weeks - 1) * spacing) / weeks
        cell_h = (self.height() - 2 * pad - label_h - (rows - 1) * spacing) / rows
        cell = max(3.0, min(cell_w, cell_h))

        grid_w = weeks * cell + (weeks - 1) * spacing
        grid_h = rows * cell + (rows - 1) * spacing
        x0 = (self.width() - grid_w) / 2
        y0 = (self.height() - (grid_h + label_h)) / 2

        # Count submissions per day (LeetCode timestamps are UTC midnight)
        date_counts = {}
        for ts_str, count in self.submission_calendar.items():
            try:
                d = datetime.fromtimestamp(int(ts_str), tz=timezone.utc).date()
                date_counts[d] = date_counts.get(d, 0) + int(count)
            except (ValueError, TypeError):
                continue

        # Columns start on Sunday, last column contains today
        today = date.today()
        days_since_sunday = (today.weekday() + 1) % 7
        start_date = today - timedelta(days=days_since_sunday + (weeks - 1) * 7)

        radius = max(1.5, cell * 0.25)
        painter.setPen(Qt.PenStyle.NoPen)
        for w in range(weeks):
            for r in range(rows):
                cur_date = start_date + timedelta(days=w * 7 + r)
                if cur_date > today:
                    continue
                x = x0 + w * (cell + spacing)
                y = y0 + r * (cell + spacing)
                painter.setBrush(QBrush(self._color_for(date_counts.get(cur_date, 0))))
                if cur_date == today:
                    painter.setPen(QPen(QColor(255, 255, 255, 220), 1.2))  # highlight today
                else:
                    painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(QRectF(x, y, cell, cell), radius, radius)

        # Month labels under the grid
        painter.setPen(QColor(205, 205, 215))
        font = QFont("Arial", 8)
        font.setBold(True)
        painter.setFont(font)
        label_y = y0 + grid_h + 4
        for w in range(weeks):
            col_date = start_date + timedelta(days=w * 7)
            if col_date > today:
                break
            if w == 0:
                # skip the first label if the month changes right away (would overlap)
                if (start_date + timedelta(days=7)).month != col_date.month:
                    continue
            elif col_date.month == (start_date + timedelta(days=(w - 1) * 7)).month:
                continue
            x = x0 + w * (cell + spacing)
            painter.drawText(
                QRectF(x, label_y, 40, label_h - 4),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                col_date.strftime("%b"),
            )


class ResizableContainer(QFrame):
    """Rounded card with optional background image and a resize grip."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else None
        self._scaled_cache = None
        self._scaled_cache_size = None

        self.sizegrip = QSizeGrip(self)
        self.sizegrip.setStyleSheet("background: transparent;")
        self.sizegrip.resize(18, 18)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sizegrip.move(self.width() - 20, self.height() - 20)
        self.sizegrip.raise_()

    def _get_scaled(self):
        if self._scaled_cache is None or self._scaled_cache_size != self.size():
            self._scaled_cache = self.pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._scaled_cache_size = self.size()
        return self._scaled_cache

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(rect, 14, 14)
        painter.setClipPath(path)

        # Solid base
        painter.fillPath(path, QBrush(QColor("#1e1e24")))

        # Background image (cover-fit) + dark overlay for readability
        if self.pixmap and not self.pixmap.isNull():
            scaled = self._get_scaled()
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
            painter.fillPath(path, QColor(0, 0, 0, 110))


class LeetCodeWidget(QWidget):
    stats_ready = pyqtSignal(dict)
    stats_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        flags = Qt.WindowType.FramelessWindowHint
        if not SHOW_IN_TASKBAR:
            flags |= Qt.WindowType.Tool  # Tool windows are hidden from the taskbar
        if STAY_ON_TOP:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumWidth(480)  # height minimum comes from the layout so nothing overlaps
        self.resize(540, 360)

        self.drag_position = QPoint()
        self._dragging = False  # True only while dragging the card itself (not resizing)
        self.setMouseTracking(True)  # needed so hovering the border updates the cursor

        # Debounced save of window geometry
        self.save_timer = QTimer(self)
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(500)
        self.save_timer.timeout.connect(self.save_config)

        self.init_ui()
        self.load_config()

        self.stats_ready.connect(self.apply_stats)
        self.stats_failed.connect(self.streak_label.setText)

        self.fetch_leetcode_stats()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fetch_leetcode_stats)
        self.timer.start(REFRESH_INTERVAL)

    # ------------------------------ UI -------------------------------------
    def init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(RESIZE_EDGE, RESIZE_EDGE, RESIZE_EDGE, RESIZE_EDGE)

        self.container = ResizableContainer(self)
        self.container.setCursor(Qt.CursorShape.ArrowCursor)  # don't inherit resize cursors
        root_layout.addWidget(self.container)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 4)
        self.container.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(10)

        # Title
        title = QLabel(f"LeetCode  \u2022  {LEETCODE_USERNAME}", self)
        title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title.setStyleSheet("color: #d0d0d8; border: none; background: transparent;")
        main_layout.addWidget(title)

        # Top row: total solved + difficulty chips
        top_row = QHBoxLayout()

        solved_box = QVBoxLayout()
        self.total_solved_label = QLabel("0", self)
        self.total_solved_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.total_solved_label.setStyleSheet("color: #ffffff; border: none; background: transparent;")
        self.total_solved_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        solved_subtext = QLabel("Solved", self)
        solved_subtext.setFont(QFont("Arial", 10))
        solved_subtext.setStyleSheet("color: #a0a0ab; border: none; background: transparent;")
        solved_subtext.setAlignment(Qt.AlignmentFlag.AlignCenter)

        solved_box.addWidget(self.total_solved_label)
        solved_box.addWidget(solved_subtext)
        top_row.addLayout(solved_box)

        stats_box = QVBoxLayout()
        self.easy_label = QLabel("Easy  0 / 0", self)
        self.easy_label.setStyleSheet(
            "background-color: rgba(30, 45, 40, 220); color: #00b8a3; "
            "border-radius: 6px; padding: 4px 10px; font-weight: bold;")
        self.med_label = QLabel("Med.  0 / 0", self)
        self.med_label.setStyleSheet(
            "background-color: rgba(45, 40, 30, 220); color: #ffc01e; "
            "border-radius: 6px; padding: 4px 10px; font-weight: bold;")
        self.hard_label = QLabel("Hard  0 / 0", self)
        self.hard_label.setStyleSheet(
            "background-color: rgba(45, 30, 35, 220); color: #ff375f; "
            "border-radius: 6px; padding: 4px 10px; font-weight: bold;")
        stats_box.addWidget(self.easy_label)
        stats_box.addWidget(self.med_label)
        stats_box.addWidget(self.hard_label)

        top_row.addLayout(stats_box)
        main_layout.addLayout(top_row)

        # Heatmap
        self.calendar_grid = CalendarGridWidget(self)
        main_layout.addWidget(self.calendar_grid, 1)

        # Footer
        self.streak_label = QLabel("Total Active Days: --  |  Max Streak: --", self)
        self.streak_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.streak_label.setStyleSheet("color: #d0d0d8; border: none; background: transparent;")
        self.streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.streak_label)

    # --------------------------- DATA FETCHING -----------------------------
    def fetch_leetcode_stats(self):
        # Run network call off the UI thread so the widget never freezes
        threading.Thread(target=self._fetch_worker, daemon=True).start()

    def _fetch_worker(self):
        headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                           "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"),
            "Referer": "https://leetcode.com",
            "Content-Type": "application/json",
        }
        query = """
        query getUserProfile($username: String!) {
          allQuestionsCount {
            difficulty
            count
          }
          matchedUser(username: $username) {
            submitStats {
              acSubmissionNum {
                difficulty
                count
              }
            }
            userCalendar {
              streak
              totalActiveDays
              submissionCalendar
            }
          }
        }
        """
        try:
            res = requests.post(
                "https://leetcode.com/graphql",
                json={"query": query, "variables": {"username": LEETCODE_USERNAME}},
                headers=headers,
                timeout=8,
            )
            data = res.json()["data"]
            if not data.get("matchedUser"):
                self.stats_failed.emit(f"User '{LEETCODE_USERNAME}' not found!")
                return
            self.stats_ready.emit(data)
        except Exception:
            self.stats_failed.emit("Failed to sync stats. Retrying...")

    def apply_stats(self, data):
        user = data["matchedUser"]
        user_ac = {i["difficulty"]: i["count"] for i in user["submitStats"]["acSubmissionNum"]}
        all_q = {i["difficulty"]: i["count"] for i in data["allQuestionsCount"]}
        calendar = user["userCalendar"] or {}

        self.total_solved_label.setText(str(user_ac.get("All", 0)))
        self.easy_label.setText(f"Easy   {user_ac.get('Easy', 0)} / {all_q.get('Easy', 0)}")
        self.med_label.setText(f"Med.   {user_ac.get('Medium', 0)} / {all_q.get('Medium', 0)}")
        self.hard_label.setText(f"Hard   {user_ac.get('Hard', 0)} / {all_q.get('Hard', 0)}")
        self.streak_label.setText(
            f"Total Active Days: {calendar.get('totalActiveDays', 0)}  |  "
            f"Max Streak: {calendar.get('streak', 0)}"
        )
        self.calendar_grid.set_calendar_data(calendar.get("submissionCalendar", "{}"))

    # ------------------------ POSITION / SIZE MEMORY -----------------------
    def load_config(self):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.resize(int(cfg.get("w", 540)), int(cfg.get("h", 360)))
            if "x" in cfg and "y" in cfg:
                self.move(int(cfg["x"]), int(cfg["y"]))
        except Exception:
            pass  # first run or bad config: use defaults

    def save_config(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({
                    "x": self.x(), "y": self.y(),
                    "w": self.width(), "h": self.height(),
                }, f)
        except Exception:
            pass

    def moveEvent(self, event):
        super().moveEvent(event)
        if hasattr(self, "save_timer"):
            self.save_timer.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "save_timer"):
            self.save_timer.start()

    def closeEvent(self, event):
        self.save_config()
        super().closeEvent(event)

    # ------------------------- DRAG + RIGHT-CLICK MENU ---------------------
    def _edges_at(self, pos):
        """Return (left, right, top, bottom) booleans for a position near the window border."""
        e = RESIZE_EDGE
        return (pos.x() < e, pos.x() >= self.width() - e,
                pos.y() < e, pos.y() >= self.height() - e)

    def _update_cursor(self, pos):
        left, right, top, bottom = self._edges_at(pos)
        if (left and top) or (right and bottom):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif (right and top) or (left and bottom):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif left or right:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif top or bottom:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.unsetCursor()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        left, right, top, bottom = self._edges_at(event.position().toPoint())
        if left or right or top or bottom:
            edges = Qt.Edge(0)
            if left:
                edges |= Qt.Edge.LeftEdge
            if right:
                edges |= Qt.Edge.RightEdge
            if top:
                edges |= Qt.Edge.TopEdge
            if bottom:
                edges |= Qt.Edge.BottomEdge
            self._dragging = False
            handle = self.windowHandle()
            if handle:
                handle.startSystemResize(edges)  # native OS resize on any side/corner
            event.accept()
            return
        self._dragging = True
        self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging and (event.buttons() & Qt.MouseButton.LeftButton):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        elif not self._dragging:
            self._update_cursor(event.position().toPoint())

    def mouseReleaseEvent(self, event):
        self._dragging = False
        event.accept()

    def leaveEvent(self, event):
        self.unsetCursor()
        super().leaveEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        refresh_action = menu.addAction("Refresh now")
        top_action = menu.addAction("Always on top")
        top_action.setCheckable(True)
        top_action.setChecked(bool(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))
        menu.addSeparator()
        quit_action = menu.addAction("Quit")

        chosen = menu.exec(event.globalPos())
        if chosen == refresh_action:
            self.streak_label.setText("Refreshing...")
            self.fetch_leetcode_stats()
        elif chosen == top_action:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, top_action.isChecked())
            self.show()  # setWindowFlag hides the window; show it again
        elif chosen == quit_action:
            self.close()
            QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = LeetCodeWidget()
    widget.show()
    sys.exit(app.exec())
