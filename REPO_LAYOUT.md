# Repository Layout (Transition)

The repository is being organized into separate MATLAB and Python workspaces with shared fixtures:

- `matlab/` for MATLAB code and tests
- `python/` for Python port code and tests
- `fixtures/` for language-agnostic parity fixtures

## Current transition policy
- Existing legacy MATLAB files at root are preserved for stability.
- New MATLAB work should be created under `matlab/`.
- New Python work should be created under `python/`.
- New parity fixtures should be written under `fixtures/matlab_reference/`.

## Migration note
A full physical move of legacy MATLAB files can be performed in a dedicated migration change after CI and path updates are prepared.
