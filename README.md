# LaunchVehicleLab (LVLab)

> **Open-Source Launch-Vehicle Preliminary Design, Simulation, and Multidisciplinary Analysis Platform**
>
> **Status:** Pre-alpha educational and research software. Not intended for flight qualification, safety-critical operations, or production vehicle engineering.

---

## 🤖 AI Context & Collaboration Guide

If you are an AI assistant or autonomous agent working on this repository, strictly adhere to the following core architectural invariants:

1. **Strict Core/UI Decoupling (Clean Scientific Core):**
   - The numerical and scientific core (`src/launchvehiclelab/core/`) must remain **100% headless** and free of any graphical dependencies (no `PySide6`, `Qt`, or `QML` imports anywhere in `core/`).
   - All interfaces (CLI, future PySide6/QML desktop UI, notebooks, scripts) must consume the same immutable Core Python API.
2. **Validation-First Development (No Silent Assumptions):**
   - Do not implement or advance a model without explicit documentation and test verification.
   - Every physical model must state: (1) what it calculates, (2) equations and sign conventions, (3) explicit assumptions and validity domain, (4) how it was verified against analytical benchmarks or published reference data.
   - Never output pseudoscientific "false precision" (e.g., avoid `41,837.392 kg` without uncertainty/model context; output `41.8 t` with explicit model assumptions).
3. **Dimensional Safety & Units Policy:**
   - User inputs, CLI parameters, and file serializers may accept explicitly dimensioned quantities (via `Pint` or explicit CLI flags like `--initial-mass-kg`).
   - Core numerical solvers, ODE integrators, and optimizers must operate strictly on normalized **SI base units (`float` / `np.ndarray`)** internally.
4. **Machine-Readable CLI & Versioned Persistence:**
   - The CLI (`lvlab`) outputs versioned, structured JSON containing `schema_version`, `model`, `inputs`, `constants`, `outputs`, and `assumptions`.
   - Project save files must use human-readable, schema-versioned JSON (`.lvlab`), never raw Python `pickle`.
5. **Standard Benchmark Case Study:**
   - The canonical recurring benchmark is: **500 kg payload to a notional 500 km circular Low-Earth Orbit (LEO)**.

---

## 🏛️ System Architecture

### 1. Long-Term Calculation Chain

```text
Mission ──► ΔV Budget ──► Staging ──► Mass / Geometry ──► Propulsion / Aerodynamics / Structures
                                                                     │
                                                                     ▼
Validation ◄── Optimization ◄── Stability / Guidance ◄── Trajectory (ODE)
```

### 2. Layered Decoupled Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Clients & User Interfaces                         │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌─────────────────┐  │
│  │   CLI (lvlab JSON)    │  │  PySide6 / QML (V0.5) │  │ Python Scripts/ │  │
│  │   (Machine & AI)      │  │  (Desktop Engineering)│  │   Notebooks     │  │
│  └───────────┬───────────┘  └───────────┬───────────┘  └────────┬────────┘  │
└──────────────┼──────────────────────────┼───────────────────────┼───────────┘
               │                          │                       │
┌──────────────▼──────────────────────────▼───────────────────────▼───────────┐
│                      Application & ViewModels Layer                         │
│  - Parameter validation (Pint)       - Project persistence (.lvlab JSON)    │
│  - Analysis coordination             - Asynchronous job execution           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Pure SI data & typed dataclasses
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    LaunchVehicleLab Scientific Core                         │
│  - Mission & Orbit Target            - Standard Atmosphere 1976             │
│  - Velocity Budget (ΔV)              - Low-order Aerodynamics (CD, q)       │
│  - Ideal & Mass-Coupled Staging      - SciPy solve_ivp Trajectory Engine    │
│  - Subsystem Mass & Tank Geometry    - Stability & Structural Margins       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Bidirectional verification
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    Validation & Verification Matrix                         │
│  - Closed-form analytical benchmarks - Tolerance & numerical convergence    │
│  - NASA CEA propulsion cross-checks  - Automated regression test suite      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Scientific Module Contracts

