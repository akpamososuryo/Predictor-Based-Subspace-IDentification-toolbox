from __future__ import annotations

from typing import cast

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.optimize import fminbound

type ArrayF64 = NDArray[np.float64]
type XOut = ArrayF64 | list[ArrayF64]


def _as_2d_float64(x: object, name: str) -> ArrayF64:
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr[np.newaxis, :]
    if arr.ndim != 2:
        raise ValueError(f"DORDVARMAX expects '{name}' to be a 2D matrix.")
    return arr


def _ensure_row_major_samples(arr: ArrayF64) -> ArrayF64:
    if arr.shape[1] < arr.shape[0]:
        return arr.T.copy()
    return arr


def _eval_varmax(
    y: ArrayF64,
    z: ArrayF64,
    p: int,
    r: int,
    varmax: ArrayF64,
) -> ArrayF64:
    l_out = y.shape[0]
    m = r + 2 * l_out
    n_total = y.shape[1] + p

    z_work = z.copy()
    e_full = np.zeros((l_out, n_total), dtype=np.float64)
    h_blocks: list[ArrayF64] = []
    for i in range(1, p + 1):
        row0 = (i - 1) * m + r + l_out
        row1 = i * m
        z_work[row0:row1, :] = e_full[:, i - 1 : n_total + i - p - 1]
        h_blocks.append(varmax[:, row0:row1])

    e = y - varmax @ z_work
    e_f = e.copy()
    for t in range(e.shape[1]):
        for i in range(1, p + 1):
            if t - i >= 0:
                # MATLAB eval_varmax builds an FIR polynomial H(q^-1) and filters raw residuals E.
                e_f[:, t] = e_f[:, t] - h_blocks[i - 1] @ e[:, t - i]
    return e_f


def _rls_ew_track(
    z_col: ArrayF64,
    y_col: ArrayF64,
    theta: ArrayF64,
    p_mat: ArrayF64,
    lamb: float,
) -> tuple[ArrayF64, ArrayF64]:
    denom = lamb + z_col.T @ p_mat @ z_col
    p_next = (1.0 / lamb) * (p_mat - (p_mat @ np.outer(z_col, z_col) @ p_mat) / denom)
    p_next = 0.5 * (p_next + p_next.T)
    e = y_col - theta @ z_col
    theta_next = theta + np.outer(e, z_col) @ p_next
    return theta_next, p_next


def _gradient_obj(
    x: float,
    *,
    y: ArrayF64,
    z: ArrayF64,
    p: int,
    r: int,
    n: int,
    varmax: ArrayF64,
    direction: ArrayF64,
) -> float:
    e_x = _eval_varmax(y, z, p, r, varmax + x * direction)
    return float(np.linalg.norm(e_x.T, ord="fro") ** 2) / float(n)


