from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat
from scipy.optimize import linear_sum_assignment

from pbsid.lti.dvar2eig import dvar2eig
from pbsid.parity_report_utils import write_parity_report

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "fixtures" / "matlab_reference" / "dvar2eig_fixture.mat"
)


def _max_abs_rel(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    diff = np.abs(a - b)
    denom = np.maximum(np.abs(b), 1e-12)
    return float(np.max(diff)), float(np.max(diff / denom))


def _align_covariance_order(
    e_got: np.ndarray, cov_got: np.ndarray, e_ref: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Align eigenvalue/covariance ordering across MATLAB/NumPy eig conventions."""
    cost = np.abs(e_ref[:, np.newaxis] - e_got[np.newaxis, :])
    row_ind, col_ind = linear_sum_assignment(cost)

    e_out = np.empty_like(e_got)
    e_out[row_ind] = e_got[col_ind]

    idx_pairs = np.column_stack((2 * row_ind, 2 * row_ind + 1)).reshape(-1)
    got_pairs = np.column_stack((2 * col_ind, 2 * col_ind + 1)).reshape(-1)

    cov_out = np.empty_like(cov_got)
    cov_out[idx_pairs[:, np.newaxis], idx_pairs[np.newaxis, :]] = cov_got[
        got_pairs[:, np.newaxis], got_pairs[np.newaxis, :]
    ]
    return e_out, cov_out


@pytest.mark.parity
def test_dvar2eig_parity_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDvar2eigFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=False, struct_as_record=False)

    n_cases = int(np.asarray(m.get("n_cases", [[1]])).item())
    if n_cases < 3:
        pytest.skip(
            "Fixture has fewer than 3 cases. Regenerate with: testutils.generateDvar2eigFixture"
        )

    rows: list[dict[str, str | float | int | bool]] = []

    for i in range(n_cases):
        case_label = f"case_{i + 1}"
        a = np.asarray(m["A_cases"][..., i], dtype=np.float64)
        p = np.asarray(m["P_cases"][..., i], dtype=np.float64)

        e_py, cov_e_py = dvar2eig(p, a)
        e_ref = np.asarray(m["E_cases"][..., i]).reshape(-1)
        cov_e_ref = np.asarray(m["covE_cases"][..., i], dtype=np.float64)

        e_aligned, cov_e_aligned = _align_covariance_order(e_py, cov_e_py, e_ref)

        # Compare sorted eigenvalues to decouple any residual ordering ambiguity.
        e_py_sorted = np.sort_complex(e_aligned)
        e_ref_sorted = np.sort_complex(e_ref)

        max_abs_e, max_rel_e = _max_abs_rel(e_py_sorted, e_ref_sorted)
        e_ok = np.allclose(e_py_sorted, e_ref_sorted, atol=1e-12, rtol=1e-9)
        rows.append(
            {
                "function": "dvar2eig",
                "case": case_label,
                "metric": "E",
                "max_abs": max_abs_e,
                "max_rel": max_rel_e,
                "atol": 1e-12,
                "rtol": 1e-9,
                "pass": bool(e_ok),
            }
        )
        assert e_ok, (
            f"E {case_label} mismatch: max_abs={max_abs_e:.3e}, max_rel={max_rel_e:.3e}, "
            f"shape_got={e_py_sorted.shape}, shape_ref={e_ref_sorted.shape}"
        )

        max_abs_cov, max_rel_cov = _max_abs_rel(cov_e_aligned, cov_e_ref)
        cov_ok = np.allclose(cov_e_aligned, cov_e_ref, atol=1e-12, rtol=1e-9)
        rows.append(
            {
                "function": "dvar2eig",
                "case": case_label,
                "metric": "covE",
                "max_abs": max_abs_cov,
                "max_rel": max_rel_cov,
                "atol": 1e-12,
                "rtol": 1e-9,
                "pass": bool(cov_ok),
            }
        )
        assert cov_ok, (
            f"covE {case_label} mismatch: max_abs={max_abs_cov:.3e}, max_rel={max_rel_cov:.3e}, "
            f"shape_got={cov_e_aligned.shape}, shape_ref={cov_e_ref.shape}"
        )

    write_parity_report("dvar2eig_parity_report", rows)
