# LaunchVehicleLab

Open-source launch-vehicle preliminary design and simulation platform.

> **Status:** Pre-alpha educational and research software. Not intended for
> flight qualification, safety-critical use, or operational vehicle design.

## Current capability

The first vertical slice implements the ideal Tsiolkovsky rocket equation as:

- a reusable Python function;
- a versioned, JSON-producing command-line interface (CLI);
- a tested and documented scientific model.

The scientific core has no desktop UI dependency. Future interfaces—including
PySide6/QML—will call the same validated core API.

## Repository layout

```text
LaunchVehicleLab/
├── docs/models/                 Scientific model notes
├── src/launchvehiclelab/
│   ├── core/                    UI-independent scientific core
│   └── cli.py                   Command-line interface
├── tests/                       Automated verification
├── pyproject.toml               Python version and dependencies
└── README.md                    Setup and usage guide
```

## First-time setup on a new computer

### 1. Install the required tools

Install:

- [Git](https://git-scm.com/downloads);
- [Python 3.14](https://www.python.org/downloads/);
- [Visual Studio Code](https://code.visualstudio.com/);
- the Microsoft **Python** extension in VS Code;
- [GitHub CLI](https://cli.github.com/) if you want to authenticate and manage
  GitHub from the terminal.

On macOS with Homebrew:

```bash
brew install git python gh
```

Confirm the tools:

```bash
git --version
python3 --version
gh --version
```

This project currently requires Python 3.14 or newer. Do not rely on the
operating system's bundled Python.

### 2. Authenticate GitHub

```bash
gh auth login
gh auth setup-git
gh auth status
```

Choose `GitHub.com`, `HTTPS`, and browser authentication when prompted.

### 3. Clone the repository

Use a normal local development folder that is **not synchronized by iCloud,
OneDrive, Dropbox, or another file-sync service**.

Recommended macOS location:

```bash
mkdir -p ~/Developer
cd ~/Developer
git clone https://github.com/nrhb11/LaunchVehicleLab.git
cd LaunchVehicleLab
```

On macOS, `~/Developer/LaunchVehicleLab` expands to a local path such as
`/Users/your-name/Developer/LaunchVehicleLab`. This is the canonical working
location; do not keep a second active clone in iCloud Documents or Desktop.

Recommended Windows location:

```powershell
mkdir $HOME\Developer
cd $HOME\Developer
git clone https://github.com/nrhb11/LaunchVehicleLab.git
cd LaunchVehicleLab
```

Clone the repository only once on each device. On later sessions, use
`git pull --ff-only` instead of cloning it again.

### 4. Create the virtual environment

The virtual environment is local to each computer. It is intentionally ignored
by Git and must not be copied or uploaded.

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
py -3.14 -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Verify the installation:

```bash
python --version
pytest
lvlab --version
```

Expected result: all tests pass and `lvlab --version` prints `0.1.0`.

### 5. Configure VS Code

Open the repository folder, not an individual Python file:

```bash
code .
```

Then:

1. open the Command Palette;
2. choose **Python: Select Interpreter**;
3. select `venv/bin/python` on macOS/Linux or
   `venv\Scripts\python.exe` on Windows;
4. open a new VS Code terminal and confirm `python --version`.

If VS Code selects a global or operating-system Python, tests and imports may
behave differently from the project environment.

## Using the project today

Activate the virtual environment before running commands.

macOS/Linux:

```bash
cd ~/Developer/LaunchVehicleLab
source venv/bin/activate
```

### Command-line interface

Calculate ideal delta-v:

```bash
lvlab rocket-equation \
  --specific-impulse-s 300 \
  --initial-mass-kg 10000 \
  --final-mass-kg 4000
```

The command returns machine-readable JSON containing:

- `schema_version` and model identity;
- normalized inputs and constants;
- ideal delta-v in metres per second;
- the assumptions excluded from the model.

The current example produces approximately `2695.72 m/s`. This is an ideal
rocket-equation result, not a complete launch trajectory or vehicle design.

### Python API

```python
from launchvehiclelab.core import ideal_delta_v

delta_v = ideal_delta_v(
    specific_impulse_s=300.0,
    initial_mass_kg=10_000.0,
    final_mass_kg=4_000.0,
)
print(delta_v)
```

### Run verification

```bash
pytest
```

Run the tests after every scientific or interface change. A model is not ready
to merge merely because it produces a plausible-looking number.

## Daily Git and multi-device workflow

GitHub is the authoritative shared copy. Use the same sequence on every device.

Before starting work:

```bash
cd ~/Developer/LaunchVehicleLab
git status
git pull --ff-only
source venv/bin/activate  # macOS/Linux
pytest
```

Create a branch for a focused change:

```bash
git switch -c feat/short-description
```

After editing:

```bash
pytest
git status
git add path/to/the/files-you-changed
git commit -m "Describe the completed change"
git push -u origin HEAD
```

Open a pull request on GitHub, review the diff and test result, then merge it.
Before switching to another computer, make sure there are no uncommitted changes
and that the branch has been pushed.

On the other computer:

```bash
git switch main
git pull --ff-only
```

Do not work on the same branch from two computers at the same time unless you
are comfortable resolving Git conflicts.

## Why iCloud does not replace GitHub

iCloud synchronizes files, while Git understands commits, branches, merges, and
project history. Waiting for iCloud to finish is not equivalent to running
`git pull`.

Do not place the active Git working copy in an iCloud-synchronized Documents or
Desktop folder. File-sync services may independently synchronize:

- partially written source files;
- the `.git` internal database;
- locks and temporary files;
- uncommitted edits;
- the `venv` environment and platform-specific binaries.

That can create conflict copies, mix two devices' uncommitted work, or damage a
working tree. It also gives no reliable commit showing which change is the
intentional version.

Use this division of responsibility:

| Content | Where it belongs |
| --- | --- |
| Source code, tests, docs, configuration | Git + GitHub |
| Commit history, branches, pull requests | Git + GitHub |
| `venv`, caches, generated build files | Local device only |
| Passwords, tokens, `.env` secrets | Local secure storage only |
| Exported reports or personal notes | iCloud if desired |

If a repository currently lives inside an iCloud-synchronized folder, finish
and push all work, clone a fresh working copy under `~/Developer`, verify its
tests, and only then delete the old synchronized copy. Clone rather than moving
the directory so the new working tree starts from GitHub's verified state.

## Troubleshooting

### The wrong Python version is running

```bash
which -a python3
python3 --version
python --version
```

Activate `venv`. If it was created with the wrong Python version, remove only
that disposable `venv` directory and recreate it with Python 3.14.

### `ModuleNotFoundError: No module named 'launchvehiclelab'`

From the repository root:

```bash
source venv/bin/activate
python -m pip install -e ".[dev]"
```

### GitHub authentication fails

```bash
gh auth login
gh auth setup-git
gh auth status
```

Never paste a GitHub token into a tracked file.

### `git pull` reports local changes or a conflict

Run `git status` and do not use destructive reset commands. Commit the intended
work on its branch or ask for help resolving the conflict before pulling again.

### A new dependency was added

Reactivate the environment and reinstall from project metadata:

```bash
python -m pip install -e ".[dev]"
pytest
```

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
