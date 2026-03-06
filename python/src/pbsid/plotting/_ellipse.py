from __future__ import annotations

import numpy as np
from matplotlib.axes import Axes
from scipy.stats import chi2


def plot_covariance_ellipse(
    ax: Axes,
    cov: np.ndarray,
    center: np.ndarray,
    *,
    confidence: float,
    color: str = "k",
    linewidth: float = 0.9,
    alpha: float = 1.0,
) -> None:
    cov_arr = np.asarray(cov, dtype=np.float64)
    center_arr = np.asarray(center, dtype=np.float64).reshape(2)
    if cov_arr.shape != (2, 2):
        raise ValueError(f"Expected a 2x2 covariance matrix, received shape {cov_arr.shape}.")

    conf = float(np.clip(confidence, 1e-9, 1.0 - 1e-9))
    scale = float(np.sqrt(chi2.ppf(conf, df=2)))

    eigvals, eigvecs = np.linalg.eigh(cov_arr)
    radii = scale * np.sqrt(np.maximum(eigvals, 0.0))

    theta = np.linspace(0.0, 2.0 * np.pi, 200, dtype=np.float64)
    circle = np.vstack((np.cos(theta), np.sin(theta)))
    ellipse = eigvecs @ np.diag(radii) @ circle
    ax.plot(
        center_arr[0] + ellipse[0, :],
        center_arr[1] + ellipse[1, :],
        color=color,
        linewidth=linewidth,
        alpha=alpha,
    )