| Module | Core Responsibility | Key Inputs | Key Outputs | Initial Validation Strategy |
| :--- | :--- | :--- | :--- | :--- |
| **`mission`** | Define payload, target orbit, and launch assumptions | Payload mass, target altitude $h$, inclination $i$ | `MissionSpec`, `OrbitTarget` | Orbital mechanics closed forms |
| **`delta_v`** | Transparent velocity-budget abstraction | `MissionSpec`, loss/margin model | `DeltaVBudget` (orbital $v$, $\Delta v_{grav}$, $\Delta v_{aero}$, margins) | Analytic orbital velocity & textbook launch budgets |
| **`staging`** | Allocate performance & mass across stages | $\Delta V$ requirement, $I_{sp}$, structural fractions $\epsilon$ | `StageSizingResult`, mass ratios | Lagrange multiplier analytic minimum mass |
| **`mass`** | Subsystem/component mass breakdown | Stage propellant, structural model, engine specs | `MassBreakdown`, GLOW (Gross Liftoff Weight) | Mass conservation & textbook historical empirical fits |
| **`geometry`** | Dimensions and tank packaging | Stage propellant mass, $O/F$ ratio, propellant densities | `VehicleGeometry`, `StageGeometry`, tank lengths/diameters | Geometric volume identities |
| **`propulsion`**| Propulsion performance maps | Thrust, $I_{sp}$, expansion ratio, ambient pressure | `PropulsionState` | Standard isentropic expansion; later NASA CEA adapter |
| **`aerodynamics`**| Atmospheric loads & dynamic pressure | Velocity, altitude, Mach number, vehicle geometry | $q = \frac{1}{2}\rho v^2$, drag force $D$, $C_D(Ma)$ curve | 1976 Standard Atmosphere tables, ballistic benchmarks |
| **`trajectory`**| Point-mass / 3DOF state propagation | Vehicle, environment, steering/pitch profile | `TrajectoryResult` (time series of states & events) | Vacuum flat-earth analytical solutions, SciPy tolerance convergence |
| **`structures`**| Preliminary tank/shell load & margin checks | Geometry, axial acceleration, dynamic pressure, materials | Stress levels, structural margins of safety | Thin-walled pressure vessel equations |
| **`stability`** | Center of Gravity (CG) and Center of Pressure (CP) | Mass distribution history, geometry, aerodynamics | $X_{cg}(t)$, $X_{cp}(t)$, static margin | Analytical geometric centroids & moments |
| **`guidance`**  | Prescribed pitch/steering law execution | Flight time, altitude, dynamic pressure | Commanded pitch angle $	heta(t)$ | Deterministic profile integration |
| **`optimization`**| Constrained design parameter optimization | Design variables, constraints, objective function | `OptimizationResult` | `scipy.optimize` benchmarks (e.g., mass-optimal staging) |
| **`validation`**| Automated benchmarking & report generation | Model outputs + analytical/published reference cases | `ValidationReport` | Continuous regression test suite (`pytest`) |

---

## 🗺️ Version Roadmap & Milestone Tracker

### Phase 1: Scientific Core Foundation (Current Focus)
- [x] **V0.1 — Mission Model, ΔV Budget, Ideal Staging & CLI** *(Completed)*
  - [x] Tsiolkovsky ideal rocket equation function (`core/rocket_equation.py`).
  - [x] Versioned JSON CLI output contract (`lvlab rocket-equation`).
  - [x] Initial domain dataclasses (`OrbitTarget`, `MissionSpec`, `DeltaVBudget`, `StageSpec`).
  - [x] Orbit circular velocity & launch $\Delta V$ budget model (`DeltaVBudget` in `core/delta_v.py`).
  - [x] Analytical two-stage sizing optimization under ideal assumptions (`core/staging.py`).
