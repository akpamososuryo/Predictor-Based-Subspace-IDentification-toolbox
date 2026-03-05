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

## Dependency Policy
- Preferred stack: `numpy`, `scipy`, `python-control`, `slycot`, `pytest`.
- For sparse/BPDN paths, use `cvxpy` where needed.
- If a MATLAB internal API has no Python equivalent, implement a local adapter and document it.
