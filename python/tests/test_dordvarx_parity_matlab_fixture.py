from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from pbsid.lti.dordvarx import dordvarx

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
) -> None:
    s, x, varx, umat, zps = dordvarx(u, y, f, p, reg="none", opt="gcv", weight=weight, no_d=no_d)

    _assert_close(f"S_{tag}", s, np.asarray(m[f"S_{tag}"], dtype=np.float64), atol=1e-8, rtol=1e-6)
    _assert_close(
        f"VARX_{tag}", varx, np.asarray(m[f"VARX_{tag}"], dtype=np.float64), atol=1e-8, rtol=1e-6
    )
    _assert_close(
        f"Zps_{tag}", zps, np.asarray(m[f"Zps_{tag}"], dtype=np.float64), atol=1e-8, rtol=1e-6
    )

    x_ref = np.asarray(m[f"X_{tag}"], dtype=np.float64)
    u_ref = np.asarray(m[f"U_{tag}"], dtype=np.float64)
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

    m = loadmat(FIXTURE_PATH, struct_as_record=False)

    u = np.asarray(m["u_base"], dtype=np.float64)
    y = np.asarray(m["y_base"], dtype=np.float64)
    f = int(np.asarray(m["f_base"]).item())
    p = int(np.asarray(m["p_base"]).item())

    _assert_case(tag="base", m=m, u=u, y=y, f=f, p=p, weight=0, no_d=0)
    _assert_case(tag="weight1", m=m, u=u, y=y, f=f, p=p, weight=1, no_d=0)
    _assert_case(tag="noD", m=m, u=u, y=y, f=f, p=p, weight=0, no_d=1)
