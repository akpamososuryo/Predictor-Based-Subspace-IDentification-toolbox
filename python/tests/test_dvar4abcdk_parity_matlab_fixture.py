from __future__ import annotations

from pathlib import Path
from typing import cast

import numpy as np
import pytest
from scipy.io import loadmat

from pbsid.lti.dvar4abcdk import dvar4abcdk
from pbsid.parity_report_utils import write_parity_report

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "fixtures" / "matlab_reference" / "dvar4abcdk_fixture.mat"
)


def _max_abs_rel(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    diff = np.abs(a - b)
    denom = np.maximum(np.abs(b), 1e-12)
    return float(np.max(diff)), float(np.max(diff / denom))


def _record_metric(
    *,
    rows: list[dict[str, str | float | int | bool]],
    case: str,
    metric: str,
    got: np.ndarray,
    ref: np.ndarray,
    atol: float,
    rtol: float,
) -> None:
    max_abs, max_rel = _max_abs_rel(got, ref)
    ok = np.allclose(got, ref, atol=atol, rtol=rtol)
    rows.append(
        {
            "function": "dvar4abcdk",
            "case": case,
            "metric": metric,
            "max_abs": max_abs,
            "max_rel": max_rel,
            "atol": atol,
            "rtol": rtol,
            "pass": bool(ok),
        }
    )
    assert ok, (
        f"{metric}_{case} mismatch: max_abs={max_abs:.3e}, max_rel={max_rel:.3e}, "
        f"shape_got={got.shape}, shape_ref={ref.shape}"
    )


@pytest.mark.parity
def test_dvar4abcdk_parity_base_and_stable1_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDvar4abcdkFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=False, struct_as_record=False)
    n_cases = int(np.asarray(m.get("n_cases", [[1]])).item())
    if n_cases < 3:
        pytest.skip(
            "Fixture has fewer than 3 cases. Regenerate with: testutils.generateDvar4abcdkFixture"
        )

    rows: list[dict[str, str | float | int | bool]] = []
    for i in range(n_cases):
        case_label = f"c{i + 1}"

        x_b = np.asarray(m[f"x_base_{case_label}"], dtype=np.float64)
        u_b = np.asarray(m[f"u_base_{case_label}"], dtype=np.float64)
        y_b = np.asarray(m[f"y_base_{case_label}"], dtype=np.float64)
        f_b = int(np.asarray(m[f"f_base_{case_label}"]).item())
        p_b = int(np.asarray(m[f"p_base_{case_label}"]).item())
        a_b = np.asarray(m[f"A_base_{case_label}"], dtype=np.float64)
        b_b = np.asarray(m[f"B_base_{case_label}"], dtype=np.float64)
        c_b = np.asarray(m[f"C_base_{case_label}"], dtype=np.float64)
        d_b = np.asarray(m[f"D_base_{case_label}"], dtype=np.float64)
        k_b = np.asarray(m[f"K_base_{case_label}"], dtype=np.float64)
        uproj_b = np.asarray(m[f"U_base_{case_label}"], dtype=np.float64)
        zps_b = np.asarray(m[f"Zps_base_{case_label}"], dtype=np.float64)

        base_result = cast(
            tuple[
                np.ndarray,
                np.ndarray,
                np.ndarray,
                np.ndarray,
                np.ndarray,
                np.ndarray,
                np.ndarray,
            ],
            dvar4abcdk(
                x_b,
                u_b,
                y_b,
                f_b,
                p_b,
                a_b,
                b_b,
                c_b,
                d_b,
                k_b,
                uproj_b,
                zps_b,
                return_deltas=True,
            ),
        )
        p_cov_b, sigma_b, da_b, db_b, dc_b, dd_b, dk_b = base_result

        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="P",
            got=p_cov_b,
            ref=np.asarray(m[f"P_base_{case_label}"], dtype=np.float64),
            atol=1e-8,
            rtol=1e-6,
        )
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="sigma",
            got=sigma_b,
            ref=np.asarray(m[f"sigma_base_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
        )
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="dA",
            got=da_b,
            ref=np.asarray(m[f"dA_base_{case_label}"], dtype=np.float64),
            atol=1e-8,
            rtol=1e-6,
        )
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="dB",
            got=db_b,
            ref=np.asarray(m[f"dB_base_{case_label}"], dtype=np.float64),
            atol=1e-8,
            rtol=1e-6,
        )
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="dC",
            got=dc_b,
            ref=np.asarray(m[f"dC_base_{case_label}"], dtype=np.float64),
            atol=1e-8,
            rtol=1e-6,
        )
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="dD",
            got=dd_b,
            ref=np.asarray(m[f"dD_base_{case_label}"], dtype=np.float64),
            atol=1e-8,
            rtol=1e-6,
        )
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="dK",
            got=dk_b,
            ref=np.asarray(m[f"dK_base_{case_label}"], dtype=np.float64),
            atol=1e-8,
            rtol=1e-6,
        )

        x_s1 = np.asarray(m[f"x_stable1_{case_label}"], dtype=np.float64)
        u_s1 = np.asarray(m[f"u_stable1_{case_label}"], dtype=np.float64)
        y_s1 = np.asarray(m[f"y_stable1_{case_label}"], dtype=np.float64)
        f_s1 = int(np.asarray(m[f"f_stable1_{case_label}"]).item())
        p_s1 = int(np.asarray(m[f"p_stable1_{case_label}"]).item())
        a_s1 = np.asarray(m[f"A_stable1_{case_label}"], dtype=np.float64)
        b_s1 = np.asarray(m[f"B_stable1_{case_label}"], dtype=np.float64)
        c_s1 = np.asarray(m[f"C_stable1_{case_label}"], dtype=np.float64)
        d_s1 = np.asarray(m[f"D_stable1_{case_label}"], dtype=np.float64)
        k_s1 = np.asarray(m[f"K_stable1_{case_label}"], dtype=np.float64)
        uproj_s1 = np.asarray(m[f"U_stable1_{case_label}"], dtype=np.float64)
        zps_s1 = np.asarray(m[f"Zps_stable1_{case_label}"], dtype=np.float64)

        stable_result = cast(
            tuple[
                np.ndarray,
                np.ndarray,
                np.ndarray,
                np.ndarray,
                np.ndarray,
                np.ndarray,
                np.ndarray,
            ],
            dvar4abcdk(
                x_s1,
                u_s1,
                y_s1,
                f_s1,
                p_s1,
                a_s1,
                b_s1,
                c_s1,
                d_s1,
                k_s1,
                uproj_s1,
                zps_s1,
                return_deltas=True,
            ),
        )
        p_cov_s1, sigma_s1, da_s1, db_s1, dc_s1, dd_s1, dk_s1 = stable_result

        _record_metric(
            rows=rows,
            case=f"stable1_{case_label}",
            metric="P",
            got=p_cov_s1,
            ref=np.asarray(m[f"P_stable1_{case_label}"], dtype=np.float64),
            atol=2e-5,
            rtol=2e-4,
        )
        _record_metric(
            rows=rows,
            case=f"stable1_{case_label}",
            metric="sigma",
            got=sigma_s1,
            ref=np.asarray(m[f"sigma_stable1_{case_label}"], dtype=np.float64),
            atol=1e-8,
            rtol=1e-6,
        )
        _record_metric(
            rows=rows,
            case=f"stable1_{case_label}",
            metric="dA",
            got=da_s1,
            ref=np.asarray(m[f"dA_stable1_{case_label}"], dtype=np.float64),
            atol=5e-5,
            rtol=2e-4,
        )
        _record_metric(
            rows=rows,
            case=f"stable1_{case_label}",
            metric="dB",
            got=db_s1,
            ref=np.asarray(m[f"dB_stable1_{case_label}"], dtype=np.float64),
            atol=5e-5,
            rtol=2e-4,
        )
        _record_metric(
            rows=rows,
            case=f"stable1_{case_label}",
            metric="dC",
            got=dc_s1,
            ref=np.asarray(m[f"dC_stable1_{case_label}"], dtype=np.float64),
            atol=1e-7,
            rtol=1e-5,
        )
        _record_metric(
            rows=rows,
            case=f"stable1_{case_label}",
            metric="dD",
            got=dd_s1,
            ref=np.asarray(m[f"dD_stable1_{case_label}"], dtype=np.float64),
            atol=1e-7,
            rtol=1e-5,
        )
        _record_metric(
            rows=rows,
            case=f"stable1_{case_label}",
            metric="dK",
            got=dk_s1,
            ref=np.asarray(m[f"dK_stable1_{case_label}"], dtype=np.float64),
            atol=5e-5,
            rtol=2e-4,
        )

    write_parity_report("dvar4abcdk_parity_report", rows)