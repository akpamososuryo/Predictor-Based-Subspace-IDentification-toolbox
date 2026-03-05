---
description: "Port one MATLAB function to Python with fixture-based parity checks and a concise mismatch report."
---

# Port One Function with Parity

Port `${input:function_name}` from MATLAB to Python.

## Inputs
- MATLAB source path: `${input:matlab_file}`
- Target Python module path: `${input:python_file}`
- Fixture path(s): `${input:fixture_paths}`
- Tolerance (abs/rel): `${input:tolerance}`

## Requirements
- Preserve MATLAB behavior first.
- Keep implementation in `float64` unless test constraints require otherwise.
- Add or update tests for shape checks and numeric parity.
- Report unsupported MATLAB-specific behavior explicitly.
- Keep changes Ruff-compatible with project settings (`E`, `F`, `I`, `UP`, `B`, `SIM`) and Python 3.12 typing style.
- Use `loadmat(..., squeeze_me=False)` for new parity fixtures, and normalize any 1D vectors to
  2D single-channel matrices before dimensionality validation.
- Keep this normalization in an API-boundary helper (for example `_as_2d_float64`) and treat it as
  required behavior for parity-safe ports.

## Deliverables
- Python implementation.
- Python tests using fixtures.
- Short parity report:
  - max abs error
  - max rel error
  - branch coverage notes
  - remaining gaps
- Validation summary from `python/`:
  - `ruff check .`
  - `python -m mypy --config-file pyproject.toml src tests`
  - `python -m pytest tests -q`
