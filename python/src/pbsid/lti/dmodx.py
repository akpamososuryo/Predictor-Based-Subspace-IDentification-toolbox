from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .modx import modx

ArrayF64 = NDArray[np.float64]


def dmodx(X: ArrayLike | Sequence[ArrayLike], n: int) -> ArrayF64 | list[ArrayF64]:
    """Estimate/truncate the state sequence to system order ``n``.

    MATLAB parity target: ``dmodx.m``.
    """
    return modx(X, n)