def _exls_reg_none(
    y: ArrayF64,
    z: ArrayF64,
    p: int,
    r: int,
    tol: float,
    method: str,
    varmax0: ArrayF64 | None = None,
) -> tuple[ArrayF64, ArrayF64]:
    n = y.shape[1] + p
    l_out = y.shape[0]
    m = r + 2 * l_out

    varmax = np.zeros((l_out, z.shape[0]), dtype=np.float64) if varmax0 is None else varmax0.copy()
    cost_prev = 1e10

    method_l = method.lower()
    if method_l in {"grad", "gradient"}:
        lamb = 1.0
        maxit = 100
        k = 1
        while k <= maxit:
            e = _eval_varmax(y, z, p, r, varmax)
            cost = float(np.linalg.norm(e.T, ord="fro") ** 2)
            converged = abs(cost_prev - cost) <= (tol**2) * n

            e_full = np.zeros((l_out, n), dtype=np.float64)
            e_full[:, p:n] = e
            for i in range(1, p + 1):
                row0 = (i - 1) * m + r + l_out
                row1 = i * m
                z[row0:row1, :] = e_full[:, i - 1 : n + i - p - 1]

            direction = e @ z.T

            def objective(
                x: float,
                y_: ArrayF64 = y,
                z_: ArrayF64 = z,
                p_: int = p,
                r_: int = r,
                n_: int = n,
                varmax_: ArrayF64 = varmax,
                direction_: ArrayF64 = direction,
            ) -> float:
                return _gradient_obj(
                    x,
                    y=y_,
                    z=z_,
                    p=p_,
                    r=r_,
                    n=n_,
                    varmax=varmax_,
                    direction=direction_,
                )

            lamb = float(fminbound(objective, 0.0, lamb, xtol=1e-4, maxfun=500))
            varmax = varmax + lamb * direction

            cost_prev = cost
            k += 1
            if converged:
                break

        return varmax, z

    if method_l == "els":
        ireg = np.sqrt(tol)
        p_scalar = ireg
        lamb = tol ** (1.0 / n)
        maxit = 10
        k = 1
        p0 = p_scalar

        while k <= maxit:
            p_current = np.eye(z.shape[0], dtype=np.float64) / p0

            for i_col in range(n - p):
                varmax, p_current = _rls_ew_track(
                    z[:, i_col], y[:, i_col], varmax, p_current, lamb
                )
                e_col = y[:, i_col] - varmax @ z[:, i_col]

                if i_col != (n - p - 1):
                    for j in range(l_out):
                        for blk in range(0, p - 1):
                            dst = blk * m + r + l_out + j
                            src = (blk + 1) * m + r + l_out + j
                            z[dst, i_col + 1] = z[src, i_col]
                        z[(p - 1) * m + r + l_out + j, i_col + 1] = e_col[j]

            e = y - varmax @ z
            cost = float(np.linalg.norm(e.T, ord="fro") ** 2)
            converged = abs(cost_prev - cost) <= (tol**2) * n

            e_full = np.zeros((l_out, n), dtype=np.float64)
            e_full[:, p:n] = e
            for i in range(1, p + 1):
                row0 = (i - 1) * m + r + l_out
                row1 = i * m
                z[row0:row1, :] = e_full[:, i - 1 : n + i - p - 1]

            k += 1
            lamb = (lamb**n) ** (1.0 / (k * n))
            cost_prev = cost
            if converged:
                break

        return varmax, z

    raise ValueError("Unknown DORDVARMAX method.")


