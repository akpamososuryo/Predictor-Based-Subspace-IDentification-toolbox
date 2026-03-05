from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import loadmat

from pbsid.lti.dvar2frd import dvar2frd

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2] / "fixtures" / "matlab_reference" / "dvar2frd_fixture.mat"
)


def _max_abs_rel(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    diff = np.abs(a - b)
    denom = np.maximum(np.abs(b), 1e-12)
    return float(np.max(diff)), float(np.max(diff / denom))


@pytest.mark.parity
def test_dvar2frd_parity_varx_fixture() -> None:
    if not FIXTURE_PATH.exists():
        pytest.skip(
            "Missing MATLAB fixture. Generate with: testutils.generateDvar2frdFixture in MATLAB."
        )

    m = loadmat(FIXTURE_PATH, squeeze_me=False, struct_as_record=False)

    p_cov = np.asarray(m["P"], dtype=np.float64)
    w = np.asarray(m["w"], dtype=np.float64).reshape(-1)
    h = float(np.asarray(m["h"]).item())
    p = int(np.asarray(m["p"]).item())
    varx = np.asarray(m["VARX"], dtype=np.float64)

    g_py, cov_g_py = dvar2frd(p_cov, w, h, p, varx)
    g_ref = np.asarray(m["G"], dtype=np.complex128)
    cov_g_ref = np.asarray(m["covG"], dtype=np.float64)

    max_abs_g, max_rel_g = _max_abs_rel(g_py, g_ref)
    assert np.allclose(g_py, g_ref, atol=1e-8, rtol=1e-6), (
        f"G mismatch: max_abs={max_abs_g:.3e}, max_rel={max_rel_g:.3e}, "
        f"shape_got={g_py.shape}, shape_ref={g_ref.shape}"
    )

    max_abs_cov, max_rel_cov = _max_abs_rel(cov_g_py, cov_g_ref)
    assert np.allclose(cov_g_py, cov_g_ref, atol=1e-7, rtol=1e-5), (
        f"covG mismatch: max_abs={max_abs_cov:.3e}, max_rel={max_rel_cov:.3e}, "
        f"shape_got={cov_g_py.shape}, shape_ref={cov_g_ref.shape}"
    )
