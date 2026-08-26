"""Apple HIG Pro Telemetry Dashboard with Expandable View Dropdown & Animated Tracking Beacon."""

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from launchvehiclelab.core.domain import TrajectoryResult
from launchvehiclelab.ui.theme import (
    BG_BASE,
    BG_CARD,
    BG_CARD_HOVER,
    BG_PANEL,
    BORDER_HAIRLINE,
    COLOR_ALERT_CORAL,
    COLOR_CYAN,
    COLOR_ELECTRIC_BLUE,
    COLOR_FLIGHT_GREEN,
    COLOR_GOLD,
    COLOR_METHANE_VIOLET,
    COLOR_SUNSET_AMBER,
    SPACE_BLACK,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_TERTIARY,
)
from launchvehiclelab.ui.widgets.events_table import EventsTable


def _setup_apple_hig_axes(ax, title: str, xlabel: str, ylabel: str) -> None:
    """Style Matplotlib Axes adhering to Apple Human Interface Guidelines."""
    ax.set_facecolor(SPACE_BLACK)
    ax.set_title(title, color=TEXT_PRIMARY, fontsize=10, fontweight="bold", pad=8, loc="left")
    ax.set_xlabel(xlabel, color=TEXT_TERTIARY, fontsize=9)
    ax.set_ylabel(ylabel, color=TEXT_TERTIARY, fontsize=9)
    ax.tick_params(colors=TEXT_TERTIARY, labelsize=8, width=0.5, length=3)

    for spine in ax.spines.values():
        spine.set_color(BORDER_HAIRLINE)
        spine.set_linewidth(0.5)

    ax.grid(True, axis="y", linestyle=":", alpha=0.25, color="#27272a", linewidth=0.5)
    ax.grid(False, axis="x")