- [x] **V0.2 — Mass Breakdown, Tank Geometry & Coupled Sizing** *(Completed)*
  - [x] Subsystem mass models (structural fraction $\epsilon$, engine $T/W$, avionics, fairing in `core/mass.py`).
  - [x] Tank sizing (propellant volume from densities & $O/F$ mixture ratio in `core/geometry.py`).
  - [x] Coupled mass-geometry sizing convergence coordinator (`application/coordinator.py`).
- [x] **V0.3 — Environment, Atmosphere & Low-Order Aerodynamics** *(Completed)*
  - [x] US Standard Atmosphere 1976 implementation (temperature, pressure, density, speed of sound vs altitude in `core/atmosphere.py`).
  - [x] Dynamic pressure $q(t)$ calculation and Max-$Q$ detection (`core/aerodynamics.py`).
  - [x] Subsonic / transonic / supersonic drag coefficient $C_D(Ma)$ parameterization (`core/aerodynamics.py`).
- [x] **V0.4 — Numerical Trajectory Engine & Event Handling** *(Completed)*
  - [x] High-precision 3DOF point-mass ascent trajectory simulation engine with gravity turn guidance (`core/trajectory.py`).
  - [x] Discrete event state machine (Liftoff, Pitchover, Transonic, Max-$Q$, MECO, Staging, Fairing Jettison, SECO, Orbit Injection).
  - [x] Canonical 0-to-Orbit numerical flight simulation benchmark study (`examples/two_stage_leo_500kg.py`).

- [x] **V0.5 — PySide6 Desktop Application Beta** *(Completed)*
  - [x] Modern dark-glassmorphism macOS native interface (`ui/theme.py`, `ui/widgets/main_window.py`).
  - [x] Real-time 2D vector rocket blueprint canvas with dimension callouts (`ui/widgets/rocket_canvas.py`).
  - [x] Interactive multi-curve flight dynamics plots and Max-Q annotation (`ui/widgets/trajectory_view.py`).
  - [x] Chronological flight mission event sequence timeline table (`ui/widgets/events_table.py`).
  - [x] Full `.lvlab` project persistence integration and `lvlab-gui` executable command.
- [ ] **V0.6 — Structural Margins & CG/CP Static Stability**
  - [ ] Tank pressure/bending stress checks.
  - [ ] Time-varying Center of Gravity $X_{cg}(t)$ and Center of Pressure $X_{cp}(t)$ tracking.
- [ ] **V0.7 — Multivariable Optimization & Trade Studies**
  - [ ] Automated parameter sweeps and `scipy.optimize` constrained optimization.
  - [ ] Payload vs orbit capability curves and mass sensitivity trade studies.
- [ ] **V0.8 — Advanced Propulsion & NASA CEA Integration**
  - [ ] Chamber thermochemistry & expansion performance validation via NASA CEA adapter.
- [ ] **V0.9 — Uncertainty Analysis & OpenMDAO Integration**
  - [ ] Monte Carlo dispersion and parameter uncertainty propagation.
- [ ] **V1.0 — Public Stable Research Release**
  - [ ] Complete documentation suite (MkDocs), three end-to-end validated launcher case studies, cross-platform CI releases.

---

## 📂 Target Repository Layout

