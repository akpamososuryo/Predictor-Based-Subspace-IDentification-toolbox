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

## Deliverables
- Python implementation.
- Python tests using fixtures.
- Short parity report:
  - max abs error
  - max rel error
  - branch coverage notes
  - remaining gaps
