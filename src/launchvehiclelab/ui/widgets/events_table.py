"""Mission flight event sequence timeline table widget."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from launchvehiclelab.core.domain import TrajectoryResult
from launchvehiclelab.ui.theme import (
    ACCENT_BLUE,
    ACCENT_GREEN,
    ACCENT_RED,
    DARK_TEXT_PRIMARY,
    DARK_TEXT_SECONDARY,
)


class EventsTable(QWidget):
    """Interactive table displaying the sequential chronological flight milestones."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Timestamp (T+)",
            "Altitude (km)",
            "Velocity (m/s)",
            "Event Milestone",
            "Description & Physics Summary",
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

        layout.addWidget(self.table)

    def update_events(self, traj: TrajectoryResult) -> None:
        self.table.setRowCount(len(traj.events))

        for row, ev in enumerate(traj.events):
            t_item = QTableWidgetItem(f"T+{ev.time_s:6.1f} s")
            t_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            alt_item = QTableWidgetItem(f"{ev.altitude_m / 1000.0:6.1f} km")
            alt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            v_item = QTableWidgetItem(f"{ev.velocity_m_per_s:6.1f} m/s")
            v_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            name_item = QTableWidgetItem(ev.name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            # Event-specific badge color
            if "Max-Q" in ev.name:
                name_item.setForeground(Qt.GlobalColor.red)
            elif "Orbit" in ev.name or "Liftoff" in ev.name:
                name_item.setForeground(Qt.GlobalColor.green)
            else:
                name_item.setForeground(Qt.GlobalColor.cyan)

            desc_item = QTableWidgetItem(ev.description)
            desc_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            self.table.setItem(row, 0, t_item)
            self.table.setItem(row, 1, alt_item)
            self.table.setItem(row, 2, v_item)
            self.table.setItem(row, 3, name_item)
            self.table.setItem(row, 4, desc_item)
