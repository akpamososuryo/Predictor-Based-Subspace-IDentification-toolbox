# Copilot Instructions for PBSID MATLAB-to-Python Port

## Mission
Port the MATLAB PBSID toolbox to Python with numerical-parity-first discipline.

## Core Rules
- Preserve behavior before refactoring.
- Treat MATLAB outputs as the source of truth for parity checks.
- Prefer deterministic fixtures and reproducible seeds.
- Use `float64` for all core numeric paths unless a test requires otherwise.
- Keep matrix shape conventions explicit at API boundaries.
- Do not silently change defaults from MATLAB behavior.
- Prefer `loadmat(..., squeeze_me=False)` in parity tests to preserve MATLAB shape metadata.
- Still treat 1D arrays as valid single-channel data at Python API boundaries and normalize them
	to 2D before strict shape checks.
- Treat this 1D-to-2D normalization as mandatory API-boundary behavior for every new/edited ported
	Python function (for example via a local `_as_2d_float64` helper).

## Porting Order
1. LTI core: `dordvarx -> dmodx -> dx2abcdk`.
2. LPV and PLPV pipelines.
3. Nonlinear Hammerstein/Wiener variants.
4. Recursive and variance tools.
5. Plotting and convenience wrappers.

## Parity Policy
- Verify parity with tolerance-based comparisons, not bitwise equality.
- Report max absolute and relative errors for each fixture.
- When parity fails, explain whether the cause is algorithmic, numerical, or API mismatch.

## Testing Policy
- Add or update MATLAB tests to cover new branch paths before porting that path.
- Add Python tests that consume the same fixtures and assert agreed tolerances.
- Keep CI deterministic and platform-aware.

## Python Style and Lint Policy
- Keep Python changes compliant with `python/pyproject.toml` Ruff settings (`E`, `F`, `I`, `UP`, `B`, `SIM`).
- Use Python 3.12 syntax and typing forms (for example `X | Y`, `list[str]`, `dict[str, float]`).
- Keep line length at or below 100 characters and use double-quoted strings.
- Prefer explicit, readable control flow that avoids common Ruff bugbear and simplification warnings.
- Before finalizing a Python port change, run from `python/`:
	- `ruff check .`
	- `python -m mypy --config-file pyproject.toml src tests`
	- `python -m pytest tests -q`

## Dependency Policy
- Preferred stack: `numpy`, `scipy`, `python-control`, `slycot`, `pytest`.
- For sparse/BPDN paths, use `cvxpy` where needed.
- If a MATLAB internal API has no Python equivalent, implement a local adapter and document it.
