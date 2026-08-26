"""Aerospace Technical CAD Cutaway Vector Blueprint Canvas Widget."""

from math import cos, sin

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget

from launchvehiclelab.core.domain import CoupledVehicleResult, TrajectoryResult
from launchvehiclelab.ui.theme import (
    BG_BASE,
    BG_CARD,
    BG_PANEL,
    BORDER_HAIRLINE,
    COLOR_ALERT_CORAL,
    COLOR_CYAN,
    COLOR_ELECTRIC_BLUE,
    COLOR_FLIGHT_GREEN,
    COLOR_GOLD,
    COLOR_METHANE_VIOLET,
    COLOR_SUNSET_AMBER,
    PROPELLANT_COLORS,
    SPACE_BLACK,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_TERTIARY,
)


class RocketCanvas(QWidget):
    """High-fidelity aerospace technical cutaway vector canvas with internal structures and leader callouts."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._vehicle: CoupledVehicleResult | None = None
        self._trajectory: TrajectoryResult | None = None
        self._current_time_s: float = 0.0
        self._flame_phase: float = 0.0

        self.setMinimumSize(360, 540)
        self.setStyleSheet(f"background-color: {SPACE_BLACK}; border: 1px solid {BORDER_HAIRLINE}; border-radius: 12px;")

    def set_vehicle(self, vehicle: CoupledVehicleResult) -> None:
        self._vehicle = vehicle
        self.update()

    def set_trajectory(self, trajectory: TrajectoryResult) -> None:
        self._trajectory = trajectory
        self.update()

    def set_flight_time(self, time_s: float) -> None:
        self._current_time_s = time_s
        self._flame_phase += 0.25
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # 1. Technical Dark CAD Canvas Background
        painter.fillRect(0, 0, w, h, QColor(SPACE_BLACK))

        # Precision 24px Engineering Grid
        grid_pen = QPen(QColor("#131317"), 0.5)
        painter.setPen(grid_pen)
        for gx in range(0, w, 24):
            painter.drawLine(gx, 0, gx, h)
        for gy in range(0, h, 24):
            painter.drawLine(0, gy, w, gy)

        # Technical Corner Registration Marks
        corner_pen = QPen(QColor("#2a2a32"), 1.0)
        painter.setPen(corner_pen)
        for cx_val in [24, w - 24]:
            for cy_val in [24, h - 24]:
                painter.drawLine(cx_val - 6, cy_val, cx_val + 6, cy_val)
                painter.drawLine(cx_val, cy_val - 6, cx_val, cy_val + 6)

        if self._vehicle is None:
            painter.setPen(QColor(TEXT_MUTED))
            painter.setFont(QFont("-apple-system", 12, QFont.Weight.Medium))
            painter.drawText(
                QRectF(0, 0, w, h),
                Qt.AlignmentFlag.AlignCenter,
                "AEROSPACE CAD BLUEPRINT\nClick 'Size Vehicle' to generate technical cutaway.",
            )
            return

        v = self._vehicle
        geom = v.vehicle_geometry
        total_len = max(1.0, geom.total_length_m)

        # Flight Phase State
        t = self._current_time_s
        t_meco = 174.0
        t_staging = 176.6
        t_fairing = 186.6
        t_seco = 496.7

        is_s1_firing = (0.0 < t < t_meco)
        is_staged = (t >= t_staging)
        is_s2_firing = (t_staging <= t < t_seco)
        is_fairing_open = (t >= t_fairing)

        # Layout Geometry
        margin_y = 60.0
        drawable_h = h - 2.0 * margin_y - 45.0
        scale_y = drawable_h / total_len
        center_x = w * 0.44

        def m_to_px(meters: float) -> float:
            return meters * scale_y

        def d_to_px(diameter_m: float) -> float:
            return max(20.0, diameter_m * scale_y * 2.1)

        cur_y = margin_y

        # Centerline Datum
        centerline_pen = QPen(QColor("#27272a"), 0.75, Qt.PenStyle.DashDotLine)
        painter.setPen(centerline_pen)
        painter.drawLine(int(center_x), int(margin_y - 20), int(center_x), int(h - 20))

        # -------------------------------------------------------------
        # 1. Payload Fairing & Satellite Bus
        # -------------------------------------------------------------
        fairing = geom.fairing
        f_dia_px = d_to_px(fairing.diameter_m)
        f_len_px = m_to_px(fairing.total_length_m)
        f_nose_px = m_to_px(fairing.nose_cone_length_m)

        if not is_fairing_open:
            # Closed Composite Fairing (Technical Cutaway: Left skin, Right payload bay)
            top_pt = QPointF(center_x, cur_y)
            left_shoulder = QPointF(center_x - f_dia_px / 2.0, cur_y + f_nose_px)
            right_shoulder = QPointF(center_x + f_dia_px / 2.0, cur_y + f_nose_px)
            left_base = QPointF(center_x - f_dia_px / 2.0, cur_y + f_len_px)
            right_base = QPointF(center_x + f_dia_px / 2.0, cur_y + f_len_px)

            fairing_path = QPainterPath()
            fairing_path.moveTo(top_pt)
            fairing_path.quadTo(QPointF(center_x - f_dia_px * 0.35, cur_y + f_nose_px * 0.6), left_shoulder)
            fairing_path.lineTo(left_base)
            fairing_path.lineTo(right_base)
            fairing_path.lineTo(right_shoulder)
            fairing_path.quadTo(QPointF(center_x + f_dia_px * 0.35, cur_y + f_nose_px * 0.6), top_pt)
            fairing_path.closeSubpath()

            # Technical gradient fill
            f_grad = QLinearGradient(center_x - f_dia_px / 2.0, 0, center_x + f_dia_px / 2.0, 0)
            f_grad.setColorAt(0.0, QColor("#1e2229"))
            f_grad.setColorAt(0.5, QColor("#2d333f"))
            f_grad.setColorAt(0.51, QColor("#14171d"))
            f_grad.setColorAt(1.0, QColor("#1b1f26"))
            painter.setBrush(QBrush(f_grad))
            painter.setPen(QPen(QColor(COLOR_CYAN), 1.0))
            painter.drawPath(fairing_path)

            # Internal Payload Adapter Cone inside fairing
            adapter_path = QPainterPath()
            adapter_path.moveTo(center_x - f_dia_px * 0.25, cur_y + f_len_px)
            adapter_path.lineTo(center_x - f_dia_px * 0.15, cur_y + f_len_px * 0.6)
            adapter_path.lineTo(center_x + f_dia_px * 0.15, cur_y + f_len_px * 0.6)
            adapter_path.lineTo(center_x + f_dia_px * 0.25, cur_y + f_len_px)
            painter.setBrush(QColor("#2c3440"))
            painter.setPen(QPen(QColor("#64748b"), 0.75))
            painter.drawPath(adapter_path)

            # Technical Leader Callout
            self._draw_leader_callout(
                painter,
                center_x + f_dia_px / 2.0,
                cur_y + f_len_px * 0.4,
                center_x + f_dia_px / 2.0 + 35,
                cur_y + f_len_px * 0.35,
                "PAYLOAD FAIRING",
                f"Ø{fairing.diameter_m:.1f}m · L {fairing.total_length_m:.1f}m · {fairing.internal_volume_m3:.1f} m³",
            )
        else:
            # Satellite Deployment (Solar Array Spread)
            sat_w = f_dia_px * 0.55
            sat_h = f_len_px * 0.65
            sat_rect = QRectF(center_x - sat_w / 2.0, cur_y + f_len_px * 0.2, sat_w, sat_h)

            sat_grad = QLinearGradient(center_x - sat_w / 2.0, 0, center_x + sat_w / 2.0, 0)
            sat_grad.setColorAt(0.0, QColor("#854d0e"))
            sat_grad.setColorAt(0.5, QColor("#eab308"))
            sat_grad.setColorAt(1.0, QColor("#854d0e"))
            painter.setBrush(QBrush(sat_grad))
            painter.setPen(QPen(QColor("#fde047"), 1.0))
            painter.drawRoundedRect(sat_rect, 3.0, 3.0)

            # Solar Array Panels
            painter.setBrush(QColor("#1e3a8a"))
            painter.setPen(QPen(QColor(COLOR_CYAN), 0.75))
            painter.drawRect(QRectF(center_x - sat_w * 1.3, cur_y + f_len_px * 0.35, sat_w * 0.7, sat_h * 0.4))
            painter.drawRect(QRectF(center_x + sat_w * 0.6, cur_y + f_len_px * 0.35, sat_w * 0.7, sat_h * 0.4))

            self._draw_leader_callout(
                painter,
                center_x + sat_w / 2.0,
                cur_y + f_len_px * 0.4,
                center_x + f_dia_px / 2.0 + 35,
                cur_y + f_len_px * 0.35,
                "SATELLITE DEPLOYED",
                f"{v.mission.payload_mass_kg:,.0f} kg Payload in LEO",
            )

        cur_y += f_len_px

        # -------------------------------------------------------------
        # 2. Stage 2 (Upper Stage Technical Cutaway)
        # -------------------------------------------------------------
        s2 = v.stage2
        s2_dia_px = d_to_px(s2.geometry.diameter_m)
        s2_len_px = m_to_px(s2.geometry.total_length_m)

        # Stage 2 LOX Tank
        ox2_len_px = m_to_px(s2.geometry.oxidizer_tank.total_length_m)
        self._draw_cad_tank(
            painter,
            center_x,
            cur_y,
            s2_dia_px,
            ox2_len_px,
            QColor(PROPELLANT_COLORS["LOX"]),
            "S2 LOX",
            f"{s2.oxidizer_mass_kg:,.0f} kg",
        )
        cur_y += ox2_len_px

        # Stage 2 Fuel Tank (Common Bulkhead Dome)
        fuel2_len_px = m_to_px(s2.geometry.fuel_tank.total_length_m)
        fuel2_color = QColor(PROPELLANT_COLORS["CH4"] if "METH" in s2.propellant_combo.name else PROPELLANT_COLORS["RP1"])
        self._draw_cad_tank(
            painter,
            center_x,
            cur_y,
            s2_dia_px,
            fuel2_len_px,
            fuel2_color,
            "S2 FUEL",
            f"{s2.fuel_mass_kg:,.0f} kg",
        )
        cur_y += fuel2_len_px

        # Stage 2 Vacuum Engine Nozzle
        skirt2_px = max(9.0, s2_len_px - ox2_len_px - fuel2_len_px)
        self._draw_cad_engine_bay(painter, center_x, cur_y, s2_dia_px, skirt2_px, 1)
        cur_y += skirt2_px

        # Stage 2 Callout
        self._draw_leader_callout(
            painter,
            center_x + s2_dia_px / 2.0,
            cur_y - s2_len_px / 2.0,
            center_x + s2_dia_px / 2.0 + 35,
            cur_y - s2_len_px / 2.0,
            "STAGE 2 UPPER STAGE",
            f"{s2.propellant_combo.name} · ΔV {s2.sizing.delta_v_m_per_s:,.0f} m/s",
        )

        # Stage 2 Exhaust Plume
        if is_s2_firing:
            self._draw_mach_diamonds(painter, center_x, cur_y, s2_dia_px * 0.5, 36.0, QColor(COLOR_METHANE_VIOLET))

        # -------------------------------------------------------------
        # 3. Interstage Structure & Separation
        # -------------------------------------------------------------
        interstage_px = max(10.0, m_to_px(geom.interstage_length_m))
        if is_staged:
            cur_y += 20.0
            painter.setPen(QPen(QColor(COLOR_ALERT_CORAL), 1.0, Qt.PenStyle.DashLine))
            painter.drawLine(int(center_x - s2_dia_px * 0.7), int(cur_y), int(center_x + s2_dia_px * 0.7), int(cur_y))
        else:
            self._draw_cad_interstage(painter, center_x, cur_y, s2_dia_px, d_to_px(geom.stage1.diameter_m), interstage_px)
            cur_y += interstage_px

        # -------------------------------------------------------------
        # 4. Stage 1 (Booster Technical Cutaway)
        # -------------------------------------------------------------
        s1 = v.stage1
        s1_dia_px = d_to_px(s1.geometry.diameter_m)
        s1_len_px = m_to_px(s1.geometry.total_length_m)

        opacity = 0.22 if is_staged else 1.0
        painter.setOpacity(opacity)

        # S1 LOX Tank
        ox1_len_px = m_to_px(s1.geometry.oxidizer_tank.total_length_m)
        self._draw_cad_tank(
            painter,
            center_x,
            cur_y,
            s1_dia_px,
            ox1_len_px,
            QColor(PROPELLANT_COLORS["LOX"]),
            "S1 LOX",
            f"{s1.oxidizer_mass_kg:,.0f} kg",
        )
        cur_y += ox1_len_px

        # S1 Fuel Tank
        fuel1_len_px = m_to_px(s1.geometry.fuel_tank.total_length_m)
        self._draw_cad_tank(
            painter,
            center_x,
            cur_y,
            s1_dia_px,
            fuel1_len_px,
            QColor(PROPELLANT_COLORS["RP1"]),
            "S1 FUEL",
            f"{s1.fuel_mass_kg:,.0f} kg",
        )
        cur_y += fuel1_len_px

        # S1 Booster Base (3-Engine Cluster)
        skirt1_px = max(12.0, s1_len_px - ox1_len_px - fuel1_len_px)
        self._draw_cad_engine_bay(painter, center_x, cur_y, s1_dia_px, skirt1_px, 3)
        cur_y += skirt1_px

        # Stage 1 Callout
        self._draw_leader_callout(
            painter,
            center_x + s1_dia_px / 2.0,
            cur_y - s1_len_px / 2.0,
            center_x + s1_dia_px / 2.0 + 35,
            cur_y - s1_len_px / 2.0,
            "STAGE 1 BOOSTER",
            f"{s1.propellant_combo.name} · ΔV {s1.sizing.delta_v_m_per_s:,.0f} m/s",
        )

        # S1 Exhaust Flame Plume (Supersonic Shock Diamonds)
        if is_s1_firing:
            painter.setOpacity(1.0)
            self._draw_mach_diamonds(painter, center_x, cur_y, s1_dia_px * 0.8, 55.0, QColor(COLOR_SUNSET_AMBER))

        painter.setOpacity(1.0)

        # -------------------------------------------------------------
        # 5. Technical Dimension Datum Line (Left Side)
        # -------------------------------------------------------------
        dim_x = center_x - max(s1_dia_px, f_dia_px) * 0.75 - 28.0
        dim_pen = QPen(QColor(BORDER_HAIRLINE), 1.0)
        painter.setPen(dim_pen)
        painter.drawLine(int(dim_x), int(margin_y), int(dim_x), int(cur_y))

        # Precision Tick Arrowheads
        painter.drawLine(int(dim_x - 4), int(margin_y), int(dim_x + 4), int(margin_y))
        painter.drawLine(int(dim_x - 4), int(cur_y), int(dim_x + 4), int(cur_y))

        painter.save()
        painter.translate(dim_x - 14, (margin_y + cur_y) / 2.0)
        painter.rotate(-90)
        painter.setPen(QColor(TEXT_SECONDARY))
        painter.setFont(QFont("SF Mono, Monaco, Menlo, monospace", 9, QFont.Weight.Bold))
        painter.drawText(
            QRectF(-120, -12, 240, 16),
            Qt.AlignmentFlag.AlignCenter,
            f"HEIGHT {geom.total_length_m:.2f} m · L/D {geom.fineness_ratio:.1f}",
        )
        painter.restore()

    def _draw_cad_tank(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        width_px: float,
        height_px: float,
        fluid_color: QColor,
        title: str,
        subtitle: str,
    ) -> None:
        """Draw an aerospace cutaway tank: internal common bulkheads, isogrid wall texture, fluid gradient."""
        cap_h = min(height_px * 0.22, width_px * 0.22)
        rect = QRectF(cx - width_px / 2.0, top_y, width_px, height_px)

        # Outer Tank Contour with 2:1 Ellipsoidal Caps
        path = QPainterPath()
        path.addRoundedRect(rect, width_px * 0.12, cap_h)

        # Aerospace Anodized / Cryogenic Gradient with Inner Cutaway
        grad = QLinearGradient(cx - width_px / 2.0, 0, cx + width_px / 2.0, 0)
        grad.setColorAt(0.0, QColor("#111317"))
        grad.setColorAt(0.3, fluid_color.darker(300))
        grad.setColorAt(0.5, fluid_color.darker(160))
        grad.setColorAt(0.7, fluid_color.darker(300))
        grad.setColorAt(1.0, QColor("#111317"))

        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(BORDER_HAIRLINE), 1.0))
        painter.drawPath(path)

        # Internal Isogrid Stringer Texture Lines (Right Half)
        painter.setPen(QPen(fluid_color.darker(180), 0.5, Qt.PenStyle.DotLine))
        iso_spacing = 14.0
        for iy in range(int(top_y + cap_h), int(top_y + height_px - cap_h), int(iso_spacing)):
            painter.drawLine(int(cx), iy, int(cx + width_px / 2.0 - 2), iy)

        # Internal Center Feedline Pipe
        pipe_pen = QPen(QColor("#52525b"), 1.5)
        painter.setPen(pipe_pen)
        painter.drawLine(int(cx), int(top_y), int(cx), int(top_y + height_px))

        # Precision Tank Labels (Left-aligned & crisp)
        painter.setPen(QColor(TEXT_PRIMARY))
        painter.setFont(QFont("-apple-system", 9, QFont.Weight.Bold))
        painter.drawText(
            QRectF(cx - width_px / 2.0, top_y + height_px * 0.25, width_px, 14),
            Qt.AlignmentFlag.AlignCenter,
            title,
        )
        painter.setPen(QColor(TEXT_SECONDARY))
        painter.setFont(QFont("SF Mono, Monaco, Menlo, monospace", 8))
        painter.drawText(
            QRectF(cx - width_px / 2.0, top_y + height_px * 0.55, width_px, 14),
            Qt.AlignmentFlag.AlignCenter,
            subtitle,
        )

    def _draw_cad_engine_bay(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        width_px: float,
        height_px: float,
        bells: int,
    ) -> None:
        rect = QRectF(cx - width_px / 2.0, top_y, width_px, height_px)
        painter.setBrush(QColor("#0d0e12"))
        painter.setPen(QPen(QColor(BORDER_HAIRLINE), 0.75))
        painter.drawRect(rect)

        # Engine Bells
        bell_spacing = width_px / (bells + 1)
        for i in range(bells):
            bx = cx - width_px / 2.0 + (i + 1) * bell_spacing
            b_w = bell_spacing * 0.55

            bell_path = QPainterPath()
            bell_path.moveTo(bx - b_w * 0.25, top_y)
            bell_path.lineTo(bx + b_w * 0.25, top_y)
            bell_path.lineTo(bx + b_w * 0.48, top_y + height_px)
            bell_path.lineTo(bx - b_w * 0.48, top_y + height_px)
            bell_path.closeSubpath()

            painter.setBrush(QColor("#27272a"))
            painter.setPen(QPen(QColor("#52525b"), 0.75))
            painter.drawPath(bell_path)

    def _draw_cad_interstage(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        top_w: float,
        bot_w: float,
        height_px: float,
    ) -> None:
        path = QPainterPath()
        path.moveTo(cx - top_w / 2.0, top_y)
        path.lineTo(cx + top_w / 2.0, top_y)
        path.lineTo(cx + bot_w / 2.0, top_y + height_px)
        path.lineTo(cx - bot_w / 2.0, top_y + height_px)
        path.closeSubpath()

        painter.setBrush(QColor("#090a0d"))
        painter.setPen(QPen(QColor(BORDER_HAIRLINE), 0.75))
        painter.drawPath(path)

        # Truss Lattice Pattern
        painter.setPen(QPen(QColor("#3f3f46"), 0.5, Qt.PenStyle.DashLine))
        painter.drawLine(int(cx - top_w * 0.4), int(top_y), int(cx + bot_w * 0.4), int(top_y + height_px))
        painter.drawLine(int(cx + top_w * 0.4), int(top_y), int(cx - bot_w * 0.4), int(top_y + height_px))

    def _draw_mach_diamonds(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        base_w: float,
        flame_len: float,
        core_color: QColor,
    ) -> None:
        """Physically accurate supersonic rocket exhaust plume with diamond shock waves."""
        flicker = sin(self._flame_phase) * 3.5
        total_flame = flame_len + flicker

        # Outer Expansion Plume
        plume_path = QPainterPath()
        plume_path.moveTo(cx - base_w / 2.0, top_y)
        plume_path.quadTo(cx - base_w * 0.9, top_y + total_flame * 0.55, cx, top_y + total_flame)
        plume_path.quadTo(cx + base_w * 0.9, top_y + total_flame * 0.55, cx + base_w / 2.0, top_y)
        plume_path.closeSubpath()

        p_grad = QRadialGradient(cx, top_y + total_flame * 0.3, total_flame)
        p_grad.setColorAt(0.0, QColor("#ffffff"))
        p_grad.setColorAt(0.25, core_color.lighter(160))
        p_grad.setColorAt(0.7, core_color)
        p_grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(p_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(plume_path)

        # Mach Shock Diamonds (3 small bright diamonds along plume center)
        painter.setBrush(QColor("#ffffff"))
        for d_idx in range(1, 4):
            dy = top_y + (d_idx * total_flame * 0.22)
            dw = base_w * 0.18 * (1.0 - d_idx * 0.2)
            dh = 4.0

            d_path = QPainterPath()
            d_path.moveTo(cx, dy - dh)
            d_path.lineTo(cx + dw, dy)
            d_path.lineTo(cx, dy + dh)
            d_path.lineTo(cx - dw, dy)
            d_path.closeSubpath()
            painter.drawPath(d_path)

    def _draw_leader_callout(
        self,
        painter: QPainter,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        title: str,
        subtitle: str,
    ) -> None:
        """Technical engineering leader line with dot marker and frosted glass text card."""
        # Leader line
        line_pen = QPen(QColor("#3f3f46"), 0.75)
        painter.setPen(line_pen)
        painter.drawLine(int(start_x), int(start_y), int(start_x + 12), int(end_y))
        painter.drawLine(int(start_x + 12), int(end_y), int(end_x), int(end_y))

        # Origin Dot
        painter.setBrush(QColor(COLOR_CYAN))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(start_x, start_y), 2.0, 2.0)

        # Callout Text
        painter.setPen(QColor(TEXT_PRIMARY))
        painter.setFont(QFont("-apple-system", 9, QFont.Weight.Bold))
        painter.drawText(int(end_x + 6), int(end_y - 2), title)

        painter.setPen(QColor(TEXT_TERTIARY))
        painter.setFont(QFont("SF Mono, Monaco, Menlo, monospace", 8))
        painter.drawText(int(end_x + 6), int(end_y + 12), subtitle)
