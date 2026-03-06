from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import ArrayLike


def dbodemag(
    frd: ArrayLike,
    w: ArrayLike,
    h: float,
    *,
    g_real: ArrayLike | None = None,
    axes: np.ndarray | None = None,
) -> np.ndarray:
    response = np.asarray(frd, dtype=np.complex128)
    omega = np.asarray(w, dtype=np.float64).reshape(-1)
    if response.ndim != 3:
        raise ValueError(f"Expected a 3D frequency-response array, received shape {response.shape}.")
    if response.shape[2] != omega.size:
        raise ValueError("Number of frequency points must match the response third dimension.")

    real_response = None if g_real is None else np.asarray(g_real, dtype=np.complex128)
    if real_response is not None and real_response.shape != response.shape:
        raise ValueError("Real-response array must have the same shape as the identified response.")

    n_outputs, n_inputs, _ = response.shape
    if axes is None:
        _, axes_obj = plt.subplots(
            n_outputs,
            n_inputs,
            figsize=(3.8 * n_inputs, 3.0 * n_outputs),
            squeeze=False,
            sharex=True,
        )
    else:
        axes_obj = np.atleast_2d(np.asarray(axes, dtype=object))

    cutoff_hz = (np.pi / h) / (2.0 * np.pi)
    freq_hz = omega / (2.0 * np.pi)

    for row in range(n_outputs):
        for col in range(n_inputs):
            axis = axes_obj[row, col]
            mag = 20.0 * np.log10(np.maximum(np.abs(response[row, col, :]), 1e-12))
            axis.semilogx(freq_hz, mag, color="k", linewidth=2.0)
            if real_response is not None:
                mag_real = 20.0 * np.log10(np.maximum(np.abs(real_response[row, col, :]), 1e-12))
                axis.semilogx(freq_hz, mag_real, "k--", linewidth=1.0)
            axis.axvline(cutoff_hz, color="k", linewidth=0.8)
            axis.set_xlabel("Frequency (Hz)")
            axis.set_ylabel("Magnitude (dB)")
            axis.grid(True, which="both", alpha=0.25)

    return axes_obj