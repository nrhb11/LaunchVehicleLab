# Propellant Properties and Tank Geometry Packaging Model

## Purpose

This model computes propellant fluid allocations from mixture ratios ($O/F$), sizes cylindrical storage tanks with standard 2:1 ellipsoidal bulkheads, determines stage lengths and fairing dimensions, and aggregates the overall launch vehicle geometric stack and fineness ratio ($L/D$).

## Equations and Conventions

### 1. Propellant Mass Split

For a stage carrying total usable propellant $m_{\text{prop}}$ with oxidizer-to-fuel mass ratio $r = (O/F)$:

$$m_{\text{ox}} = m_{\text{prop}} \cdot \left(\frac{r}{1 + r}\right)$$

$$m_{\text{fuel}} = m_{\text{prop}} \cdot \left(\frac{1}{1 + r}\right)$$

### 2. Tank Volumetric Sizing with Ullage

For fluid density $\rho$ and volumetric ullage fraction $f_{\text{ullage}}$ (default $4\%$):

$$V_{\text{req}} = \left(\frac{m}{\rho}\right) \cdot (1 + f_{\text{ullage}})$$

### 3. 2:1 Ellipsoidal Bulkheads and Cylindrical Section

For a cylindrical tank with diameter $D$ (radius $R = D/2$) and 2:1 oblate ellipsoidal dome heads (semi-minor axis $b = D/4$, dome height $h_{\text{dome}} = D/4$):

- **Combined volume of two dome heads:**
  $$V_{\text{2\_domes}} = \frac{\pi D^3}{12}$$

- **Cylinder length:**
  $$L_{\text{cyl}} = \max\left(0, \frac{V_{\text{req}} - V_{\text{2\_domes}}}{\pi R^2}\right)$$

- **Total tank length:**
  $$L_{\text{tank}} = L_{\text{cyl}} + 2 \cdot h_{\text{dome}} = L_{\text{cyl}} + \frac{D}{2}$$

- **Dome surface area (oblate spheroid half):**
  $$A_{\text{dome}} = \frac{1}{2} \pi R^2 \left(1 + \frac{1 - e^2}{e} \operatorname{arctanh}(e)\right), \quad e = \frac{\sqrt{3}}{2} \approx 0.866025$$

### 4. Vehicle Fineness Ratio

$$\Lambda = \frac{L_{\text{total}}}{D_{\text{stage1}}}$$

## Assumptions and Limitations

- Assumes separate, un-nested oxidizer and fuel tanks (common bulkhead configurations will be added in future iterations).
- 2:1 ellipsoidal heads are standard aerospace convention providing optimal membrane stress distribution without hoop discontinuity bending.
- Diameters are held constant across each stage cylindrical section.

## Verification

- **Volume Conservation**: Checked numerically in `tests/test_geometry.py`.
- **Dome Identities**: Compared with closed-form ellipsoid surface integrals and CAD volume formulas.
