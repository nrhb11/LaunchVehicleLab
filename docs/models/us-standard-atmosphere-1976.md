# US Standard Atmosphere 1976 Model

## 1. Overview & Mathematical Formulation

The **1976 U.S. Standard Atmosphere** is an idealized, steady-state model of the Earth's atmosphere from sea level to $86\,\text{km}$ geopotential altitude. It assumes hydrostatic equilibrium and ideal gas behavior.

### Geopotential Altitude Conversion
Because gravitational acceleration decreases with distance from Earth's center, geometric altitude $h$ is mapped to geopotential altitude $H$:
$$H = \frac{R_E \cdot h}{R_E + h}$$
where nominal Earth radius $R_E = 6356.766\,\text{km}$.

---

## 2. Seven Standard Atmospheric Layers

The atmosphere is divided into layers characterized by base geopotential altitude $H_b$, base temperature $T_b$, base pressure $p_b$, and constant temperature lapse rate $L_b = \frac{dT}{dH}$:

| Layer | Regime | $H_b$ (km) | $T_b$ (K) | $p_b$ (Pa) | $L_b$ (K/km) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **0** | Troposphere | 0.0 | 288.15 | 101,325.0 | -6.5 |
| **1** | Tropopause | 11.0 | 216.65 | 22,632.06 | 0.0 (Isothermal) |
| **2** | Stratosphere | 20.0 | 216.65 | 5,474.89 | +1.0 |
| **3** | Stratosphere | 32.0 | 228.65 | 868.02 | +2.8 |
| **4** | Stratopause | 47.0 | 270.65 | 110.91 | 0.0 (Isothermal) |
| **5** | Mesosphere | 51.0 | 270.65 | 66.94 | -2.8 |
| **6** | Mesosphere | 71.0 | 214.65 | 3.96 | -2.0 |

---

## 3. Governing Thermodynamic Equations

### 1. Temperature
For a given layer with $L_b \neq 0$:
$$T(H) = T_b + L_b (H - H_b)$$
For isothermal layers ($L_b = 0$):
$$T(H) = T_b$$

### 2. Barometric Pressure
- **Gradient Layer ($L_b \neq 0$)**:
  $$p(H) = p_b \left( \frac{T_b}{T(H)} \right)^{\frac{g_0}{R_{\text{air}} L_b}}$$
- **Isothermal Layer ($L_b = 0$)**:
  $$p(H) = p_b \exp\left( -\frac{g_0 (H - H_b)}{R_{\text{air}} T_b} \right)$$
where $g_0 = 9.80665\,\text{m/s}^2$ and $R_{\text{air}} = 287.05287\,\text{J/(kg}\cdot\text{K)}$.

### 3. Density & Speed of Sound
$$\rho = \frac{p}{R_{\text{air}} T}$$
$$a = \sqrt{\gamma_{\text{air}} R_{\text{air}} T} \quad (\gamma_{\text{air}} = 1.4)$$

---

## 4. Software Implementation
The model is implemented in [`src/launchvehiclelab/core/atmosphere.py`](file:///Users/nrhb/Documents/LVL/src/launchvehiclelab/core/atmosphere.py) and exposed as:
```python
from launchvehiclelab.core import us_standard_atmosphere_1976

state = us_standard_atmosphere_1976(altitude_m=11000.0)
print(f"Density: {state.density_kg_per_m3:.4f} kg/m^3, Speed of Sound: {state.speed_of_sound_m_per_s:.1f} m/s")
```
