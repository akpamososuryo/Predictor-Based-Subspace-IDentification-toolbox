from __future__ import annotations

import numpy as np
import pytest

from pbsid.lti.dordfir import dordfir


def _make_io(
    *, n_samples: int = 240, r: int = 2, l_out: int = 1, seed: int = 7
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    u = rng.standard_normal((r, n_samples))

    b = rng.standard_normal((l_out, r)) * 0.4
    y = np.zeros((l_out, n_samples), dtype=np.float64)
    for k in range(1, n_samples):
        y[:, k] = 0.8 * y[:, k - 1] + b @ u[:, k - 1] + 0.01 * rng.standard_normal(l_out)
    return u, y


def test_dordfir_single_shapes_and_finite() -> None:
    u, y = _make_io()
    f = 5
    p = 10

    s, x, fir = dordfir(u, y, f, p)

    assert s.ndim == 1
    assert x.ndim == 2
    assert fir.shape == (1, p * 2 + 2)
    assert x.shape[1] == y.shape[1] - p
    assert np.all(np.isfinite(s))
    assert np.all(np.isfinite(x))
    assert np.all(np.isfinite(fir))


def test_dordfir_no_d_option_changes_fir_width() -> None:
    u, y = _make_io(seed=9)
    f = 4
    p = 8

    _, _, fir_with_d = dordfir(u, y, f, p, no_d=0)
    _, _, fir_without_d = dordfir(u, y, f, p, no_d=1)

    assert fir_with_d.shape[1] == p * 2 + 2
    assert fir_without_d.shape[1] == p * 2


def test_dordfir_batch_returns_list_x() -> None:
    u1, y1 = _make_io(seed=11)
    u2, y2 = _make_io(seed=12)
    f = 5
    p = 10

    s, x, fir = dordfir([u1, u2], [y1, y2], f, p)

    assert s.ndim == 1
    assert isinstance(x, list)
    assert len(x) == 2
    assert x[0].shape[1] == y1.shape[1] - p
    assert x[1].shape[1] == y2.shape[1] - p
    assert fir.ndim == 2


def test_dordfir_rejects_unsupported_regularization() -> None:
    u, y = _make_io(seed=13)
    with pytest.raises(NotImplementedError, match="reg='none'"):
        _ = dordfir(u, y, f=5, p=10, reg="tikh")
