from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

type ArrayF64 = NDArray[np.float64]
type ArrayC128 = NDArray[np.complex128]


def _as_2d_float64(x: object, name: str) -> ArrayF64:
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr[np.newaxis, :]
    if arr.ndim != 2:
        raise ValueError(f"DVAR2FRD expects '{name}' to be a 2D matrix.")
    return arr


def _as_1d_float64(x: object, name: str) -> ArrayF64:
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim == 2 and 1 in arr.shape:
        arr = arr.reshape(-1)
    if arr.ndim != 1:
        raise ValueError(f"DVAR2FRD expects '{name}' to be a 1D frequency vector.")
    return arr


def dvar2frd(
    p_cov: ArrayLike,
    w: ArrayLike,
    h: float,
    p: int,
    varx: ArrayLike,
) -> tuple[ArrayC128, ArrayF64]:
    """Estimate frequency response and covariance from VARX covariance.

    MATLAB parity target: ``dvar2frd.m`` five-input mode
    ``dvar2frd(P, w, h, p, VARX)``.

    The seven/eight-input state-space forms are not yet ported.
    """
    if p < 1:
        raise ValueError("DVAR2FRD expects p to be a positive integer.")

    p_arr = _as_2d_float64(p_cov, "P")
    w_arr = _as_1d_float64(w, "w")
    varx_arr = _as_2d_float64(varx, "VARX")

    n_y = varx_arr.shape[0]
    m = int(np.floor(varx_arr.shape[1] / p))
    r = m - n_y
    if r < 0:
        raise ValueError("DVAR2FRD could not infer non-negative input dimension r from VARX.")

    has_d = (varx_arr.shape[1] / m) > p if m > 0 else False
    n_freq = w_arr.size

    g = np.zeros((n_y, r + n_y, n_freq), dtype=np.complex128)
    cov_g = np.zeros((n_y, r + n_y, n_freq, 2, 2), dtype=np.float64)

    n_param = p * n_y * (n_y + r) + (r * n_y if has_d else 0)
    if p_arr.shape[0] < n_param or p_arr.shape[1] < n_param:
        raise ValueError("DVAR2FRD expects P to cover all VARX parameters.")
    p_use = p_arr[:n_param, :n_param]

    for q in range(n_freq):
        g_q = np.zeros((n_y, r + n_y), dtype=np.complex128)

        for j in range(0, p + 1):
            if j == 0:
                if has_d:
                    g_q = np.hstack(
                        (varx_arr[:, p * m : p * m + r], np.eye(n_y, dtype=np.float64))
                    )
                else:
                    g_q = np.hstack(
                        (np.zeros((n_y, r), dtype=np.float64), np.eye(n_y, dtype=np.float64))
                    )
            else:
                phase = np.exp(-j * w_arr[q] * 1j * h)
                u_blk = phase * varx_arr[:, (p - j) * m : (p - j) * m + r]
                y_blk = -phase * varx_arr[:, (p - j) * m + r : (p - j) * m + r + n_y]
                g_q = g_q + np.hstack((u_blk, y_blk))

        gyy = g_q[:, r : r + n_y]
        g_q = np.hstack((np.linalg.pinv(gyy) @ g_q[:, :r], np.linalg.pinv(gyy)))
        g[:, :, q] = g_q

        t_left = np.block(
            [[np.eye(r, dtype=np.complex128), np.zeros((r, n_y), dtype=np.complex128)],
             [np.zeros((n_y, r), dtype=np.complex128), -g_q[:, r : r + n_y]]]
        )
        t = np.kron(t_left.T, g_q[:, r : r + n_y])

        grad_varx = np.zeros((n_y * (n_y + r), n_param), dtype=np.complex128)
        exp_terms = np.exp(-np.arange(p, 0, -1, dtype=np.float64) * w_arr[q] * 1j * h)

        for c in range(n_y):
            gradc = np.zeros((n_y,), dtype=np.float64)
            gradc[c] = 1.0
            for v in range(r + n_y):
                gradv = np.zeros((n_y * (n_y + r),), dtype=np.float64)
                gradv[v * n_y : (v + 1) * n_y] = gradc
                grad_varx[v * n_y + c, : p * n_y * (n_y + r)] = np.kron(exp_terms, gradv)

                if has_d:
                    if v < r:
                        gradd = np.zeros((n_y * r,), dtype=np.float64)
                        gradd[v * n_y : (v + 1) * n_y] = gradc
                        start = p * n_y * (n_y + r)
                        grad_varx[v * n_y + c, start : start + n_y * r] = gradd
                    else:
                        start = p * n_y * (n_y + r)
                        grad_varx[v * n_y + c, start : start + n_y * r] = 0.0

        grad_varx = t @ grad_varx

        for c in range(n_y):
            for v in range(r + n_y):
                row = grad_varx[v * n_y + c, :]
                rr = np.real(row)
                ii = np.imag(row)
                cov_g[c, v, q, 0, 0] = rr @ p_use @ rr.T
                cov_g[c, v, q, 0, 1] = rr @ p_use @ ii.T
                cov_g[c, v, q, 1, 0] = ii @ p_use @ rr.T
                cov_g[c, v, q, 1, 1] = ii @ p_use @ ii.T

    return g, cov_g
