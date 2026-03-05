from __future__ import annotations

import warnings

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .dx2abck import _force_stable_a

ArrayF64 = NDArray[np.float64]
ABCD = tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64]

def _as_2d_float64(x: object, name: str) -> ArrayF64:
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim == 1:
        arr = arr[np.newaxis, :]
    if arr.ndim != 2:
        raise ValueError(f"DX2ABCD expects '{name}' to be a 2D matrix.")
    return arr


def _ensure_row_major_samples(arr: ArrayF64) -> ArrayF64:
    if arr.shape[1] < arr.shape[0]:
        return arr.T.copy()
    return arr


def dx2abcd(
    x: ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...],
    u: ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...],
    y: ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...],
    f: int,
    p: int,
    c: str = "none",
) -> ABCD:
    """Estimate A, B, C, D from state/input/output sequences.

    MATLAB parity target: ``dx2abcd.m``.
    """
    if c is None or c == "":
        c = "none"
    c_l = c.lower()

    if f > p:
        raise ValueError("Future window size f must equal or smaller then past window p. (f <= p)")

    if isinstance(y, (list, tuple)):
        if not (isinstance(x, (list, tuple)) and isinstance(u, (list, tuple))):
            raise ValueError("For batch mode, x/u/y must all be list or tuple inputs.")
        y_batch = list(y)
        x_batch = list(x)
        u_batch = list(u)
        if not (len(x_batch) == len(y_batch) == len(u_batch)):
            raise ValueError("Batch input lengths for x, u, and y must match.")
    else:
        y_batch = [y]
        x_batch = [x]
        u_batch = [u]

    a = b = c_mat = d = None
    prev_abcd: tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64] | None = None

    for x_i, u_i, y_i in zip(x_batch, u_batch, y_batch, strict=True):
        y_arr = _ensure_row_major_samples(_as_2d_float64(y_i, "y"))
        u_arr = _ensure_row_major_samples(_as_2d_float64(u_i, "u"))
        x_arr = _ensure_row_major_samples(_as_2d_float64(x_i, "x"))

        n_samples = y_arr.shape[1]
        l_out = y_arr.shape[0]
        r = u_arr.shape[0]
        n = x_arr.shape[0]

        if r == 0:
            raise ValueError("DX2ABCD requires an input vector u.")
        if l_out == 0:
            raise ValueError("DX2ABCD requires an output vector y.")
        if n == 0:
            raise ValueError("DX2ABCD requires an state vector x.")
        if u_arr.shape[1] != n_samples:
            raise ValueError("The number of rows of vectors/matrices u and y must be the same.")
        if np.linalg.matrix_rank(u_arr) < r:
            warnings.warn(
                "The input vector u is not sufficiently exciting. (rank(u) = r)",
                RuntimeWarning,
                stacklevel=2,
            )
        if np.linalg.matrix_rank(x_arr) < n:
            raise ValueError("The state vector x is not full rank. (rank(x) = n)")

        x_cols = x_arr.shape[1]
        start = p
        stop = p + x_cols
        if stop > n_samples:
            raise ValueError("Window sizes and state sequence imply out-of-range indexing for u/y.")

        u_t = u_arr[:, start:stop]
        y_t = y_arr[:, start:stop]

        xu_prev = np.vstack((x_arr[:, :-1], u_t[:, :-1]))
        if prev_abcd is None:
            cd = y_t[:, :-1] @ np.linalg.pinv(xu_prev)
        else:
            _, _, c0, d0 = prev_abcd
            cd0 = np.hstack((c0, d0))
            cd = cd0 + (y_t[:, :-1] - cd0 @ xu_prev) @ np.linalg.pinv(xu_prev)

        z = np.vstack((x_arr[:, :-1], u_t[:, :-1]))
        if prev_abcd is None:
            ab = x_arr[:, 1:] @ np.linalg.pinv(z)
        else:
            a0, b0, _, _ = prev_abcd
            ab0 = np.hstack((a0, b0))
            ab = ab0 + (x_arr[:, 1:] - ab0 @ z) @ np.linalg.pinv(z)

        a = ab[:, :n]
        b = ab[:, n : n + r]
        c_mat = cd[:, :n]
        d = cd[:, n : n + r]

        if c_l in {"stable", "stable1", "stable2"} and np.max(np.abs(np.linalg.eigvals(a))) >= 1.0:
            e = y_t - cd @ np.vstack((x_arr, u_t))
            stable_mode = "stable1" if c_l in {"stable", "stable1"} else "stable2"
            a = _force_stable_a(
                c_mode=stable_mode,
                a=a,
                c_mat=c_mat,
                x_arr=x_arr,
                u_prev=u_t[:, :-1],
                e_prev=e[:, :-1],
                p=p,
                r=r,
                l_out=l_out,
            )

            z_b = u_t[:, :-1]
            if prev_abcd is None:
                b = (x_arr[:, 1:] - a @ x_arr[:, :-1]) @ np.linalg.pinv(z_b)
            else:
                _, b0, _, _ = prev_abcd
                b = b0 + (x_arr[:, 1:] - a @ x_arr[:, :-1] - b0 @ z_b) @ np.linalg.pinv(z_b)

        prev_abcd = (a, b, c_mat, d)

    assert a is not None and b is not None and c_mat is not None and d is not None
    return a, b, c_mat, d
