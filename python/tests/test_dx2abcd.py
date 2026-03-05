from __future__ import annotations

import numpy as np
import pytest

from pbsid.lti.dx2abcd import dx2abcd


def _make_data(
    *, n_samples: int = 260, seed: int = 31
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    a = np.array([[0.82]], dtype=np.float64)
    b = np.array([[0.35]], dtype=np.float64)
    c = np.array([[1.0]], dtype=np.float64)
    d = np.array([[0.1]], dtype=np.float64)

    u = rng.standard_normal((1, n_samples))
    x = np.zeros((1, n_samples - 10), dtype=np.float64)
    y = np.zeros((1, n_samples), dtype=np.float64)

    for k in range(1, n_samples):
        xk = a @ np.array([[x[0, k - 1 - 10] if k - 1 - 10 >= 0 else 0.0]]) + b * u[:, [k - 1]]
        y[:, [k]] = c @ xk + d * u[:, [k]]
        if k - 10 >= 0:
            x[:, [k - 10]] = xk

    return x, u, y


def test_dx2abcd_single_shapes_and_finite() -> None:
    x, u, y = _make_data()

    a, b, c, d = dx2abcd(x, u, y, f=5, p=10)

    assert a.shape == (1, 1)
    assert b.shape == (1, 1)
    assert c.shape == (1, 1)
    assert d.shape == (1, 1)
    assert np.all(np.isfinite(a))
    assert np.all(np.isfinite(b))
    assert np.all(np.isfinite(c))
    assert np.all(np.isfinite(d))


def test_dx2abcd_batch_runs() -> None:
    x1, u1, y1 = _make_data(seed=32)
    x2, u2, y2 = _make_data(seed=33)

    a, b, c, d = dx2abcd([x1, x2], [u1, u2], [y1, y2], f=5, p=10)

    assert a.shape == (1, 1)
    assert b.shape == (1, 1)
    assert c.shape == (1, 1)
    assert d.shape == (1, 1)


def test_dx2abcd_rejects_f_greater_than_p() -> None:
    x, u, y = _make_data(seed=34)
    with pytest.raises(ValueError, match="f <= p"):
        _ = dx2abcd(x, u, y, f=11, p=10)
