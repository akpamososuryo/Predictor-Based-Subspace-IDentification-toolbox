---
description: "Use when implementing or editing Python port code for PBSID parity with MATLAB."
applyTo: "python/**/*.py"
---

# Python Porting Rules

## Numerical Behavior
- Use `numpy.float64` arrays in core algorithms.
- Match MATLAB linear algebra intent first, then optimize.
- Use `numpy.linalg.pinv` when MATLAB path uses pseudoinverse semantics.
- Be explicit about transposes because MATLAB and NumPy row/column defaults differ.

## Index and Shape Translation
- Translate MATLAB 1-based indexing to Python 0-based indexing carefully.
- Preserve matrix orientation expected by the algorithm.
- Add assertions for expected shapes near function boundaries.
- In parity tests, prefer `loadmat(..., squeeze_me=False)` so fixture dimensions are preserved.
- Independently of fixture-loading style, coerce 1D arrays to 2D single-channel matrices before
	strict shape checks at API boundaries.
- Prefer a shared helper pattern (for example `_as_2d_float64`) in each module to keep this
	behavior consistent.
- Consider this boundary coercion a required safeguard (not optional cleanup): do not remove it in
	follow-up refactors when simplifying code paths.

## API Design
- Keep function signatures close to MATLAB names during parity phase.
- Avoid premature object abstractions until fixture parity is stable.
- Document any unavoidable deviations in docstrings under a "MATLAB parity note".

## Typing and Static Analysis
- Use Python 3.12 typing conventions (for example `X | Y` instead of `Union[X, Y]`).
- Keep `src/` layout importability in mind when adding tests and type checks.
- Do not configure deprecated NumPy mypy plugins.
- Use built-in generics (`list`, `dict`, `tuple`) instead of `typing.List`-style aliases.
- Keep imports sorted and free of unused symbols.
- Prefer direct `isinstance(..., (list, tuple))` checks in batch branches so mypy can narrow types.
- For APIs with union return signatures (for example with optional extra outputs), narrow with
	assertions or `typing.cast` at call sites/tests before attribute access or tuple unpacking.

## Ruff Compatibility
- Ensure code passes project Ruff rules from `python/pyproject.toml` (`E`, `F`, `I`, `UP`, `B`, `SIM`).
- Keep lines within 100 characters.
- Prefer double-quoted string literals.
- Avoid broad `# noqa` suppression; if unavoidable, scope it narrowly and justify it in code review notes.

## Error Handling
- Raise clear exceptions for invalid dimensions and unsupported modes.
- Do not auto-correct invalid user inputs silently.

## Output Validation
- For each ported function, include fixture-based tests and tolerance checks.
- Print concise diagnostics on mismatch: shape, norm error, failing slice.
- Consider a function "parity-complete" only when all are present:
	- MATLAB fixture generator in `tests/+testutils/`.
	- MATLAB golden fixture in `fixtures/matlab_reference/`.
	- Python parity test that executes against the fixture (not just a scaffolded skip path).
- If fixture generation cannot be executed locally, keep an explicit `pytest.skip(...)` message with the
	exact MATLAB command needed, and mark the parity item as pending.
- Validate each port increment by running from `python/`:
	- `ruff check .`
	- `python -m mypy --config-file pyproject.toml src tests`
	- `python -m pytest tests -q`
	- `python -m pytest tests -q -m parity`

## Dependency Typing Notes
- If third-party runtime dependencies are available but type stubs are not (for example `scipy.*`
	in this repo), keep `ignore_missing_imports` scoped in `pyproject.toml` overrides rather than
	adding broad `type: ignore` comments in source files.