```text
LaunchVehicleLab/
├── docs/                        # Project documentation (MkDocs)
│   ├── architecture/            # Architectural blueprints & design decisions
│   ├── models/                  # Mathematical models, equations, assumptions
│   ├── theory/                  # Astrodynamics & propulsion background notes
│   └── tutorials/               # Step-by-step sizing tutorials
├── src/
│   └── launchvehiclelab/
│       ├── core/                # Headless scientific core (SI units only)
│       │   ├── domain.py        # Shared immutable dataclasses
│       │   ├── rocket_equation.py # Tsiolkovsky formulation
│       │   ├── delta_v.py       # Orbital requirements & loss models
│       │   ├── staging.py       # Stage allocation & sizing
│       │   ├── mass.py          # Mass breakdown & estimation
│       │   ├── geometry.py      # Tank, stage, and fairing sizing
│       │   ├── atmosphere.py    # 1976 Standard Atmosphere
│       │   ├── aerodynamics.py  # Drag, dynamic pressure, CD curves
│       │   ├── trajectory.py    # solve_ivp ODE ascent equations
│       │   └── validation.py    # Benchmarking runners
│       ├── application/         # Orchestration & workflows
│       │   └── coordinator.py   # Coupled sizing loops
│       ├── adapters/            # External tools & formats
│       │   ├── persistence.py   # Versioned .lvlab JSON serializer
│       │   └── cea/             # Optional NASA CEA adapter
│       ├── ui/                  # Desktop GUI (V0.5+)
│       │   ├── qml/             # Declarative QML views
│       │   └── viewmodels/      # Python-QML bridge view models
│       └── cli.py               # JSON-producing CLI entry point (lvlab)
├── tests/                       # Automated test suite (pytest)
│   ├── unit/                    # Analytical & domain unit tests
│   ├── validation/              # Textbook benchmark comparisons
│   └── regression/              # Fixed golden vector checks
├── examples/                    # Runnable mission case studies
│   └── two_stage_leo_500kg.py
├── pyproject.toml               # Package configuration & dependencies
└── README.md                    # Project roadmap and guide
```

---

## 🚀 Getting Started & Local Development

### 1. Prerequisites
- **Python:** `>= 3.14` (Recommended: virtual environment isolated from OS Python).
- **Tools:** Git, VS Code (with Microsoft Python Extension).

### 2. Environment Setup

**macOS / Linux:**
```bash
# Clone the repository (do NOT place inside an iCloud/cloud-synced folder)
git clone https://github.com/nrhb11/LaunchVehicleLab.git
cd LaunchVehicleLab

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install package in editable development mode
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/nrhb11/LaunchVehicleLab.git
cd LaunchVehicleLab

python -m venv venv
venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 3. Verify Installation & Run Verification Suite
```bash
# Run all automated tests
pytest

# Verify CLI installation
lvlab --version
```

### 4. Interactive Desktop GUI (PySide6)

Launch the modern macOS native desktop visual application:
```bash
lvlab-gui
# or:
python -m launchvehiclelab.ui
```

### 5. Running Analyses via CLI

Calculate ideal $\Delta V$:
```bash
lvlab rocket-equation \
  --specific-impulse-s 300 \
  --initial-mass-kg 10000 \
  --final-mass-kg 4000
```

Compute launch $\Delta V$ budget for 500 km LEO from $28.5^\circ$ latitude:
```bash
lvlab delta-v-budget \
  --altitude-m 500000 \
  --latitude-deg 28.5 \
  --azimuth-deg 90
```

Analytically optimize a two-stage launch vehicle:
```bash
lvlab two-stage-sizing \
  --payload-kg 500 \
  --target-delta-v 9047.4 \
  --stage1-isp 300 \
  --stage2-isp 360 \
  --stage1-eps 0.08 \
  --stage2-eps 0.10
```

Run multidisciplinary coupled mass-geometry vehicle sizing & export project:
```bash
lvlab coupled-sizing \
  --payload-kg 500 \
  --altitude-m 500000 \
  --stage1-diameter-m 1.4 \
  --stage2-diameter-m 1.4 \
  --export-file my_launcher.lvlab
