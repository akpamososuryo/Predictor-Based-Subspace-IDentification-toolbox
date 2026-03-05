from __future__ import annotations

from typing import cast

import numpy as np
import pytest

from pbsid.lti.dvar4abcdk import dvar4abcdk


def _make_problem(
    *, n_samples: int = 240, p: int = 10, seed: int = 71
) -> dict[str, np.ndarray | int]:
    rng = np.random.default_rng(seed)

    l_out = 1
    r = 1
    n = 1

    y = rng.standard_normal((l_out, n_samples))
    u = rng.standard_normal((r, n_samples))
    x = rng.standard_normal((n, n_samples - p))

    a = np.array([[0.78]], dtype=np.float64)
    b = np.array([[0.21]], dtype=np.float64)
    c = np.array([[0.95]], dtype=np.float64)
    d = np.array([[0.05]], dtype=np.float64)
    k = np.array([[0.12]], dtype=np.float64)

    m = r + l_out
    z_cols = p * m
    u_proj = rng.standard_normal((n, n_samples - p))
    zps = rng.standard_normal((n_samples - p, z_cols))

    return {
        "x": x,
        "u": u,
        "y": y,
        "f": 5,
        "p": p,
        "a": a,
        "b": b,
        "c": c,
        "d": d,
        "k": k,
        "u_proj": u_proj,
        "zps": zps,
    }


def test_dvar4abcdk_shapes_and_finite() -> None:
    d = _make_problem()

    p_cov, sigma = cast(
        tuple[np.ndarray, np.ndarray],
        dvar4abcdk(
            d["x"],
            d["u"],
            d["y"],
            int(d["f"]),
            int(d["p"]),
            d["a"],
            d["b"],
            d["c"],
            d["d"],
            d["k"],
            d["u_proj"],
            d["zps"],
        ),
    )

    assert p_cov.ndim == 2
    assert sigma.shape == (1, 1)
    assert np.all(np.isfinite(p_cov))
    assert np.all(np.isfinite(sigma))


def test_dvar4abcdk_return_deltas() -> None:
    d = _make_problem(seed=72)

    p_cov, sigma, da, db, dc, dd, dk = cast(
        tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray],
        dvar4abcdk(
            d["x"],
            d["u"],
            d["y"],
            int(d["f"]),
            int(d["p"]),
            d["a"],
            d["b"],
            d["c"],
            d["d"],
            d["k"],
            d["u_proj"],
            d["zps"],
            return_deltas=True,
        ),
    )

    assert sigma.shape == (1, 1)
    assert da.shape == (1, 1)
    assert db.shape == (1, 1)
    assert dc.shape == (1, 1)
    assert dd.shape == (1, 1)
    assert dk.shape == (1, 1)
    assert np.all(np.isfinite(p_cov))


def test_dvar4abcdk_rejects_f_greater_than_p() -> None:
    d = _make_problem(seed=73)
    with pytest.raises(ValueError, match="f <= p"):
        _ = dvar4abcdk(
            d["x"],
            d["u"],
            d["y"],
            int(d["p"]) + 1,
            int(d["p"]),
            d["a"],
            d["b"],
            d["c"],
            d["d"],
            d["k"],
            d["u_proj"],
            d["zps"],
        )
