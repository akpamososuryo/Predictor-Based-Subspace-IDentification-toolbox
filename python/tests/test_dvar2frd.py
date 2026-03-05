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


def _make_ss_case() -> tuple[
    np.ndarray,
    np.ndarray,
    float,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    rng = np.random.default_rng(90)
    n = 3
    r = 2
    l_out = 2
    a = np.array([[0.83, 0.08, 0.0], [-0.05, 0.79, 0.04], [0.0, 0.03, 0.74]], dtype=np.float64)
    b = 0.2 * rng.standard_normal((n, r))
    c = 0.2 * rng.standard_normal((l_out, n))
    k = 0.1 * rng.standard_normal((n, l_out))
    d = 0.05 * rng.standard_normal((l_out, r))
    w = np.linspace(0.2, 2.0, 6, dtype=np.float64)
    h = 0.05

    n_param_abck = n * n + (r + l_out) * n + n * l_out
    p_abck = np.eye(n_param_abck, dtype=np.float64) * 1e-3

    n_param_abcdk = n_param_abck + r * l_out
    p_abcdk = np.eye(n_param_abcdk, dtype=np.float64) * 1e-3

    return p_abck, p_abcdk, h, w, a, b, c, d, k, np.array([r, l_out], dtype=np.int64)


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


def test_dvar2frd_abck_shapes_and_finite() -> None:
    p_abck, _, h, w, a, b, c, _, k, dims = _make_ss_case()
    r = int(dims[0])
    l_out = int(dims[1])

    g, cov_g = dvar2frd(p_abck, w, h, a, b, c, k)

    assert g.shape == (l_out, r + l_out, w.size)
    assert cov_g.shape == (l_out, r + l_out, w.size, 2, 2)
    assert np.all(np.isfinite(np.real(g)))
    assert np.all(np.isfinite(np.imag(g)))
    assert np.all(np.isfinite(cov_g))


def test_dvar2frd_abcdk_shapes_and_finite() -> None:
    _, p_abcdk, h, w, a, b, c, d, k, dims = _make_ss_case()
    r = int(dims[0])
    l_out = int(dims[1])

    g, cov_g = dvar2frd(p_abcdk, w, h, a, b, c, d, k)

    assert g.shape == (l_out, r + l_out, w.size)
    assert cov_g.shape == (l_out, r + l_out, w.size, 2, 2)
    assert np.all(np.isfinite(np.real(g)))
    assert np.all(np.isfinite(np.imag(g)))
    assert np.all(np.isfinite(cov_g))


def test_dvar2frd_abck_accepts_column_frequency_vector() -> None:
    p_abck, _, h, w, a, b, c, _, k, _ = _make_ss_case()
    w_col = w[:, np.newaxis]

    g1, cov1 = dvar2frd(p_abck, w, h, a, b, c, k)
    g2, cov2 = dvar2frd(p_abck, w_col, h, a, b, c, k)

    np.testing.assert_allclose(g1, g2, atol=1e-12, rtol=0.0)
    np.testing.assert_allclose(cov1, cov2, atol=1e-12, rtol=0.0)


def test_dvar2frd_abck_rejects_too_small_covariance() -> None:
    p_abck, _, h, w, a, b, c, _, k, _ = _make_ss_case()
    bad_p = np.eye(p_abck.shape[0] - 1, dtype=np.float64)

    with pytest.raises(ValueError, match="ABCK"):
        _ = dvar2frd(bad_p, w, h, a, b, c, k)
