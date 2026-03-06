# MATLAB to Python Porting Guide

## Overview
This document describes the porting strategy for PBSID Toolbox from MATLAB to Python.

## Knowledge Map
Use this index to decide where repo knowledge should be updated:
- Porting policy and parity lessons: `PORTING.md` (this file)
- Test and check commands: `running-tests.md`
- Fixture schema and generator requirements: `fixtures/README.md`
- Parity artifact interpretation: `python/parity_reports/README.md`

When adding new guidance, update the source file above first, then add a short cross-reference
in the related documents if needed.

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

### Control-System API Preference
- For control-oriented example code, prefer direct `control` / `control.matlab` APIs
	(`control.matlab.ss`, `control.matlab.feedback`, `control.matlab.lsim`,
	`control.matlab.freqresp`, with direct `control.*` calls only where the matlab-style layer is not
	a practical fit) over extra wrapper layers when practical.
- The goal is to keep the Python example flow visually and behaviorally close to the MATLAB example
	flow and reduce discrepancies introduced by custom abstraction layers.
	new control abstraction.
- If a helper is still needed, keep it as a thin MATLAB-to-`control.matlab` mapping rather than a
	new control abstraction.

### MATLAB File Port Structure
- Port MATLAB functions into individual Python files by default instead of folding their logic into
	shared helper modules.
- If MATLAB has a standalone public file such as `snr.m`, the Python port should also live in its
	own module (for example `snr.py`) and be imported where needed.
- Reserve shared helper modules for genuinely Python-side glue code, not for housing direct ports of
	separate MATLAB functions.
- If a helper is intended to be reusable beyond a single example or notebook, place it under
	`python/src/` as part of the package instead of under `python/examples/`.

### Pseudoinverse for Regression
- MATLAB `regress(Y, Z)` computes `Y @ pinv(Z)`
- Use `np.linalg.pinv()` not `lstsq()` for direct equivalence

### Indexing
- MATLAB 1-indexed → Python 0-indexed
- Example: `y(:, p+1:N)` in MATLAB = `y[:, p:N]` in Python

## Testing Strategy
- Generate reference data in MATLAB (`.mat` files)
- Compare Python outputs against MATLAB with < 1e-8 relative error
- Store shared reference fixtures in `fixtures/matlab_reference/`
- Treat parity as complete only when all are present for each ported function:
	- MATLAB fixture generator in `tests/+testutils/`
	- fixture file in `fixtures/matlab_reference/`
	- Python parity test that runs against the fixture without skipping
- If local MATLAB tooling is unavailable, keep parity tests with an explicit skip and generation command,
	and track the fixture as a temporary gap.

## Example Validation
- For Python example ports, use the published MATLAB reference pages under `examples/html/` as a
	comparison target in addition to the source `.m` files.
- Compare both textual outputs and visuals where the HTML includes them, especially:
	- singular-value plots,
	- pole locations,
	- Bode / frequency-response figures,
	- printed SNR / VAF summaries.
- Treat the HTML pages as the easiest review surface for checking whether the Python example results
	still look like the MATLAB example after refactors.
- When the MATLAB page is driven by unseeded random simulation, use the HTML as a structural and
	visual reference rather than expecting exact numeric equality in the printed SNR / VAF values.
- When porting MATLAB examples or other MATLAB scripts to Jupyter notebooks, treat each MATLAB `%%`
	section marker as a notebook section boundary and split the port into separate notebook cells
	accordingly, rather than collapsing multiple MATLAB sections into one large code cell.
- When porting MATLAB examples to Jupyter notebooks, carry over the MATLAB plots as part of the
	notebook workflow whenever practical. Prefer `numpy`, `scipy`, and `python-control` for the
	Python-side implementation; if a needed plot is not readily available there, check for an existing
	MATLAB plotting helper in the workspace before introducing a custom plotting helper.
