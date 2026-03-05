from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .dvar4abck import _as_2d_float64, _ensure_row_major_samples, _obs_cont_sum

ArrayF64 = NDArray[np.float64]


def dvar4abcdk(
    x: ArrayLike,
    u: ArrayLike | None,
    y: ArrayLike,
    f: int,
    p: int,
    a: ArrayLike,
    b: ArrayLike,
    c: ArrayLike,
    d: ArrayLike,
    k: ArrayLike,
    u_proj: ArrayLike,
    zps: ArrayLike,
    *,
    return_deltas: bool = False,
) -> (
    tuple[ArrayF64, ArrayF64]
    | tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64]
):
    """Asymptotic variance of PBSIDopt (VARX-only) ABCDK estimation.

    MATLAB parity target: ``dvar4abcdk.m``.
    """
    if f > p:
        raise ValueError("Future window size f must equal or smaller then past window p. (f <= p)")

    y_arr = _ensure_row_major_samples(_as_2d_float64(y, "y"))
    x_arr = _ensure_row_major_samples(_as_2d_float64(x, "x"))
    n_samples = y_arr.shape[1]
    l_out = y_arr.shape[0]
    n = x_arr.shape[0]

    if l_out == 0:
        raise ValueError("DVAR4ABCDK requires an output vector y.")

    if u is None:
        u_arr = np.zeros((0, n_samples), dtype=np.float64)
        r = 0
    else:
        u_arr = _ensure_row_major_samples(_as_2d_float64(u, "u"))
        r = u_arr.shape[0]
        if u_arr.shape[1] != n_samples:
            raise ValueError("The number of rows of vectors/matrices u and y must be the same.")

    m = r + l_out
    z_all = np.vstack((u_arr, y_arr))
    z = np.zeros((p * m, n_samples - p), dtype=np.float64)
    for i in range(1, p + 1):
        row0 = (i - 1) * m
        row1 = i * m
        z[row0:row1, :] = z_all[:, i - 1 : n_samples + i - p - 1]

    a_arr = _as_2d_float64(a, "a")
    _as_2d_float64(b, "b")
    c_arr = _as_2d_float64(c, "c")
    d_arr = _as_2d_float64(d, "d")
    k_arr = _as_2d_float64(k, "k")
    u_proj_arr = _as_2d_float64(u_proj, "u_proj")
    zps_arr = _as_2d_float64(zps, "zps")

    u_proj_arr = u_proj_arr[:n, :]
    if (zps_arr.shape[1] / m) > p:
        zps_arr = zps_arr[:, : p * m]

    u_trim = u_arr[:, p : p + x_arr.shape[1]]
    y_trim = y_arr[:, p : p + x_arr.shape[1]]

    e = y_trim - c_arr @ x_arr - d_arr @ u_trim
    sigma = (e @ e.T) / float(max(e.shape))

    ll = np.asarray(
        np.linalg.pinv(np.vstack((x_arr[:, :-1], u_trim[:, :-1], e[:, :-1]))),
        dtype=np.float64,
    )
    ll2 = np.asarray(np.linalg.pinv(np.vstack((x_arr, u_trim))), dtype=np.float64)

    term1 = _obs_cont_sum(
        zps_arr,
        np.eye(n_samples - p, dtype=np.float64),
        l_out,
        r,
        f,
        p,
        ll,
        z[:, 1:],
        u_proj_arr,
    )
    term2 = _obs_cont_sum(
        zps_arr,
        np.eye(n_samples - p, dtype=np.float64),
        l_out,
        r,
        f,
        p,
        ll,
        z[:, :-1],
        a_arr @ u_proj_arr,
    )
    term3 = _obs_cont_sum(
        zps_arr,
        np.eye(n_samples - p, dtype=np.float64),
        l_out,
        r,
        f,
        p,
        ll2,
        z,
        -c_arr @ u_proj_arr,
    )

    alpha1 = term1 - term2
    alpha2 = term3

    beta1 = -np.kron(ll.T @ z[:, :-1].T @ zps_arr.T, k_arr)
    beta2 = -np.kron(ll2.T @ z.T @ zps_arr.T, np.eye(l_out, dtype=np.float64))

    g = np.vstack((alpha1 + beta1, alpha2 + beta2))
    if l_out == 1:
        p_cov = sigma * (g @ g.T)
    else:
        p_cov = g @ np.kron(np.eye(n_samples - p, dtype=np.float64), sigma) @ g.T

    if not return_deltas:
        return p_cov, sigma

    dtheta = g @ e.reshape(-1, order="F")

    n_a = n * n
    n_b = n * r
    n_k = n * l_out
    n_c = l_out * n
    n_d = l_out * r

    i0 = 0
    i1 = n_a
    da = dtheta[i0:i1].reshape((n, n), order="F")
    i0 = i1
    i1 = i0 + n_b
    db = dtheta[i0:i1].reshape((n, r), order="F")
    i0 = i1
    i1 = i0 + n_k
    dk = dtheta[i0:i1].reshape((n, l_out), order="F")
    i0 = i1
    i1 = i0 + n_c
    dc = dtheta[i0:i1].reshape((l_out, n), order="F")
    i0 = i1
    i1 = i0 + n_d
    dd = dtheta[i0:i1].reshape((l_out, r), order="F")

    return p_cov, sigma, da, db, dc, dd, dk
