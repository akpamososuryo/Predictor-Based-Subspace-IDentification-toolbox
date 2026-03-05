## Running tests

Knowledge references:
- Porting and parity policy: `PORTING.md`
- Fixture requirements: `fixtures/README.md`
- Parity report interpretation: `python/parity_reports/README.md`

Open MATLAB and set the Current Folder to the repository root (the folder that contains this `README.md`).

Then run:

```matlab
results = runtests("tests");
disp(table(results))
assert(all([results.Passed]), "Some tests failed");
```

### What CI runs

The GitHub Actions workflow runs the same test suite on Windows, Linux, and macOS using MATLAB R2025b.

## Running Python checks

From repository root:

```powershell
Set-Location python
```

Run unit tests:

```powershell
python -m pytest tests
```

Run fixture parity tests only:

```powershell
python -m pytest tests -m parity
```

Parity fixture expectation:
- MATLAB fixture generators now target at least 3 deterministic datasets per case (`n_cases >= 3`).
- If parity tests skip with a message about case count, regenerate fixtures in MATLAB:

```matlab
testutils.generateDvar2eigFixture
testutils.generateDordvarmaxFixture
testutils.generateDordfirFixture
testutils.generateDmodxFixture
testutils.generateDvar2frdFixture
testutils.generateDordvarxFixture
testutils.generateDx2abcdkFixture
testutils.generateDx2abckFixture
```

Run linting and formatting checks:

```powershell
python -m ruff check src tests
python -m ruff format --check src tests
```

Run type checks:

```powershell
python -m mypy --config-file pyproject.toml src tests
```

### Windows environment note

On some Windows setups, direct invocation of a specific interpreter path can fail during NumPy import
(for example BLAS/FPE startup issues) even when the conda environment itself is valid.

If this occurs, run commands through conda process isolation:

```powershell
conda run -n pbsid-py python -m pytest python/tests -q
conda run -n pbsid-py python -m pytest python/tests -q -m parity
conda run -n pbsid-py python -m ruff check python/src python/tests
conda run -n pbsid-py python -m mypy --config-file python/pyproject.toml python/src python/tests
```

### Notes

- Tests are deterministic and should not depend on your local workspace state.
- Some functionality may require optional MATLAB toolboxes. Tests that require unavailable toolboxes should be skipped rather than failing the whole suite.
- For Python, run checks from `python/` to align with the `src/` package layout.
- A function is parity-complete only when its MATLAB fixture generator, fixture `.mat`, and Python
	parity test are all present. If MATLAB tooling is unavailable, keep explicit skip messages with
	the exact fixture-generation command.
- Do not lower parity tolerances to mask implementation drift. Fix algorithm mismatches first.
- Parity test runs write comparison tables to `python/parity_reports/` as both `.csv` and `.md` files.
- Future fixture standard: every new fixture-backed parity test must enforce `n_cases >= 3`,
	write md/csv reports via `write_parity_report`, and keep tolerances as tight as observed error
	envelopes allow (document and justify any looser stable-branch thresholds).
- If a guidance update is discovered while debugging tests, update `PORTING.md` first and add a short
	cross-reference here only when it affects command usage or execution workflow.
