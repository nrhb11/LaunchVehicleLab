"""Apple Final Cut Pro inspired Mission Event Inspector Table."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from launchvehiclelab.core.domain import TrajectoryResult
from launchvehiclelab.ui.theme import (
    BG_CARD,
    BG_PANEL,
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


class EventsTable(QWidget):
    """Interactive table displaying the chronological flight sequence with active event highlight."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._trajectory: TrajectoryResult | None = None
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Timecode",
            "Altitude",
            "Velocity",
            "Milestone Event",
            "Physics & Subsystem Operations",
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addWidget(self.table)

    def update_events(self, traj: TrajectoryResult) -> None:
        self._trajectory = traj
        self.table.setRowCount(len(traj.events))

        for row, ev in enumerate(traj.events):
            t_item = QTableWidgetItem(f"T+{ev.time_s:05.1f} s")
            t_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            t_item.setFont(QFont("SF Mono, Monaco, Menlo, monospace", 11, QFont.Weight.Bold))
            t_item.setForeground(QColor(COLOR_ELECTRIC_BLUE))

            alt_item = QTableWidgetItem(f"{ev.altitude_m / 1000.0:6.1f} km")
            alt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            alt_item.setFont(QFont("SF Mono, Monaco, Menlo, monospace", 11))

            v_item = QTableWidgetItem(f"{ev.velocity_m_per_s:6.1f} m/s")
            v_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            v_item.setFont(QFont("SF Mono, Monaco, Menlo, monospace", 11))

            name_item = QTableWidgetItem(ev.name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            name_item.setFont(QFont("-apple-system", 11, QFont.Weight.Bold))

            # Color coding
            if "Max-Q" in ev.name:
                name_item.setForeground(QColor(COLOR_ALERT_CORAL))
            elif "Orbit" in ev.name or "Liftoff" in ev.name:
                name_item.setForeground(QColor(COLOR_FLIGHT_GREEN))
            elif "Separation" in ev.name or "Ignition" in ev.name:
                name_item.setForeground(QColor(COLOR_METHANE_VIOLET))
            else:
                name_item.setForeground(QColor(COLOR_CYAN))

            desc_item = QTableWidgetItem(ev.description)
            desc_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            desc_item.setForeground(QColor(TEXT_SECONDARY))

            self.table.setItem(row, 0, t_item)
            self.table.setItem(row, 1, alt_item)
            self.table.setItem(row, 2, v_item)
            self.table.setItem(row, 3, name_item)
            self.table.setItem(row, 4, desc_item)

    def highlight_event_at_time(self, time_s: float) -> None:
        """Highlight active chronological flight event based on scrubbed time."""
        if not self._trajectory or not self._trajectory.events:
            return

        active_row = 0
        for row, ev in enumerate(self._trajectory.events):
            if ev.time_s <= time_s:
                active_row = row
            else:
                break

        self.table.selectRow(active_row)
