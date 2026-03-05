import numpy as np
import pytest

from pbsid.lti.modx import modx


def test_modx_single_matrix_truncates_rows():
    X = np.arange(30, dtype=np.float64).reshape(5, 6)
    x = modx(X, 3)
    assert not isinstance(x, list)
    assert x.shape == (3, 6)
    np.testing.assert_allclose(x, X[:3, :])


def test_modx_batch_truncates_each_entry():
    X1 = np.arange(20, dtype=np.float64).reshape(4, 5)
    X2 = np.arange(30, dtype=np.float64).reshape(6, 5)
    out = modx([X1, X2], 2)

    assert isinstance(out, list)
    assert out[0].shape == (2, 5)
    assert out[1].shape == (2, 5)
    np.testing.assert_allclose(out[0], X1[:2, :])
    np.testing.assert_allclose(out[1], X2[:2, :])


def test_modx_rejects_invalid_order():
    X = np.ones((3, 4), dtype=np.float64)
    with pytest.raises(ValueError, match="System order of zero or lower"):
        modx(X, 0)


def test_modx_rejects_when_n_exceeds_rows():
    X = np.ones((2, 5), dtype=np.float64)
    with pytest.raises(ValueError, match="number of rows of matrix X"):
        modx(X, 3)


def test_modx_rejects_non_2d():
    with pytest.raises(ValueError, match="expects a 2D matrix"):
        modx(np.array([1.0, 2.0, 3.0]), 1)