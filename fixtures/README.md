# Shared Fixtures

Shared cross-language fixtures live here.

## Layout
- `fixtures/matlab_reference/` for MATLAB-generated golden outputs
- additional subfolders can be added per function family

## Requirements
- Fixtures must be deterministic.
- Include metadata for seed, dimensions, and algorithm mode.
- Use fixtures for MATLAB-to-Python parity tests.
- Each new fixture should have a paired MATLAB generator script in `tests/+testutils/`.
- Fixture-backed Python parity tests should reference these files directly and avoid silent skips.
- If fixture generation is blocked by missing tooling, tests must skip explicitly and state the exact
	MATLAB command required to generate the fixture.