```

Inspect a saved `.lvlab` project file:
```bash
lvlab inspect-project --file my_launcher.lvlab
```

Query 1976 US Standard Atmosphere at any altitude:
```bash
lvlab atmosphere --altitude-m 11000
```

Compute dynamic pressure and aerodynamic drag:
```bash
lvlab aerodynamics --altitude-m 11000 --velocity-m-per-s 600 --diameter-m 1.4
```

Simulate 0-to-Orbit 3DOF ascent flight trajectory:
```bash
lvlab simulate-trajectory --payload-kg 500 --altitude-m 500000 --export-file flight.lvlab
```

### 5. Python API Usage

```python
from launchvehiclelab.adapters import save_project
from launchvehiclelab.application import run_coupled_sizing
from launchvehiclelab.core import (
    PROPELLANT_COMBINATIONS,
    MissionSpec,
    OrbitTarget,
    simulate_ascent_trajectory,
)

# 1. Define mission: 500 kg to 500 km LEO
mission = MissionSpec(
    payload_mass_kg=500.0,
    target=OrbitTarget(altitude_m=500_000.0),
    launch_latitude_rad=0.4974,  # 28.5 deg
)

# 2. Run coupled multidisciplinary vehicle sizing
vehicle = run_coupled_sizing(
    mission=mission,
    stage1_combo=PROPELLANT_COMBINATIONS["KEROLOX"],
    stage2_combo=PROPELLANT_COMBINATIONS["METHALOX"],
    stage1_diameter_m=1.4,
    stage2_diameter_m=1.4,
)

# 3. Simulate continuous 3DOF ascent flight trajectory
trajectory = simulate_ascent_trajectory(vehicle)

print(f"Max-Q: {trajectory.max_q_pa / 1000.0:.2f} kPa at Alt {trajectory.max_q_alt_m / 1000.0:.1f} km")
print(f"Orbit Insertion Vel: {trajectory.final_orbit_velocity_m_per_s:.1f} m/s")

# 4. Save complete mission, geometry, and flight trajectory
save_project(vehicle, "canonical_mission.lvlab", trajectory=trajectory)
```

### 6. Canonical Educational Benchmark Case Study

Run the verified 500 kg to 500 km LEO launcher sizing & flight simulation study:
```bash
python examples/two_stage_leo_500kg.py
```

---

## 📐 Scientific Policy & Validation Ladder

Validation is treated as a mandatory release gate:

```text
Algebraic Unit Tests  ──►  Analytic Verification  ──►  Numerical Convergence  ──►  Reference Validation (CEA/Literature)
(Bounds & Signs)          (Closed-form Equations)     (Tolerance Sweeps)         (Independent Cross-Checks)
```

Every model added to `docs/models/` must answer:
1. **What does this model calculate?**
2. **What equations and conventions are implemented?**
3. **What are the assumptions and valid operational domain?**
4. **What benchmark/test case was used to verify it?**

---

## 🛠️ Multi-Device Git Workflow & Cloud Sync Rules

⚠️ **CRITICAL RULE:** Do **NOT** keep active Git working copies inside cloud-synchronized folders (such as **iCloud**, **OneDrive**, or **Dropbox**). Cloud syncing can corrupt the `.git` internal database, synchronize partial writes, and lock virtual environment binaries.

**Standard Work Cycle:**
```bash
# Start of session
git pull --ff-only
source venv/bin/activate
pytest

# Create branch for new model or feature
git switch -c feat/delta-v-budget

# Work, test, and commit
pytest
git add src/ docs/ tests/
git commit -m "feat(core): implement circular orbit velocity and delta-v budget"
git push -u origin HEAD
```

---

## 📚 References & Recommended Reading
- **Space Systems Design:** *Space Mission Engineering: The New SMAD* (Wertz et al.)
- **Astrodynamics:** *Fundamentals of Astrodynamics and Applications*, 5th Ed. (Vallado)
- **Rocket Propulsion:** *Rocket Propulsion Elements*, 10th Ed. (Sutton, Biblarz, Morehart)
- **Multidisciplinary Design Optimization:** *OpenMDAO & Dymos Documentation* (NASA / OpenMDAO.org)
