# LaunchVehicleLab

Open-source launch-vehicle preliminary design and simulation platform.

> **Status:** Pre-alpha educational and research software. Not intended for
> flight qualification, safety-critical use, or operational vehicle design.

## Current capability

The first vertical slice implements the ideal Tsiolkovsky rocket equation as:

- a reusable Python function;
- a JSON-producing command-line interface;
- a tested and documented scientific model.

The scientific core has no desktop UI dependency. Future interfaces—including
PySide6/QML—will call the same validated core API.

## Quick start

Python 3.14 or newer is required.

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
```

Run the first calculation:

```bash
lvlab rocket-equation \
  --specific-impulse-s 300 \
  --initial-mass-kg 10000 \
  --final-mass-kg 4000
```

The command prints machine-readable JSON so scripts and AI clients can consume
the result without parsing presentation text.

## Scientific policy

Every model must state:

1. what it calculates;
2. the equations and conventions it implements;
3. its assumptions and valid domain;
4. how its output was checked.

See [the ideal rocket equation model note](docs/models/ideal-rocket-equation.md).

## Roadmap

- **V0.1:** mission model, delta-v budget, ideal staging, CLI, and validation.
- **V0.2:** mass, geometry, coupled sizing, and project persistence.
- **V0.3:** atmosphere, low-order aerodynamics, and dynamic pressure.
- **V0.4:** point-mass trajectory propagation and event handling.
- **V0.5:** PySide6/QML desktop beta using the existing core API.
