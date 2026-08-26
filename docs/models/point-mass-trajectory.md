# Point-Mass Ascent Trajectory & Flight Event Engine

## 1. Physical Flight Dynamics (2D / 3DOF Equations of Motion)

The point-mass ascent simulation integrates equations of motion over a spherical Earth in the vertical flight plane with state vector $\vec{y} = [r, x, v_r, v_x, m]^T$:

$$\frac{dr}{dt} = v_r$$
$$\frac{dx}{dt} = \frac{R_E}{r} v_x$$
$$\frac{dv_r}{dt} = \frac{F_r - D_r}{m} - \frac{\mu_{\oplus}}{r^2} + \frac{v_x^2}{r}$$
$$\frac{dv_x}{dt} = \frac{F_x - D_x}{m} - \frac{v_r v_x}{r}$$
$$\frac{dm}{dt} = -\frac{F}{g_0 I_{sp}}$$

where:
- $r$: Radial distance from Earth center ($h = r - R_E$).
- $x$: Ground arc downrange distance along Earth's surface.
- $v_r$: Vertical (radial) velocity component.
- $v_x$: Horizontal (tangential) velocity component.
- $F_r = F \sin\theta, F_x = F \cos\theta$: Thrust resolved at pitch attitude angle $\theta(t)$ above horizontal.
- $D_r = D \frac{v_r}{v}, D_x = D \frac{v_x}{v}$: Aerodynamic drag opposing velocity vector.
- $\frac{v_x^2}{r}$: Centrifugal acceleration from Earth curvature.
- $-\frac{v_r v_x}{r}$: Coriolis/coordinate transport term in rotating spherical frame.

---

## 2. Flight Phase Guidance Laws

```
  Altitude
     ^
  500km |                                          .-~* Orbit Insertion (SECO, 7.6 km/s)
        |                                   .-~'
  100km |----------------------------.-~' (Fairing Jettison in Vacuum)
        |                     .-~' (Stage 1 Separation / Stage 2 Ignition)
   75km |              .-~' (MECO)
   11km |       .-~' (Max-Q: peak aerodynamic pressure)
    0km +----*-------------------------------------------------> Downrange
         Liftoff / Pitchover Kick
```

### Phase 1: Vertical Liftoff ($t \le t_{\text{kick}}$)
- Pure vertical climb ($\theta = 90^\circ, v_x = 0$) to clear launch pad tower and avoid ground turbulence.

### Phase 2: Atmospheric Gravity Turn ($t_{\text{kick}} < t \le t_{\text{MECO}}$)
- Pitchover schedule tilts thrust angle $\theta(t) = 90^\circ - (90^\circ - \theta_{\text{MECO}}) \left(\frac{t - t_{\text{kick}}}{t_{\text{MECO}} - t_{\text{kick}}}\right)^{0.65}$.
- The velocity vector naturally aligns with the vehicle axis, maintaining aerodynamic angle of attack $\alpha \approx 0$ to minimize aerodynamic bending moments at Max-Q.

### Phase 3: Stage 2 Vacuum Guidance ($t > t_{\text{sep}}$)
- Linear thrust pitch schedule towards horizontal ($\theta \to 0^\circ$).
- Closed-loop proportional-derivative trim steers radial velocity $v_r \to 0$ precisely as target altitude $r \to r_{\text{target}}$ and velocity reaches circular speed $v \to v_{\text{circ}}$.

---

## 3. Discrete Mission Flight Events
The simulation automatically detects and timestamps key mission milestones:
1. **Liftoff** ($T+0\,\text{s}$)
2. **Pitchover Program Initiation** ($T+12\,\text{s}$)
3. **Transonic Crossing** ($Ma = 1.0$)
4. **Max-Q** (Peak dynamic pressure $q_{\text{max}}$)
5. **MECO** (Main Engine Cutoff)
6. **Stage 1 Separation & Stage 2 Ignition**
7. **Payload Fairing Jettison** ($h \ge 100\,\text{km}, q < 20\,\text{Pa}$)
8. **SECO & Target Orbit Insertion**

---

## 4. Software Implementation
The model is implemented in [`src/launchvehiclelab/core/trajectory.py`](file:///Users/nrhb/Documents/LVL/src/launchvehiclelab/core/trajectory.py) and can be simulated via CLI:
```bash
lvlab simulate-trajectory --payload-kg 500 --altitude-m 500000
```
