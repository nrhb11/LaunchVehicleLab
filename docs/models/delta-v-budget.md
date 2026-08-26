# Orbital Velocity and Launch $\Delta V$ Budget Model

## Purpose

This model calculates the circular orbital insertion velocity for a given target altitude and computes the total velocity budget ($\Delta V_{\text{total}}$) required for orbital launch, accounting for Earth surface rotation assistance, empirical flight losses (gravity, aerodynamic drag, steering/backpressure), and safety margins.

## Equations and Conventions

### 1. Circular Orbit Velocity

For a spherical primary body with standard gravitational parameter $\mu$ and mean equatorial radius $R_E$:

$$v_{\text{circ}} = \sqrt{\frac{\mu}{R_E + h}}$$

where:
- $\mu_{\oplus} = 3.986004418 \times 10^{14}\,\text{m}^3/\text{s}^2$ (WGS 84);
- $R_{\oplus} = 6.378137 \times 10^6\,\text{m}$;
- $h$ is the circular orbit altitude above the spherical surface in metres ($m$).

### 2. Earth Rotation Surface Tangential Velocity Boost

The eastward surface velocity imparted to the launch vehicle by planetary rotation is:

$$v_{\text{boost}} = \omega_{\oplus} \cdot R_{\oplus} \cdot \cos(\phi) \cdot \sin(A_z)$$

where:
- $\omega_{\oplus} = 7.292115 \times 10^{-5}\,\text{rad/s}$;
- $\phi$ is the launch site geocentric latitude ($\text{rad}$);
- $A_z$ is the launch azimuth angle ($\text{rad}$, with $A_z = \pi/2$ corresponding to due East).

### 3. Total Velocity Budget

$$\Delta V_{\text{ideal\_burn}} = v_{\text{circ}} - v_{\text{boost}}$$

$$\Delta V_{\text{subtotal}} = \Delta V_{\text{ideal\_burn}} + \Delta v_{\text{grav}} + \Delta v_{\text{drag}} + \Delta v_{\text{steer}}$$

$$\Delta V_{\text{total}} = \Delta V_{\text{subtotal}} \cdot (1 + f_{\text{margin}})$$

## Assumptions and Limitations

- Assumes an unperturbed Keplerian circular orbit target (oblateness $J_2$, atmospheric drag decay, and third-body perturbations are omitted in preliminary sizing).
- Flight losses ($\Delta v_{\text{grav}}$, $\Delta v_{\text{drag}}$, $\Delta v_{\text{steer}}$) are modeled as lumped preliminary design allocations rather than integrated flight-path observables. Detailed time-series dynamic integration is deferred to the V0.4 numerical trajectory engine.
- Valid only for orbital altitudes $h \ge 0$.

## Verification

- **Analytical Hand Calculation**: Benchmarked against classical circular orbital velocity equations for standard Low Earth Orbit ($h = 500\,\text{km}$, $v_{\text{circ}} \approx 7612.6\,\text{m/s}$).
- **Azimuth & Latitude Checks**: Verified boundary behavior (zero boost at poles or for pure polar/due-north launches, maximal boost at the equator due East $\approx 465.1\,\text{m/s}$).
- **Automated Test Suite**: Enforced via `tests/test_delta_v.py`.
