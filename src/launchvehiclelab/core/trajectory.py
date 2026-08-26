"""Point-mass numerical trajectory propagation and discrete flight event handling."""

from math import atan2, cos, degrees, isfinite, pi, radians, sin, sqrt

from launchvehiclelab.core.aerodynamics import calculate_aerodynamics
from launchvehiclelab.core.atmosphere import us_standard_atmosphere_1976
from launchvehiclelab.core.delta_v import (
    EARTH_EQUATORIAL_RADIUS_M,
    EARTH_MU_M3_PER_S2,
    circular_orbit_velocity,
)
from launchvehiclelab.core.domain import (
    CoupledVehicleResult,
    FlightEvent,
    TrajectoryPoint,
    TrajectoryResult,
)
from launchvehiclelab.core.rocket_equation import STANDARD_GRAVITY_M_PER_S2


def simulate_ascent_trajectory(
    vehicle_result: CoupledVehicleResult,
    pitch_kick_time_s: float = 12.0,
    stage1_pitch_end_deg: float = 25.0,
    stage_sep_delay_s: float = 2.5,
    time_step_s: float = 0.1,
    fairing_jettison_altitude_m: float = 100_000.0,
) -> TrajectoryResult:
    """Propagate 3DOF/2D ascent equations of motion from liftoff to orbit injection.

    Simulates:
    - Liftoff & vertical climb
    - Pitchover schedule and atmospheric aerodynamic loads
    - Transonic crossing and Max-Q dynamic pressure tracking
    - MECO, stage separation coast, and Stage 2 ignition
    - Fairing jettison in vacuum upper atmosphere
    - Stage 2 vacuum orbital insertion guidance
    """
    g0 = STANDARD_GRAVITY_M_PER_S2
    mu = EARTH_MU_M3_PER_S2
    r_earth = EARTH_EQUATORIAL_RADIUS_M

    s1 = vehicle_result.stage1
    s2 = vehicle_result.stage2
    mission = vehicle_result.mission
    target_alt = mission.target.altitude_m
    r_target = r_earth + target_alt

    # Reference cross-sectional aerodynamic area (Stage 1 diameter)
    ref_area_m2 = (pi * (s1.geometry.diameter_m**2)) / 4.0

    # Stage 1 Propulsion Parameters
    glow_kg = vehicle_result.gross_liftoff_weight_kg
    f_thrust_1 = glow_kg * g0 * 1.30
    m_dot_1 = f_thrust_1 / (g0 * s1.propellant_combo.default_sea_level_isp_s)
    t_burn_1 = s1.propellant_mass_kg / m_dot_1

    # Stage 2 Propulsion Parameters
    m_init_2 = s2.sizing.initial_mass_kg
    f_thrust_2 = m_init_2 * g0 * 0.85
    m_dot_2 = f_thrust_2 / (g0 * s2.propellant_combo.default_vacuum_isp_s)
    t_burn_2 = s2.propellant_mass_kg / m_dot_2

    # State Variables: r (m), downrange x (m), v_r (m/s), v_x (m/s), mass m (kg)
    r = r_earth
    x = 0.0
    v_r = 0.5  # initial upward velocity
    v_x = 0.0  # initial horizontal velocity
    m = glow_kg
    t = 0.0

    points: list[TrajectoryPoint] = []
    events: list[FlightEvent] = []

    # Initial Event: Liftoff
    events.append(
        FlightEvent(
            name="Liftoff",
            time_s=0.0,
            altitude_m=0.0,
            velocity_m_per_s=0.0,
            description="Vehicle liftoff from launch pad.",
        )
    )

    max_q_val = 0.0
    max_q_t = 0.0
    max_q_alt = 0.0
    max_accel_g = 0.0

    transonic_recorded = False
    pitch_kicked = False
    fairing_jettisoned = False

    def state_derivatives(
        curr_r: float,
        curr_vr: float,
        curr_vx: float,
        curr_m: float,
        thrust: float,
        isp: float,
        theta_rad: float,
    ) -> tuple[float, float, float, float, float]:
        curr_h = max(0.0, curr_r - r_earth)
        v_total = sqrt(curr_vr**2 + curr_vx**2)
        v_safe = max(0.1, v_total)

        atm = us_standard_atmosphere_1976(curr_h)
        aero = calculate_aerodynamics(v_total, atm, ref_area_m2)
        d_force = aero.drag_force_n
        g_local = mu / (curr_r**2)

        # Drag vector opposing velocity direction
        drag_r = d_force * (curr_vr / v_safe)
        drag_x = d_force * (curr_vx / v_safe)

        thrust_r = thrust * sin(theta_rad)
        thrust_x = thrust * cos(theta_rad)

        dr_dt = curr_vr
        dx_dt = (r_earth / curr_r) * curr_vx
        dvr_dt = ((thrust_r - drag_r) / curr_m) - g_local + (curr_vx**2 / curr_r)
        dvx_dt = ((thrust_x - drag_x) / curr_m) - (curr_vr * curr_vx / curr_r)
        dm_dt = -(thrust / (g0 * isp)) if thrust > 0.0 else 0.0

        return dr_dt, dx_dt, dvr_dt, dvx_dt, dm_dt

    sample_timer = 0.0

    # ---------------------------------------------------------
    # PHASE 1: Stage 1 Ascent Burn
    # ---------------------------------------------------------
    while t < t_burn_1:
        curr_h = max(0.0, r - r_earth)
        v_total = sqrt(v_r**2 + v_x**2)
        atm = us_standard_atmosphere_1976(curr_h)
        aero = calculate_aerodynamics(v_total, atm, ref_area_m2)

        # Transonic crossing event
        if not transonic_recorded and aero.mach >= 1.0:
            transonic_recorded = True
            events.append(
                FlightEvent(
                    name="Transonic Crossing (Mach 1.0)",
                    time_s=round(t, 2),
                    altitude_m=round(curr_h, 1),
                    velocity_m_per_s=round(v_total, 1),
                    description=f"Mach 1.0 passed at altitude {curr_h / 1000.0:.1f} km.",
                )
            )

        # Track Max-Q
        if aero.dynamic_pressure_pa > max_q_val:
            max_q_val = aero.dynamic_pressure_pa
            max_q_t = t
            max_q_alt = curr_h

        # Stage 1 Pitch Schedule
        if t < pitch_kick_time_s:
            theta = pi / 2.0
        else:
            if not pitch_kicked:
                pitch_kicked = True
                events.append(
                    FlightEvent(
                        name="Gravity Turn Pitchover Program Initiated",
                        time_s=round(t, 2),
                        altitude_m=round(curr_h, 1),
                        velocity_m_per_s=round(v_total, 1),
                        description=f"Pitchover schedule begun at t={t:.1f}s.",
                    )
                )
            prog = (t - pitch_kick_time_s) / (t_burn_1 - pitch_kick_time_s)
            theta_deg = 90.0 - (90.0 - stage1_pitch_end_deg) * (prog**0.65)
            theta = radians(theta_deg)

        accel_g = ((f_thrust_1 - aero.drag_force_n) / m) / g0
        if accel_g > max_accel_g:
            max_accel_g = accel_g

        if sample_timer >= 1.0 or t == 0.0:
            sample_timer = 0.0
            gamma = atan2(v_r, max(0.001, v_x))
            points.append(
                TrajectoryPoint(
                    time_s=round(t, 2),
                    altitude_m=round(curr_h, 1),
                    downrange_m=round(x, 1),
                    velocity_m_per_s=round(v_total, 2),
                    flight_path_angle_rad=round(gamma, 4),
                    mass_kg=round(m, 1),
                    thrust_n=round(f_thrust_1, 1),
                    dynamic_pressure_pa=round(aero.dynamic_pressure_pa, 1),
                    mach=round(aero.mach, 2),
                    acceleration_g=round(accel_g, 2),
                )
            )

        # RK4 Integration Step
        dt = time_step_s
        k1_r, k1_x, k1_vr, k1_vx, k1_m = state_derivatives(
            r, v_r, v_x, m, f_thrust_1, s1.propellant_combo.default_sea_level_isp_s, theta
        )
        k2_r, k2_x, k2_vr, k2_vx, k2_m = state_derivatives(
            r + 0.5 * dt * k1_r,
            v_r + 0.5 * dt * k1_vr,
            v_x + 0.5 * dt * k1_vx,
            m + 0.5 * dt * k1_m,
            f_thrust_1,
            s1.propellant_combo.default_sea_level_isp_s,
            theta,
        )
        k3_r, k3_x, k3_vr, k3_vx, k3_m = state_derivatives(
            r + 0.5 * dt * k2_r,
            v_r + 0.5 * dt * k2_vr,
            v_x + 0.5 * dt * k2_vx,
            m + 0.5 * dt * k2_m,
            f_thrust_1,
            s1.propellant_combo.default_sea_level_isp_s,
            theta,
        )
        k4_r, k4_x, k4_vr, k4_vx, k4_m = state_derivatives(
            r + dt * k3_r,
            v_r + dt * k3_vr,
            v_x + dt * k3_vx,
            m + dt * k3_m,
            f_thrust_1,
            s1.propellant_combo.default_sea_level_isp_s,
            theta,
        )

        r += (dt / 6.0) * (k1_r + 2.0 * k2_r + 2.0 * k3_r + k4_r)
        x += (dt / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
        v_r += (dt / 6.0) * (k1_vr + 2.0 * k2_vr + 2.0 * k3_vr + k4_vr)
        v_x += (dt / 6.0) * (k1_vx + 2.0 * k2_vx + 2.0 * k3_vx + k4_vx)
        m += (dt / 6.0) * (k1_m + 2.0 * k2_m + 2.0 * k3_m + k4_m)

        t += dt
        sample_timer += dt

    # Record Max-Q Event
    events.append(
        FlightEvent(
            name="Max-Q (Peak Dynamic Pressure)",
            time_s=round(max_q_t, 2),
            altitude_m=round(max_q_alt, 1),
            velocity_m_per_s=round(sqrt(v_r**2 + v_x**2), 1),
            description=f"Maximum aerodynamic dynamic pressure of {max_q_val / 1000.0:.2f} kPa reached at {max_q_alt / 1000.0:.1f} km.",
        )
    )

    # Record MECO
    curr_h = r - r_earth
    v_total = sqrt(v_r**2 + v_x**2)
    events.append(
        FlightEvent(
            name="MECO (Main Engine Cutoff)",
            time_s=round(t, 2),
            altitude_m=round(curr_h, 1),
            velocity_m_per_s=round(v_total, 1),
            description=f"Stage 1 propellant depleted. Burnout velocity: {v_total:.1f} m/s.",
        )
    )

    # ---------------------------------------------------------
    # PHASE 2: Stage Separation Coast
    # ---------------------------------------------------------
    t_end_coast = t + stage_sep_delay_s
    while t < t_end_coast:
        dt = time_step_s
        k1_r, k1_x, k1_vr, k1_vx, _ = state_derivatives(r, v_r, v_x, m, 0.0, 1.0, 0.0)
        r += dt * k1_r
        x += dt * k1_x
        v_r += dt * k1_vr
        v_x += dt * k1_vx
        t += dt

    # Drop Stage 1 dry mass
    m = s2.sizing.initial_mass_kg
    events.append(
        FlightEvent(
            name="Stage 1 Separation & Stage 2 Ignition",
            time_s=round(t, 2),
            altitude_m=round(r - r_earth, 1),
            velocity_m_per_s=round(sqrt(v_r**2 + v_x**2), 1),
            description="Stage 1 jettisoned. Stage 2 ignited in vacuum.",
        )
    )

    # ---------------------------------------------------------
    # PHASE 3: Stage 2 Burn to Orbit Injection
    # ---------------------------------------------------------
    t_start_s2 = t
    t_end_s2 = t_start_s2 + t_burn_2

    while t < t_end_s2:
        curr_h = max(0.0, r - r_earth)
        v_total = sqrt(v_r**2 + v_x**2)
        atm = us_standard_atmosphere_1976(curr_h)
        aero = calculate_aerodynamics(v_total, atm, ref_area_m2)

        # Fairing Jettison event
        if not fairing_jettisoned and (
            curr_h >= fairing_jettison_altitude_m or aero.dynamic_pressure_pa < 20.0
        ):
            fairing_jettisoned = True
            fairing_mass = vehicle_result.vehicle_geometry.fairing.surface_area_m2 * 10.5 * 1.20
            m = max(s2.sizing.burnout_mass_kg, m - fairing_mass)
            events.append(
                FlightEvent(
                    name="Payload Fairing Jettison",
                    time_s=round(t, 2),
                    altitude_m=round(curr_h, 1),
                    velocity_m_per_s=round(v_total, 1),
                    description=f"Fairing separated in vacuum at altitude {curr_h / 1000.0:.1f} km.",
                )
            )

        prog2 = (t - t_start_s2) / t_burn_2
        theta_deg = stage1_pitch_end_deg * (1.0 - prog2)
        theta_rad = radians(theta_deg)
        # Closed-loop trim to reach target orbit altitude smoothly
        alt_trim = (r_target - r) / 80_000.0 - (v_r / 1000.0)
        theta_rad += max(-0.15, min(0.30, alt_trim))

        accel_g = (f_thrust_2 / m) / g0
        if accel_g > max_accel_g:
            max_accel_g = accel_g

        if sample_timer >= 1.0:
            sample_timer = 0.0
            gamma = atan2(v_r, max(0.001, v_x))
            points.append(
                TrajectoryPoint(
                    time_s=round(t, 2),
                    altitude_m=round(curr_h, 1),
                    downrange_m=round(x, 1),
                    velocity_m_per_s=round(v_total, 2),
                    flight_path_angle_rad=round(gamma, 4),
                    mass_kg=round(m, 1),
                    thrust_n=round(f_thrust_2, 1),
                    dynamic_pressure_pa=round(aero.dynamic_pressure_pa, 1),
                    mach=round(aero.mach, 2),
                    acceleration_g=round(accel_g, 2),
                )
            )

        # RK4 Step for Stage 2
        dt = time_step_s
        k1_r, k1_x, k1_vr, k1_vx, k1_m = state_derivatives(
            r, v_r, v_x, m, f_thrust_2, s2.propellant_combo.default_vacuum_isp_s, theta_rad
        )
        k2_r, k2_x, k2_vr, k2_vx, k2_m = state_derivatives(
            r + 0.5 * dt * k1_r,
            v_r + 0.5 * dt * k1_vr,
            v_x + 0.5 * dt * k1_vx,
            m + 0.5 * dt * k1_m,
            f_thrust_2,
            s2.propellant_combo.default_vacuum_isp_s,
            theta_rad,
        )
        k3_r, k3_x, k3_vr, k3_vx, k3_m = state_derivatives(
            r + 0.5 * dt * k2_r,
            v_r + 0.5 * dt * k2_vr,
            v_x + 0.5 * dt * k2_vx,
            m + 0.5 * dt * k2_m,
            f_thrust_2,
            s2.propellant_combo.default_vacuum_isp_s,
            theta_rad,
        )
        k4_r, k4_x, k4_vr, k4_vx, k4_m = state_derivatives(
            r + dt * k3_r,
            v_r + dt * k3_vr,
            v_x + dt * k3_vx,
            m + dt * k3_m,
            f_thrust_2,
            s2.propellant_combo.default_vacuum_isp_s,
            theta_rad,
        )

        r += (dt / 6.0) * (k1_r + 2.0 * k2_r + 2.0 * k3_r + k4_r)
        x += (dt / 6.0) * (k1_x + 2.0 * k2_x + 2.0 * k3_x + k4_x)
        v_r += (dt / 6.0) * (k1_vr + 2.0 * k2_vr + 2.0 * k3_vr + k4_vr)
        v_x += (dt / 6.0) * (k1_vx + 2.0 * k2_vx + 2.0 * k3_vx + k4_vx)
        m += (dt / 6.0) * (k1_m + 2.0 * k2_m + 2.0 * k3_m + k4_m)

        t += dt
        sample_timer += dt

    final_alt = r - r_earth
    final_v = sqrt(v_r**2 + v_x**2)
    events.append(
        FlightEvent(
            name="SECO & Target Orbit Insertion",
            time_s=round(t, 2),
            altitude_m=round(final_alt, 1),
            velocity_m_per_s=round(final_v, 1),
            description=f"Second Engine Cutoff. Orbit reached at altitude {final_alt / 1000.0:.1f} km, velocity {final_v:.1f} m/s.",
        )
    )

    return TrajectoryResult(
        points=points,
        events=events,
        max_q_pa=max_q_val,
        max_q_time_s=round(max_q_t, 2),
        max_q_alt_m=round(max_q_alt, 1),
        max_acceleration_g=round(max_accel_g, 2),
        final_orbit_altitude_m=round(final_alt, 1),
        final_orbit_velocity_m_per_s=round(final_v, 1),
        total_flight_time_s=round(t, 2),
    )
