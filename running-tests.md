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

### Notes

- Tests are deterministic and should not depend on your local workspace state.
- Some functionality may require optional MATLAB toolboxes. Tests that require unavailable toolboxes should be skipped rather than failing the whole suite.
