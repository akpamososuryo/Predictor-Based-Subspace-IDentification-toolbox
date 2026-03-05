---
description: "Audit a MATLAB file for untested branches and propose deterministic tests plus fixture outputs needed for porting."
---

# Branch Audit for Port Readiness

Audit `${input:matlab_file}`.

## Tasks
- Enumerate logical branches, mode switches, and error paths.
- Identify which branches are already covered by current MATLAB tests.
- List uncovered branches with exact trigger conditions.
- Propose deterministic MATLAB test cases for each uncovered branch.
- Specify fixture outputs to export for Python parity tests.

## Output Format
- Covered branches.
- Uncovered branches with trigger inputs.
- Proposed test names and locations.
- Fixture schema for each test case.
- Porting risk notes by severity.