def dordvarmax(
    u: ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...] | None,
    y: ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...],
    f: int,
    p: int,
    method: str = "gradient",
    tol: float = 1e-6,
    reg: str = "none",
    opt: str | float = "gcv",
    weight: int | bool = 0,
    no_d: int | bool = 0,
) -> tuple[ArrayF64, XOut, ArrayF64, ArrayF64]:
    """Closed-loop LTI order estimation using VARMAX-based preprocessing.

    MATLAB parity target: ``dordvarmax.m``.

    Notes:
    - Current Python port supports ``reg='none'``.
    - `method` values ``'gradient'`` and ``'els'`` are accepted and use the
      same iterative whitening core in this parity phase.
    """
    if f < 1 or p < 1:
        raise ValueError("Past/future windows must be positive integers.")

    reg_l = str(reg).lower()
    if reg_l != "none":
        raise NotImplementedError("dordvarmax currently supports only reg='none'.")

    _ = opt
    method_l = str(method).lower()
    if method_l not in {"gradient", "grad", "els"}:
        raise ValueError("DORDVARMAX method must be one of: gradient, grad, els.")

    weight_flag = int(bool(weight))
    no_d_flag = bool(no_d)

    if isinstance(y, (list, tuple)):
        y_batch = list(y)
        if isinstance(u, (list, tuple)):
            u_batch = cast(list[ArrayLike | None], list(u))
            if len(u_batch) != len(y_batch):
                raise ValueError("Batch input lengths for u and y must match.")
        elif u is None:
            u_batch = [None] * len(y_batch)
        else:
            raise ValueError("For batch mode, u must be list/tuple or None.")
        batch = len(y_batch)
    else:
        y_batch = [y]
        u_batch = [cast(ArrayLike | None, u)]
        batch = 1

    zz: list[ArrayF64] = []
    xx: list[ArrayF64] = []
    varmax: ArrayF64 | None = None

    for u_i, y_i in zip(u_batch, y_batch, strict=True):
        y_arr = _ensure_row_major_samples(_as_2d_float64(y_i, "y"))
        n_samples = y_arr.shape[1]
        l_out = y_arr.shape[0]
        if l_out == 0:
            raise ValueError("DORDVARMAX requires an output vector y.")

        if u_i is None:
            u_arr = np.zeros((0, n_samples), dtype=np.float64)
            r = 0
        else:
            u_arr = _ensure_row_major_samples(_as_2d_float64(u_i, "u"))
            r = u_arr.shape[0]
            if u_arr.shape[1] != n_samples:
                raise ValueError("The number of rows of vectors/matrices u and y must be the same.")

        if p >= n_samples:
            raise ValueError("Past window p must be smaller than the number of samples.")

        m = r + 2 * l_out
        z_all = np.vstack((u_arr, y_arr, np.zeros((l_out, n_samples), dtype=np.float64)))
        z = np.zeros((p * m, n_samples - p), dtype=np.float64)
        for i in range(1, p + 1):
            row0 = (i - 1) * m
            row1 = i * m
            z[row0:row1, :] = z_all[:, i - 1 : n_samples + i - p - 1]

        y_reg = y_arr[:, p:n_samples]
        u_reg = u_arr[:, p:n_samples]
        if not no_d_flag:
            z = np.vstack((z, u_reg))

        varmax, z = _exls_reg_none(y_reg, z, p, r, tol, method_l, varmax0=varmax)
        zz.append(z)

    assert varmax is not None

    first_y = _ensure_row_major_samples(_as_2d_float64(y_batch[0], "y"))
    first_u = u_batch[0]
    r0 = 0 if first_u is None else _ensure_row_major_samples(_as_2d_float64(first_u, "u")).shape[0]
    l0 = first_y.shape[0]
    m0 = r0 + 2 * l0

    lk = np.zeros((f * l0, p * m0), dtype=np.float64)
    if weight_flag == 0:
        for i in range(1, f + 1):
            row0 = (i - 1) * l0
            row1 = i * l0
            n_cols = (p - i + 1) * m0
            col0 = p * m0 - n_cols
            lk[row0:row1, col0 : p * m0] = varmax[:, :n_cols]
    else:
        for i in range(0, f):
            row0 = i * l0
            row1 = (i + 1) * l0
            col0 = i * m0
            lk[row0:row1, col0 : p * m0] = varmax[:, : (p - i) * m0]
            if i != 0:
                for j in range(0, i):
                    j0 = j * l0
                    j1 = (j + 1) * l0
                    idx0 = (p - i + j) * m0 + r0
                    idx1 = idx0 + l0
                    lk[row0:row1, :] = lk[row0:row1, :] + varmax[:, idx0:idx1] @ lk[j0:j1, :]

    z_cat = np.hstack(zz) if batch > 1 else zz[0]
    u_svd, s, vh = np.linalg.svd(lk @ z_cat[: p * m0, :], full_matrices=False)
    x_cat = np.diag(np.sqrt(s)) @ vh

    umat = np.diag(1.0 / np.sqrt(s)) @ u_svd.T
    if weight_flag == 1:
        lk0 = np.zeros((f * l0, p * m0), dtype=np.float64)
        for i in range(1, f + 1):
            row0 = (i - 1) * l0
            row1 = i * l0
            n_cols = (p - i + 1) * m0
            col0 = p * m0 - n_cols
            lk0[row0:row1, col0 : p * m0] = varmax[:, :n_cols]
        umat = np.diag(1.0 / np.sqrt(s)) @ u_svd.T @ (lk @ np.linalg.pinv(lk0))

    if batch > 1:
        start = 0
        for z_k in zz:
            width = z_k.shape[1]
            xx.append(x_cat[:, start : start + width])
            start += width
        return s, xx, varmax, umat

    return s, x_cat, varmax, umat
