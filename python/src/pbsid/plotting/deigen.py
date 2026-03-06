from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import ArrayLike


def _as_complex_columns(values: ArrayLike) -> np.ndarray:
    arr = np.asarray(values)
    if arr.ndim == 0:
        return np.asarray([[complex(arr)]], dtype=np.complex128)
    if arr.ndim == 1:
        return np.asarray(arr, dtype=np.complex128).reshape(-1, 1)
    if arr.ndim == 2:
        return np.asarray(arr, dtype=np.complex128)
    raise ValueError(f"Expected a 1D or 2D eigenvalue array, received shape {arr.shape}.")


def deigen(
    e: ArrayLike,
    er: ArrayLike | None = None,
    *,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    eigen_sets = _as_complex_columns(e)
    axis = ax if ax is not None else plt.subplots(figsize=(5.5, 5.5))[1]

    theta = np.linspace(0.0, 2.0 * np.pi, 1000)
    axis.plot(np.cos(theta), np.sin(theta), color=(0.4, 0.4, 0.4), label="STABBND")

    if er is not None:
        reference = np.asarray(er, dtype=np.complex128).reshape(-1)
        axis.plot(
            reference.real,
            reference.imag,
            "k+",
            linewidth=0.1,
            markersize=10,
            label="TRUE",
        )

    for index in range(eigen_sets.shape[1]):
        values = eigen_sets[:, index]
        axis.plot(values.real, values.imag, "x", color=(0.7, 0.7, 0.7), markersize=8)

    axis.set_aspect("equal", adjustable="box")
    axis.set_xlim(-1.0, 1.0)
    axis.set_ylim(-1.0, 1.0)
    axis.set_xlabel("Real axis")
    axis.set_ylabel("Imaginary axis")
    axis.grid(False)
    return axis