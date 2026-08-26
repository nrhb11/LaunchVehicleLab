"""Interactive multi-curve trajectory & flight dynamics dashboard widget."""

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from launchvehiclelab.core.domain import TrajectoryResult
from launchvehiclelab.ui.theme import (
    ACCENT_AMBER,
    ACCENT_BLUE,
    ACCENT_GREEN,
    ACCENT_PURPLE,
    ACCENT_RED,
    DARK_BG_CARD,
    DARK_BG_PANEL,
    DARK_BORDER,
    DARK_TEXT_PRIMARY,
    DARK_TEXT_SECONDARY,
)


def _setup_dark_axes(ax, title: str, xlabel: str, ylabel: str) -> None:
    """Apply modern dark styling to a Matplotlib Axes."""
    ax.set_facecolor(DARK_BG_CARD)
    ax.set_title(title, color=DARK_TEXT_PRIMARY, fontsize=12, fontweight="bold", pad=10)
    ax.set_xlabel(xlabel, color=DARK_TEXT_SECONDARY, fontsize=10)
    ax.set_ylabel(ylabel, color=DARK_TEXT_SECONDARY, fontsize=10)
    ax.tick_params(colors=DARK_TEXT_SECONDARY, labelsize=9)
    for spine in ax.spines.values():
        spine.set_color(DARK_BORDER)
    ax.grid(True, linestyle="--", alpha=0.35, color=DARK_BORDER)


