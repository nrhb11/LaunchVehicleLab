"""Apple Final Cut Pro & CAD Studio inspired 2D vector rocket blueprint canvas."""

from math import sin

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
    PROPELLANT_COLORS,
    SPACE_BLACK,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


class RocketCanvas(QWidget):
    """High-end studio CAD vector canvas drawing the active dimensioned rocket with exhaust plumes."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._vehicle: CoupledVehicleResult | None = None
        self._trajectory: TrajectoryResult | None = None
        self._current_time_s: float = 0.0
        self._flame_phase: float = 0.0

        self.setMinimumSize(340, 520)
        self.setStyleSheet(f"background-color: {SPACE_BLACK}; border: 1px solid {BORDER_SUBTLE}; border-radius: 12px;")

    def set_vehicle(self, vehicle: CoupledVehicleResult) -> None:
        self._vehicle = vehicle
        self.update()

    def set_trajectory(self, trajectory: TrajectoryResult) -> None:
        self._trajectory = trajectory
        self.update()

    def set_flight_time(self, time_s: float) -> None:
        self._current_time_s = time_s
        self._flame_phase += 0.3
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # 1. Background OLED Canvas with Aerospace Blueprint Grid
        painter.fillRect(0, 0, w, h, QColor(SPACE_BLACK))

        # Precision Engineering Dot Grid
        grid_pen = QPen(QColor("#1f1f23"), 1)
        painter.setPen(grid_pen)
        for gx in range(0, w, 28):
            for gy in range(0, h, 28):
                painter.drawPoint(gx, gy)

        # Crosshairs at corners
        cross_pen = QPen(QColor(BORDER_SUBTLE), 1)
        painter.setPen(cross_pen)
        painter.drawLine(20, 20, 35, 20)
        painter.drawLine(20, 20, 20, 35)
        painter.drawLine(w - 20, 20, w - 35, 20)
        painter.drawLine(w - 20, 20, w - 20, 35)

        if self._vehicle is None:
            painter.setPen(QColor(TEXT_MUTED))
            painter.setFont(QFont("-apple-system", 13, QFont.Weight.Medium))
            painter.drawText(
                QRectF(0, 0, w, h),
                Qt.AlignmentFlag.AlignCenter,
                "Ready to Size Vehicle.\nClick 'Size Vehicle' to generate blueprint.",
            )
            return

        v = self._vehicle
        geom = v.vehicle_geometry
        total_len = max(1.0, geom.total_length_m)

        # Flight State Evaluation
        t = self._current_time_s
        t_meco = 174.0
        t_staging = 176.6
        t_fairing = 186.6
        t_seco = 496.7

        is_s1_firing = (0.0 < t < t_meco)
        is_staged = (t >= t_staging)
        is_s2_firing = (t_staging <= t < t_seco)
        is_fairing_open = (t >= t_fairing)

        # Scaling Dimensions
        margin_y = 60.0
        drawable_h = h - 2.0 * margin_y - 40.0  # leave room for flame
        scale_y = drawable_h / total_len
        center_x = w * 0.42

        def m_to_px(meters: float) -> float:
            return meters * scale_y

        def d_to_px(diameter_m: float) -> float:
            return max(18.0, diameter_m * scale_y * 2.3)

        cur_y = margin_y

        # -------------------------------------------------------------
        # 1. Payload Fairing / Satellite Deployment
        # -------------------------------------------------------------
        fairing = geom.fairing
        f_dia_px = d_to_px(fairing.diameter_m)
        f_len_px = m_to_px(fairing.total_length_m)
        f_nose_px = m_to_px(fairing.nose_cone_length_m)

        if not is_fairing_open:
            # Closed Carbon Composite Fairing with Gloss Specular Highlights
            top_pt = QPointF(center_x, cur_y)
            left_shoulder = QPointF(center_x - f_dia_px / 2.0, cur_y + f_nose_px)
            right_shoulder = QPointF(center_x + f_dia_px / 2.0, cur_y + f_nose_px)
            left_base = QPointF(center_x - f_dia_px / 2.0, cur_y + f_len_px)
            right_base = QPointF(center_x + f_dia_px / 2.0, cur_y + f_len_px)

            f_path = QPainterPath()
            f_path.moveTo(top_pt)
            f_path.quadTo(QPointF(center_x - f_dia_px * 0.35, cur_y + f_nose_px * 0.6), left_shoulder)
            f_path.lineTo(left_base)
            f_path.lineTo(right_base)
            f_path.lineTo(right_shoulder)
            f_path.quadTo(QPointF(center_x + f_dia_px * 0.35, cur_y + f_nose_px * 0.6), top_pt)
            f_path.closeSubpath()

            f_grad = QLinearGradient(center_x - f_dia_px / 2.0, 0, center_x + f_dia_px / 2.0, 0)
            f_grad.setColorAt(0.0, QColor("#1e293b"))
            f_grad.setColorAt(0.4, QColor("#475569"))
            f_grad.setColorAt(0.6, QColor("#64748b"))
            f_grad.setColorAt(1.0, QColor("#1e293b"))

            painter.setBrush(QBrush(f_grad))
            painter.setPen(QPen(QColor(COLOR_CYAN), 1.2))
            painter.drawPath(f_path)

            self._draw_glass_badge(
                painter,
                center_x + f_dia_px / 2.0 + 16,
                cur_y + f_len_px * 0.4,
                "Fairing",
                f"Ø{fairing.diameter_m:.1f}m · {fairing.internal_volume_m3:.1f}m³",
            )
        else:
            # Fairing Jettisoned: Glowing Satellite Gold Payload Revealed!
            sat_w = f_dia_px * 0.6
            sat_h = f_len_px * 0.7
            sat_rect = QRectF(center_x - sat_w / 2.0, cur_y + f_len_px * 0.2, sat_w, sat_h)
            sat_grad = QLinearGradient(center_x - sat_w / 2.0, 0, center_x + sat_w / 2.0, 0)
            sat_grad.setColorAt(0.0, QColor("#b45309"))
            sat_grad.setColorAt(0.5, QColor("#fbbf24"))
            sat_grad.setColorAt(1.0, QColor("#b45309"))
            painter.setBrush(QBrush(sat_grad))
            painter.setPen(QPen(QColor("#fef08a"), 1.2))
            painter.drawRoundedRect(sat_rect, 4.0, 4.0)

            # Solar Array Panels
            painter.setBrush(QColor("#1e3a8a"))
            painter.setPen(QPen(QColor(COLOR_CYAN), 1.0))
            painter.drawRect(QRectF(center_x - sat_w * 1.2, cur_y + f_len_px * 0.35, sat_w * 0.6, sat_h * 0.4))
            painter.drawRect(QRectF(center_x + sat_w * 0.6, cur_y + f_len_px * 0.35, sat_w * 0.6, sat_h * 0.4))

            self._draw_glass_badge(
                painter,
                center_x + f_dia_px / 2.0 + 16,
                cur_y + f_len_px * 0.4,
                "Payload Deployed",
                f"{v.mission.payload_mass_kg:,.0f} kg to LEO",
            )

        cur_y += f_len_px

        # -------------------------------------------------------------
        # 2. Stage 2 (Upper Stage)
        # -------------------------------------------------------------
        s2 = v.stage2
        s2_dia_px = d_to_px(s2.geometry.diameter_m)
        s2_len_px = m_to_px(s2.geometry.total_length_m)

        # S2 Oxidizer Tank (Electric Cyan)
        ox2_len_px = m_to_px(s2.geometry.oxidizer_tank.total_length_m)
        self._draw_specular_tank(
            painter,
            center_x,
            cur_y,
            s2_dia_px,
            ox2_len_px,
            QColor(PROPELLANT_COLORS["LOX"]),
            f"S2 LOX ({s2.oxidizer_mass_kg:,.0f} kg)",
        )
        cur_y += ox2_len_px

        # S2 Fuel Tank (Methane Purple / Kerosene Amber)
        fuel2_len_px = m_to_px(s2.geometry.fuel_tank.total_length_m)
        fuel2_color = QColor(PROPELLANT_COLORS["CH4"] if "METH" in s2.propellant_combo.name else PROPELLANT_COLORS["RP1"])
        self._draw_specular_tank(
            painter,
            center_x,
            cur_y,
            s2_dia_px,
            fuel2_len_px,
            fuel2_color,
            f"S2 Fuel ({s2.fuel_mass_kg:,.0f} kg)",
        )
        cur_y += fuel2_len_px

        # S2 Engine & Skirt
        skirt2_px = max(8.0, s2_len_px - ox2_len_px - fuel2_len_px)
        self._draw_engine_skirt(painter, center_x, cur_y, s2_dia_px, skirt2_px, 1)
        cur_y += skirt2_px

        # Stage 2 Vacuum Flame Plume
        if is_s2_firing:
            self._draw_exhaust_plume(painter, center_x, cur_y, s2_dia_px * 0.7, 35.0, QColor(COLOR_METHANE_VIOLET))

        # -------------------------------------------------------------
        # 3. Interstage Structure & Separation
        # -------------------------------------------------------------
        interstage_px = max(10.0, m_to_px(geom.interstage_length_m))
        if is_staged:
            # Draw Separation Ring Gap
            cur_y += 18.0
            painter.setPen(QPen(QColor(COLOR_ALERT_CORAL), 1.0, Qt.PenStyle.DashLine))
            painter.drawLine(int(center_x - s2_dia_px * 0.8), int(cur_y), int(center_x + s2_dia_px * 0.8), int(cur_y))
        else:
            self._draw_interstage(painter, center_x, cur_y, s2_dia_px, d_to_px(geom.stage1.diameter_m), interstage_px)
            cur_y += interstage_px

        # -------------------------------------------------------------
        # 4. Stage 1 (Booster) - Dims if Staged
        # -------------------------------------------------------------
        s1 = v.stage1
        s1_dia_px = d_to_px(s1.geometry.diameter_m)
        s1_len_px = m_to_px(s1.geometry.total_length_m)

        opacity = 0.25 if is_staged else 1.0
        painter.setOpacity(opacity)

        # S1 Oxidizer Tank (Cyan)
        ox1_len_px = m_to_px(s1.geometry.oxidizer_tank.total_length_m)
        self._draw_specular_tank(
            painter,
            center_x,
            cur_y,
            s1_dia_px,
            ox1_len_px,
            QColor(PROPELLANT_COLORS["LOX"]),
            f"S1 LOX ({s1.oxidizer_mass_kg:,.0f} kg)",
        )
        cur_y += ox1_len_px

        # S1 Fuel Tank (Amber RP-1)
        fuel1_len_px = m_to_px(s1.geometry.fuel_tank.total_length_m)
        self._draw_specular_tank(
            painter,
            center_x,
            cur_y,
            s1_dia_px,
            fuel1_len_px,
            QColor(PROPELLANT_COLORS["RP1"]),
            f"S1 Fuel ({s1.fuel_mass_kg:,.0f} kg)",
        )
        cur_y += fuel1_len_px

        # S1 Booster Base & 3-Bell Cluster
        skirt1_px = max(12.0, s1_len_px - ox1_len_px - fuel1_len_px)
        self._draw_engine_skirt(painter, center_x, cur_y, s1_dia_px, skirt1_px, 3)
        cur_y += skirt1_px

        # S1 Exhaust Flame Plume (Golden / Orange Shock Diamonds)
        if is_s1_firing:
            painter.setOpacity(1.0)
            self._draw_exhaust_plume(painter, center_x, cur_y, s1_dia_px * 0.9, 50.0, QColor(COLOR_SUNSET_AMBER))

        painter.setOpacity(1.0)

        # -------------------------------------------------------------
        # 5. Dimension Callout Line (Left Side)
        # -------------------------------------------------------------
        dim_x = center_x - max(s1_dia_px, f_dia_px) * 0.8 - 25.0
        dim_pen = QPen(QColor(BORDER_ACCENT), 1.5)
        painter.setPen(dim_pen)
        painter.drawLine(int(dim_x), int(margin_y), int(dim_x), int(cur_y))
        painter.drawLine(int(dim_x - 4), int(margin_y), int(dim_x + 4), int(margin_y))
        painter.drawLine(int(dim_x - 4), int(cur_y), int(dim_x + 4), int(cur_y))

        # Vertical text badge
        painter.save()
        painter.translate(dim_x - 12, (margin_y + cur_y) / 2.0)
        painter.rotate(-90)
        painter.setPen(QColor(TEXT_SECONDARY))
        painter.setFont(QFont("-apple-system", 10, QFont.Weight.Bold))
        painter.drawText(
            QRectF(-120, -15, 240, 18),
            Qt.AlignmentFlag.AlignCenter,
            f"TOTAL HEIGHT: {geom.total_length_m:.2f} m  (L/D = {geom.fineness_ratio:.1f})",
        )
        painter.restore()

    def _draw_specular_tank(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        width_px: float,
        height_px: float,
        color: QColor,
        label: str,
    ) -> None:
        """Draw a glossy metallic fluid tank with 2:1 ellipsoidal heads and specular highlights."""
        cap_h = min(height_px * 0.25, width_px * 0.25)
        rect = QRectF(cx - width_px / 2.0, top_y, width_px, height_px)

        path = QPainterPath()
        path.addRoundedRect(rect, width_px * 0.15, cap_h)

        # Metallic Fluid Gradient with Specular Light Stripe
        grad = QLinearGradient(cx - width_px / 2.0, 0, cx + width_px / 2.0, 0)
        grad.setColorAt(0.0, color.darker(220))
        grad.setColorAt(0.35, color.darker(110))
        grad.setColorAt(0.55, color.lighter(130))  # Specular reflection sheen
        grad.setColorAt(0.85, color)
        grad.setColorAt(1.0, color.darker(220))

        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor("#27272a"), 1.0))
        painter.drawPath(path)

        # Label inside tank
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("-apple-system", 10, QFont.Weight.DemiBold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)

    def _draw_engine_skirt(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        width_px: float,
        height_px: float,
        bells: int,
    ) -> None:
        rect = QRectF(cx - width_px / 2.0, top_y, width_px, height_px)
        painter.setBrush(QColor("#18181b"))
        painter.setPen(QPen(QColor(BORDER_SUBTLE), 1.0))
        painter.drawRect(rect)

        # Draw Engine Bell Cones
        bell_spacing = width_px / (bells + 1)
        for i in range(bells):
            bx = cx - width_px / 2.0 + (i + 1) * bell_spacing
            b_w = bell_spacing * 0.6
            bell_path = QPainterPath()
            bell_path.moveTo(bx - b_w * 0.3, top_y)
            bell_path.lineTo(bx + b_w * 0.3, top_y)
            bell_path.lineTo(bx + b_w * 0.5, top_y + height_px)
            bell_path.lineTo(bx - b_w * 0.5, top_y + height_px)
            bell_path.closeSubpath()
            painter.setBrush(QColor("#3f3f46"))
            painter.setPen(QPen(QColor("#71717a"), 1.0))
            painter.drawPath(bell_path)

    def _draw_interstage(
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

        painter.setBrush(QColor("#09090b"))
        painter.setPen(QPen(QColor(BORDER_ACCENT), 1.0, Qt.PenStyle.DashLine))
        painter.drawPath(path)

        painter.setPen(QColor(TEXT_MUTED))
        painter.setFont(QFont("-apple-system", 9, QFont.Weight.Medium))
        painter.drawText(
            QRectF(cx - bot_w / 2.0, top_y, bot_w, height_px),
            Qt.AlignmentFlag.AlignCenter,
            "── Staging Ring ──",
        )

    def _draw_exhaust_plume(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        base_w: float,
        flame_len: float,
        core_color: QColor,
    ) -> None:
        """Dynamic supersonic exhaust flame with animated shock diamonds."""
        flicker = sin(self._flame_phase) * 4.0
        total_flame = flame_len + flicker

        flame_path = QPainterPath()
        flame_path.moveTo(cx - base_w / 2.0, top_y)
        flame_path.quadTo(cx - base_w * 0.8, top_y + total_flame * 0.6, cx, top_y + total_flame)
        flame_path.quadTo(cx + base_w * 0.8, top_y + total_flame * 0.6, cx + base_w / 2.0, top_y)
        flame_path.closeSubpath()

        f_grad = QRadialGradient(cx, top_y + total_flame * 0.3, total_flame)
        f_grad.setColorAt(0.0, QColor("#ffffff"))
        f_grad.setColorAt(0.3, core_color.lighter(150))
        f_grad.setColorAt(0.8, core_color)
        f_grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(f_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(flame_path)

    def _draw_glass_badge(
        self,
        painter: QPainter,
        x: float,
        y: float,
        title: str,
        subtitle: str = "",
    ) -> None:
        badge_w = 140.0
        badge_h = 32.0 if subtitle else 20.0
        rect = QRectF(x, y - badge_h / 2.0, badge_w, badge_h)

        painter.setBrush(QColor("#18181b"))
        painter.setPen(QPen(QColor(BORDER_SUBTLE), 1.0))
        painter.drawRoundedRect(rect, 6.0, 6.0)

        painter.setPen(QColor(TEXT_PRIMARY))
        painter.setFont(QFont("-apple-system", 10, QFont.Weight.Bold))
        painter.drawText(int(x + 8), int(y - (4 if subtitle else 0)), title)

        if subtitle:
            painter.setPen(QColor(TEXT_SECONDARY))
            painter.setFont(QFont("-apple-system", 9))
            painter.drawText(int(x + 8), int(y + 11), subtitle)
