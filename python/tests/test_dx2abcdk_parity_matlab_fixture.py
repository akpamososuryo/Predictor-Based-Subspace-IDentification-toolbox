from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from pbsid.lti.dx2abcdk import dx2abcdk
from pbsid.parity_report_utils import write_parity_report

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "fixtures" / "matlab_reference" / "dx2abcdk_fixture.mat"
)


def _max_abs_rel(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    diff = np.abs(a - b)
    denom = np.maximum(np.abs(b), 1e-12)
    return float(np.max(diff)), float(np.max(diff / denom))


def _match_shape(ref: np.ndarray, got: np.ndarray) -> np.ndarray:
    """Align squeezed MATLAB vectors with expected 2D Python matrix shapes."""
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
    ref2 = _match_shape(ref, got)
    max_abs, max_rel = _max_abs_rel(got, ref2)
    ok = np.allclose(got, ref2, atol=atol, rtol=rtol)
    rows.append(
        {
            "function": "dx2abcdk",
            "case": case,
            "metric": metric,
            "max_abs": max_abs,
            "max_rel": max_rel,
            "atol": atol,
            "rtol": rtol,
            "pass": bool(ok),
        }
    )
    _assert_close(f"{metric}_{case}", got, ref, atol=atol, rtol=rtol)


@pytest.mark.parity
def test_dx2abcdk_parity_baseline_and_stable1_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDx2abcdkFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=False, struct_as_record=False)
    n_cases = int(np.asarray(m.get("n_cases", [[1]])).item())
    if n_cases < 3:
        pytest.skip(
            "Fixture has fewer than 3 cases. Regenerate with: testutils.generateDx2abcdkFixture"
        )

    rows: list[dict[str, str | float | int | bool]] = []

    for i in range(n_cases):
        case_label = f"c{i + 1}"
        x_base = np.asarray(m[f"x_base_{case_label}"], dtype=np.float64)
        u_base = np.asarray(m[f"u_base_{case_label}"], dtype=np.float64)
        y_base = np.asarray(m[f"y_base_{case_label}"], dtype=np.float64)
        f_base = int(np.asarray(m[f"f_base_{case_label}"]).item())
        p_base = int(np.asarray(m[f"p_base_{case_label}"]).item())

        a, b, c, d, k = dx2abcdk(x_base, u_base, y_base, f_base, p_base, c="none", return_k=True)

        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="A",
            got=a,
            ref=np.asarray(m[f"A_base_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
        )
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="B",
            got=b,
            ref=np.asarray(m[f"B_base_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
        )
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="C",
            got=c,
            ref=np.asarray(m[f"C_base_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
        )
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="D",
            got=d,
            ref=np.asarray(m[f"D_base_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
        )
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="K",
            got=k,
            ref=np.asarray(m[f"K_base_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
        )

        x_s1 = np.asarray(m[f"x_stable1_{case_label}"], dtype=np.float64)
        u_s1 = np.asarray(m[f"u_stable1_{case_label}"], dtype=np.float64)
        y_s1 = np.asarray(m[f"y_stable1_{case_label}"], dtype=np.float64)
        f_s1 = int(np.asarray(m[f"f_stable1_{case_label}"]).item())
        p_s1 = int(np.asarray(m[f"p_stable1_{case_label}"]).item())

        a1, b1, c1, d1, k1 = dx2abcdk(x_s1, u_s1, y_s1, f_s1, p_s1, c="stable1", return_k=True)

        _record_metric(
            rows=rows,
            case=f"stable1_{case_label}",
            metric="A",
            got=a1,
            ref=np.asarray(m[f"A_stable1_{case_label}"], dtype=np.float64),
            atol=5e-3,
            rtol=8e-5,
        )
        _record_metric(
            rows=rows,
            case=f"stable1_{case_label}",
            metric="B",
            got=b1,
            ref=np.asarray(m[f"B_stable1_{case_label}"], dtype=np.float64),
            atol=5e-3,
            rtol=1e-4,
        )
        _record_metric(
            rows=rows,
            case=f"stable1_{case_label}",
            metric="C",
            got=c1,
            ref=np.asarray(m[f"C_stable1_{case_label}"], dtype=np.float64),
            atol=5e-6,
            rtol=1e-6,
        )
        _record_metric(
            rows=rows,
            case=f"stable1_{case_label}",
            metric="D",
            got=d1,
            ref=np.asarray(m[f"D_stable1_{case_label}"], dtype=np.float64),
            atol=5e-6,
            rtol=1e-6,
        )
        _record_metric(
            rows=rows,
            case=f"stable1_{case_label}",
            metric="K",
            got=k1,
            ref=np.asarray(m[f"K_stable1_{case_label}"], dtype=np.float64),
            atol=2e-2,
            rtol=1e-4,
        )

    write_parity_report("dx2abcdk_parity_report", rows)