class TrajectoryView(QWidget):
    """Consolidated Apple Pro Dashboard integrating 4 dynamics charts and event table under an expandable view dropdown."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._trajectory: TrajectoryResult | None = None
        self._tracking_beacons: list = []

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # -------------------------------------------------------------
        # 1. Expandable Apple Pro View Selector Bar (Top Right)
        # -------------------------------------------------------------
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_PANEL};
                border-bottom: 1px solid {BORDER_HAIRLINE};
                padding: 4px 8px;
            }}
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(4, 2, 4, 4)
        header_layout.setSpacing(10)

        view_icon_lbl = QLabel("📊")
        view_icon_lbl.setStyleSheet("font-size: 14px;")
        header_layout.addWidget(view_icon_lbl)

        # Sleek Expandable View Dropdown Menu
        self.view_combo = QComboBox()
        self.view_combo.addItems([
            "📈 Ascent Flight Arc Profile",
            "🌪️ Aerodynamic Max-Q Dynamic Pressure",
            "⚡ Inertial Velocity & Mach Number",
            "🚀 Axial G-Force Acceleration",
            "⏱️ Flight Mission Event Timeline",
        ])
        self.view_combo.setMinimumWidth(260)
        self.view_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {BG_CARD};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_HAIRLINE};
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 0.3px;
            }}
            QComboBox:hover {{
                background-color: {BG_CARD_HOVER};
                border-color: {COLOR_ELECTRIC_BLUE};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid {BORDER_HAIRLINE};
            }}
            QComboBox QAbstractItemView {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_HAIRLINE};
                border-radius: 8px;
                padding: 4px;
                selection-background-color: rgba(10, 132, 255, 0.3);
                selection-color: #ffffff;
            }}
        """)
        self.view_combo.currentIndexChanged.connect(self._on_view_selected)
        header_layout.addWidget(self.view_combo)
        header_layout.addStretch()

        # Telemetry Status Chip
        self.status_chip = QLabel("● REAL-TIME 3DOF TRACKING")
        self.status_chip.setStyleSheet(f"color: {COLOR_FLIGHT_GREEN}; font-size: 9px; font-weight: 700; letter-spacing: 0.6px;")
        header_layout.addWidget(self.status_chip)

        layout.addWidget(header_frame)

        # -------------------------------------------------------------
        # 2. Unified Stacked Views Container
        # -------------------------------------------------------------
        self.stack = QStackedWidget()

        # View 0: Altitude vs Downrange
        self.canvas_alt = self._create_canvas()
        self.stack.addWidget(self.canvas_alt)

        # View 1: Dynamic Pressure & Max-Q
        self.canvas_q = self._create_canvas()
        self.stack.addWidget(self.canvas_q)

        # View 2: Velocity & Mach Number
        self.canvas_v = self._create_canvas()
        self.stack.addWidget(self.canvas_v)

        # View 3: Axial G-Force
        self.canvas_g = self._create_canvas()
        self.stack.addWidget(self.canvas_g)

        # View 4: Mission Event Stream Table
        self.events_table = EventsTable()
        self.stack.addWidget(self.events_table)

        layout.addWidget(self.stack, 1)

    def _create_canvas(self) -> FigureCanvas:
        fig = Figure(figsize=(5.5, 3.8), facecolor=SPACE_BLACK, tight_layout=True, dpi=100)
        return FigureCanvas(fig)

    def _on_view_selected(self, view_index: int) -> None:
        self.stack.setCurrentIndex(view_index)

    def update_trajectory(self, traj: TrajectoryResult) -> None:
        self._trajectory = traj
        self.events_table.update_events(traj)

        if not traj.points:
            return

        t = [p.time_s for p in traj.points]
        alt_km = [p.altitude_m / 1000.0 for p in traj.points]
        downrange_km = [p.downrange_m / 1000.0 for p in traj.points]
        v_mps = [p.velocity_m_per_s for p in traj.points]
        q_kpa = [p.dynamic_pressure_pa / 1000.0 for p in traj.points]
        accel_g = [p.acceleration_g for p in traj.points]
        mach = [p.mach for p in traj.points]

        self._tracking_beacons.clear()

        # -------------------------------------------------------------
        # 1. Altitude Arc vs Downrange
        # -------------------------------------------------------------
        fig1 = self.canvas_alt.figure
        fig1.clear()
        ax1 = fig1.add_subplot(111)
        _setup_apple_hig_axes(ax1, "ASCENT TRAJECTORY FLIGHT ARC", "Downrange Ground Distance (km)", "Altitude (km)")
        ax1.plot(downrange_km, alt_km, color=COLOR_ELECTRIC_BLUE, linewidth=1.75, label="Ascent Profile")
        ax1.fill_between(downrange_km, alt_km, color=COLOR_ELECTRIC_BLUE, alpha=0.06)

        if traj.final_orbit_altitude_m > 0:
            ax1.axhline(
                traj.final_orbit_altitude_m / 1000.0,
                color=COLOR_FLIGHT_GREEN,
                linestyle="--",
                linewidth=1.0,
                alpha=0.7,
                label=f"Target LEO ({traj.final_orbit_altitude_m/1000:.0f} km)",
            )

        # Active Tracking Beacon Dot & Floating Callout
        b_scat1 = ax1.scatter([downrange_km[0]], [alt_km[0]], color=COLOR_ELECTRIC_BLUE, s=45, zorder=6, edgecolors="#ffffff", linewidths=1.5)
        b_annot1 = ax1.annotate(
            f"Alt: {alt_km[0]:.1f} km",
            xy=(downrange_km[0], alt_km[0]),
            xytext=(downrange_km[0] + 25, alt_km[0] + 15),
            color=TEXT_PRIMARY,
            fontsize=8,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", facecolor=BG_CARD, edgecolor=COLOR_ELECTRIC_BLUE, lw=0.8),
        )
        self._tracking_beacons.append((
            ax1, None, b_scat1, b_annot1, self.canvas_alt,
            lambda pt: pt.downrange_m / 1000.0,
            lambda pt: pt.altitude_m / 1000.0,
            lambda pt: f"h: {pt.altitude_m/1000:.1f} km | x: {pt.downrange_m/1000:.1f} km",
        ))

        ax1.legend(facecolor=BG_CARD, edgecolor=BORDER_HAIRLINE, labelcolor=TEXT_PRIMARY, fontsize=8, loc="lower right")
        self.canvas_alt.draw()

        # -------------------------------------------------------------
        # 2. Dynamic Pressure & Max-Q
        # -------------------------------------------------------------
        fig2 = self.canvas_q.figure
        fig2.clear()
        ax2 = fig2.add_subplot(111)
        _setup_apple_hig_axes(ax2, "AERODYNAMIC DYNAMIC PRESSURE q(t)", "Flight Time (s)", "Dynamic Pressure (kPa)")
        ax2.plot(t, q_kpa, color=COLOR_SUNSET_AMBER, linewidth=1.75, label="Dynamic Pressure q(t)")
        ax2.fill_between(t, q_kpa, color=COLOR_SUNSET_AMBER, alpha=0.06)

        max_q_kpa = traj.max_q_pa / 1000.0
        ax2.scatter([traj.max_q_time_s], [max_q_kpa], color=COLOR_ALERT_CORAL, s=36, zorder=5)
        ax2.annotate(
            f"Max-Q: {max_q_kpa:.1f} kPa\n(T+{traj.max_q_time_s:.1f}s)",
            xy=(traj.max_q_time_s, max_q_kpa),
            xytext=(traj.max_q_time_s + 18, max_q_kpa + 2.5),
            arrowprops=dict(facecolor=COLOR_ALERT_CORAL, edgecolor=COLOR_ALERT_CORAL, arrowstyle="->", lw=0.9),
            color=TEXT_PRIMARY,
            fontsize=8,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=BG_CARD, edgecolor=COLOR_ALERT_CORAL, lw=0.8),
        )

        line_q = ax2.axvline(0.0, color=COLOR_ALERT_CORAL, linestyle="-", linewidth=1.2, alpha=0.8)
        b_scat2 = ax2.scatter([t[0]], [q_kpa[0]], color=COLOR_SUNSET_AMBER, s=45, zorder=6, edgecolors="#ffffff", linewidths=1.5)
        b_annot2 = ax2.annotate(
            f"q: {q_kpa[0]:.1f} kPa",
            xy=(t[0], q_kpa[0]),
            xytext=(t[0] + 12, q_kpa[0] + 2),
            color=TEXT_PRIMARY,
            fontsize=8,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", facecolor=BG_CARD, edgecolor=COLOR_SUNSET_AMBER, lw=0.8),
        )
        self._tracking_beacons.append((
            ax2, line_q, b_scat2, b_annot2, self.canvas_q,
            lambda pt: pt.time_s,
            lambda pt: pt.dynamic_pressure_pa / 1000.0,
            lambda pt: f"q: {pt.dynamic_pressure_pa/1000:.1f} kPa",
        ))

        ax2.legend(facecolor=BG_CARD, edgecolor=BORDER_HAIRLINE, labelcolor=TEXT_PRIMARY, fontsize=8, loc="upper right")
        self.canvas_q.draw()

        # -------------------------------------------------------------
        # 3. Velocity & Mach Number
        # -------------------------------------------------------------
        fig3 = self.canvas_v.figure
        fig3.clear()
        ax3 = fig3.add_subplot(111)
        _setup_apple_hig_axes(ax3, "INERTIAL VELOCITY & MACH NUMBER", "Flight Time (s)", "Velocity (m/s)")
        l1 = ax3.plot(t, v_mps, color=COLOR_CYAN, linewidth=1.75, label="Inertial Velocity")
        ax3.fill_between(t, v_mps, color=COLOR_CYAN, alpha=0.05)

        ax3_mach = ax3.twinx()
        ax3_mach.set_ylabel("Mach", color=COLOR_METHANE_VIOLET, fontsize=8)
        ax3_mach.tick_params(colors=COLOR_METHANE_VIOLET, labelsize=8, width=0.5, length=3)
        l2 = ax3_mach.plot(t, mach, color=COLOR_METHANE_VIOLET, linestyle="--", linewidth=1.2, label="Mach Number")
        for spine in ax3_mach.spines.values():
            spine.set_color(BORDER_HAIRLINE)
            spine.set_linewidth(0.5)

        line_v = ax3.axvline(0.0, color=COLOR_ALERT_CORAL, linestyle="-", linewidth=1.2, alpha=0.8)
        b_scat3 = ax3.scatter([t[0]], [v_mps[0]], color=COLOR_CYAN, s=45, zorder=6, edgecolors="#ffffff", linewidths=1.5)
        b_annot3 = ax3.annotate(
            f"v: {v_mps[0]:.1f} m/s",
            xy=(t[0], v_mps[0]),
            xytext=(t[0] + 12, v_mps[0] + 300),
            color=TEXT_PRIMARY,
            fontsize=8,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", facecolor=BG_CARD, edgecolor=COLOR_CYAN, lw=0.8),
        )
        self._tracking_beacons.append((
            ax3, line_v, b_scat3, b_annot3, self.canvas_v,
            lambda pt: pt.time_s,
            lambda pt: pt.velocity_m_per_s,
            lambda pt: f"v: {pt.velocity_m_per_s:.1f} m/s (M {pt.mach:.1f})",
        ))

        lines = l1 + l2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, facecolor=BG_CARD, edgecolor=BORDER_HAIRLINE, labelcolor=TEXT_PRIMARY, fontsize=8, loc="upper left")
        self.canvas_v.draw()

        # -------------------------------------------------------------
        # 4. Axial G-Force
        # -------------------------------------------------------------
        fig4 = self.canvas_g.figure
        fig4.clear()
        ax4 = fig4.add_subplot(111)
        _setup_apple_hig_axes(ax4, "AXIAL ACCELERATION (G-FORCE)", "Flight Time (s)", "Acceleration (g)")
        ax4.plot(t, accel_g, color=COLOR_FLIGHT_GREEN, linewidth=1.75, label="Axial G-force")
        ax4.fill_between(t, accel_g, color=COLOR_FLIGHT_GREEN, alpha=0.06)
        ax4.axhline(traj.max_acceleration_g, color=COLOR_ALERT_CORAL, linestyle=":", linewidth=1.0, label=f"Peak: {traj.max_acceleration_g:.2f}g")

        line_g = ax4.axvline(0.0, color=COLOR_ALERT_CORAL, linestyle="-", linewidth=1.2, alpha=0.8)
        b_scat4 = ax4.scatter([t[0]], [accel_g[0]], color=COLOR_FLIGHT_GREEN, s=45, zorder=6, edgecolors="#ffffff", linewidths=1.5)
        b_annot4 = ax4.annotate(
            f"g: {accel_g[0]:.2f}g",
            xy=(t[0], accel_g[0]),
            xytext=(t[0] + 12, accel_g[0] + 0.3),
            color=TEXT_PRIMARY,
            fontsize=8,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", facecolor=BG_CARD, edgecolor=COLOR_FLIGHT_GREEN, lw=0.8),
        )
        self._tracking_beacons.append((
            ax4, line_g, b_scat4, b_annot4, self.canvas_g,
            lambda pt: pt.time_s,
            lambda pt: pt.acceleration_g,
            lambda pt: f"G: {pt.acceleration_g:.2f}g",
        ))

        ax4.legend(facecolor=BG_CARD, edgecolor=BORDER_HAIRLINE, labelcolor=TEXT_PRIMARY, fontsize=8, loc="upper left")
        self.canvas_g.draw()

    def set_flight_time(self, time_s: float) -> None:
        """Move vertical playhead line, animated tracking beacon dot, and floating annotation callouts."""
        if not self._trajectory or not self._trajectory.points:
            return

        pts = self._trajectory.points
        closest_pt = min(pts, key=lambda p: abs(p.time_s - time_s))

        for ax, line_v, scat, annot, canvas, get_x, get_y, get_label in self._tracking_beacons:
            x_val = get_x(closest_pt)
            y_val = get_y(closest_pt)

            if line_v is not None:
                line_v.set_xdata([time_s, time_s])

            if scat is not None:
                scat.set_offsets([[x_val, y_val]])

            if annot is not None:
                annot.xy = (x_val, y_val)
                annot.set_text(get_label(closest_pt))
                x_span = ax.get_xlim()[1] - ax.get_xlim()[0]
                y_span = ax.get_ylim()[1] - ax.get_ylim()[0]
                annot.set_position((x_val + x_span * 0.04, y_val + y_span * 0.05))

            canvas.draw_idle()

        self.events_table.highlight_event_at_time(time_s)
