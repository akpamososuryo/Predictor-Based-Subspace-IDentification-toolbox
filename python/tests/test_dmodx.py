from __future__ import annotations

import numpy as np
import pytest

from pbsid.lti.dmodx import dmodx


def test_dmodx_single_matrix_truncates_rows() -> None:
    x = np.arange(30, dtype=np.float64).reshape(5, 6)
    out = dmodx(x, 3)
    assert out.shape == (3, 6)
    np.testing.assert_allclose(out, x[:3, :])


def test_dmodx_batch_truncates_each_entry() -> None:
    x1 = np.arange(20, dtype=np.float64).reshape(4, 5)
    x2 = np.arange(30, dtype=np.float64).reshape(6, 5)

    out = dmodx([x1, x2], 2)

    assert isinstance(out, list)
    assert out[0].shape == (2, 5)
    assert out[1].shape == (2, 5)
    np.testing.assert_allclose(out[0], x1[:2, :])
    np.testing.assert_allclose(out[1], x2[:2, :])


def test_dmodx_rejects_invalid_order() -> None:
    x = np.ones((3, 4), dtype=np.float64)
    with pytest.raises(ValueError, match="System order of zero or lower"):
        _ = dmodx(x, 0)


def test_dmodx_rejects_when_n_exceeds_rows() -> None:
    x = np.ones((2, 5), dtype=np.float64)
    with pytest.raises(ValueError, match="number of rows of matrix X"):
        _ = dmodx(x, 3)
