from __future__ import annotations

from math import erf, sqrt

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import ArrayLike

from pbsid.plotting._ellipse import plot_covariance_ellipse


def deigensd(
    e: ArrayLike,
    ecov: ArrayLike,
    sd: float,
    er: ArrayLike | None = None,
    *,
    ax: plt.Axes | None = None,
) -> plt.Axes:
    eigenvalues = np.asarray(e, dtype=np.complex128).reshape(-1)
    covariance = np.asarray(ecov, dtype=np.float64)
    if covariance.shape != (2 * eigenvalues.size, 2 * eigenvalues.size):
        raise ValueError("Ecov must be a 2n x 2n covariance matrix for n eigenvalues.")

    axis = ax if ax is not None else plt.subplots(figsize=(5.5, 5.5))[1]
    theta = np.linspace(0.0, 2.0 * np.pi, 1000, dtype=np.float64)
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

    axis.plot(eigenvalues.real, eigenvalues.imag, "x", color=(0.7, 0.7, 0.7), markersize=8)

    confidence = erf(sd / sqrt(2.0))
    for index, eig in enumerate(eigenvalues):
        block = covariance[2 * index : 2 * index + 2, 2 * index : 2 * index + 2]
        plot_covariance_ellipse(
            axis,
            block,
            np.array([eig.real, eig.imag], dtype=np.float64),
            confidence=confidence,
        )

    axis.set_aspect("equal", adjustable="box")
    axis.set_xlim(-1.0, 1.0)
    axis.set_ylim(-1.0, 1.0)
    axis.set_xlabel("Real axis")
    axis.set_ylabel("Imaginary axis")
    axis.grid(False)
    return axis