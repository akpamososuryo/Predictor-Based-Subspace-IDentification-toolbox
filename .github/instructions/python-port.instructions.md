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

## API Design
- Keep function signatures close to MATLAB names during parity phase.
- Avoid premature object abstractions until fixture parity is stable.
- Document any unavoidable deviations in docstrings under a "MATLAB parity note".

## Error Handling
- Raise clear exceptions for invalid dimensions and unsupported modes.
- Do not auto-correct invalid user inputs silently.

## Output Validation
- For each ported function, include fixture-based tests and tolerance checks.
- Print concise diagnostics on mismatch: shape, norm error, failing slice.
