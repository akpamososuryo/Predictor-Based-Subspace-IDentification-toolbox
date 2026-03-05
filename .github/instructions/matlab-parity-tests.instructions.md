---
description: "Use when creating or updating MATLAB tests to ensure branch and mode coverage before Python porting."
applyTo: "tests/**/*.m"
---

# MATLAB Parity Test Expansion

## Goal
Exercise all important algorithm modes and branches in MATLAB before porting them to Python.

## Mandatory Coverage Areas
- `private/regress.m` modes: `none`, `tikh`, `tsvd`, `bpdn`, `nuclear`.
- `regress` option selectors: scalar, `gcv`, `lcurve`, `aic`, `sv` where applicable.
- Batch-update paths where `X0` is provided.
- Stability-enforcement branches in `*x2abcdk` functions.
- Optional-toolbox dependent paths should be tested with guarded skip logic.

## Test Design
- Keep tests deterministic (fixed seeds).
- Use small synthetic systems for branch activation.
- Verify both dimensions and finite-value sanity.
- Prefer direct branch-targeted tests over broad smoke tests.

## Skip and Guard Policy
- Use `assumeFail` only for genuinely unavailable dependencies or unsupported signatures.
- Include skip reason with function and branch name.

## Exit Criteria for Porting a Branch
- MATLAB branch has a deterministic test.
- Baseline outputs for that branch are saved as fixtures.
- Python parity test exists and references the same fixture set.
