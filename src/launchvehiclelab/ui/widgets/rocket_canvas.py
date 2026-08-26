"""High-resolution 2D dimensioned rocket vector blueprint canvas widget."""

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import QWidget

from launchvehiclelab.core.domain import CoupledVehicleResult
from launchvehiclelab.ui.theme import (
    ACCENT_BLUE,
    DARK_BG_MAIN,
    DARK_BG_PANEL,
    DARK_BORDER,
    DARK_TEXT_MUTED,
    DARK_TEXT_PRIMARY,
    DARK_TEXT_SECONDARY,
    PROPELLANT_COLORS,
)


class RocketCanvas(QWidget):
    """Custom vector canvas dynamically drawing the entire dimensioned launch vehicle stack."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._vehicle: CoupledVehicleResult | None = None
        self.setMinimumSize(320, 500)
        self.setStyleSheet(f"background-color: {DARK_BG_PANEL}; border-radius: 8px;")

    def set_vehicle(self, vehicle: CoupledVehicleResult) -> None:
        self._vehicle = vehicle
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Background grid
        painter.fillRect(0, 0, w, h, QColor(DARK_BG_PANEL))
        grid_pen = QPen(QColor(DARK_BORDER), 1, Qt.PenStyle.DotLine)
        painter.setPen(grid_pen)
        for gx in range(0, w, 40):
            painter.drawLine(gx, 0, gx, h)
        for gy in range(0, h, 40):
            painter.drawLine(0, gy, w, gy)

        if self._vehicle is None:
            # Placeholder text
            painter.setPen(QColor(DARK_TEXT_MUTED))
            painter.setFont(QFont("-apple-system", 13))
            painter.drawText(
                QRectF(0, 0, w, h),
                Qt.AlignmentFlag.AlignCenter,
                "Ready to size vehicle.\nClick 'Size Rocket' to render blueprint.",
            )
            return

        v = self._vehicle
        geom = v.vehicle_geometry
        total_len = max(1.0, geom.total_length_m)

        # Scale and Margins
        margin_y = 50.0
        margin_x = 70.0
        drawable_h = h - 2.0 * margin_y
        scale_y = drawable_h / total_len
        # Width scale factor
        max_d = max(geom.stage1.diameter_m, geom.fairing.diameter_m)
        center_x = w * 0.42

        # Drawing Cursor (starts at top of Fairing Nose)
        cur_y = margin_y

        def m_to_px(meters: float) -> float:
            return meters * scale_y

        def d_to_px(diameter_m: float) -> float:
            return max(16.0, diameter_m * scale_y * 2.2)

        # -------------------------------------------------------------
        # 1. Payload Fairing
        # -------------------------------------------------------------
        fairing = geom.fairing
        f_dia_px = d_to_px(fairing.diameter_m)
        f_len_px = m_to_px(fairing.total_length_m)
        f_nose_px = m_to_px(fairing.nose_cone_length_m)
        f_cyl_px = max(4.0, f_len_px - f_nose_px)

        # Fairing Path (Ogive Nose Cone + Cylinder)
        fairing_path = QPainterPath()
        top_pt = QPointF(center_x, cur_y)
        left_shoulder = QPointF(center_x - f_dia_px / 2.0, cur_y + f_nose_px)
        right_shoulder = QPointF(center_x + f_dia_px / 2.0, cur_y + f_nose_px)
        left_base = QPointF(center_x - f_dia_px / 2.0, cur_y + f_len_px)
        right_base = QPointF(center_x + f_dia_px / 2.0, cur_y + f_len_px)

        fairing_path.moveTo(top_pt)
        fairing_path.quadTo(QPointF(center_x - f_dia_px * 0.4, cur_y + f_nose_px * 0.6), left_shoulder)
        fairing_path.lineTo(left_base)
        fairing_path.lineTo(right_base)
        fairing_path.lineTo(right_shoulder)
        fairing_path.quadTo(QPointF(center_x + f_dia_px * 0.4, cur_y + f_nose_px * 0.6), top_pt)
        fairing_path.closeSubpath()

        # Gradient fill
        f_grad = QLinearGradient(center_x - f_dia_px / 2.0, 0, center_x + f_dia_px / 2.0, 0)
        f_grad.setColorAt(0.0, QColor("#334155"))
        f_grad.setColorAt(0.5, QColor("#64748b"))
        f_grad.setColorAt(1.0, QColor("#334155"))
        painter.setBrush(QBrush(f_grad))
        painter.setPen(QPen(QColor(ACCENT_BLUE), 1.5))
        painter.drawPath(fairing_path)

        # Label Fairing
        self._draw_annotation(
            painter,
            center_x + f_dia_px / 2.0 + 15,
            cur_y + f_len_px / 2.0,
            f"Fairing (Ø{fairing.diameter_m:.1f}m, L={fairing.total_length_m:.1f}m)",
            f"Vol: {fairing.internal_volume_m3:.1f} m³",
        )

        cur_y += f_len_px

        # -------------------------------------------------------------
        # 2. Stage 2 (Upper Stage)
        # -------------------------------------------------------------
        s2 = v.stage2
        s2_dia_px = d_to_px(s2.geometry.diameter_m)
        s2_len_px = m_to_px(s2.geometry.total_length_m)

        # Stage 2 Tank 1: LOX (Cyan)
        ox2_len_px = m_to_px(s2.geometry.oxidizer_tank.total_length_m)
        self._draw_tank(
            painter,
            center_x,
            cur_y,
            s2_dia_px,
            ox2_len_px,
            QColor(PROPELLANT_COLORS["LOX"]),
            f"S2 LOX ({s2.oxidizer_mass_kg:,.0f} kg)",
        )
        cur_y += ox2_len_px

        # Stage 2 Tank 2: Fuel (Purple/Amber)
        fuel2_len_px = m_to_px(s2.geometry.fuel_tank.total_length_m)
        fuel2_color = QColor(PROPELLANT_COLORS["CH4"] if "METH" in s2.propellant_combo.name else PROPELLANT_COLORS["RP1"])
        self._draw_tank(
            painter,
            center_x,
            cur_y,
            s2_dia_px,
            fuel2_len_px,
            fuel2_color,
            f"S2 Fuel ({s2.fuel_mass_kg:,.0f} kg)",
        )
        cur_y += fuel2_len_px

        # Stage 2 Skirt / Nozzle
        skirt2_px = max(8.0, s2_len_px - ox2_len_px - fuel2_len_px)
        self._draw_skirt(painter, center_x, cur_y, s2_dia_px, skirt2_px, "S2 Vac Engine")
        cur_y += skirt2_px

        # -------------------------------------------------------------
        # 3. Interstage
        # -------------------------------------------------------------
        interstage_px = max(10.0, m_to_px(geom.interstage_length_m))
        self._draw_interstage(painter, center_x, cur_y, s2_dia_px, d_to_px(geom.stage1.diameter_m), interstage_px)
        cur_y += interstage_px

        # -------------------------------------------------------------
        # 4. Stage 1 (Booster)
        # -------------------------------------------------------------
        s1 = v.stage1
        s1_dia_px = d_to_px(s1.geometry.diameter_m)
        s1_len_px = m_to_px(s1.geometry.total_length_m)

        # Stage 1 Tank 1: LOX (Cyan)
        ox1_len_px = m_to_px(s1.geometry.oxidizer_tank.total_length_m)
        self._draw_tank(
            painter,
            center_x,
            cur_y,
            s1_dia_px,
            ox1_len_px,
            QColor(PROPELLANT_COLORS["LOX"]),
            f"S1 LOX ({s1.oxidizer_mass_kg:,.0f} kg)",
        )
        cur_y += ox1_len_px

        # Stage 1 Tank 2: Fuel (Amber)
        fuel1_len_px = m_to_px(s1.geometry.fuel_tank.total_length_m)
        self._draw_tank(
            painter,
            center_x,
            cur_y,
            s1_dia_px,
            fuel1_len_px,
            QColor(PROPELLANT_COLORS["RP1"]),
            f"S1 Fuel ({s1.fuel_mass_kg:,.0f} kg)",
        )
        cur_y += fuel1_len_px

        # Stage 1 Engine Skirt & Multi-Engine Bells
        skirt1_px = max(12.0, s1_len_px - ox1_len_px - fuel1_len_px)
        self._draw_booster_base(painter, center_x, cur_y, s1_dia_px, skirt1_px)
        cur_y += skirt1_px

        # -------------------------------------------------------------
        # 5. Overall Dimension Callout Line
        # -------------------------------------------------------------
        dim_x = center_x - max_d * scale_y * 1.5 - 25.0
        dim_pen = QPen(QColor(DARK_TEXT_SECONDARY), 1.5)
        painter.setPen(dim_pen)
        painter.drawLine(dim_x, margin_y, dim_x, cur_y)
        painter.drawLine(dim_x - 5, margin_y, dim_x + 5, margin_y)
        painter.drawLine(dim_x - 5, cur_y, dim_x + 5, cur_y)

        # Dimension Text
        painter.save()
        painter.translate(dim_x - 10, (margin_y + cur_y) / 2.0)
        painter.rotate(-90)
        painter.setPen(QColor(DARK_TEXT_PRIMARY))
        painter.setFont(QFont("-apple-system", 11, QFont.Weight.Bold))
        painter.drawText(
            QRectF(-100, -20, 200, 20),
            Qt.AlignmentFlag.AlignCenter,
            f"Total Height: {geom.total_length_m:.2f} m  (L/D = {geom.fineness_ratio:.1f})",
        )
        painter.restore()

    def _draw_tank(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        width_px: float,
        height_px: float,
        color: QColor,
        label: str,
    ) -> None:
        """Render a propellant tank with 2:1 ellipsoidal rounded caps and fluid gradient."""
        cap_h = min(height_px * 0.25, width_px * 0.25)
        rect = QRectF(cx - width_px / 2.0, top_y, width_px, height_px)

        path = QPainterPath()
        path.addRoundedRect(rect, width_px * 0.15, cap_h)

        grad = QLinearGradient(cx - width_px / 2.0, 0, cx + width_px / 2.0, 0)
        grad.setColorAt(0.0, color.darker(160))
        grad.setColorAt(0.5, color)
        grad.setColorAt(1.0, color.darker(160))

        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(DARK_BORDER), 1.2))
        painter.drawPath(path)

        # Internal text
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("-apple-system", 10, QFont.Weight.DemiBold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)

    def _draw_skirt(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        width_px: float,
        height_px: float,
        label: str,
    ) -> None:
        rect = QRectF(cx - width_px / 2.0, top_y, width_px, height_px)
        painter.setBrush(QColor("#1e293b"))
        painter.setPen(QPen(QColor(DARK_BORDER), 1.0))
        painter.drawRect(rect)

        # Nozzle cone
        nozzle_path = QPainterPath()
        nozzle_path.moveTo(cx - width_px * 0.15, top_y)
        nozzle_path.lineTo(cx + width_px * 0.15, top_y)
        nozzle_path.lineTo(cx + width_px * 0.30, top_y + height_px)
        nozzle_path.lineTo(cx - width_px * 0.30, top_y + height_px)
        nozzle_path.closeSubpath()
        painter.setBrush(QColor("#475569"))
        painter.drawPath(nozzle_path)

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

        painter.setBrush(QColor("#0f172a"))
        painter.setPen(QPen(QColor(ACCENT_BLUE), 1.0, Qt.PenStyle.DashLine))
        painter.drawPath(path)

        # Center line
        painter.setPen(QColor(DARK_TEXT_MUTED))
        painter.setFont(QFont("-apple-system", 9))
        painter.drawText(
            QRectF(cx - bot_w / 2.0, top_y, bot_w, height_px),
            Qt.AlignmentFlag.AlignCenter,
            "── Staging ──",
        )

    def _draw_booster_base(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        width_px: float,
        height_px: float,
    ) -> None:
        rect = QRectF(cx - width_px / 2.0, top_y, width_px, height_px)
        painter.setBrush(QColor("#1e293b"))
        painter.setPen(QPen(QColor(DARK_BORDER), 1.0))
        painter.drawRect(rect)

        # Draw 3 Engine Nozzles at Base
        n_bells = 3
        bell_w = width_px / (n_bells + 1)
        for i in range(n_bells):
            bx = cx - width_px / 2.0 + (i + 1) * (width_px / (n_bells + 1))
            n_path = QPainterPath()
            n_path.moveTo(bx - bell_w * 0.2, top_y)
            n_path.lineTo(bx + bell_w * 0.2, top_y)
            n_path.lineTo(bx + bell_w * 0.45, top_y + height_px)
            n_path.lineTo(bx - bell_w * 0.45, top_y + height_px)
            n_path.closeSubpath()
            painter.setBrush(QColor("#64748b"))
            painter.drawPath(n_path)

    def _draw_annotation(
        self,
        painter: QPainter,
        x: float,
        y: float,
        title: str,
        subtitle: str = "",
    ) -> None:
        painter.setPen(QColor(DARK_TEXT_PRIMARY))
        painter.setFont(QFont("-apple-system", 11, QFont.Weight.DemiBold))
        painter.drawText(int(x), int(y - 6), title)
        if subtitle:
            painter.setPen(QColor(DARK_TEXT_SECONDARY))
            painter.setFont(QFont("-apple-system", 10))
            painter.drawText(int(x), int(y + 12), subtitle)
