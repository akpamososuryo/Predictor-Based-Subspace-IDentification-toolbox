from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import ArrayLike


def dbodemagsd(
    g: ArrayLike,
    cov_g: ArrayLike,
    sd: float,
    w: ArrayLike,
    h: float,
    g_real: ArrayLike | None = None,
) -> np.ndarray:
    response = np.asarray(g, dtype=np.complex128)
    covariance = np.asarray(cov_g, dtype=np.float64)
    omega = np.asarray(w, dtype=np.float64).reshape(-1)
    if response.ndim != 3 or response.shape[2] != omega.size:
        raise ValueError("Responses must be 3D and match the number of frequency points.")
    if covariance.shape != response.shape + (2, 2):
        raise ValueError("covG must match G with trailing 2x2 covariance blocks.")

    real_response = None if g_real is None else np.asarray(g_real, dtype=np.complex128)
    if real_response is not None and real_response.shape != response.shape:
        raise ValueError("Real-response array must have the same shape as the estimated response.")

    real_part = np.real(response)
    imag_part = np.imag(response)
    abs_response = np.maximum(np.abs(response), 1e-12)
    sda = np.sqrt(
        np.maximum(
            (real_part**2) * covariance[:, :, :, 0, 0]
            + 2.0 * (real_part * imag_part) * covariance[:, :, :, 1, 0]
            + (imag_part**2) * covariance[:, :, :, 1, 1],
            0.0,
        )
    ) / abs_response

    n_outputs, n_inputs, _ = response.shape
    fig, axes = plt.subplots(
        n_outputs,
        n_inputs,
        figsize=(4.2 * n_inputs, 3.4 * n_outputs),
        squeeze=False,
        sharex=True,
    )
    freq_hz = omega / (2.0 * np.pi)
    nyquist_hz = (np.pi / h) / (2.0 * np.pi)

    for row in range(n_outputs):
        for col in range(n_inputs):
            axis = axes[row, col]
            mag = np.abs(response[row, col, :])
            lower = np.maximum(mag - sd * sda[row, col, :], 1e-5)
            upper = np.maximum(mag + sd * sda[row, col, :], 1e-5)
            axis.fill_between(
                freq_hz,
                20.0 * np.log10(lower),
                20.0 * np.log10(upper),
                color="0.85",
                linewidth=0.0,
            )
            axis.semilogx(
                freq_hz,
                20.0 * np.log10(np.maximum(mag, 1e-12)),
                color="k",
                linewidth=1.8,
            )
            if real_response is not None:
                mag_real = 20.0 * np.log10(np.maximum(np.abs(real_response[row, col, :]), 1e-12))
                axis.semilogx(freq_hz, mag_real, "k--", linewidth=1.0)
            axis.axvline(nyquist_hz, color="k", linewidth=0.8)
            axis.set_xlabel("Frequency (Hz)")
            axis.set_ylabel("Magnitude (dB)")
            axis.grid(True, which="both", alpha=0.25)

    fig.tight_layout()
    return axes