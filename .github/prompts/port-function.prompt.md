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
- Add a MATLAB fixture generator under `tests/+testutils/` when introducing a new parity fixture.
- Ensure the MATLAB fixture file is present under `fixtures/matlab_reference/`.
- Keep parity tests actionable: skip is allowed only when fixture generation is blocked, and must include
  the exact MATLAB command needed to generate the fixture.
- Report unsupported MATLAB-specific behavior explicitly.
- Keep changes Ruff-compatible with project settings (`E`, `F`, `I`, `UP`, `B`, `SIM`) and Python 3.12 typing style.
- Use `loadmat(..., squeeze_me=False)` for new parity fixtures, and normalize any 1D vectors to
  2D single-channel matrices before dimensionality validation.
- Keep this normalization in an API-boundary helper (for example `_as_2d_float64`) and treat it as
  required behavior for parity-safe ports.
- For batch-mode functions, use direct `isinstance(..., (list, tuple))` narrowing (not helper bools)
  so mypy infers list/tuple element types correctly.
- If returned outputs have union tuple shapes, add explicit narrowing/casts in tests before tuple
  unpacking.

## Deliverables
- Python implementation.
- Python tests using fixtures.
- MATLAB fixture generator script (if new fixture is required).
- Fixture-backed parity test with explicit tolerances and mismatch diagnostics.
- Short parity report:
  - max abs error
  - max rel error
  - branch coverage notes
  - remaining gaps
- Validation summary from `python/`:
  - `ruff check .`
  - `python -m mypy --config-file pyproject.toml src tests`
  - `python -m pytest tests -q`
  - `python -m pytest tests -q -m parity`
