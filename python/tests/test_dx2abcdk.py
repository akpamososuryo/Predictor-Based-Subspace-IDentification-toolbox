from __future__ import annotations

import numpy as np
import pytest

from pbsid.lti.dx2abcdk import dx2abcdk


def _make_consistent_dataset(
    *,
    n: int = 2,
    r: int = 1,
    L: int = 1,
    n_samples: int = 220,
    p: int = 10,
    seed: int = 123,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, int]:
    rng = np.random.default_rng(seed)

    a = np.array([[0.72, 0.10], [-0.08, 0.64]], dtype=np.float64)
    b = rng.standard_normal((n, r)) * 0.2
    c = rng.standard_normal((L, n)) * 0.4
    d = rng.standard_normal((L, r)) * 0.05
    k = rng.standard_normal((n, L)) * 0.08

    u = rng.standard_normal((r, n_samples))
    e = 0.02 * rng.standard_normal((L, n_samples))
    x = np.zeros((n, n_samples), dtype=np.float64)
    y = np.zeros((L, n_samples), dtype=np.float64)

    for t in range(n_samples - 1):
        y[:, t] = c @ x[:, t] + d @ u[:, t] + e[:, t]
        x[:, t + 1] = a @ x[:, t] + b @ u[:, t] + k @ e[:, t]
    y[:, -1] = c @ x[:, -1] + d @ u[:, -1] + e[:, -1]

    # Match MATLAB flow: x comes from dmodx with N-p columns.
    x_id = x[:, p:]
    return x_id, u, y, 5, p


def _make_unstable_dataset(
    *,
    n: int = 2,
    r: int = 1,
    l_out: int = 1,
    n_samples: int = 260,
    p: int = 10,
    seed: int = 321,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, int, int]:
    rng = np.random.default_rng(seed)

    a = np.array([[1.15, 0.02], [0.00, 1.04]], dtype=np.float64)
    b = rng.standard_normal((n, r)) * 0.2
    c = rng.standard_normal((l_out, n)) * 0.5
    d = rng.standard_normal((l_out, r)) * 0.03
    k = rng.standard_normal((n, l_out)) * 0.05

    u = rng.standard_normal((r, n_samples))
    e = 0.01 * rng.standard_normal((l_out, n_samples))
    x = np.zeros((n, n_samples), dtype=np.float64)
    y = np.zeros((l_out, n_samples), dtype=np.float64)

    for t in range(n_samples - 1):
        y[:, t] = c @ x[:, t] + d @ u[:, t] + e[:, t]
        x[:, t + 1] = a @ x[:, t] + b @ u[:, t] + k @ e[:, t]
    y[:, -1] = c @ x[:, -1] + d @ u[:, -1] + e[:, -1]

    x_id = x[:, p:]
    return x_id, u, y, 5, p


def test_dx2abcdk_baseline_shapes_and_finite() -> None:
    x, u, y, f, p = _make_consistent_dataset()

    # Pass column-oriented y/u to exercise transpose handling.
    a, b, c, d = dx2abcdk(x, u.T, y.T, f, p)

    assert a.shape == (2, 2)
    assert b.shape == (2, 1)
    assert c.shape == (1, 2)
    assert d.shape == (1, 1)

    assert np.all(np.isfinite(a))
    assert np.all(np.isfinite(b))
    assert np.all(np.isfinite(c))
    assert np.all(np.isfinite(d))


def test_dx2abcdk_return_k_shapes_and_finite() -> None:
    x, u, y, f, p = _make_consistent_dataset(seed=456)
    a, b, c, d, k = dx2abcdk(x, u, y, f, p, return_k=True)

    assert a.shape == (2, 2)
    assert b.shape == (2, 1)
    assert c.shape == (1, 2)
    assert d.shape == (1, 1)
    assert k.shape == (2, 1)

    assert np.all(np.isfinite(k))


def test_dx2abcdk_rejects_invalid_windows() -> None:
    x, u, y, _, p = _make_consistent_dataset()
    with pytest.raises(ValueError, match="f <= p"):
        _ = dx2abcdk(x, u, y, f=p + 1, p=p)


def test_dx2abcdk_stable1_enforces_stability() -> None:
    x, u, y, f, p = _make_unstable_dataset()
    a, b, c, d = dx2abcdk(x, u, y, f, p, c="stable1")

    assert a.shape == (2, 2)
    assert b.shape == (2, 1)
    assert c.shape == (1, 2)
    assert d.shape == (1, 1)
    assert np.max(np.abs(np.linalg.eigvals(a))) < 1.0


def test_dx2abcdk_stable2_enforces_stability() -> None:
    x, u, y, f, p = _make_unstable_dataset(seed=654)
    a0, _, _, _ = dx2abcdk(x, u, y, f, p, c="none")
    a, b, c, d = dx2abcdk(x, u, y, f, p, c="stable2")

    assert a.shape == (2, 2)
    assert b.shape == (2, 1)
    assert c.shape == (1, 2)
    assert d.shape == (1, 1)

    rho0 = float(np.max(np.abs(np.linalg.eigvals(a0))))
    rho = float(np.max(np.abs(np.linalg.eigvals(a))))
    assert np.isfinite(rho)
    assert rho <= rho0 + 1e-12


def test_dx2abcdk_batch_inputs_run() -> None:
    x1, u1, y1, f, p = _make_consistent_dataset(seed=111)
    x2, u2, y2, _, _ = _make_consistent_dataset(seed=222)

    a, b, c, d, k = dx2abcdk([x1, x2], [u1, u2], [y1, y2], f, p, return_k=True)

    assert a.shape == (2, 2)
    assert b.shape == (2, 1)
    assert c.shape == (1, 2)
    assert d.shape == (1, 1)
    assert k.shape == (2, 1)

    assert np.all(np.isfinite(a))
    assert np.all(np.isfinite(b))
    assert np.all(np.isfinite(c))
    assert np.all(np.isfinite(d))
    assert np.all(np.isfinite(k))
