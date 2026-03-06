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


def _fill_cov_from_gradient(
    cov_g: ArrayF64, row: ArrayC128, p_use: ArrayF64, c: int, v: int, q: int
) -> None:
    rr = np.real(row)
    ii = np.imag(row)
    cov_g[c, v, q, 0, 0] = rr @ p_use @ rr.T
    cov_g[c, v, q, 0, 1] = rr @ p_use @ ii.T
    cov_g[c, v, q, 1, 0] = ii @ p_use @ rr.T
    cov_g[c, v, q, 1, 1] = ii @ p_use @ ii.T


def _dvar2frd_varx(
    p_arr: ArrayF64,
    w_arr: ArrayF64,
    h: float,
    p: int,
    varx_arr: ArrayF64,
) -> tuple[ArrayC128, ArrayF64]:
    if p < 1:
        raise ValueError("DVAR2FRD expects p to be a positive integer.")

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
                    start = p * n_y * (n_y + r)
                    if v < r:
                        gradd = np.zeros((n_y * r,), dtype=np.float64)
                        gradd[v * n_y : (v + 1) * n_y] = gradc
                        grad_varx[v * n_y + c, start : start + n_y * r] = gradd
                    else:
                        grad_varx[v * n_y + c, start : start + n_y * r] = 0.0

        grad_varx = t @ grad_varx

        for c in range(n_y):
            for v in range(r + n_y):
                _fill_cov_from_gradient(cov_g, grad_varx[v * n_y + c, :], p_use, c, v, q)

    return g, cov_g


def _build_dar(a_inv: ArrayC128, c_arr: ArrayF64, bk: ArrayF64) -> ArrayC128:
    left = np.asarray(c_arr @ a_inv, dtype=np.complex128)
    right = np.asarray(a_inv @ bk, dtype=np.complex128)
    d_blocks = np.einsum("cb,jv->jbcv", left, right, optimize=True)
    reshaped = d_blocks.reshape(a_inv.shape[0] * a_inv.shape[0], c_arr.shape[0], bk.shape[1])
    return np.asarray(reshaped, dtype=np.complex128)


def _dvar2frd_abck(
    p_arr: ArrayF64,
    w_arr: ArrayF64,
    h: float,
    a_arr: ArrayF64,
    b_arr: ArrayF64,
    c_arr: ArrayF64,
    k_arr: ArrayF64,
) -> tuple[ArrayC128, ArrayF64]:
    n_y = c_arr.shape[0]
    n = c_arr.shape[1]
    r = b_arr.shape[1]
    bk = np.hstack((b_arr, k_arr))
    d_mat = np.hstack((np.zeros((n_y, r), dtype=np.float64), np.eye(n_y, dtype=np.float64)))

    n_param = n * n + (r + n_y) * n + n * n_y
    if p_arr.shape[0] < n_param or p_arr.shape[1] < n_param:
        raise ValueError("DVAR2FRD expects P to cover all ABCK parameters.")
    p_use = p_arr[:n_param, :n_param]

    s = np.exp(w_arr * 1j * h)
    n_freq = s.size
    g = np.zeros((n_y, r + n_y, n_freq), dtype=np.complex128)
    cov_g = np.zeros((n_y, r + n_y, n_freq, 2, 2), dtype=np.float64)
    n2 = n * n

    for q in range(n_freq):
        a_inv = np.linalg.inv(s[q] * np.eye(n, dtype=np.complex128) - a_arr)
        d_cr = a_inv @ bk
        d_br = (c_arr @ a_inv).conj().T
        d_ar = _build_dar(a_inv, c_arr, bk)

        for c in range(n_y):
            for v in range(r + n_y):
                grad = np.conj(np.concatenate((d_ar[:, c, v], d_br[:, c], d_cr[:, v])))
                idx_a = np.arange(0, n2)
                idx_b = np.arange(n2 + v * n, n2 + (v + 1) * n)
                idx_c = n2 + (r + n_y) * n + c + np.arange(n) * n_y
                idx = np.concatenate((idx_a, idx_b, idx_c))
                p_sub = p_use[np.ix_(idx, idx)]
                _fill_cov_from_gradient(cov_g, grad, p_sub, c, v, q)
                g[c, v, q] = d_mat[c, v] + c_arr[c, :] @ a_inv @ bk[:, v]

    return g, cov_g


