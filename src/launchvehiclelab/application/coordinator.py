"""Coupled sizing loop and multidisciplinary analysis coordination."""

from launchvehiclelab.core import (
    PROPELLANT_COMBINATIONS,
    CoupledStageResult,
    CoupledVehicleResult,
    MissionSpec,
    PropellantCombination,
    StageSpec,
    assemble_vehicle_geometry,
    calculate_delta_v_budget,
    estimate_fairing_mass,
    estimate_stage_subsystems,
    optimize_two_stage,
    size_fairing_geometry,
    size_stage_geometry,
)


def run_coupled_sizing(
    mission: MissionSpec,
    stage1_combo: PropellantCombination | None = None,
    stage2_combo: PropellantCombination | None = None,
    stage1_diameter_m: float = 1.4,
    stage2_diameter_m: float = 1.4,
    fairing_diameter_m: float | None = None,
    stage1_tw_liftoff: float = 1.30,
    stage2_tw_vac: float = 0.85,
    initial_eps1: float = 0.08,
    initial_eps2: float = 0.10,
    max_iterations: int = 40,
    tolerance_glow_kg: float = 0.5,
) -> CoupledVehicleResult:
    """Execute iterative coupled mass-geometry sizing until vehicle convergence.

    Coordinates:
        Mission -> DeltaV Budget -> Optimal Staging -> Tank Geometry ->
        Subsystem Dry Mass -> Structural Fraction Update -> Convergence Check
    """
    s1_combo = stage1_combo or PROPELLANT_COMBINATIONS["KEROLOX"]
    s2_combo = stage2_combo or PROPELLANT_COMBINATIONS["METHALOX"]
    fairing_d = fairing_diameter_m or stage2_diameter_m

    # 1. Delta-V Budget
    budget = calculate_delta_v_budget(
        target=mission.target,
        launch_latitude_rad=mission.launch_latitude_rad,
        launch_azimuth_rad=mission.launch_azimuth_rad,
    )

    # 2. Fairing Geometry & Mass Allocation
    fairing_geom = size_fairing_geometry(
        payload_mass_kg=mission.payload_mass_kg,
        diameter_m=fairing_d,
        cylinder_length_m=1.8,
    )
    fairing_dry_mass = estimate_fairing_mass(fairing_geom)

    # Effective payload carried by upper stage (satellite + fairing)
    effective_payload_kg = mission.payload_mass_kg + fairing_dry_mass

    eps1 = initial_eps1
    eps2 = initial_eps2
    prev_glow = 0.0
    iterations_run = 0

    latest_staging = None
    latest_s1_geom = None
    latest_s2_geom = None
    latest_s1_mass = None
    latest_s2_mass = None

    for iteration in range(1, max_iterations + 1):
        iterations_run = iteration

        # A. Analytical Optimal Staging
        s1_spec = StageSpec("Stage 1", s1_combo.default_sea_level_isp_s, eps1)
        s2_spec = StageSpec("Stage 2", s2_combo.default_vacuum_isp_s, eps2)

        staging_res = optimize_two_stage(
            payload_mass_kg=effective_payload_kg,
            target_delta_v_m_per_s=budget.total_delta_v_m_per_s,
            stage1_spec=s1_spec,
            stage2_spec=s2_spec,
        )
        latest_staging = staging_res

        # B. Geometry Packaging
        m_prop1 = staging_res.stage1.propellant_mass_kg
        m_prop2 = staging_res.stage2.propellant_mass_kg

        s1_geom = size_stage_geometry(
            propellant_mass_kg=m_prop1,
            propellant_combo=s1_combo,
            diameter_m=stage1_diameter_m,
        )
        s2_geom = size_stage_geometry(
            propellant_mass_kg=m_prop2,
            propellant_combo=s2_combo,
            diameter_m=stage2_diameter_m,
        )
        latest_s1_geom = s1_geom
        latest_s2_geom = s2_geom

        # C. Bottom-up Subsystem Masses
        s2_mass = estimate_stage_subsystems(
            stage_geom=s2_geom,
            propellant_mass_kg=m_prop2,
            stage_initial_mass_kg=staging_res.stage2.initial_mass_kg,
            thrust_to_weight=stage2_tw_vac,
            engine_thrust_to_weight=65.0,
            avionics_mass_kg=45.0,
            fairing_mass_kg=0.0,  # Fairing accounted in upper payload
        )

        s1_mass = estimate_stage_subsystems(
            stage_geom=s1_geom,
            propellant_mass_kg=m_prop1,
            stage_initial_mass_kg=staging_res.gross_liftoff_weight_kg,
            thrust_to_weight=stage1_tw_liftoff,
            engine_thrust_to_weight=80.0,
            avionics_mass_kg=35.0,
            interstage_mass_kg=35.0,
        )
        latest_s1_mass = s1_mass
        latest_s2_mass = s2_mass

        # D. Calculate updated structural fractions
        new_eps1 = s1_mass.total_dry_mass_kg / (s1_mass.total_dry_mass_kg + m_prop1)
        new_eps2 = s2_mass.total_dry_mass_kg / (s2_mass.total_dry_mass_kg + m_prop2)

        # Check convergence
        current_glow = staging_res.gross_liftoff_weight_kg
        glow_diff = abs(current_glow - prev_glow)
        eps_diff = max(abs(new_eps1 - eps1), abs(new_eps2 - eps2))

        if iteration > 1 and glow_diff < tolerance_glow_kg and eps_diff < 1e-4:
            break

        prev_glow = current_glow
        # Relaxation update to guarantee smooth, damped convergence
        eps1 = 0.5 * eps1 + 0.5 * new_eps1
        eps2 = 0.5 * eps2 + 0.5 * new_eps2

    # Assemble final vehicle results
    vehicle_geom = assemble_vehicle_geometry(
        stage1_geom=latest_s1_geom,
        stage2_geom=latest_s2_geom,
        fairing_geom=fairing_geom,
        interstage_length_m=0.8,
    )

    s1_mr = s1_combo.default_mixture_ratio_of
    s2_mr = s2_combo.default_mixture_ratio_of

    coupled_stage1 = CoupledStageResult(
        name="Stage 1 (Booster)",
        propellant_combo=s1_combo,
        propellant_mass_kg=latest_staging.stage1.propellant_mass_kg,
        oxidizer_mass_kg=latest_staging.stage1.propellant_mass_kg * (s1_mr / (1.0 + s1_mr)),
        fuel_mass_kg=latest_staging.stage1.propellant_mass_kg * (1.0 / (1.0 + s1_mr)),
        sizing=latest_staging.stage1,
        geometry=latest_s1_geom,
        mass_breakdown=latest_s1_mass,
        effective_structural_fraction=latest_s1_mass.total_dry_mass_kg
        / (latest_s1_mass.total_dry_mass_kg + latest_staging.stage1.propellant_mass_kg),
    )

    coupled_stage2 = CoupledStageResult(
        name="Stage 2 (Upper Stage)",
        propellant_combo=s2_combo,
        propellant_mass_kg=latest_staging.stage2.propellant_mass_kg,
        oxidizer_mass_kg=latest_staging.stage2.propellant_mass_kg * (s2_mr / (1.0 + s2_mr)),
        fuel_mass_kg=latest_staging.stage2.propellant_mass_kg * (1.0 / (1.0 + s2_mr)),
        sizing=latest_staging.stage2,
        geometry=latest_s2_geom,
        mass_breakdown=latest_s2_mass,
        effective_structural_fraction=latest_s2_mass.total_dry_mass_kg
        / (latest_s2_mass.total_dry_mass_kg + latest_staging.stage2.propellant_mass_kg),
    )

    payload_ratio_pct = (mission.payload_mass_kg / latest_staging.gross_liftoff_weight_kg) * 100.0

    return CoupledVehicleResult(
        mission=mission,
        delta_v_budget=budget,
        vehicle_geometry=vehicle_geom,
        stage1=coupled_stage1,
        stage2=coupled_stage2,
        gross_liftoff_weight_kg=latest_staging.gross_liftoff_weight_kg,
        payload_ratio_percent=payload_ratio_pct,
        iterations_to_converge=iterations_run,
    )
