from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

type ArrayF64 = NDArray[np.float64]
type XOut = ArrayF64 | list[ArrayF64]


def _as_2d_float64(x: object, name: str) -> ArrayF64:
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim == 1:
        # MATLAB fixture vectors loaded with squeeze_me=True become 1D arrays.
        arr = arr[np.newaxis, :]
    if arr.ndim != 2:
        raise ValueError(f"DORDVARX expects '{name}' to be a 2D matrix.")
    return arr


def _ensure_row_major_samples(arr: ArrayF64) -> ArrayF64:
    if arr.shape[1] < arr.shape[0]:
        return arr.T.copy()
    return arr


def _regress_none(
    y: ArrayF64, p: ArrayF64, x0: ArrayF64 | None = None
) -> tuple[ArrayF64, ArrayF64]:
    zps = np.linalg.pinv(p)
    if x0 is None:
        return y @ zps, zps
    return x0 + (y - x0 @ p) @ zps, zps


def dordvarx(
    u: ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...] | None,
    y: ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...],
    f: int,
    p: int,
    reg: str = "none",
    opt: str | float = "gcv",
    weight: int | bool = 0,
    no_d: int | bool = 0,
) -> tuple[ArrayF64, XOut, ArrayF64, ArrayF64, ArrayF64]:
    """Closed-loop LTI order estimation and state-sequence preprocessing.

    MATLAB parity target: ``dordvarx.m``. This implementation currently supports
    the `reg="none"` path, including batch updates and `weight` modes 0/1.
    """
    reg_l = str(reg).lower()
    if reg_l != "none":
        raise NotImplementedError(
            "dordvarx currently supports only reg='none' in the Python port."
        )

    if f < 1 or p < 1:
        raise ValueError("Past/future windows must be positive integers.")
    if f > p:
        raise ValueError("Future window size f must equal or smaller then past window p. (f <= p)")

    _ = opt
    weight_flag = int(bool(weight))
    no_d_flag = bool(no_d)

    if isinstance(y, (list, tuple)):
        y_batch = list(y)
        if isinstance(u, (list, tuple)):
            u_batch = list(u)
            if len(u_batch) != len(y_batch):
                raise ValueError("Batch input lengths for u and y must match.")
        elif u is None:
            u_batch = [None] * len(y_batch)
        else:
            raise ValueError("For batch mode, u must be list/tuple or None.")
        batch = len(y_batch)
    else:
        y_batch = [y]
        u_batch = [u]
        batch = 1

    zz: list[ArrayF64] = []
    xx: list[ArrayF64] = []
    varx: ArrayF64 | None = None
    zps_out: ArrayF64 | None = None
    z_last: ArrayF64 | None = None

    for u_i, y_i in zip(u_batch, y_batch, strict=True):
        y_arr = _ensure_row_major_samples(_as_2d_float64(y_i, "y"))
        n_samples = y_arr.shape[1]
        l_out = y_arr.shape[0]

        if l_out == 0:
            raise ValueError("DORDVARX requires an output vector y.")

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

        m = r + l_out
        z_all = np.vstack((u_arr, y_arr))
        z = np.zeros((p * m, n_samples - p), dtype=np.float64)
        for i in range(1, p + 1):
            row0 = (i - 1) * m
            row1 = i * m
            z[row0:row1, :] = z_all[:, i - 1 : n_samples + i - p - 1]

        y_reg = y_arr[:, p:n_samples]
        u_reg = u_arr[:, p:n_samples]
        if not no_d_flag:
            z = np.vstack((z, u_reg))

        varx, zps_out = _regress_none(y_reg, z, varx)
        zz.append(z)
        z_last = z

    assert varx is not None and zps_out is not None and z_last is not None

    if u_batch[0] is None:
        r0 = 0
    else:
        r0 = _ensure_row_major_samples(_as_2d_float64(u_batch[0], "u")).shape[0]
    l0 = _ensure_row_major_samples(_as_2d_float64(y_batch[0], "y")).shape[0]
    m0 = r0 + l0

    lk = np.zeros((f * l0, p * m0), dtype=np.float64)
    if weight_flag == 0:
        for i in range(1, f + 1):
            row0 = (i - 1) * l0
            row1 = i * l0
            n_cols = (p - i + 1) * m0
            col0 = p * m0 - n_cols
            lk[row0:row1, col0 : p * m0] = varx[:, :n_cols]
    else:
        for i in range(0, f):
            row0 = i * l0
            row1 = (i + 1) * l0
            col0 = i * m0
            lk[row0:row1, col0 : p * m0] = varx[:, : (p - i) * m0]
            if i != 0:
                for j in range(0, i):
                    j0 = j * l0
                    j1 = (j + 1) * l0
                    idx0 = (p - i + j) * m0 + r0
                    idx1 = idx0 + l0
                    lk[row0:row1, :] = lk[row0:row1, :] + varx[:, idx0:idx1] @ lk[j0:j1, :]

    if batch > 1:
        qq = np.zeros((f * l0, f * l0), dtype=np.float64)
        for z_k in zz:
            zp = z_k[: p * m0, :]
            qq = qq + lk @ zp @ zp.T @ lk.T

        u_svd, s_mat, _ = np.linalg.svd(qq, full_matrices=False)
        s = np.sqrt(s_mat)
        s_sqrt = np.sqrt(s)
        # Equivalent to (U*diag(sqrt(S)))\LK in MATLAB.
        ui_lk = np.linalg.solve(u_svd @ np.diag(s_sqrt), lk)

        for z_k in zz:
            xx.append(ui_lk @ z_k[: p * m0, :])

        u_out = np.diag(1.0 / np.sqrt(s)) @ u_svd.T
        if weight_flag == 1:
            lk0 = np.zeros((f * l0, p * m0), dtype=np.float64)
            for i in range(1, f + 1):
                row0 = (i - 1) * l0
                row1 = i * l0
                n_cols = (p - i + 1) * m0
                col0 = p * m0 - n_cols
                lk0[row0:row1, col0 : p * m0] = varx[:, :n_cols]
            u_out = np.diag(1.0 / np.sqrt(s)) @ u_svd.T @ (lk @ np.linalg.pinv(lk0))

        return s, xx, varx, u_out, zps_out

    svd_in = lk @ z_last[: p * m0, :]
    u_svd, s, vh = np.linalg.svd(svd_in, full_matrices=False)
    x = np.diag(np.sqrt(s)) @ vh

    u_out = np.diag(1.0 / np.sqrt(s)) @ u_svd.T
    if weight_flag == 1:
        lk0 = np.zeros((f * l0, p * m0), dtype=np.float64)
        for i in range(1, f + 1):
            row0 = (i - 1) * l0
            row1 = i * l0
            n_cols = (p - i + 1) * m0
            col0 = p * m0 - n_cols
            lk0[row0:row1, col0 : p * m0] = varx[:, :n_cols]
        u_out = np.diag(1.0 / np.sqrt(s)) @ u_svd.T @ (lk @ np.linalg.pinv(lk0))

    return s, x, varx, u_out, zps_out
