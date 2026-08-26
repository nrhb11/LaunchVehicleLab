# Ideal Multi-Stage Rocket Sizing and Optimization Model

## Purpose

This model calculates mass breakdowns, stage mass ratios, and the optimal allocation of velocity increments ($\Delta V_i$) across a two-stage tandem launch vehicle to minimize total Gross Liftoff Weight (GLOW) for a prescribed payload mass and target total velocity budget.

## Equations and Conventions

### 1. Stage Mass Definitions

For each stage $i \in \{1, 2\}$, the stage hardware and propellant mass are related by the structural coefficient $\epsilon_i$:

$$\epsilon_i = \frac{m_{s, i}}{m_{s, i} + m_{p, i}}$$

where:
- $m_{s, i}$ is the dry structural mass of stage $i$ ($\text{kg}$);
- $m_{p, i}$ is the usable propellant mass of stage $i$ ($\text{kg}$).

Consequently:

$$m_{s, i} = m_{p, i} \cdot \left(\frac{\epsilon_i}{1 - \epsilon_i}\right)$$

### 2. Stage-Wise Mass Stacking and Velocity Increment

- **Upper Stage ($i = 2$):**
  $$m_{0, 2} = m_{p, 2} + m_{s, 2} + m_{\text{payload}}$$
  $$m_{f, 2} = m_{s, 2} + m_{\text{payload}}$$
  $$R_2 = \frac{m_{0, 2}}{m_{f, 2}}$$
  $$\Delta V_2 = g_0 \cdot I_{sp, 2} \cdot \ln(R_2)$$

- **Booster Stage ($i = 1$):**
  $$m_{0, 1} = m_{p, 1} + m_{s, 1} + m_{0, 2}$$
  $$m_{f, 1} = m_{s, 1} + m_{0, 2}$$
  $$R_1 = \frac{m_{0, 1}}{m_{f, 1}}$$
  $$\Delta V_1 = g_0 \cdot I_{sp, 1} \cdot \ln(R_1)$$

- **Total Vehicle:**
  $$\text{GLOW} = m_{0, 1}$$
  $$\Delta V_{\text{total}} = \Delta V_1 + \Delta V_2$$

### 3. Sizing and Optimization (GLOW Minimization)

Let the stage growth step factor be defined as $X_i = \frac{m_{0, i}}{m_{\text{payload}, i}}$:

$$X_i(\Delta V_i) = \frac{(1 - \epsilon_i) \cdot \exp\left(\frac{\Delta V_i}{g_0 I_{sp, i}}\right)}{1 - \epsilon_i \cdot \exp\left(\frac{\Delta V_i}{g_0 I_{sp, i}}\right)}$$

The total initial mass is:

$$\text{GLOW} = m_{\text{payload}} \cdot X_1(\Delta V_1) \cdot X_2(\Delta V_2)$$

subject to:

$$\Delta V_1 + \Delta V_2 = \Delta V_{\text{target}}, \quad 0 < \Delta V_i < g_0 I_{sp, i} \ln\left(\frac{1}{\epsilon_i}\right)$$

The optimal velocity partition $(\Delta V_1^*, \Delta V_2^*)$ is determined by 1D convex minimization.

## Assumptions and Limitations

- Assumes pure serial (tandem) staging without parallel strap-on boosters.
- Assumes constant stage-average specific impulse $I_{sp, i}$.
- Structural mass scales linearly with stage loaded propellant via constant $\epsilon_i$.
- Interstage adapters, fairing separation events, and propellant residuals are treated as included within the effective structural fraction $\epsilon_i$ at this preliminary design level.

## Verification

- **Symmetric Benchmark**: When $I_{sp, 1} = I_{sp, 2}$ and $\epsilon_1 = \epsilon_2$, the model rigorously verifies the classical textbook equal-velocity division theorem: $\Delta V_1^* = \Delta V_2^* = \frac{1}{2} \Delta V_{\text{total}}$.
- **Mass Conservation**: Round-trip consistency between forward evaluation (`evaluate_two_stage`) and inverse optimization (`optimize_two_stage`) checked to $10^{-6}$ relative tolerance.
- **Automated Test Suite**: Enforced via `tests/test_staging.py`.
