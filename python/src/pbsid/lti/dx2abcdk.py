from __future__ import annotations

from typing import cast, overload

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.linalg import eig, solve_discrete_are

ArrayF64 = NDArray[np.float64]
ABCD = tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64]
ABCDK = tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64]

def _as_2d_float64(x: object, name: str) -> ArrayF64:
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim == 1:
        # MATLAB vectors may load from .mat as 1D arrays; treat as single-channel signals.
        arr = arr[np.newaxis, :]
    if arr.ndim != 2:
        raise ValueError(f"DX2ABCDK expects '{name}' to be a 2D matrix.")
    return arr


def _ensure_row_major_samples(arr: ArrayF64) -> ArrayF64:
    if arr.shape[1] < arr.shape[0]:
        return arr.T.copy()
    return arr


def _force_stable_a(
    *,
    c_mode: str,
    a: ArrayF64,
    c_mat: ArrayF64,
    x_arr: ArrayF64,
    u_prev: ArrayF64,
    e_prev: ArrayF64,
    p: int,
    r: int,
    l_out: int,
) -> ArrayF64:
    n = a.shape[0]

    if c_mode == "stable2":
        gamma = 1.0 - 1e-8
        z_full = np.vstack((u_prev, e_prev, x_arr[:, :-1]))
        _, r_qr = np.linalg.qr(z_full.T, mode="reduced")
        sigma_block = r_qr[r + l_out : r + l_out + n, r + l_out : r + l_out + n]
        sigma_s = sigma_block.T @ sigma_block

        eye_n = np.eye(n, dtype=np.float64)
        kron_sigma = np.kron(sigma_s, sigma_s)
        p0 = np.kron(a @ sigma_s, a @ sigma_s) - (gamma**2) * kron_sigma
        p1 = -(gamma**2) * (np.kron(sigma_s, eye_n) + np.kron(eye_n, sigma_s))
        p2 = -(gamma**2) * np.kron(eye_n, eye_n)

        zeros_n2 = np.zeros((n * n, n * n), dtype=np.float64)
        eye_n2 = np.eye(n * n, dtype=np.float64)
        a1 = np.block([[zeros_n2, -eye_n2], [p0, p1]])
        a2 = -np.block([[eye_n2, zeros_n2], [zeros_n2, p2]])

        theta = eig(a1, a2, right=False)
        theta_real = np.real(theta[np.isclose(np.imag(theta), 0.0)])
        theta_real = theta_real[np.isfinite(theta_real)]
        if theta_real.size == 0:
            raise ValueError("stable2 branch failed to find a real generalized eigenvalue.")

        c_scale = float(np.sqrt(np.max(theta_real)))
        z_prev = np.vstack((x_arr[:, :-1], u_prev, e_prev))
        right_aug = np.vstack((c_scale * np.eye(n), np.zeros((l_out + r, n), dtype=np.float64)))
        aug = np.hstack((z_prev, right_aug))
        left_aug = np.hstack((x_arr[:, 1:], np.zeros((n, n), dtype=np.float64)))
        abk = left_aug @ np.linalg.pinv(aug)
        return abk[:, :n]

    gamma_obs = np.zeros(((p + 1) * l_out, n), dtype=np.float64)
    for i in range(1, p + 1):
        row0 = (i - 1) * l_out
        row1 = i * l_out
        if i == 1:
            gamma_obs[row0:row1, :] = c_mat
        else:
            gamma_obs[row0:row1, :] = gamma_obs[row0 - l_out : row0, :] @ a

    return np.linalg.pinv(gamma_obs[: p * l_out, :]) @ gamma_obs[l_out : (p + 1) * l_out, :]


@overload
def dx2abcdk(
    x: ArrayLike,
    u: ArrayLike | None,
    y: ArrayLike,
    f: int,
    p: int,
    c: str = "none",
    *,
    return_k: bool,
) -> ABCDK: ...


@overload
def dx2abcdk(
    x: ArrayLike,
    u: ArrayLike | None,
    y: ArrayLike,
    f: int,
    p: int,
    c: str = "none",
    *,
    return_k: bool = False,
) -> ABCD: ...


