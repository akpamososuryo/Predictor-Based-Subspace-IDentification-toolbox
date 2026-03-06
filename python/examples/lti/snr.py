from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

ArrayF64 = NDArray[np.float64]


def _as_2d_float64(data: ArrayF64) -> ArrayF64:
    arr = np.asarray(data, dtype=np.float64)
    if arr.ndim == 1:
        return arr.reshape(-1, 1)
    if arr.ndim != 2:
        raise ValueError(f"Expected a 1D or 2D array, received shape {arr.shape}.")
    return arr


def _samples_first(data: ArrayF64) -> ArrayF64:
    arr = _as_2d_float64(data)
    if arr.shape[1] > arr.shape[0]:
        return arr.T
    return arr


def snr_db(y: ArrayF64, y_ref: ArrayF64) -> ArrayF64:
    """Port of MATLAB snr.m for the examples layer."""
    y_2d = _samples_first(y)
    y_ref_2d = _samples_first(y_ref)

    if y_ref_2d.shape[0] != y_2d.shape[0]:
        raise ValueError("Both signals should have an equal number of samples.")
    if y_ref_2d.shape[1] != y_2d.shape[1]:
        raise ValueError("Both signals should have an equal number of components.")

    with np.errstate(divide="ignore", invalid="ignore"):
        snr = 10.0 * np.log10(np.var(y_2d, axis=0) / np.var(y_2d - y_ref_2d, axis=0))
    return np.asarray(snr, dtype=np.float64)