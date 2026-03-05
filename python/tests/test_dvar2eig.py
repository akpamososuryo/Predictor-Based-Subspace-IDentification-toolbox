from __future__ import annotations

import numpy as np
import pytest

from pbsid.lti.dvar2eig import dvar2eig


def test_dvar2eig_returns_expected_shapes() -> None:
    a = np.array([[0.8, 0.0], [0.0, 0.6]], dtype=np.float64)
    p = np.eye(4, dtype=np.float64) * 1e-3

    e, cov_e = dvar2eig(p, a)

    assert e.shape == (2,)
    assert cov_e.shape == (4, 4)
    assert np.all(np.isfinite(np.real(e)))
    assert np.all(np.isfinite(np.imag(e)))
    assert np.all(np.isfinite(cov_e))


def test_dvar2eig_matches_eigenvalues() -> None:
    a = np.array([[0.85, 0.0], [0.0, 0.25]], dtype=np.float64)
    p = np.eye(4, dtype=np.float64)

    e, _ = dvar2eig(p, a)

    np.testing.assert_allclose(np.sort(np.real(e)), np.array([0.25, 0.85]), atol=1e-12, rtol=0.0)


def test_dvar2eig_uses_top_left_p_block_only() -> None:
    a = np.array([[0.8, 0.0], [0.0, 0.6]], dtype=np.float64)

    p_small = np.eye(4, dtype=np.float64) * 1e-4
    p_big = np.zeros((6, 6), dtype=np.float64)
    p_big[:4, :4] = p_small
    p_big[4:, 4:] = np.eye(2, dtype=np.float64) * 1e9

    _, cov_small = dvar2eig(p_small, a)
    _, cov_big = dvar2eig(p_big, a)

    np.testing.assert_allclose(cov_big, cov_small, atol=1e-12, rtol=1e-12)


def test_dvar2eig_rejects_non_square_a() -> None:
    p = np.eye(4, dtype=np.float64)
    a = np.ones((2, 3), dtype=np.float64)

    with pytest.raises(ValueError, match="square"):
        _ = dvar2eig(p, a)


def test_dvar2eig_rejects_small_p() -> None:
    a = np.eye(2, dtype=np.float64)
    p = np.eye(3, dtype=np.float64)

    with pytest.raises(ValueError, match=r"n\^2"):
        _ = dvar2eig(p, a)
