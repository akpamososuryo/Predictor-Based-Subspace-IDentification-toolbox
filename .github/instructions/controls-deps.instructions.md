---
description: "Use when selecting or modifying control-system and optimization dependencies for the Python port."
applyTo: "**/*.py"
---

# Control and Dependency Mapping

## Preferred Python Libraries
- `numpy`, `scipy` for matrix and signal numerics.
- `control` (`python-control`) for state-space utilities.
- `slycot` to improve control-related numeric robustness.
- `cvxpy` for sparse/BPDN-like optimization paths.
- `pytest` and `numpy.testing` for validation.

## MATLAB to Python Mapping
- `ss`, `c2d`, `d2c`: `control.StateSpace`, `control.c2d`.
- `dare`: `scipy.linalg` or `control.dare`.
- `ode15s`: `scipy.integrate.solve_ivp(method='BDF' or 'Radau')`.
- `.mat` fixtures: `scipy.io.loadmat/savemat`.

## Known Gaps
- MATLAB `idss` behavior is not fully 1:1 with `python-control` objects.
- MATLAB internal APIs (for example `ltipack.*`) need local replacement logic.
- Exact numerical identity is not guaranteed across platforms; enforce tolerances.

## Fallback Strategy
- If `slycot` is unavailable, use SciPy-based fallback and mark expected tolerance widening.
- If convex solver support is unavailable for `cvxpy`, skip only affected sparse tests with explicit reason.
