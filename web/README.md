# LaunchVehicleLab web studio preview

Interactive **web replica** of the desktop studio. Use it to try layout and
interaction before those changes land in the PySide6 app.

The Python package in `src/launchvehiclelab` remains the product. This folder
does not replace it.

## Run

```bash
cd web
npm install
npm run dev
```

Then open the URL Vite prints (default `http://127.0.0.1:5173`).

## What it includes

- Two-stage coupled sizing + simplified 3DOF ascent (TypeScript port of the core)
- Desktop-style chrome: menu bar, toolbar, dock panels, status bar
- Vehicle cutaway, ascent traces, event table, timeline scrubber

Shortcuts: `Space` play/pause, `Ctrl+Enter` size, arrow keys scrub.

## Status

Prototype for UI iteration. Numbers are close to the Python benchmark
(500 kg / 500 km LEO) but the Qt desktop app is still the source of truth.
