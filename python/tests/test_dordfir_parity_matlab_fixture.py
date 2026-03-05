from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from pbsid.lti.dordfir import dordfir
from pbsid.parity_report_utils import write_parity_report

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "fixtures" / "matlab_reference" / "dordfir_fixture.mat"
)


def _match_shape(ref: np.ndarray, got: np.ndarray) -> np.ndarray:
    if ref.shape == got.shape:
        return ref
    if ref.ndim == got.ndim == 2 and ref.T.shape == got.shape:
        return ref.T
    if ref.ndim == 1 and got.ndim == 2 and ref.reshape(1, -1).shape == got.shape:
        return ref.reshape(1, -1)
    if ref.ndim == 2 and got.ndim == 1 and ref.reshape(-1).shape == got.shape:
        return ref.reshape(-1)
    return ref


def _max_abs_rel(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    diff = np.abs(a - b)
    denom = np.maximum(np.abs(b), 1e-12)
    return float(np.max(diff)), float(np.max(diff / denom))


def _align_row_signs(got: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """Align row signs to handle SVD vector sign indeterminacy."""
    if got.ndim != 2 or ref.ndim != 2 or got.shape != ref.shape:
        return got

    aligned = got.copy()
    for i in range(got.shape[0]):
        score = float(np.dot(aligned[i, :], ref[i, :]))
        if score < 0.0:
            aligned[i, :] *= -1.0
    return aligned


def _record_metric(
    *,
    rows: list[dict[str, str | float | int | bool]],
    case: str,
    metric: str,
    got: np.ndarray,
    ref: np.ndarray,
    atol: float,
    rtol: float,
    sign_invariant_rows: bool = False,
) -> None:
    ref2 = _match_shape(ref, got)
    got_eval = _align_row_signs(got, ref2) if sign_invariant_rows else got
    max_abs, max_rel = _max_abs_rel(got_eval, ref2)
    ok = np.allclose(got_eval, ref2, atol=atol, rtol=rtol)
    rows.append(
        {
            "function": "dordfir",
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
        f"shape_got={got.shape}, shape_ref={ref2.shape}"
    )


@pytest.mark.parity
def test_dordfir_parity_base_and_no_d_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDordfirFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=False, struct_as_record=False)
    n_cases = int(np.asarray(m.get("n_cases", [[1]])).item())
    if n_cases < 3:
        pytest.skip(
            "Fixture has fewer than 3 cases. Regenerate with: testutils.generateDordfirFixture"
        )

    rows: list[dict[str, str | float | int | bool]] = []

    for i in range(n_cases):
        case_label = f"c{i + 1}"
        u = np.asarray(m[f"u_{case_label}"], dtype=np.float64)
        y = np.asarray(m[f"y_{case_label}"], dtype=np.float64)
        f = int(np.asarray(m[f"f_{case_label}"]).item())
        p = int(np.asarray(m[f"p_{case_label}"]).item())

        s_b, x_b, fir_b = dordfir(u, y, f, p, reg="none", opt="gcv", no_d=0)
        assert not isinstance(x_b, list)
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="S",
            got=s_b,
            ref=np.asarray(m[f"S_base_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
        )
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="X",
            got=x_b,
            ref=np.asarray(m[f"X_base_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
            sign_invariant_rows=True,
        )
        _record_metric(
            rows=rows,
            case=f"base_{case_label}",
            metric="FIR",
            got=fir_b,
            ref=np.asarray(m[f"FIR_base_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
        )

        s_n, x_n, fir_n = dordfir(u, y, f, p, reg="none", opt="gcv", no_d=1)
        assert not isinstance(x_n, list)
        _record_metric(
            rows=rows,
            case=f"noD_{case_label}",
            metric="S",
            got=s_n,
            ref=np.asarray(m[f"S_noD_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
        )
        _record_metric(
            rows=rows,
            case=f"noD_{case_label}",
            metric="X",
            got=x_n,
            ref=np.asarray(m[f"X_noD_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
            sign_invariant_rows=True,
        )
        _record_metric(
            rows=rows,
            case=f"noD_{case_label}",
            metric="FIR",
            got=fir_n,
            ref=np.asarray(m[f"FIR_noD_{case_label}"], dtype=np.float64),
            atol=1e-10,
            rtol=1e-7,
        )

    write_parity_report("dordfir_parity_report", rows)