def _dvar2frd_abcdk(
    p_arr: ArrayF64,
    w_arr: ArrayF64,
    h: float,
    a_arr: ArrayF64,
    b_arr: ArrayF64,
    c_arr: ArrayF64,
    d_arr: ArrayF64,
    k_arr: ArrayF64,
) -> tuple[ArrayC128, ArrayF64]:
    n_y = c_arr.shape[0]
    n = c_arr.shape[1]
    r = b_arr.shape[1]
    bk = np.hstack((b_arr, k_arr))
    d_mat = np.hstack((d_arr, np.eye(n_y, dtype=np.float64)))

    n_param = n * n + (r + n_y) * n + n * n_y + r * n_y
    if p_arr.shape[0] < n_param or p_arr.shape[1] < n_param:
        raise ValueError("DVAR2FRD expects P to cover all ABCDK parameters.")
    p_use = p_arr[:n_param, :n_param]

    s = np.exp(w_arr * 1j * h)
    n_freq = s.size
    g = np.zeros((n_y, r + n_y, n_freq), dtype=np.complex128)
    cov_g = np.zeros((n_y, r + n_y, n_freq, 2, 2), dtype=np.float64)
    n2 = n * n

    for q in range(n_freq):
        a_inv = np.linalg.inv(s[q] * np.eye(n, dtype=np.complex128) - a_arr)
        d_cr = a_inv @ bk
        d_br = (c_arr @ a_inv).conj().T
        d_ar = _build_dar(a_inv, c_arr, bk)

        for c in range(n_y):
            for v in range(r + n_y):
                idx_a = np.arange(0, n2)
                idx_b = np.arange(n2 + v * n, n2 + (v + 1) * n)
                idx_c = n2 + (r + n_y) * n + c + np.arange(n) * n_y
                base_idx = np.concatenate((idx_a, idx_b, idx_c))

                if v < r:
                    idx_d = n2 + (r + n_y) * n + n * n_y + v * n_y + c
                    idx = np.concatenate((base_idx, np.array([idx_d], dtype=np.int64)))
                    grad = np.conj(
                        np.concatenate(
                            (d_ar[:, c, v], d_br[:, c], d_cr[:, v], np.array([1.0 + 0.0j]))
                        )
                    )
                    p_sub = p_use[np.ix_(idx, idx)]
                else:
                    grad_base = np.conj(np.concatenate((d_ar[:, c, v], d_br[:, c], d_cr[:, v])))
                    grad = np.concatenate((grad_base, np.array([0.0 + 0.0j])))
                    p_sub = np.zeros((base_idx.size + 1, base_idx.size + 1), dtype=np.float64)
                    p_sub[:-1, :-1] = p_use[np.ix_(base_idx, base_idx)]

                _fill_cov_from_gradient(cov_g, grad, p_sub, c, v, q)
                g[c, v, q] = d_mat[c, v] + c_arr[c, :] @ a_inv @ bk[:, v]

    return g, cov_g


def dvar2frd(
    p_cov: ArrayLike,
    w: ArrayLike,
    h: float,
    *args: ArrayLike,
) -> tuple[ArrayC128, ArrayF64]:
    """Estimate frequency response and covariance in the frequency domain.

    MATLAB parity target: ``dvar2frd.m`` supporting:
    - ``dvar2frd(P, w, h, p, VARX)``
    - ``dvar2frd(P, w, h, A, B, C, K)``
    - ``dvar2frd(P, w, h, A, B, C, D, K)``
    """
    p_arr = _as_2d_float64(p_cov, "P")
    w_arr = _as_1d_float64(w, "w")
    if len(args) == 2:
        p = int(np.asarray(args[0]).item())
        varx_arr = _as_2d_float64(args[1], "VARX")
        return _dvar2frd_varx(p_arr, w_arr, h, p, varx_arr)

    if len(args) == 4:
        a_arr = _as_2d_float64(args[0], "A")
        b_arr = _as_2d_float64(args[1], "B")
        c_arr = _as_2d_float64(args[2], "C")
        k_arr = _as_2d_float64(args[3], "K")
        return _dvar2frd_abck(p_arr, w_arr, h, a_arr, b_arr, c_arr, k_arr)

    if len(args) == 5:
        a_arr = _as_2d_float64(args[0], "A")
        b_arr = _as_2d_float64(args[1], "B")
        c_arr = _as_2d_float64(args[2], "C")
        d_arr = _as_2d_float64(args[3], "D")
        k_arr = _as_2d_float64(args[4], "K")
        return _dvar2frd_abcdk(p_arr, w_arr, h, a_arr, b_arr, c_arr, d_arr, k_arr)

    raise ValueError("DVAR2FRD requires five, seven or eight input arguments.")
