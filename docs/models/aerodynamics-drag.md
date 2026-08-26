# Aerodynamics, Drag Coefficients & Dynamic Pressure

## 1. Dynamic Pressure ($q$)

Dynamic pressure represents the kinetic energy per unit volume of fluid moving relative to the launch vehicle:
$$q(t) = \frac{1}{2} \rho(h) v^2(t)$$

As a rocket climbs:
- Flight velocity $v(t)$ increases rapidly under engine thrust.
- Atmospheric density $\rho(h)$ decays exponentially with altitude.
The product $\rho(h) v^2(t)$ reaches a distinct peak known as **Max-Q** (Maximum Dynamic Pressure), typically occurring between $10\,\text{km}$ and $14\,\text{km}$ at dynamic pressures of $30 \sim 40\,\text{kPa}$. This is the moment of greatest aerodynamic and structural stress on the vehicle.

---

## 2. Drag Coefficient Regime Parameterization $C_D(Ma)$

The total drag coefficient $C_D$ varies across subsonic, transonic, supersonic, and hypersonic flow regimes:

```
        CD
        ^
   0.50 |             .-.  (Transonic Wave Drag Peak ~ Mach 1.05 - 1.2)
        |            /   \
   0.40 |           /     \
        |          /       `---.
   0.30 |         /             `---.
   0.20 |--------'                   `------- (Hypersonic Newtonian Limit)
        +-----------------------------------> Mach
          0.5   0.8   1.0   1.2   2.0   5.0
```

### 1. Subsonic Flow ($Ma < 0.8$)
Dominated by skin friction and base suction:
$$C_D(Ma) = C_{D, \text{subsonic}} \approx 0.22$$

### 2. Transonic Flow ($0.8 \le Ma \le 1.2$)
Characterized by shock wave formation and detached sonic booms:
$$C_D(Ma) = C_{D, \text{sub}} + (C_{D, \text{peak}} - C_{D, \text{sub}}) \sin^2\left(\frac{\pi (Ma - 0.8)}{2 \times 0.4}\right)$$
where $C_{D, \text{peak}} \approx 0.48$.

### 3. Supersonic Decay ($Ma > 1.2$)
Shock waves become attached and bow wave drag decreases according to slender-body theory:
$$C_D(Ma) = C_{D, \text{hyp}} + \frac{C_{D, \text{peak}} - C_{D, \text{hyp}}}{1.0 + 0.75 (Ma - 1.2)}$$
approaching asymptotic limit $C_{D, \text{hypersonic}} \approx 0.20$.

---

## 3. Total Aerodynamic Drag Force

$$D(t) = q(t) \cdot S_{\text{ref}} \cdot C_D(Ma)$$
where reference cross-sectional area $S_{\text{ref}} = \frac{\pi D^2}{4}$.

---

## 4. Software Implementation
The model is implemented in [`src/launchvehiclelab/core/aerodynamics.py`](file:///Users/nrhb/Documents/LVL/src/launchvehiclelab/core/aerodynamics.py).
