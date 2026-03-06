from __future__ import annotations

import numpy as np
import pytest

from pbsid.lti.dordvarx import dordvarx


def _make_u_y(
    *, n_samples: int = 260, r: int = 2, l_out: int = 1, seed: int = 17
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    u = rng.standard_normal((r, n_samples))

    y = np.zeros((l_out, n_samples), dtype=np.float64)
    a = np.array([[0.85]], dtype=np.float64)
    b = rng.standard_normal((l_out, r)) * 0.3
    for k in range(1, n_samples):
        y[:, k] = (a @ y[:, [k - 1]]).ravel() + (b @ u[:, [k - 1]]).ravel()
    return u, y


def test_dordvarx_single_shapes_and_finite() -> None:
    u, y = _make_u_y()
    s, x, varx, umat, zps = dordvarx(u, y, f=5, p=10)
    assert not isinstance(x, list)

    assert s.ndim == 1
    assert x.ndim == 2
    assert varx.ndim == 2
    assert umat.ndim == 2
    assert zps.ndim == 2

    assert x.shape[1] == y.shape[1] - 10
    assert np.all(np.isfinite(s))
    assert np.all(np.isfinite(x))
    assert np.all(np.isfinite(varx))


def test_dordvarx_no_d_changes_varx_width() -> None:
    u, y = _make_u_y(seed=19)

    _, _, varx_with_d, _, _ = dordvarx(u, y, f=4, p=8, no_d=0)
    _, _, varx_without_d, _, _ = dordvarx(u, y, f=4, p=8, no_d=1)

    r = u.shape[0]
    l_out = y.shape[0]
    m = r + l_out

    assert varx_with_d.shape[1] == 8 * m + r
    assert varx_without_d.shape[1] == 8 * m


def test_dordvarx_batch_returns_list_x() -> None:
    u1, y1 = _make_u_y(seed=21)
    u2, y2 = _make_u_y(seed=22)

    s, x, varx, umat, zps = dordvarx([u1, u2], [y1, y2], f=5, p=10)

    assert s.ndim == 1
    assert isinstance(x, list)
    assert len(x) == 2
    assert x[0].shape[1] == y1.shape[1] - 10
    assert x[1].shape[1] == y2.shape[1] - 10
    assert varx.ndim == 2
    assert umat.ndim == 2
    assert zps.ndim == 2


def test_dordvarx_weight_mode_runs() -> None:
    u, y = _make_u_y(seed=23)
    s, x, varx, umat, zps = dordvarx(u, y, f=5, p=10, weight=1)
    assert not isinstance(x, list)

    assert s.ndim == 1
    assert x.ndim == 2
    assert varx.ndim == 2
    assert umat.ndim == 2
    assert zps.ndim == 2


def test_dordvarx_tikh_gcv_runs() -> None:
    u, y = _make_u_y(seed=24)
    s, x, varx, umat, zps = dordvarx(u, y, f=5, p=10, reg="tikh", opt="gcv")
    assert not isinstance(x, list)
    assert s.ndim == 1
    assert x.ndim == 2
    assert varx.ndim == 2
    assert umat.ndim == 2
    assert zps.ndim == 2
    assert np.all(np.isfinite(varx))


def test_dordvarx_rejects_unsupported_regularization() -> None:
    u, y = _make_u_y(seed=124)
    with pytest.raises(NotImplementedError, match="reg='none' and reg='tikh'"):
        _ = dordvarx(u, y, f=5, p=10, reg="tsvd")


def test_dordvarx_rejects_f_greater_than_p() -> None:
    u, y = _make_u_y(seed=25)
    with pytest.raises(ValueError, match="f <= p"):
        _ = dordvarx(u, y, f=12, p=10)