def dx2abcdk(
    x: ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...],
    u: ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...] | None,
    y: ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...],
    f: int,
    p: int,
    c: str = "none",
    *,
    return_k: bool = False,
) -> ABCD | ABCDK:
    """Estimate A, B, C, D and optionally K from state/input/output sequences.

    MATLAB parity target: ``dx2abcdk.m`` (single-dataset baseline path).

        Supports baseline, stability-enforced A estimation (stable/stable1/stable2),
        optional Riccati-based K estimation, and batch-list inputs.
    """
    if c is None or c == "":
        c = "none"
    c_l = c.lower()

    if f > p:
        raise ValueError("Future window size f must equal or smaller then past window p. (f <= p)")

    if isinstance(y, (list, tuple)):
        if not (isinstance(x, (list, tuple)) and (isinstance(u, (list, tuple)) or u is None)):
            raise ValueError("For batch mode, x/u/y must all be list or tuple inputs.")
        y_batch = list(y)
        x_batch = list(x)
        u_batch: list[ArrayLike | None]
        u_batch = [None] * len(y_batch) if u is None else cast(list[ArrayLike | None], list(u))
        if not (len(x_batch) == len(y_batch) == len(u_batch)):
            raise ValueError("Batch input lengths for x, u, and y must match.")
    else:
        y_batch = [y]
        x_batch = [x]
        u_batch = [cast(ArrayLike | None, u)]

    a = b = c_mat = d = k_mat = None
    prev_abcdk: tuple[ArrayF64, ArrayF64, ArrayF64, ArrayF64, ArrayF64] | None = None
    vw_prev: ArrayF64 | None = None

    for x_i, u_i, y_i in zip(x_batch, u_batch, y_batch, strict=True):
        y_arr = _ensure_row_major_samples(_as_2d_float64(y_i, "y"))
        x_arr = _ensure_row_major_samples(_as_2d_float64(x_i, "x"))

        n = x_arr.shape[0]
        l_out, n_samples = y_arr.shape

        if l_out == 0:
            raise ValueError("DX2ABCDK requires an output vector y.")
        if n == 0:
            raise ValueError("DX2ABCDK requires a state vector x.")

        if u_i is None:
            u_arr = np.zeros((0, n_samples), dtype=np.float64)
        else:
            u_arr = _ensure_row_major_samples(_as_2d_float64(u_i, "u"))

        if u_arr.shape[1] != n_samples:
            raise ValueError("The number of rows of vectors/matrices u and y must be the same.")

        r = u_arr.shape[0]

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
        if prev_abcdk is None:
            cd = y_t[:, :-1] @ np.linalg.pinv(xu_prev)
        else:
            _, _, c0, d0, _ = prev_abcdk
            cd0 = np.hstack((c0, d0))
            cd = cd0 + (y_t[:, :-1] - cd0 @ xu_prev) @ np.linalg.pinv(xu_prev)

        e = y_t - cd @ np.vstack((x_arr, u_t))
        z = np.vstack((x_arr[:, :-1], u_t[:, :-1], e[:, :-1]))

        if prev_abcdk is None:
            abk = x_arr[:, 1:] @ np.linalg.pinv(z)
        else:
            a0, b0, _, _, k0 = prev_abcdk
            abk0 = np.hstack((a0, b0, k0))
            abk = abk0 + (x_arr[:, 1:] - abk0 @ z) @ np.linalg.pinv(z)

        a = abk[:, :n]
        b = abk[:, n : n + r]
        c_mat = cd[:, :n]
        d = cd[:, n : n + r]
        k_mat = abk[:, n + r : n + r + l_out]

        if c_l in {"stable", "stable1", "stable2"} and np.max(np.abs(np.linalg.eigvals(a))) >= 1.0:
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

            z_bk = np.vstack((u_t[:, :-1], e[:, :-1]))
            if prev_abcdk is None:
                bk = (x_arr[:, 1:] - a @ x_arr[:, :-1]) @ np.linalg.pinv(z_bk)
            else:
                _, b0, _, _, k0 = prev_abcdk
                bk0 = np.hstack((b0, k0))
                bk = bk0 + (x_arr[:, 1:] - a @ x_arr[:, :-1] - bk0 @ z_bk) @ np.linalg.pinv(z_bk)

            b = bk[:, :r]
            k_mat = bk[:, r : r + l_out]

        if return_k and c_l != "nostable":
            lhs = np.block([[a, b], [c_mat, d]]) @ np.vstack((x_arr[:, :-1], u_t[:, :-1]))
            vw = np.vstack((x_arr[:, 1:], y_t[:, :-1])) - lhs

            if vw_prev is not None:
                vw = np.hstack((vw, vw_prev))

            denom = float(max(vw.shape))
            qsr = (vw @ vw.T) / denom
            q = qsr[:n, :n]
            s = qsr[:n, n : n + l_out]
            r_cov = qsr[n : n + l_out, n : n + l_out]

            xric = solve_discrete_are(a.T, c_mat.T, q, r_cov, s=s)
            innovation_cov = c_mat @ xric @ c_mat.T + r_cov
            gain_num = a @ xric @ c_mat.T + s
            k_mat = np.linalg.solve(innovation_cov.T, gain_num.T).T
            vw_prev = vw

        prev_abcdk = (a, b, c_mat, d, k_mat)

    assert (
        a is not None
        and b is not None
        and c_mat is not None
        and d is not None
        and k_mat is not None
    )

    if return_k:
        return a, b, c_mat, d, k_mat
    return a, b, c_mat, d
