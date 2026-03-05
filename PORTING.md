# MATLAB to Python Porting Guide

## Overview
This document describes the porting strategy for PBSID Toolbox from MATLAB to Python.

## Porting Status
- [x] `order_varx()` - Order estimation (CORE algorithm)
- [ ] `modx()` - Model identification
- [ ] `dx2abcdk()` - LTI model extraction
- [ ] `idafflpv` class - LPV state-space model
- [ ] Remaining utilities

## Key Design Decisions

### NumPy/SciPy instead of MATLAB
- MATLAB: `svd(A) → [U, S, V]`
- Python: `scipy.linalg.svd(A) → U, S, Vh` (note: Vh not V)
- Always use `float64` explicitly

### Pseudoinverse for Regression
- MATLAB `regress(Y, Z)` computes `Y @ pinv(Z)`
- Use `np.linalg.pinv()` not `lstsq()` for direct equivalence

### Indexing
- MATLAB 1-indexed → Python 0-indexed
- Example: `y(:, p+1:N)` in MATLAB = `y[:, p:N]` in Python

## Testing Strategy
- Generate reference data in MATLAB (`.mat` files)
- Compare Python outputs against MATLAB with < 1e-8 relative error
- See `pbsid_python/tests/fixtures/matlab_reference/` for reference data

## Known Issues & Gotchas
1. **Hankel matrix construction** - careful with slicing bounds
2. **LambdaKappa indexing** - off-by-one errors common in translation
3. **SVD shape mismatch** - `Vt` is already transposed

## Next Steps for Contributors
1. Port a single function (follow `order_varx.py` template)
2. Create MATLAB reference data with debug variables
3. Write unit tests comparing Python vs MATLAB
4. Document any deviations in code comments