# Subsystem Mass Breakdown and Scaling Model

## Purpose

This model provides bottom-up physics-based estimation of dry structural masses across all physical launch vehicle subsystems (tank shells, propulsion assemblies, avionics, interstages, separation fairings, and propellant residuals), replacing lumped single-coefficient assumptions with auditable component mass equations.

## Equations and Conventions

### 1. Tank Structural Shell Mass

$$m_{\text{tanks}} = A_{\text{wetted}} \cdot \sigma_{\text{struct}}$$

where $A_{\text{wetted}}$ is the sum of oxidizer tank, fuel tank, and skirt cylindrical/ellipsoidal surface areas ($\text{m}^2$), and $\sigma_{\text{struct}}$ is the effective structural areal density ($\approx 12.0 \sim 18.0\,\text{kg/m}^2$ for typical aerospace Al-Li/carbon-composite tank structures).

### 2. Propulsion System Dry Mass

$$F_{\text{req}} = m_{\text{stage, 0}} \cdot g_0 \cdot \left(\frac{T}{W}\right)_{\text{stage}}$$

$$m_{\text{engine, bare}} = \frac{F_{\text{req}}}{g_0 \cdot (T/W)_{\text{engine}}}$$

$$m_{\text{propulsion}} = 1.25 \cdot m_{\text{engine, bare}}$$

where $(T/W)_{\text{engine}}$ is the engine bare thrust-to-weight ratio (typically $60 \sim 100$), and the $1.25$ multiplier accounts for thrust mount structures, gimbal actuators, propellant feedlines, and pressurization valving.

### 3. Payload Fairing Mass

$$m_{\text{fairing}} = A_{\text{fairing}} \cdot \sigma_{\text{fairing}} \cdot (1 + f_{\text{mech}})$$

where $\sigma_{\text{fairing}} \approx 10.5\,\text{kg/m}^2$ (carbon composite honeycomb sandwich), and $f_{\text{mech}} \approx 0.20$ accounts for pneumatic jettison rails and pyrotechnic frangible joints.

### 4. Residuals and Unusable Propellants

$$m_{\text{residuals}} = m_{\text{prop}} \cdot f_{\text{residual}} \quad (f_{\text{residual}} \approx 1.2\%)$$

### 5. Effective Structural Coefficient

$$\epsilon_{\text{eff}} = \frac{m_{\text{dry}}}{m_{\text{dry}} + m_{\text{prop}}}$$

## Assumptions and Limitations

- Sizing parameters represent preliminary design empirical fits validated against historical launcher datasets (Falcon 1, Electron, Vega).
- Extreme thermal protection systems (e.g. re-entry tiles) are excluded in this expendable baseline.

## Verification

- **Subsystem Positivity and Summation**: Enforced in `tests/test_mass.py`.
- **Iterative Convergence**: Sizing loop consistency verified in `tests/test_coordinator.py`.
