from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from pbsid.lti.dx2abck import dx2abck

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "fixtures" / "matlab_reference" / "dx2abck_fixture.mat"
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


@pytest.mark.parity
def test_dx2abck_parity_baseline_and_stable1_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDx2abckFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=True, struct_as_record=False)

    x_base = np.asarray(m["x_base"], dtype=np.float64)
    u_base = np.asarray(m["u_base"], dtype=np.float64)
    y_base = np.asarray(m["y_base"], dtype=np.float64)
    f_base = int(np.asarray(m["f_base"]).item())
    p_base = int(np.asarray(m["p_base"]).item())

    a, b, c, k = dx2abck(x_base, u_base, y_base, f_base, p_base, c="none", return_k=True)

    _assert_close("A_base", a, np.asarray(m["A_base"], dtype=np.float64), atol=1e-8, rtol=1e-6)
    _assert_close("B_base", b, np.asarray(m["B_base"], dtype=np.float64), atol=1e-8, rtol=1e-6)
    _assert_close("C_base", c, np.asarray(m["C_base"], dtype=np.float64), atol=1e-8, rtol=1e-6)
    _assert_close("K_base", k, np.asarray(m["K_base"], dtype=np.float64), atol=1e-7, rtol=1e-5)

    x_s1 = np.asarray(m["x_stable1"], dtype=np.float64)
    u_s1 = np.asarray(m["u_stable1"], dtype=np.float64)
    y_s1 = np.asarray(m["y_stable1"], dtype=np.float64)
    f_s1 = int(np.asarray(m["f_stable1"]).item())
    p_s1 = int(np.asarray(m["p_stable1"]).item())

    a1, b1, c1, k1 = dx2abck(x_s1, u_s1, y_s1, f_s1, p_s1, c="stable1", return_k=True)

    _assert_close(
        "A_stable1", a1, np.asarray(m["A_stable1"], dtype=np.float64), atol=5e-3, rtol=1e-4
    )
    _assert_close(
        "B_stable1", b1, np.asarray(m["B_stable1"], dtype=np.float64), atol=5e-3, rtol=1e-3
    )
    _assert_close(
        "C_stable1", c1, np.asarray(m["C_stable1"], dtype=np.float64), atol=5e-3, rtol=1e-4
    )
    _assert_close(
        "K_stable1", k1, np.asarray(m["K_stable1"], dtype=np.float64), atol=5e-3, rtol=1e-3
    )
