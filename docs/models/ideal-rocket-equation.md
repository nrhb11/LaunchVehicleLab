# Ideal rocket equation

## Purpose

This model calculates the ideal velocity increment available from a propulsion
stage under a deliberately simplified set of assumptions.

## Equation

The implementation uses the Tsiolkovsky rocket equation:

```text
delta_v = g0 * Isp * ln(m_initial / m_final)
```

where `g0 = 9.80665 m/s^2`, specific impulse is measured in seconds, and both
masses are supplied in kilograms.

## Assumptions and limitations

- Specific impulse is constant.
- The calculation is ideal and does not include gravity, aerodynamic, steering,
  residual-propellant, or finite-burn losses.
- The model does not size tanks, engines, structures, or propellant reserves.
- The result is not an operational launch-vehicle performance prediction.

## Verification

The automated test suite compares the implementation with an independent
direct evaluation of the documented equation. It also checks the zero-propellant
limit and rejects non-physical or non-finite inputs.
