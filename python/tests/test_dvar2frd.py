from __future__ import annotations

import numpy as np
import pytest

from pbsid.lti.dvar2frd import dvar2frd


def _make_case(
    *, p: int = 4, l_out: int = 2, r: int = 1, with_d: bool = True
) -> tuple[np.ndarray, np.ndarray, float, int, np.ndarray]:
    rng = np.random.default_rng(81 if with_d else 82)
    m = l_out + r
    width = p * m + (r if with_d else 0)
    varx = rng.standard_normal((l_out, width)).astype(np.float64) * 0.2

    n_param = p * l_out * (l_out + r) + (r * l_out if with_d else 0)
    p_cov = np.eye(n_param, dtype=np.float64) * 1e-3
    w = np.linspace(0.2, 2.0, 6, dtype=np.float64)
    h = 0.05
    return p_cov, w, h, p, varx


def test_dvar2frd_shapes_with_d() -> None:
    p_cov, w, h, p, varx = _make_case(with_d=True)

    g, cov_g = dvar2frd(p_cov, w, h, p, varx)

    l_out = varx.shape[0]
    m = int(np.floor(varx.shape[1] / p))
    r = m - l_out

    assert g.shape == (l_out, r + l_out, w.size)
    assert cov_g.shape == (l_out, r + l_out, w.size, 2, 2)
    assert np.all(np.isfinite(np.real(g)))
    assert np.all(np.isfinite(np.imag(g)))
    assert np.all(np.isfinite(cov_g))


def test_dvar2frd_shapes_without_d() -> None:
    p_cov, w, h, p, varx = _make_case(with_d=False)

    g, cov_g = dvar2frd(p_cov, w, h, p, varx)

    l_out = varx.shape[0]
    m = int(np.floor(varx.shape[1] / p))
    r = m - l_out

    assert g.shape == (l_out, r + l_out, w.size)
    assert cov_g.shape == (l_out, r + l_out, w.size, 2, 2)


def test_dvar2frd_accepts_column_frequency_vector() -> None:
    p_cov, w, h, p, varx = _make_case(with_d=True)
    w_col = w[:, np.newaxis]

    g1, cov1 = dvar2frd(p_cov, w, h, p, varx)
    g2, cov2 = dvar2frd(p_cov, w_col, h, p, varx)

    np.testing.assert_allclose(g1, g2, atol=1e-12, rtol=0.0)
    np.testing.assert_allclose(cov1, cov2, atol=1e-12, rtol=0.0)


def test_dvar2frd_rejects_too_small_covariance() -> None:
    p_cov, w, h, p, varx = _make_case(with_d=True)
    bad_p = np.eye(p_cov.shape[0] - 1, dtype=np.float64)

    with pytest.raises(ValueError, match="cover all VARX parameters"):
        _ = dvar2frd(bad_p, w, h, p, varx)
