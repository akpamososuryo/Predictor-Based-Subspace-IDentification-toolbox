from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray

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
    # MATLAB uses column-major A(:) and reshape(..., n, n).
    a = vec_a.reshape((n, n), order="F")
    e = np.linalg.eigvals(a)
    stacked = np.empty(2 * n, dtype=np.float64)
    stacked[0::2] = np.real(e)
    stacked[1::2] = np.imag(e)
    return stacked


def _vec2mat(vec: ArrayF64, n: int, m: int) -> ArrayF64:
    idx = np.add.outer(np.arange(n, dtype=np.int64), np.arange(m, dtype=np.int64))
    return vec[idx]


def _rombextrap(
    step_ratio: float, der_init: ArrayF64, rombexpon: tuple[int, int]
) -> tuple[ArrayF64, ArrayF64]:
    srinv = 1.0 / step_ratio
    nexpon = len(rombexpon)

    rmat = np.ones((nexpon + 2, nexpon + 1), dtype=np.float64)
    rmat[1, 1:3] = srinv ** np.array(rombexpon, dtype=np.float64)
    rmat[2, 1:3] = srinv ** (2.0 * np.array(rombexpon, dtype=np.float64))
    rmat[3, 1:3] = srinv ** (3.0 * np.array(rombexpon, dtype=np.float64))

    qromb, rromb = np.linalg.qr(rmat, mode="reduced")
    ne = der_init.size
    rhs = _vec2mat(der_init, nexpon + 2, ne - (nexpon + 2))
    rombcoefs = np.linalg.solve(rromb, qromb.T @ rhs)
    der_romb = rombcoefs[0, :]

    resid = rhs - rmat @ rombcoefs
    s = np.sqrt(np.sum(resid**2, axis=0))
    rinv = np.linalg.solve(rromb, np.eye(nexpon + 1, dtype=np.float64))
    cov1 = np.sum(rinv**2, axis=1)
    errest = s * 12.7062047361747 * np.sqrt(cov1[0])
    return der_romb, errest


def _jacobianest(fun: Callable[[ArrayF64], ArrayF64], x0: ArrayF64) -> ArrayF64:
    nx = x0.size
    max_step = 100.0
    step_ratio = 2.0

    f0 = np.asarray(fun(x0), dtype=np.float64).reshape(-1)
    n_out = f0.size
    jac = np.zeros((n_out, nx), dtype=np.float64)

    relativedelta = max_step * (step_ratio ** np.arange(0, -26, -1, dtype=np.float64))
    nsteps = relativedelta.size

    for i in range(nx):
        x0_i = x0[i]
        delta = x0_i * relativedelta if x0_i != 0 else relativedelta

        fdel = np.zeros((n_out, nsteps), dtype=np.float64)
        for j in range(nsteps):
            xp = x0.copy()
            xm = x0.copy()
            xp[i] = x0_i + delta[j]
            xm[i] = x0_i - delta[j]
            fdif = np.asarray(fun(xp), dtype=np.float64).reshape(-1) - np.asarray(
                fun(xm), dtype=np.float64
            ).reshape(-1)
            fdel[:, j] = fdif

        derest = fdel * (0.5 / delta)[np.newaxis, :]

        for j in range(n_out):
            der_romb, errest = _rombextrap(step_ratio, derest[j, :], (2, 4))
            nest = der_romb.size
            trim = np.r_[np.arange(0, 3), np.arange(nest - 3, nest)]

            order = np.argsort(der_romb)
            keep = np.ones(nest, dtype=bool)
            keep[trim] = False
            der_usable = der_romb[order][keep]
            err_usable = errest[order][keep]

            ind = int(np.argmin(err_usable))
            jac[j, i] = der_usable[ind]

    return jac


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
    vec_a = a_arr.reshape(needed, order="F")
    jac = _jacobianest(lambda x: _eig_stacked(np.asarray(x, dtype=np.float64), n), vec_a)
    cov_e = jac @ p_use @ jac.T
    e = np.linalg.eigvals(a_arr)
    return e.astype(np.complex128, copy=False), cov_e
