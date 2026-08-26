"""Apple Final Cut Pro inspired multi-track flight dynamics canvas with Playhead Tracking."""

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from launchvehiclelab.core.domain import TrajectoryResult
from launchvehiclelab.ui.theme import (
    BG_CARD,
    BG_PANEL,
    BORDER_SUBTLE,
    COLOR_ALERT_CORAL,
    COLOR_CYAN,
    COLOR_ELECTRIC_BLUE,
    COLOR_FLIGHT_GREEN,
    COLOR_METHANE_VIOLET,
    COLOR_SUNSET_AMBER,
    SPACE_BLACK,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


def _setup_fcp_axes(ax, title: str, xlabel: str, ylabel: str) -> None:
    """Style Matplotlib Axes with Apple FCP true-black aesthetic."""
    ax.set_facecolor(SPACE_BLACK)
    ax.set_title(title, color=TEXT_PRIMARY, fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel(xlabel, color=TEXT_SECONDARY, fontsize=9)
    ax.set_ylabel(ylabel, color=TEXT_SECONDARY, fontsize=9)
    ax.tick_params(colors=TEXT_SECONDARY, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(BORDER_SUBTLE)
    ax.grid(True, linestyle="--", alpha=0.25, color="#27272a")


class TrajectoryView(QWidget):
    """Tabbed flight dynamics plots with synchronized vertical magnetic playhead tracking."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._trajectory: TrajectoryResult | None = None
        self._playhead_lines: list = []
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()

        # Tab 1: Altitude vs Downrange
        self.canvas_alt = self._create_canvas()
        self.tabs.addTab(self.canvas_alt, "📈 Altitude Profile")

        # Tab 2: Dynamic Pressure & Max-Q
        self.canvas_q = self._create_canvas()
        self.tabs.addTab(self.canvas_q, "🌪️ Max-Q Dynamic Pressure")

        # Tab 3: Velocity & Mach Number
        self.canvas_v = self._create_canvas()
        self.tabs.addTab(self.canvas_v, "⚡ Velocity && Mach")

        # Tab 4: Axial G-Force
        self.canvas_g = self._create_canvas()
        self.tabs.addTab(self.canvas_g, "🚀 Acceleration (G-force)")

        layout.addWidget(self.tabs)

    def _create_canvas(self) -> FigureCanvas:
        fig = Figure(figsize=(5.5, 3.8), facecolor=SPACE_BLACK, tight_layout=True)
        canvas = FigureCanvas(fig)
        return canvas

    def update_trajectory(self, traj: TrajectoryResult) -> None:
        self._trajectory = traj
        if not traj.points:
            return

        t = [p.time_s for p in traj.points]
        alt_km = [p.altitude_m / 1000.0 for p in traj.points]
        downrange_km = [p.downrange_m / 1000.0 for p in traj.points]
        v_mps = [p.velocity_m_per_s for p in traj.points]
        q_kpa = [p.dynamic_pressure_pa / 1000.0 for p in traj.points]
        accel_g = [p.acceleration_g for p in traj.points]
        mach = [p.mach for p in traj.points]

        self._playhead_lines.clear()

        # -------------------------------------------------------------
        # 1. Altitude vs Downrange
        # -------------------------------------------------------------
        fig1 = self.canvas_alt.figure
        fig1.clear()
        ax1 = fig1.add_subplot(111)
        _setup_fcp_axes(ax1, "ASCENT ALTITUDE PROFILE", "Downrange Ground Distance (km)", "Altitude (km)")
        ax1.plot(downrange_km, alt_km, color=COLOR_ELECTRIC_BLUE, linewidth=2.0, label="Flight Arc")
        ax1.fill_between(downrange_km, alt_km, color=COLOR_ELECTRIC_BLUE, alpha=0.08)
        if traj.final_orbit_altitude_m > 0:
            ax1.axhline(traj.final_orbit_altitude_m / 1000.0, color=COLOR_FLIGHT_GREEN, linestyle=":", alpha=0.7, label="Target LEO")
        ax1.legend(facecolor=BG_CARD, edgecolor=BORDER_SUBTLE, labelcolor=TEXT_PRIMARY, fontsize=8)
        self.canvas_alt.draw()

        # -------------------------------------------------------------
        # 2. Dynamic Pressure & Max-Q
        # -------------------------------------------------------------
        fig2 = self.canvas_q.figure
        fig2.clear()
        ax2 = fig2.add_subplot(111)
        _setup_fcp_axes(ax2, "AERODYNAMIC DYNAMIC PRESSURE q(t)", "Flight Time T+ (s)", "Dynamic Pressure (kPa)")
        ax2.plot(t, q_kpa, color=COLOR_SUNSET_AMBER, linewidth=2.0, label="Dynamic Pressure q(t)")
        ax2.fill_between(t, q_kpa, color=COLOR_SUNSET_AMBER, alpha=0.08)

        # Max-Q Marker Callout
        max_q_kpa = traj.max_q_pa / 1000.0
        ax2.scatter([traj.max_q_time_s], [max_q_kpa], color=COLOR_ALERT_CORAL, s=50, zorder=5)
        ax2.annotate(
            f"Max-Q: {max_q_kpa:.1f} kPa\n(T+{traj.max_q_time_s:.1f}s)",
            xy=(traj.max_q_time_s, max_q_kpa),
            xytext=(traj.max_q_time_s + 18, max_q_kpa + 3),
            arrowprops=dict(facecolor=COLOR_ALERT_CORAL, edgecolor=COLOR_ALERT_CORAL, arrowstyle="->", lw=1.2),
            color=TEXT_PRIMARY,
            fontsize=8,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=BG_CARD, edgecolor=COLOR_ALERT_CORAL),
        )
        line_q = ax2.axvline(0.0, color=COLOR_ALERT_CORAL, linestyle="-", linewidth=1.5, alpha=0.8)
        self._playhead_lines.append((ax2, line_q, self.canvas_q))
        ax2.legend(facecolor=BG_CARD, edgecolor=BORDER_SUBTLE, labelcolor=TEXT_PRIMARY, fontsize=8)
        self.canvas_q.draw()

        # -------------------------------------------------------------
        # 3. Velocity & Mach Number
        # -------------------------------------------------------------
        fig3 = self.canvas_v.figure
        fig3.clear()
        ax3 = fig3.add_subplot(111)
        _setup_fcp_axes(ax3, "INERTIAL VELOCITY & MACH NUMBER", "Flight Time T+ (s)", "Velocity (m/s)")
        l1 = ax3.plot(t, v_mps, color=COLOR_CYAN, linewidth=2.0, label="Velocity (m/s)")
        ax3.fill_between(t, v_mps, color=COLOR_CYAN, alpha=0.06)

        ax3_mach = ax3.twinx()
        ax3_mach.set_ylabel("Mach", color=COLOR_METHANE_VIOLET, fontsize=9)
        ax3_mach.tick_params(colors=COLOR_METHANE_VIOLET, labelsize=8)
        l2 = ax3_mach.plot(t, mach, color=COLOR_METHANE_VIOLET, linestyle="--", linewidth=1.5, label="Mach")
        for spine in ax3_mach.spines.values():
            spine.set_color(BORDER_SUBTLE)

        line_v = ax3.axvline(0.0, color=COLOR_ALERT_CORAL, linestyle="-", linewidth=1.5, alpha=0.8)
        self._playhead_lines.append((ax3, line_v, self.canvas_v))

        lines = l1 + l2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, facecolor=BG_CARD, edgecolor=BORDER_SUBTLE, labelcolor=TEXT_PRIMARY, fontsize=8)
        self.canvas_v.draw()

        # -------------------------------------------------------------
        # 4. Acceleration (G-force)
        # -------------------------------------------------------------
        fig4 = self.canvas_g.figure
        fig4.clear()
        ax4 = fig4.add_subplot(111)
        _setup_fcp_axes(ax4, "AXIAL ACCELERATION (G-FORCE)", "Flight Time T+ (s)", "Acceleration (g)")
        ax4.plot(t, accel_g, color=COLOR_FLIGHT_GREEN, linewidth=2.0, label="Axial G-force")
        ax4.fill_between(t, accel_g, color=COLOR_FLIGHT_GREEN, alpha=0.08)
        ax4.axhline(traj.max_acceleration_g, color=COLOR_ALERT_CORAL, linestyle=":", label=f"Peak: {traj.max_acceleration_g:.2f}g")

        line_g = ax4.axvline(0.0, color=COLOR_ALERT_CORAL, linestyle="-", linewidth=1.5, alpha=0.8)
        self._playhead_lines.append((ax4, line_g, self.canvas_g))
        ax4.legend(facecolor=BG_CARD, edgecolor=BORDER_SUBTLE, labelcolor=TEXT_PRIMARY, fontsize=8)
        self.canvas_g.draw()

    def set_flight_time(self, time_s: float) -> None:
        """Move vertical playhead line across dynamic pressure, velocity, and acceleration plots."""
        for ax, line, canvas in self._playhead_lines:
            line.set_xdata([time_s, time_s])
            canvas.draw_idle()
