from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from pbsid.lti.dvar4varx import dvar4varx
from pbsid.parity_report_utils import write_parity_report

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "fixtures" / "matlab_reference" / "dvar4varx_fixture.mat"
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
            "function": "dvar4varx",
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
def test_dvar4varx_parity_base_and_nod_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDvar4varxFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=False, struct_as_record=False)
    n_cases = int(np.asarray(m.get("n_cases", [[1]])).item())
    if n_cases < 3:
        pytest.skip(
            "Fixture has fewer than 3 cases. Regenerate with: testutils.generateDvar4varxFixture"
        )

    rows: list[dict[str, str | float | int | bool]] = []
    for i in range(n_cases):
        case_label = f"c{i + 1}"
        u = np.asarray(m[f"u_{case_label}"], dtype=np.float64)
        y = np.asarray(m[f"y_{case_label}"], dtype=np.float64)
        p = int(np.asarray(m[f"p_{case_label}"]).item())

        varx_b = np.asarray(m[f"VARX_base_{case_label}"], dtype=np.float64)
        zps_b = np.asarray(m[f"Zps_base_{case_label}"], dtype=np.float64)
        p_b, sigma_b = dvar4varx(u, y, p, varx_b, zps_b)

        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="P",
            got=p_b,
            ref=np.asarray(m[f"P_base_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
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

        varx_n = np.asarray(m[f"VARX_noD_{case_label}"], dtype=np.float64)
        zps_n = np.asarray(m[f"Zps_noD_{case_label}"], dtype=np.float64)
        p_n, sigma_n = dvar4varx(u, y, p, varx_n, zps_n)

        _record_metric(
            rows=rows,
            case=f"noD_{case_label}",
            metric="P",
            got=p_n,
            ref=np.asarray(m[f"P_noD_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
        )
        _record_metric(
            rows=rows,
            case=f"noD_{case_label}",
            metric="sigma",
            got=sigma_n,
            ref=np.asarray(m[f"sigma_noD_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
        )

    write_parity_report("dvar4varx_parity_report", rows)