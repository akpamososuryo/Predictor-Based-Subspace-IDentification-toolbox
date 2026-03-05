## Running tests

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

Run linting and formatting checks:

```powershell
python -m ruff check src tests
python -m ruff format --check src tests
```

Run type checks:

```powershell
python -m mypy --config-file pyproject.toml src tests
```

### Notes

- Tests are deterministic and should not depend on your local workspace state.
- Some functionality may require optional MATLAB toolboxes. Tests that require unavailable toolboxes should be skipped rather than failing the whole suite.
- For Python, run checks from `python/` to align with the `src/` package layout.
- A function is parity-complete only when its MATLAB fixture generator, fixture `.mat`, and Python
	parity test are all present. If MATLAB tooling is unavailable, keep explicit skip messages with
	the exact fixture-generation command.
