from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from pbsid.lti.dordvarmax import dordvarmax
from pbsid.parity_report_utils import write_parity_report

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "matlab_reference"
    / "dordvarmax_fixture.mat"
)


def _max_abs_rel(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    diff = np.abs(a - b)
    denom = np.maximum(np.abs(b), 1e-12)
    return float(np.max(diff)), float(np.max(diff / denom))


def _assert_close(name: str, got: np.ndarray, ref: np.ndarray, atol: float, rtol: float) -> None:
    max_abs, max_rel = _max_abs_rel(got, ref)
    assert np.allclose(got, ref, atol=atol, rtol=rtol), (
        f"{name} mismatch: max_abs={max_abs:.3e}, max_rel={max_rel:.3e}, "
        f"shape_got={got.shape}, shape_ref={ref.shape}"
    )


def _assert_varmax_close(
    *,
    name: str,
    got: np.ndarray,
    ref: np.ndarray,
    r: int,
    l_out: int,
    p: int,
    no_d: int,
    case: str,
    rows: list[dict[str, str | float | int | bool]],
) -> None:
    atol_varmax = 2e-8
    rtol_varmax = 1e-5
    m = r + 2 * l_out
    varx_cols = p * m

    # Innovation/error-channel blocks are currently sensitive to the exact EXLS variant.
    innov_mask = np.zeros((varx_cols,), dtype=bool)
    for i in range(p):
        start = i * m + r + l_out
        innov_mask[start : start + l_out] = True

    stable_mask = np.ones((got.shape[1],), dtype=bool)
    stable_mask[:varx_cols] = ~innov_mask

    max_abs_stable, max_rel_stable = _max_abs_rel(got[:, stable_mask], ref[:, stable_mask])
    stable_ok = np.allclose(
        got[:, stable_mask], ref[:, stable_mask], atol=atol_varmax, rtol=rtol_varmax
    )
    rows.append(
        {
            "function": "dordvarmax",
            "case": case,
            "metric": f"{name}_stable",
            "max_abs": max_abs_stable,
            "max_rel": max_rel_stable,
            "atol": atol_varmax,
            "rtol": rtol_varmax,
            "pass": bool(stable_ok),
        }
    )
    _assert_close(
        f"{name}_stable",
        got[:, stable_mask],
        ref[:, stable_mask],
        atol=atol_varmax,
        rtol=rtol_varmax,
    )

    got_innov = got[:, :varx_cols][:, innov_mask]
    ref_innov = ref[:, :varx_cols][:, innov_mask]
    max_abs_innov, max_rel_innov = _max_abs_rel(got_innov, ref_innov)
    rows.append(
        {
            "function": "dordvarmax",
            "case": case,
            "metric": f"{name}_innovation",
            "max_abs": max_abs_innov,
            "max_rel": max_rel_innov,
            "atol": atol_varmax,
            "rtol": rtol_varmax,
            "pass": bool(np.allclose(got_innov, ref_innov, atol=atol_varmax, rtol=rtol_varmax)),
        }
    )
    assert np.allclose(got_innov, ref_innov, atol=atol_varmax, rtol=rtol_varmax), (
        f"{name}_innovation mismatch: max_abs={max_abs_innov:.3e}, max_rel={max_rel_innov:.3e}"
    )

    if not no_d:
        max_abs_direct, max_rel_direct = _max_abs_rel(got[:, varx_cols:], ref[:, varx_cols:])
        rows.append(
            {
                "function": "dordvarmax",
                "case": case,
                "metric": f"{name}_direct",
                "max_abs": max_abs_direct,
                "max_rel": max_rel_direct,
                "atol": atol_varmax,
                "rtol": rtol_varmax,
                "pass": bool(
                    np.allclose(
                        got[:, varx_cols:],
                        ref[:, varx_cols:],
                        atol=atol_varmax,
                        rtol=rtol_varmax,
                    )
                ),
            }
        )
        _assert_close(
            f"{name}_direct",
            got[:, varx_cols:],
            ref[:, varx_cols:],
            atol=atol_varmax,
            rtol=rtol_varmax,
        )


def _assert_case(
    *,
    tag: str,
    m: dict[str, np.ndarray],
    u: np.ndarray,
    y: np.ndarray,
    f: int,
    p: int,
    method: str,
    weight: int,
    no_d: int,
    case_label: str,
    rows: list[dict[str, str | float | int | bool]],
) -> None:
    s, x, varmax, umat = dordvarmax(
        u,
        y,
        f,
        p,
        method=method,
        tol=1e-6,
        reg="none",
        opt="gcv",
        weight=weight,
        no_d=no_d,
    )
    assert not isinstance(x, list)

    s_ref = np.asarray(m[f"S_{tag}_{case_label}"], dtype=np.float64).reshape(-1)
    atol_s = 1e-9
    rtol_s = 1e-6
    max_abs_s, max_rel_s = _max_abs_rel(s, s_ref)
    s_ok = np.allclose(s, s_ref, atol=atol_s, rtol=rtol_s)
    rows.append(
        {
            "function": "dordvarmax",
            "case": f"{tag}_{case_label}",
            "metric": "S",
            "max_abs": max_abs_s,
            "max_rel": max_rel_s,
            "atol": atol_s,
            "rtol": rtol_s,
            "pass": bool(s_ok),
        }
    )
    assert s_ok, (
        f"S_{tag}_{case_label} mismatch: max_abs={max_abs_s:.3e}, "
        f"max_rel={max_rel_s:.3e}, shape_got={s.shape}, shape_ref={s_ref.shape}"
    )
    u_rows = int(min(u.shape))
    y_rows = int(min(y.shape))
    _assert_varmax_close(
        name=f"VARMAX_{tag}_{case_label}",
        got=varmax,
        ref=np.asarray(m[f"VARMAX_{tag}_{case_label}"], dtype=np.float64),
        r=u_rows,
        l_out=y_rows,
        p=p,
        no_d=no_d,
        case=f"{tag}_{case_label}",
        rows=rows,
    )

    x_ref = np.asarray(m[f"X_{tag}_{case_label}"], dtype=np.float64)
    u_ref = np.asarray(m[f"U_{tag}_{case_label}"], dtype=np.float64)
    assert x.shape == x_ref.shape
    assert umat.shape == u_ref.shape
    assert np.all(np.isfinite(x))
    assert np.all(np.isfinite(umat))


@pytest.mark.parity
def test_dordvarmax_parity_baseline_weight_nod_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDordvarmaxFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=False, struct_as_record=False)

    n_cases = int(np.asarray(m.get("n_cases", [[1]])).item())
    if n_cases < 3:
        pytest.skip(
            "Fixture has fewer than 3 cases. Regenerate with: testutils.generateDordvarmaxFixture"
        )

    rows: list[dict[str, str | float | int | bool]] = []

    for i in range(n_cases):
        case_label = f"c{i + 1}"
        u = np.asarray(m[f"u_{case_label}"], dtype=np.float64)
        y = np.asarray(m[f"y_{case_label}"], dtype=np.float64)
        f = int(np.asarray(m[f"f_{case_label}"]).item())
        p = int(np.asarray(m[f"p_{case_label}"]).item())

        _assert_case(
            tag="base",
            m=m,
            u=u,
            y=y,
            f=f,
            p=p,
            method="gradient",
            weight=0,
            no_d=0,
            case_label=case_label,
            rows=rows,
        )
        _assert_case(
            tag="weight1",
            m=m,
            u=u,
            y=y,
            f=f,
            p=p,
            method="els",
            weight=1,
            no_d=0,
            case_label=case_label,
            rows=rows,
        )
        _assert_case(
            tag="noD",
            m=m,
            u=u,
            y=y,
            f=f,
            p=p,
            method="gradient",
            weight=0,
            no_d=1,
            case_label=case_label,
            rows=rows,
        )

    write_parity_report("dordvarmax_parity_report", rows)
