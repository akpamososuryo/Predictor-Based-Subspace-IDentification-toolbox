from __future__ import annotations

import numpy as np
import pytest

from pbsid.lti.dordvarmax import dordvarmax


def _make_u_y(
    *, n_samples: int = 260, r: int = 2, l_out: int = 1, seed: int = 111
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    u = rng.standard_normal((r, n_samples))

    y = np.zeros((l_out, n_samples), dtype=np.float64)
    a = np.array([[0.86]], dtype=np.float64)
    b = rng.standard_normal((l_out, r)) * 0.25
    for k in range(1, n_samples):
        y[:, k] = (a @ y[:, [k - 1]]).ravel() + (b @ u[:, [k - 1]]).ravel()
    return u, y


def test_dordvarmax_single_shapes_and_finite() -> None:
    u, y = _make_u_y(seed=112)
    s, x, varmax, umat = dordvarmax(u, y, f=5, p=10, method="gradient")
    assert not isinstance(x, list)

    assert s.ndim == 1
    assert x.ndim == 2
    assert varmax.ndim == 2
    assert umat.ndim == 2
    assert x.shape[1] == y.shape[1] - 10
    assert np.all(np.isfinite(s))
    assert np.all(np.isfinite(x))


def test_dordvarmax_batch_returns_list_x() -> None:
    u1, y1 = _make_u_y(seed=113)
    u2, y2 = _make_u_y(seed=114)

    s, x, varmax, umat = dordvarmax([u1, u2], [y1, y2], f=5, p=10, method="els")

    assert s.ndim == 1
    assert isinstance(x, list)
    assert len(x) == 2
    assert x[0].shape[1] == y1.shape[1] - 10
    assert x[1].shape[1] == y2.shape[1] - 10
    assert varmax.ndim == 2
    assert umat.ndim == 2


def test_dordvarmax_no_d_changes_varmax_width() -> None:
    u, y = _make_u_y(seed=115)
    _, _, varmax_with_d, _ = dordvarmax(u, y, f=4, p=8, no_d=0)
    _, _, varmax_without_d, _ = dordvarmax(u, y, f=4, p=8, no_d=1)

    r = u.shape[0]
    l_out = y.shape[0]
    m = r + 2 * l_out

    assert varmax_with_d.shape[1] == 8 * m + r
    assert varmax_without_d.shape[1] == 8 * m


def test_dordvarmax_rejects_non_none_regularization() -> None:
    u, y = _make_u_y(seed=116)
    with pytest.raises(NotImplementedError, match="reg='none'"):
        _ = dordvarmax(u, y, f=5, p=10, reg="tikh")


def test_dordvarmax_rejects_unknown_method() -> None:
    u, y = _make_u_y(seed=117)
    with pytest.raises(ValueError, match="method"):
        _ = dordvarmax(u, y, f=5, p=10, method="foobar")