class TrajectoryView(QWidget):
    """Tabbed dashboard visualizing 3DOF ascent flight dynamics time series."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()

        # Tab 1: Altitude & Downrange
        self.canvas_alt = self._create_canvas()
        self.tabs.addTab(self.canvas_alt, "📈 Altitude & Profile")

        # Tab 2: Dynamic Pressure & Max-Q
        self.canvas_q = self._create_canvas()
        self.tabs.addTab(self.canvas_q, "🌪️ Max-Q Dynamic Pressure")

        # Tab 3: Flight Velocity & Mach
        self.canvas_v = self._create_canvas()
        self.tabs.addTab(self.canvas_v, "⚡ Velocity & Mach")

        # Tab 4: Acceleration (G-force)
        self.canvas_g = self._create_canvas()
        self.tabs.addTab(self.canvas_g, "🚀 Acceleration (G-force)")

        layout.addWidget(self.tabs)

    def _create_canvas(self) -> FigureCanvas:
        fig = Figure(figsize=(6, 4), facecolor=DARK_BG_PANEL, tight_layout=True)
        canvas = FigureCanvas(fig)
        return canvas

    def update_trajectory(self, traj: TrajectoryResult) -> None:
        if not traj.points:
            return

        t = [p.time_s for p in traj.points]
        alt_km = [p.altitude_m / 1000.0 for p in traj.points]
        downrange_km = [p.downrange_m / 1000.0 for p in traj.points]
        v_mps = [p.velocity_m_per_s for p in traj.points]
        q_kpa = [p.dynamic_pressure_pa / 1000.0 for p in traj.points]
        accel_g = [p.acceleration_g for p in traj.points]
        mach = [p.mach for p in traj.points]

        # -------------------------------------------------------------
        # 1. Altitude vs Downrange & Time
        # -------------------------------------------------------------
        fig1 = self.canvas_alt.figure
        fig1.clear()
        ax1 = fig1.add_subplot(111)
        _setup_dark_axes(ax1, "Ascent Altitude Profile", "Downrange Ground Distance (km)", "Altitude (km)")
        ax1.plot(downrange_km, alt_km, color=ACCENT_BLUE, linewidth=2.2, label="Flight Path")
        # Target Orbit Line
        if traj.final_orbit_altitude_m > 0:
            target_km = traj.final_orbit_altitude_m / 1000.0
            ax1.axhline(target_km, color=ACCENT_GREEN, linestyle=":", alpha=0.8, label=f"Target Orbit ({target_km:.0f} km)")
        ax1.legend(facecolor=DARK_BG_CARD, edgecolor=DARK_BORDER, labelcolor=DARK_TEXT_PRIMARY)
        self.canvas_alt.draw()

        # -------------------------------------------------------------
        # 2. Dynamic Pressure & Max-Q
        # -------------------------------------------------------------
        fig2 = self.canvas_q.figure
        fig2.clear()
        ax2 = fig2.add_subplot(111)
        _setup_dark_axes(ax2, "Dynamic Pressure q(t) & Max-Q", "Flight Time T+ (s)", "Dynamic Pressure (kPa)")
        ax2.plot(t, q_kpa, color=ACCENT_AMBER, linewidth=2.2, label="Dynamic Pressure q(t)")
        # Annotate Max-Q
        max_q_kpa = traj.max_q_pa / 1000.0
        ax2.scatter([traj.max_q_time_s], [max_q_kpa], color=ACCENT_RED, s=60, zorder=5)
        ax2.annotate(
            f"Max-Q: {max_q_kpa:.2f} kPa\n(T+{traj.max_q_time_s:.1f}s, {traj.max_q_alt_m / 1000.0:.1f} km)",
            xy=(traj.max_q_time_s, max_q_kpa),
            xytext=(traj.max_q_time_s + 20, max_q_kpa + 4),
            arrowprops=dict(facecolor=ACCENT_RED, edgecolor=ACCENT_RED, arrowstyle="->", lw=1.5),
            color=DARK_TEXT_PRIMARY,
            fontsize=10,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=DARK_BG_CARD, edgecolor=ACCENT_RED),
        )
        ax2.legend(facecolor=DARK_BG_CARD, edgecolor=DARK_BORDER, labelcolor=DARK_TEXT_PRIMARY)
        self.canvas_q.draw()

        # -------------------------------------------------------------
        # 3. Flight Velocity & Mach Number
        # -------------------------------------------------------------
        fig3 = self.canvas_v.figure
        fig3.clear()
        ax3 = fig3.add_subplot(111)
        _setup_dark_axes(ax3, "Inertial Velocity & Mach Number", "Flight Time T+ (s)", "Velocity (m/s)")
        line1 = ax3.plot(t, v_mps, color=ACCENT_BLUE, linewidth=2.2, label="Velocity (m/s)")

        # Secondary Y-axis for Mach
        ax3_mach = ax3.twinx()
        ax3_mach.set_ylabel("Mach Number", color=ACCENT_PURPLE, fontsize=10)
        ax3_mach.tick_params(colors=ACCENT_PURPLE, labelsize=9)
        line2 = ax3_mach.plot(t, mach, color=ACCENT_PURPLE, linestyle="--", linewidth=1.8, label="Mach")
        for spine in ax3_mach.spines.values():
            spine.set_color(DARK_BORDER)

        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax3.legend(lines, labels, facecolor=DARK_BG_CARD, edgecolor=DARK_BORDER, labelcolor=DARK_TEXT_PRIMARY)
        self.canvas_v.draw()

        # -------------------------------------------------------------
        # 4. Acceleration (G-force)
        # -------------------------------------------------------------
        fig4 = self.canvas_g.figure
        fig4.clear()
        ax4 = fig4.add_subplot(111)
        _setup_dark_axes(ax4, "Axial Acceleration (G-Force)", "Flight Time T+ (s)", "Acceleration (g)")
        ax4.plot(t, accel_g, color=ACCENT_GREEN, linewidth=2.2, label="Axial Load")
        ax4.axhline(traj.max_acceleration_g, color=ACCENT_RED, linestyle=":", label=f"Peak Accel: {traj.max_acceleration_g:.2f} g")
        ax4.legend(facecolor=DARK_BG_CARD, edgecolor=DARK_BORDER, labelcolor=DARK_TEXT_PRIMARY)
        self.canvas_g.draw()
