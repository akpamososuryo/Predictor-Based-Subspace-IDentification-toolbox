# Shared Fixtures

Shared cross-language fixtures live here.

## Layout
- `fixtures/matlab_reference/` for MATLAB-generated golden outputs
- additional subfolders can be added per function family

## Requirements
- Fixtures must be deterministic.
- Include metadata for seed, dimensions, and algorithm mode.
- Use fixtures for MATLAB-to-Python parity tests.
