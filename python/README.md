# Python Workspace

This directory is the home for the Python port of PBSID.

## Recommended structure
- `python/src/pbsid/` for package source
- `python/tests/` for Python tests
- `python/tools/` for fixture generation and parity utilities

## Rule
Keep Python code parity-focused with MATLAB behavior before refactoring.

## Environment
Create the conda environment from `python/environment.yml`:

```powershell
conda env create -f environment.yml
conda activate pbsid-py
```

## Validation commands
Run these from `python/`:

```powershell
python -m pytest tests
python -m ruff check src tests
python -m mypy --config-file pyproject.toml src tests
```
