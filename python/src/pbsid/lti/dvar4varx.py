from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

ArrayF64 = NDArray[np.float64]


def _as_2d_float64(x: object, name: str) -> ArrayF64:
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr[np.newaxis, :]
    if arr.ndim != 2:
        raise ValueError(f"DVAR4VARX expects '{name}' to be a 2D matrix.")
    return arr


def _ensure_row_major_samples(arr: ArrayF64) -> ArrayF64:
    if arr.shape[1] < arr.shape[0]:
        return arr.T.copy()
    return arr


def dvar4varx(
    u: ArrayLike | None,
    y: ArrayLike,
    p: int,
    varx: ArrayLike,
    zps: ArrayLike,
) -> tuple[ArrayF64, ArrayF64]:
    """Asymptotic variance of the VARX estimation.

    MATLAB parity target: ``dvar4varx.m``.
    """
    if p < 1:
        raise ValueError("Past window p must be a positive integer.")

    y_arr = _ensure_row_major_samples(_as_2d_float64(y, "y"))
    n_samples = y_arr.shape[1]
    l_out = y_arr.shape[0]

    if l_out == 0:
        raise ValueError("DVAR4VARX requires an output vector y.")

    if u is None:
        u_arr = np.zeros((0, n_samples), dtype=np.float64)
        r = 0
    else:
        u_arr = _ensure_row_major_samples(_as_2d_float64(u, "u"))
        r = u_arr.shape[0]
        if u_arr.shape[1] != n_samples:
            raise ValueError("The number of rows of vectors/matrices u and y must be the same.")

    if p >= n_samples:
        raise ValueError("Past window p must be smaller than the number of samples.")

    m = r + l_out
    z_all = np.vstack((u_arr, y_arr))
    z = np.zeros((p * m, n_samples - p), dtype=np.float64)
    for i in range(1, p + 1):
        row0 = (i - 1) * m
        row1 = i * m
        z[row0:row1, :] = z_all[:, i - 1 : n_samples + i - p - 1]

    y_reg = y_arr[:, p:n_samples]
    u_reg = u_arr[:, p:n_samples]

    varx_arr = _as_2d_float64(varx, "varx")
    if varx_arr.shape[1] > p * m:
        z = np.vstack((z, u_reg))

    e = y_reg - varx_arr @ z
    sigma = (e @ e.T) / float(e.shape[1])

    zps_arr = _as_2d_float64(zps, "zps")
    p_cov = np.zeros((l_out * zps_arr.shape[1], l_out * zps_arr.shape[1]), dtype=np.float64)
    for j in range(zps_arr.shape[0]):
        zj_col = zps_arr[j, :][:, np.newaxis]
        p_cov = p_cov + np.kron(zj_col, np.eye(l_out, dtype=np.float64)) @ sigma @ np.kron(
            zps_arr[j, :][np.newaxis, :], np.eye(l_out, dtype=np.float64)
        )

    return p_cov, sigma
