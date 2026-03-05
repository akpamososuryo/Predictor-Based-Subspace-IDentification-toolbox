from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from pbsid.lti.dordvarx import dordvarx
from pbsid.parity_report_utils import write_parity_report

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "fixtures" / "matlab_reference" / "dordvarx_fixture.mat"
)


def _max_abs_rel(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    diff = np.abs(a - b)
    denom = np.maximum(np.abs(b), 1e-12)
    return float(np.max(diff)), float(np.max(diff / denom))


def _match_shape(ref: np.ndarray, got: np.ndarray) -> np.ndarray:
    if ref.shape == got.shape:
        return ref
    if ref.ndim == 1 and got.ndim == 2 and ref.size == got.size and 1 in got.shape:
        return ref.reshape(got.shape)
    return ref


def _assert_close(name: str, got: np.ndarray, ref: np.ndarray, atol: float, rtol: float) -> None:
    ref2 = _match_shape(ref, got)
    max_abs, max_rel = _max_abs_rel(got, ref2)
    assert np.allclose(got, ref2, atol=atol, rtol=rtol), (
        f"{name} mismatch: max_abs={max_abs:.3e}, max_rel={max_rel:.3e}, "
        f"shape_got={got.shape}, shape_ref={ref2.shape}"
    )


def _assert_case(
    *,
    tag: str,
    m: dict[str, np.ndarray],
    u: np.ndarray,
    y: np.ndarray,
    f: int,
    p: int,
    weight: int,
    no_d: int,
    case_label: str,
    rows: list[dict[str, str | float | int | bool]],
) -> None:
    s, x, varx, umat, zps = dordvarx(u, y, f, p, reg="none", opt="gcv", weight=weight, no_d=no_d)
    assert not isinstance(x, list)

    s_ref = np.asarray(m[f"S_{tag}_{case_label}"], dtype=np.float64)
    varx_ref = np.asarray(m[f"VARX_{tag}_{case_label}"], dtype=np.float64)
    zps_ref = np.asarray(m[f"Zps_{tag}_{case_label}"], dtype=np.float64)

    atol_s = 1e-10
    rtol_s = 1e-6
    max_abs_s, max_rel_s = _max_abs_rel(s, _match_shape(s_ref, s))
    s_ok = np.allclose(s, _match_shape(s_ref, s), atol=atol_s, rtol=rtol_s)
    rows.append(
        {
            "function": "dordvarx",
            "case": f"{tag}_{case_label}",
            "metric": "S",
            "max_abs": max_abs_s,
            "max_rel": max_rel_s,
            "atol": atol_s,
            "rtol": rtol_s,
            "pass": bool(s_ok),
        }
    )
    _assert_close(f"S_{tag}_{case_label}", s, s_ref, atol=atol_s, rtol=rtol_s)

    atol_varx = 1e-10
    rtol_varx = 1e-6
    max_abs_varx, max_rel_varx = _max_abs_rel(varx, _match_shape(varx_ref, varx))
    varx_ok = np.allclose(varx, _match_shape(varx_ref, varx), atol=atol_varx, rtol=rtol_varx)
    rows.append(
        {
            "function": "dordvarx",
            "case": f"{tag}_{case_label}",
            "metric": "VARX",
            "max_abs": max_abs_varx,
            "max_rel": max_rel_varx,
            "atol": atol_varx,
            "rtol": rtol_varx,
            "pass": bool(varx_ok),
        }
    )
    _assert_close(f"VARX_{tag}_{case_label}", varx, varx_ref, atol=atol_varx, rtol=rtol_varx)

    atol_zps = 1e-10
    rtol_zps = 1e-6
    max_abs_zps, max_rel_zps = _max_abs_rel(zps, _match_shape(zps_ref, zps))
    zps_ok = np.allclose(zps, _match_shape(zps_ref, zps), atol=atol_zps, rtol=rtol_zps)
    rows.append(
        {
            "function": "dordvarx",
            "case": f"{tag}_{case_label}",
            "metric": "Zps",
            "max_abs": max_abs_zps,
            "max_rel": max_rel_zps,
            "atol": atol_zps,
            "rtol": rtol_zps,
            "pass": bool(zps_ok),
        }
    )
    _assert_close(f"Zps_{tag}_{case_label}", zps, zps_ref, atol=atol_zps, rtol=rtol_zps)

    x_ref = np.asarray(m[f"X_{tag}_{case_label}"], dtype=np.float64)
    u_ref = np.asarray(m[f"U_{tag}_{case_label}"], dtype=np.float64)
    assert x.shape == x_ref.shape
    assert umat.shape == u_ref.shape
    assert np.all(np.isfinite(x))
    assert np.all(np.isfinite(umat))


@pytest.mark.parity
def test_dordvarx_parity_baseline_weight_nod_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDordvarxFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=False, struct_as_record=False)
    n_cases = int(np.asarray(m.get("n_cases", [[1]])).item())
    if n_cases < 3:
        pytest.skip(
            "Fixture has fewer than 3 cases. Regenerate with: testutils.generateDordvarxFixture"
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
            weight=0,
            no_d=1,
            case_label=case_label,
            rows=rows,
        )

    write_parity_report("dordvarx_parity_report", rows)
