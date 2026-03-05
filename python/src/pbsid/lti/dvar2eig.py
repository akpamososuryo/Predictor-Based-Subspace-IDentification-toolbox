from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import linear_sum_assignment

type ArrayF64 = NDArray[np.float64]
type ArrayC128 = NDArray[np.complex128]


def _as_2d_float64(x: object, name: str) -> ArrayF64:
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr[np.newaxis, :]
    if arr.ndim != 2:
        raise ValueError(f"DVAR2EIG expects '{name}' to be a 2D matrix.")
    return arr


def _eig_stacked(vec_a: ArrayF64, n: int) -> ArrayF64:
    a = vec_a.reshape(n, n)
    e = np.linalg.eigvals(a)
    stacked = np.empty(2 * n, dtype=np.float64)
    stacked[0::2] = np.real(e)
    stacked[1::2] = np.imag(e)
    return stacked


def _match_eigen_order(reference: ArrayC128, candidate: ArrayC128) -> ArrayC128:
    """Reorder candidate eigenvalues to best match a reference ordering."""
    if reference.size != candidate.size:
        raise ValueError("Reference and candidate eigenvalue vectors must have equal length.")
    cost = np.abs(reference[:, np.newaxis] - candidate[np.newaxis, :])
    row_ind, col_ind = linear_sum_assignment(cost)
    matched = np.empty_like(candidate)
    matched[row_ind] = candidate[col_ind]
    return matched


def _central_diff_jacobian(vec_a: ArrayF64, n: int) -> ArrayF64:
    a0 = vec_a.reshape(n, n)
    e_ref = np.asarray(np.linalg.eigvals(a0), dtype=np.complex128)
    y0 = np.empty(2 * n, dtype=np.float64)
    y0[0::2] = np.real(e_ref)
    y0[1::2] = np.imag(e_ref)
    m = y0.size
    d = vec_a.size
    j = np.empty((m, d), dtype=np.float64)

    eps = np.sqrt(np.finfo(np.float64).eps)
    for k in range(d):
        h = eps * max(1.0, abs(vec_a[k]))
        vp = vec_a.copy()
        vm = vec_a.copy()
        vp[k] += h
        vm[k] -= h
        e_p = _match_eigen_order(
            e_ref, np.asarray(np.linalg.eigvals(vp.reshape(n, n)), dtype=np.complex128)
        )
        e_m = _match_eigen_order(
            e_ref, np.asarray(np.linalg.eigvals(vm.reshape(n, n)), dtype=np.complex128)
        )
        y_p = np.empty(2 * n, dtype=np.float64)
        y_m = np.empty(2 * n, dtype=np.float64)
        y_p[0::2] = np.real(e_p)
        y_p[1::2] = np.imag(e_p)
        y_m[0::2] = np.real(e_m)
        y_m[1::2] = np.imag(e_m)
        j[:, k] = (y_p - y_m) / (2.0 * h)

    return j


def dvar2eig(p: ArrayLike, a: ArrayLike) -> tuple[ArrayC128, ArrayF64]:
    """Estimate eigenvalue covariance from state matrix covariance.

    MATLAB parity target: ``dvar2eig.m``.
    """
    a_arr = _as_2d_float64(a, "A")
    if a_arr.shape[0] != a_arr.shape[1]:
        raise ValueError("DVAR2EIG expects A to be square.")

    n = a_arr.shape[0]
    p_arr = _as_2d_float64(p, "P")
    needed = n * n
    if p_arr.shape[0] < needed or p_arr.shape[1] < needed:
        raise ValueError("DVAR2EIG expects P dimensions at least n^2 by n^2.")

    p_use = p_arr[:needed, :needed]
    vec_a = a_arr.reshape(needed)
    jac = _central_diff_jacobian(vec_a, n)
    cov_e = jac @ p_use @ jac.T
    e = np.linalg.eigvals(a_arr)
    return e.astype(np.complex128, copy=False), cov_e
