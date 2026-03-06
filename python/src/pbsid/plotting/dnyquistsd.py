from __future__ import annotations

from math import erf, sqrt

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import ArrayLike

from pbsid.plotting._ellipse import plot_covariance_ellipse


def dnyquistsd(
    g: ArrayLike,
    cov_g: ArrayLike,
    sd: float,
    g_real: ArrayLike | None = None,
) -> np.ndarray:
    response = np.asarray(g, dtype=np.complex128)
    covariance = np.asarray(cov_g, dtype=np.float64)
    if response.ndim != 3:
        raise ValueError("Responses must be 3D arrays with frequency along the third axis.")
    if covariance.shape != response.shape + (2, 2):
        raise ValueError("covG must match G with trailing 2x2 covariance blocks.")

    real_response = None if g_real is None else np.asarray(g_real, dtype=np.complex128)
    if real_response is not None and real_response.shape != response.shape:
        raise ValueError("Real-response array must have the same shape as the estimated response.")

    n_outputs, n_inputs, n_freq = response.shape
    fig, axes = plt.subplots(
        n_outputs,
        n_inputs,
        figsize=(4.2 * n_inputs, 3.4 * n_outputs),
        squeeze=False,
    )
    confidence = erf(sd / sqrt(2.0))

    for row in range(n_outputs):
        for col in range(n_inputs):
            axis = axes[row, col]
            curve = response[row, col, :]
            for idx in range(n_freq):
                plot_covariance_ellipse(
                    axis,
                    covariance[row, col, idx, :, :],
                    np.array([curve[idx].real, curve[idx].imag], dtype=np.float64),
                    confidence=confidence,
                )
            axis.plot(curve.real, curve.imag, color="k", linewidth=1.8)
            if real_response is not None:
                reference = real_response[row, col, :]
                axis.plot(reference.real, reference.imag, "k--", linewidth=1.0)
            axis.axvline(0.0, color="k", linestyle=":", linewidth=0.8)
            axis.axhline(0.0, color="k", linestyle=":", linewidth=0.8)
            axis.set_xlabel("Real axis")
            axis.set_ylabel("Imaginary axis")
            axis.grid(True, alpha=0.2)

    fig.tight_layout()
    return axes