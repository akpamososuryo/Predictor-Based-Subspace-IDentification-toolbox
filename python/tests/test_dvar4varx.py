from __future__ import annotations

import numpy as np
import pytest

from pbsid.lti.dvar4varx import dvar4varx


def _make_data(*, n_samples: int = 240, seed: int = 55) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    u = rng.standard_normal((2, n_samples))
    y = np.zeros((1, n_samples), dtype=np.float64)

    a = np.array([[0.86]], dtype=np.float64)
    b = rng.standard_normal((1, 2)) * 0.2
    for k in range(1, n_samples):
        y[:, [k]] = a @ y[:, [k - 1]] + b @ u[:, [k - 1]] + 0.01 * rng.standard_normal((1, 1))

    return u, y


def test_dvar4varx_shapes_and_finite() -> None:
    u, y = _make_data()
    p = 10
    m = u.shape[0] + y.shape[0]

    varx = np.zeros((y.shape[0], p * m), dtype=np.float64)
    zps = np.eye(p * m, dtype=np.float64)

    p_cov, sigma = dvar4varx(u, y, p, varx, zps)

    assert sigma.shape == (1, 1)
    assert p_cov.shape == (zps.shape[1], zps.shape[1])
    assert np.all(np.isfinite(sigma))
    assert np.all(np.isfinite(p_cov))


def test_dvar4varx_accepts_none_u() -> None:
    _, y = _make_data(seed=56)
    p = 8
    m = y.shape[0]

    varx = np.zeros((y.shape[0], p * m), dtype=np.float64)
    zps = np.eye(p * m, dtype=np.float64)

    p_cov, sigma = dvar4varx(None, y, p, varx, zps)

    assert sigma.shape == (1, 1)
    assert p_cov.shape == (zps.shape[1], zps.shape[1])


def test_dvar4varx_handles_direct_term_columns() -> None:
    u, y = _make_data(seed=57)
    p = 10
    m = u.shape[0] + y.shape[0]

    # Include extra r columns so the implementation appends U to Z as in MATLAB.
    varx = np.zeros((y.shape[0], p * m + u.shape[0]), dtype=np.float64)
    zps = np.eye(p * m + u.shape[0], dtype=np.float64)

    p_cov, sigma = dvar4varx(u, y, p, varx, zps)

    assert sigma.shape == (1, 1)
    assert p_cov.shape == (zps.shape[1], zps.shape[1])


def test_dvar4varx_rejects_u_y_length_mismatch() -> None:
    u, y = _make_data(seed=58)
    with pytest.raises(ValueError, match="number of rows"):
        _ = dvar4varx(u[:, :-1], y, 10, np.zeros((1, 30)), np.eye(30))
