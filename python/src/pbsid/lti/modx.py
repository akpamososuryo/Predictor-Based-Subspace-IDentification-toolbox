from __future__ import annotations

from typing import TypeAlias, overload

import numpy as np
from numpy.typing import ArrayLike, NDArray

ArrayF64 = NDArray[np.float64]
BatchInput: TypeAlias = ArrayLike | list[ArrayLike] | tuple[ArrayLike, ...]
BatchOutput: TypeAlias = ArrayF64 | list[ArrayF64]


def _as_2d_float64(x: object) -> ArrayF64:
    """Convert input to a 2D float64 array."""
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError("modx expects a 2D matrix (or a sequence of 2D matrices).")
    return arr


@overload
def modx(X: list[ArrayLike] | tuple[ArrayLike, ...], n: int) -> list[ArrayF64]:
    ...


@overload
def modx(X: ArrayLike, n: int) -> ArrayF64:
    ...


def modx(X: BatchInput, n: int) -> BatchOutput:
    """
    Estimate/truncate the state sequence to system order n.

    MATLAB parity target: dmodx.m

    Parameters
    ----------
    X:
        State matrix (2D) or a batch of state matrices (list/tuple of 2D arrays).
    n:
        Desired system order. Must be >= 1.

    Returns
    -------
    ndarray or list[ndarray]
        Truncated state matrix/matrices using the first n rows.

    Raises
    ------
    ValueError
        If n < 1 or if a matrix has fewer than n rows.
    """
    if n is None or n < 1:
        raise ValueError("System order of zero or lower does not make sense!")

    # MATLAB cell-array behavior: process each batch entry independently.
    if isinstance(X, (list, tuple)):
        out: list[ArrayF64] = []
        for xk in X:
            x_arr = _as_2d_float64(xk)
            mx = x_arr.shape[0]
            if mx < n:
                raise ValueError(
                    "The number of rows of matrix X must be equal or higher than the order n."
                )
            out.append(x_arr[:n, :].copy())
        return out

    x_arr = _as_2d_float64(X)
    mx = x_arr.shape[0]
    if mx < n:
        raise ValueError("The number of rows of matrix X must be equal or higher than the order n.")
    return x_arr[:n, :].copy()
