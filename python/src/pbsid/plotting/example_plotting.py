from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from control import matlab as ml
from numpy.typing import ArrayLike

from pbsid.plotting.dbodemag import dbodemag
from pbsid.plotting.deigen import deigen


def _frequency_response(sys_model: Any, w: ArrayLike) -> np.ndarray:
    omega = np.asarray(w, dtype=np.float64)
    mag, phase, _ = ml.freqresp(sys_model, omega)
    response = np.asarray(mag, dtype=np.float64) * np.exp(1j * np.asarray(phase, dtype=np.float64))
    if response.ndim == 1:
        return response.reshape(1, 1, -1)
    return response


def plot_singular_values(series: list[tuple[ArrayLike, str, str, str]], title: str) -> None:
    _, axis = plt.subplots(figsize=(7.0, 4.0))
    for values, label, marker, color in series:
        sigma = np.asarray(values, dtype=np.float64).reshape(-1)
        axis.semilogy(np.arange(1, sigma.size + 1), sigma, marker, color=color, label=label)
    axis.set_title(title)
    axis.set_xlabel("Order index")
    axis.set_ylabel("Singular value")
    axis.legend(loc="best")
    axis.grid(True, which="both", alpha=0.3)
    plt.show()


def plot_pole_map(
    reference_poles: ArrayLike,
    models: list[tuple[str, ArrayLike, str, str]],
    title: str,
) -> None:
    _, axis = plt.subplots(figsize=(5.5, 5.5))
    clouds = [np.asarray(poles, dtype=np.complex128).reshape(-1) for _, poles, _, _ in models]
    if clouds:
        deigen(np.column_stack(clouds), np.asarray(reference_poles, dtype=np.complex128), ax=axis)
    else:
        deigen(
            np.asarray(reference_poles, dtype=np.complex128),
            np.asarray(reference_poles),
            ax=axis,
        )

    for label, poles, marker, color in models:
        values = np.asarray(poles, dtype=np.complex128).reshape(-1)
        axis.plot(values.real, values.imag, marker, color=color, linestyle="None", label=label)

    handles, labels = axis.get_legend_handles_labels()
    seen: set[str] = set()
    filtered_handles: list[Any] = []
    filtered_labels: list[str] = []
    for handle, label in zip(handles, labels, strict=False):
        if label and label not in seen:
            seen.add(label)
            filtered_handles.append(handle)
            filtered_labels.append(label)
    axis.set_title(title)
    axis.legend(filtered_handles, filtered_labels, loc="best")
    plt.show()


def plot_bode_magnitude_grid(
    reference_sys: Any,
    identified_systems: list[tuple[str, Any, str]],
    title: str,
    *,
    sample_time: float = 1.0,
    w: ArrayLike | None = None,
) -> None:
    omega = np.logspace(-2, 1, 400) if w is None else np.asarray(w, dtype=np.float64)
    reference = _frequency_response(reference_sys, omega)
    responses = [
        (label, _frequency_response(sys_model, omega), color)
        for label, sys_model, color in identified_systems
    ]

    n_outputs, n_inputs, _ = reference.shape
    fig, axes = plt.subplots(
        n_outputs,
        n_inputs,
        figsize=(4.2 * n_inputs, 3.4 * n_outputs),
        squeeze=False,
        sharex=True,
    )
    fig.suptitle(title)

    dbodemag(reference, omega, sample_time, axes=axes)
    freq_hz = omega / (2.0 * np.pi)
    for row in range(n_outputs):
        for col in range(n_inputs):
            axis = axes[row, col]
            if axis.lines:
                axis.lines[0].set_label("TRUE")
            for label, response, color in responses:
                mag = 20.0 * np.log10(np.maximum(np.abs(response[row, col, :]), 1e-12))
                axis.semilogx(freq_hz, mag, color=color, linewidth=1.1, label=label)
            if row == 0:
                axis.set_title(f"From: In({col + 1})")
            if col == 0:
                axis.set_ylabel(f"To: Out({row + 1})\nMagnitude (dB)")
            if row == n_outputs - 1:
                axis.set_xlabel("Frequency (Hz)")

    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right")
    fig.tight_layout()
    plt.show()
