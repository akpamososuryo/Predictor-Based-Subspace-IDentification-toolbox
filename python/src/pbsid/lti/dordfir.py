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
        raise ValueError(f"DORDFIR expects '{name}' to be a 2D matrix.")
    return arr


def _ensure_row_major_samples(arr: ArrayF64) -> ArrayF64:
    if arr.shape[1] < arr.shape[0]:
        return arr.T.copy()
    return arr


def _regress_none(y: ArrayF64, p: ArrayF64, x0: ArrayF64 | None = None) -> ArrayF64:
    if x0 is None:
        return y @ np.linalg.pinv(p)
    return x0 + (y - x0 @ p) @ np.linalg.pinv(p)


def dordfir(
    u: ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...],
    y: ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...],
    f: int,
    p: int,
    reg: str = "none",
    opt: str | float = "gcv",
    no_d: int | bool = 0,
) -> tuple[ArrayF64, XOut, ArrayF64]:
    """Estimate order information/state sequence for FIR-based LTI identification.

    MATLAB parity target: ``dordfir.m``. This implementation currently supports
    the `reg="none"` path and batch updates.
    """
    reg_l = str(reg).lower()
    if reg_l != "none":
        raise NotImplementedError(
            "dordfir currently supports only reg='none' in the Python port."
        )

    if f < 1 or p < 1:
        raise ValueError("Past/future windows must be positive integers.")

    # Keep argument for parity-oriented API, even when unused for reg='none'.
    _ = opt
    no_d_flag = bool(no_d)

    if isinstance(y, (list, tuple)):
        if not isinstance(u, (list, tuple)):
            raise ValueError("For batch mode, u and y must both be list/tuple inputs.")
        y_batch = list(y)
        u_batch = list(u)
        if len(u_batch) != len(y_batch):
            raise ValueError("Batch input lengths for u and y must match.")
        batch = len(y_batch)
    else:
        y_batch = [y]
        u_batch = [u]
        batch = 1

    zz: list[ArrayF64] = []
    xx: list[ArrayF64] = []
    fir: ArrayF64 | None = None

    for u_i, y_i in zip(u_batch, y_batch, strict=True):
        y_arr = _ensure_row_major_samples(_as_2d_float64(y_i, "y"))
        u_arr = _ensure_row_major_samples(_as_2d_float64(u_i, "u"))

        n = y_arr.shape[1]
        l_out = y_arr.shape[0]
        r = u_arr.shape[0]

        if r == 0:
            raise ValueError("DORDFIR requires an input vector u.")
        if l_out == 0:
            raise ValueError("DORDFIR requires an output vector y.")
        if u_arr.shape[1] != n:
            raise ValueError("The number of rows of vectors/matrices u and y must be the same.")
        if p >= n:
            raise ValueError("Past window p must be smaller than the number of samples.")

        z = np.zeros((p * r, n - p), dtype=np.float64)
        for i in range(1, p + 1):
            row0 = (i - 1) * r
            row1 = i * r
            z[row0:row1, :] = u_arr[:, i - 1 : n + i - p - 1]

        y_reg = y_arr[:, p:n]
        u_reg = u_arr[:, p:n]
        if not no_d_flag:
            z = np.vstack((z, u_reg))

        fir = _regress_none(y_reg, z, fir)
        zz.append(z)

    assert fir is not None
    r = _ensure_row_major_samples(_as_2d_float64(u_batch[0], "u")).shape[0]
    l_out = _ensure_row_major_samples(_as_2d_float64(y_batch[0], "y")).shape[0]

    lk = np.zeros((f * l_out, p * r), dtype=np.float64)
    for i in range(1, f + 1):
        row0 = (i - 1) * l_out
        row1 = i * l_out
        n_cols = (p - i + 1) * r
        col0 = p * r - n_cols
        lk[row0:row1, col0 : p * r] = fir[:, :n_cols]

    z_all = np.hstack(zz) if batch > 1 else zz[0]
    u_svd, s_diag, vh = np.linalg.svd(lk @ z_all[: p * r, :], full_matrices=False)
    _ = u_svd

    x_all = np.diag(np.sqrt(s_diag)) @ vh
    s = s_diag.copy()

    if batch > 1:
        x_tmp = x_all
        for z_k in zz:
            n_cols = z_k.shape[1]
            xx.append(x_tmp[:, :n_cols])
            x_tmp = x_tmp[:, n_cols:]
        return s, xx, fir

    return s, x_all, fir
