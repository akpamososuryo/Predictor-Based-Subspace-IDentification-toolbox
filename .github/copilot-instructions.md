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
- During parity phase, do not add non-MATLAB heuristics (for example internal eigen re-ordering,
	post-hoc covariance symmetrization, or custom optimizer defaults) unless MATLAB does the same.
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
- Do not reduce tolerances to hide algorithmic/API mismatch; fix implementation first.
- Treat parity as incomplete until all three exist for the function being ported:
	1) MATLAB fixture generator under `tests/+testutils/`,
	2) MATLAB fixture file under `fixtures/matlab_reference/`,
	3) Python parity test that runs against that fixture without skipping.
- If fixture generation is blocked by tooling availability, keep an explicit skip with generation command,
	and record this as a temporary gap (never silently treat it as done).

## Testing Policy
- Add or update MATLAB tests to cover new branch paths before porting that path.
- Add Python tests that consume the same fixtures and assert agreed tolerances.
- Keep CI deterministic and platform-aware.
- For every new Python port, include both functional unit tests and at least one fixture-based parity test.
- On Windows, if direct interpreter calls fail due environment/DLL startup issues, use
	`conda run -n <env> ...` for parity and lint/type checks.

## Python Style and Lint Policy
- Keep Python changes compliant with `python/pyproject.toml` Ruff settings (`E`, `F`, `I`, `UP`, `B`, `SIM`).
- Use Python 3.12 syntax and typing forms (for example `X | Y`, `list[str]`, `dict[str, float]`).
- Keep line length at or below 100 characters and use double-quoted strings.
- Prefer explicit, readable control flow that avoids common Ruff bugbear and simplification warnings.
- Before finalizing a Python port change, run from `python/`:
	- `ruff check .`
	- `python -m mypy --config-file pyproject.toml src tests`
	- `python -m pytest tests -q`
- For mypy compatibility on batch-enabled APIs, prefer direct `isinstance(..., (list, tuple))`
	narrowing over helper-boolean narrowing so list/tuple element types are inferred correctly.
- When a function legitimately returns a union of tuple shapes (for example optional deltas), add
	explicit type narrowing/casts in tests before tuple unpacking.

## Dependency Policy
- Preferred stack: `numpy`, `scipy`, `python-control`, `slycot`, `pytest`.
- For sparse/BPDN paths, use `cvxpy` where needed.
- If a MATLAB internal API has no Python equivalent, implement a local adapter and document it.
