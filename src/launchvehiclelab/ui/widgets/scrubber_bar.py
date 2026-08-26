"""Apple Final Cut Pro inspired Magnetic Flight Timeline & Playhead Scrubber widget."""

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from launchvehiclelab.core.domain import TrajectoryResult
from launchvehiclelab.ui.theme import (
    BG_CANVAS,
    BG_CARD,
    BG_PANEL,
    BORDER_ACCENT,
    BORDER_SUBTLE,
    COLOR_ALERT_CORAL,
    COLOR_CYAN,
    COLOR_ELECTRIC_BLUE,
    COLOR_FLIGHT_GREEN,
    COLOR_METHANE_VIOLET,
    COLOR_SUNSET_AMBER,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class TimelineTrack(QWidget):
    """Interactive custom-painted multi-track flight timeline canvas with magnetic playhead."""

    time_scrubbed = Signal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(44)
        self.setMaximumHeight(54)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._current_time_s: float = 0.0
        self._total_duration_s: float = 496.7
        self._trajectory: TrajectoryResult | None = None
        self._is_dragging: bool = False

    def set_trajectory(self, trajectory: TrajectoryResult) -> None:
        self._trajectory = trajectory
        self._total_duration_s = max(1.0, trajectory.total_flight_time_s)
        self._current_time_s = min(self._current_time_s, self._total_duration_s)
        self.update()

    def set_current_time(self, time_s: float) -> None:
        self._current_time_s = max(0.0, min(self._total_duration_s, time_s))
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._update_time_from_pos(event.position().x())

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._is_dragging:
            self._update_time_from_pos(event.position().x())

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False

    def _update_time_from_pos(self, x: float) -> None:
        margin = 12.0
        track_w = max(1.0, self.width() - 2.0 * margin)
        ratio = max(0.0, min(1.0, (x - margin) / track_w))
        new_time = ratio * self._total_duration_s
        self.set_current_time(new_time)
        self.time_scrubbed.emit(self._current_time_s)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin = 12.0
        track_w = w - 2.0 * margin
        track_h = 24.0
        track_y = (h - track_h) / 2.0

        # Background track container
        track_rect = QRectF(margin, track_y, track_w, track_h)
        painter.setBrush(QColor(BG_CANVAS))
        painter.setPen(QPen(QColor(BORDER_SUBTLE), 1.0))
        painter.drawRoundedRect(track_rect, 6.0, 6.0)

        # Draw Flight Phase Blocks
        if self._trajectory is not None and self._trajectory.events:
            evs = self._trajectory.events
            phase_colors = [
                (0.0, 12.1, QColor(COLOR_ELECTRIC_BLUE), "Pad Climb"),
                (12.1, 74.9, QColor(COLOR_FLIGHT_GREEN), "Gravity Turn"),
                (74.9, 174.0, QColor(COLOR_SUNSET_AMBER), "Stage 1 Boost"),
                (174.0, 176.6, QColor("#64748B"), "Staging"),
                (176.6, 186.6, QColor(COLOR_METHANE_VIOLET), "Stage 2 Ignition"),
                (186.6, self._total_duration_s, QColor(COLOR_CYAN), "Orbit Insertion"),
            ]

            for t_start, t_end, color, label in phase_colors:
                t_s_clamped = max(0.0, min(self._total_duration_s, t_start))
                t_e_clamped = max(0.0, min(self._total_duration_s, t_end))
                px_start = margin + (t_s_clamped / self._total_duration_s) * track_w
                px_end = margin + (t_e_clamped / self._total_duration_s) * track_w
                block_w = max(2.0, px_end - px_start)

                block_rect = QRectF(px_start, track_y + 2, block_w, track_h - 4)
                painter.setBrush(color.darker(180))
                painter.setPen(QPen(color.darker(120), 1.0))
                painter.drawRoundedRect(block_rect, 4.0, 4.0)

                # Segment label if wide enough
                if block_w > 50.0:
                    painter.setPen(color)
                    painter.setFont(QFont("-apple-system", 9, QFont.Weight.Bold))
                    painter.drawText(block_rect, Qt.AlignmentFlag.AlignCenter, label)

        # Draw Magnetic Playhead Needle (Apple FCP Red Scrubber)
        playhead_x = margin + (self._current_time_s / self._total_duration_s) * track_w

        # Needle line
        needle_pen = QPen(QColor(COLOR_ALERT_CORAL), 2.0)
        painter.setPen(needle_pen)
        painter.drawLine(int(playhead_x), int(track_y - 4), int(playhead_x), int(track_y + track_h + 4))

        # Needle Top Diamond Handle
        head_path = QPainterPath()
        head_path.moveTo(playhead_x - 6, track_y - 6)
        head_path.lineTo(playhead_x + 6, track_y - 6)
        head_path.lineTo(playhead_x, track_y)
        head_path.closeSubpath()
        painter.setBrush(QColor(COLOR_ALERT_CORAL))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(head_path)


class FlightScrubberBar(QFrame):
    """Bottom control deck integrating transport controls, speed multipliers, timecode, and timeline."""

    time_changed = Signal(float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ScrubberDeck")
        self.setStyleSheet(f"QFrame#ScrubberDeck {{ background-color: {BG_PANEL}; border-top: 1px solid {BORDER_SUBTLE}; padding: 6px 12px; }}")

        self._is_playing: bool = False
        self._playback_speed: float = 5.0  # 5x default for smooth 0-500s playback
        self._current_time_s: float = 0.0
        self._total_time_s: float = 496.7

        # Animation timer (50 Hz / 20 ms interval)
        self._timer = QTimer(self)
        self._timer.setInterval(20)
        self._timer.timeout.connect(self._on_timer_tick)

        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(12)

        # 1. Transport Controls (Reset & Play/Pause)
        self.reset_btn = QPushButton("⏮")
        self.reset_btn.setObjectName("TransportButton")
        self.reset_btn.setToolTip("Reset to T+0s")
        self.reset_btn.clicked.connect(self.reset_to_start)
        main_layout.addWidget(self.reset_btn)

        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("TransportButton")
        self.play_btn.setToolTip("Play / Pause Ascent Simulation")
        self.play_btn.clicked.connect(self.toggle_play)
        main_layout.addWidget(self.play_btn)

        # 2. Timecode HUD (e.g. T+074.9s / T+496.7s)
        self.timecode_label = QLabel("T+000.0 s")
        self.timecode_label.setStyleSheet(
            f"font-family: 'SF Mono', Monaco, Menlo, monospace; font-size: 15px; font-weight: bold; color: {COLOR_ELECTRIC_BLUE}; min-width: 85px;"
        )
        main_layout.addWidget(self.timecode_label)

        # 3. Magnetic Timeline Canvas
        self.track = TimelineTrack()
        self.track.time_scrubbed.connect(self._on_scrubbed)
        main_layout.addWidget(self.track, 1)

        # 4. Speed Multipliers (Segmented Chips: 1x, 5x, 20x, 50x)
        speed_frame = QFrame()
        speed_frame.setObjectName("SegmentedGroup")
        speed_layout = QHBoxLayout(speed_frame)
        speed_layout.setContentsMargins(2, 2, 2, 2)
        speed_layout.setSpacing(2)

        self.speed_group = QButtonGroup(self)
        for speed_val in [1.0, 5.0, 20.0, 50.0]:
            btn = QPushButton(f"{int(speed_val)}x")
            btn.setObjectName("SegmentChip")
            btn.setCheckable(True)
            if speed_val == 5.0:
                btn.setChecked(True)
            self.speed_group.addButton(btn, int(speed_val))
            speed_layout.addWidget(btn)

        self.speed_group.idClicked.connect(self._on_speed_changed)
        main_layout.addWidget(speed_frame)

    def set_trajectory(self, trajectory: TrajectoryResult) -> None:
        self._total_time_s = trajectory.total_flight_time_s
        self.track.set_trajectory(trajectory)
        self._update_time_display()

    def toggle_play(self) -> None:
        if self._is_playing:
            self.pause()
        else:
            self.play()

    def play(self) -> None:
        self._is_playing = True
        self.play_btn.setText("⏸")
        if self._current_time_s >= self._total_time_s:
            self._current_time_s = 0.0
        self._timer.start()

    def pause(self) -> None:
        self._is_playing = False
        self.play_btn.setText("▶")
        self._timer.stop()

    def reset_to_start(self) -> None:
        self.pause()
        self._current_time_s = 0.0
        self.track.set_current_time(0.0)
        self._update_time_display()
        self.time_changed.emit(0.0)

    def _on_speed_changed(self, speed_id: int) -> None:
        self._playback_speed = float(speed_id)

    def _on_timer_tick(self) -> None:
        dt = (self._timer.interval() / 1000.0) * self._playback_speed
        self._current_time_s += dt

        if self._current_time_s >= self._total_time_s:
            self._current_time_s = self._total_time_s
            self.pause()

        self.track.set_current_time(self._current_time_s)
        self._update_time_display()
        self.time_changed.emit(self._current_time_s)

    def _on_scrubbed(self, time_s: float) -> None:
        self._current_time_s = time_s
        self._update_time_display()
        self.time_changed.emit(self._current_time_s)

    def _update_time_display(self) -> None:
        self.timecode_label.setText(f"T+{self._current_time_s:05.1f} s")