- If a notebook helper is derived from a MATLAB function or plotting pattern in this workspace,
	prefer implementing it as a separate Python module rather than leaving that logic embedded inline
	in the notebook.
- In notebook ports, keep each plotting routine in its own dedicated code cell rather than bundling
	multiple figure-producing calls into a single cell.

## Parity-First Lessons Learned
- During parity phase, implement MATLAB behavior exactly before any cleanup or stabilization.
- Do not introduce heuristic behavior changes (for example eigenvalue re-ordering in Jacobian loops,
	post-hoc covariance symmetrization, or custom optimizer tolerances) unless MATLAB does the same.
- If parity fails, do not loosen tolerances as a first response. Treat tolerance changes as a last resort and
	record the algorithmic reason.
- For sensitive routines, compare Python code line-by-line against the MATLAB public function and any
	called private helper (for example `private/exls.m`, `private/jacobianest.m`).

### Parity Debugging Checklist
1. Confirm column/row major semantics match MATLAB (`A(:)`, `reshape`, block indexing).
2. Confirm helper-function behavior matches MATLAB defaults (for example optimizer tolerances).
3. Reproduce mismatch with fixture and report max absolute/relative errors and failing index.
4. Fix implementation first; only then revisit tolerances if required by unavoidable numeric differences.

### Future Fixture Rule
For every new fixture-backed parity function, keep all three by default:
1. MATLAB fixture generator emits at least 3 deterministic datasets per case/mode (`n_cases >= 3`).
2. Python parity test writes md/csv comparison output under `python/parity_reports/`.
3. Tolerances are set from observed error envelopes and kept tight (looser stable-branch bounds require explicit rationale).

### Fixture Debugging Lessons
- Debug fixture pipeline issues separately from algorithm issues; a bad fixture can look like a bad port.
- Prefer explicit variable assignment in MATLAB generators over dynamic `eval` naming where practical.
- Keep backward-compatible aliases when evolving fixture schema (`*_c1` plus legacy single-case names).
- Always load fixtures in parity tests with `loadmat(..., squeeze_me=False)` to preserve MATLAB shape metadata.
- Enforce `n_cases >= 3` in Python parity tests and skip with an explicit MATLAB regeneration command when not met.
- Use deterministic seeds and record them in fixture metadata (`meta.seeds`, `meta.n_cases`).
- If absolute deltas look large, inspect scale-aware fields first before changing tolerances.

### Fixture Debugging Checklist
1. Verify generator output keys match Python test expectations exactly (including case suffixes).
2. Verify shapes after load (`1D` vs `2D`, row-major sample orientation, transpose rules).
3. Regenerate fixture and compare only one case/mode first to isolate schema vs numeric issues.
4. Dump side-by-side values for failing matrices and include absolute and percent deltas.
5. Re-run parity report generation and confirm hotspot summary aligns with observed failures.

## Python Tooling Baseline
- Python package layout uses `python/src` and tests in `python/tests`.
- Run Python commands from `python/` (recommended) so relative paths resolve consistently.
- Use Python 3.12 typing style (`X | Y`) for unions.
- Use Ruff and mypy for static quality checks.

### Type checking notes
- For `src/` layout, configure mypy import roots via `mypy_path` in `python/pyproject.toml`.
- Do not use deprecated NumPy mypy plugin (`numpy.typing.mypy_plugin`).

## Known Issues & Gotchas
1. **Hankel matrix construction** - careful with slicing bounds
2. **LambdaKappa indexing** - off-by-one errors common in translation
3. **SVD shape mismatch** - `Vt` is already transposed

## Next Steps for Contributors
1. Port a single function (follow `order_varx.py` template)
2. Create MATLAB reference data with debug variables
3. Write unit tests comparing Python vs MATLAB
4. Run parity marker tests (`python -m pytest tests -q -m parity`)
5. Document any deviations in code comments
6. Update the appropriate knowledge file listed under `Knowledge Map`.