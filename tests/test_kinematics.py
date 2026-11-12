import math

import numpy as np
import pytest

from tagsim import first_contact, min_separation


def test_head_on():
    # gap 10, closing at 2, radius 1 -> contact when gap hits 1
    assert first_contact([10, 0], [-2, 0], 1.0, 100.0) == pytest.approx(4.5, abs=1e-15)


def test_moving_apart_never_contacts():
    assert first_contact([10, 0], [2, 0], 1.0, 1e9) is None


def test_zero_relative_velocity():
    assert first_contact([3, 4], [0, 0], 1.0, 1e9) is None
    assert first_contact([0.3, 0.4], [0, 0], 1.0, 1e9) == 0.0


def test_already_inside_or_on_boundary():
    assert first_contact([0.5, 0], [5, 0], 1.0, 1.0) == 0.0
    assert first_contact([1.0, 0], [5, 0], 1.0, 1.0) == 0.0  # |r| == eps counts


def test_pass_through_missed_by_endpoint_check():
    # Both endpoints are ~5 away; the path cuts through the disk mid-interval.
    r0, w, eps, dt = np.array([-5.0, 0.5]), np.array([1.0, 0.0]), 1.0, 10.0
    assert np.linalg.norm(r0) > eps and np.linalg.norm(r0 + dt * w) > eps
    s = first_contact(r0, w, eps, dt)
    assert s == pytest.approx(5 - math.sqrt(0.75), abs=1e-14)


def test_interval_end_is_inclusive():
    assert first_contact([10, 0], [-2, 0], 1.0, 4.5) == pytest.approx(4.5)
    assert first_contact([10, 0], [-2, 0], 1.0, 4.5 - 1e-9) is None


def test_near_tangent():
    # line y = 1 + delta: closest approach 1 + delta
    for delta, hit in [(1e-9, False), (-1e-9, True)]:
        s = first_contact([-10, 1 + delta], [1, 0], 1.0, 100.0)
        assert (s is not None) == hit
    # grazing hit lands near x = 0
    s = first_contact([-10, 1 - 1e-9], [1, 0], 1.0, 100.0)
    assert abs(s - 10) < 1e-3


def test_large_scale_root_is_accurate():
    # far approach, tiny radius: the naive root formula loses everything here
    r0, w, eps = np.array([1e6, 1e-4]), np.array([-1.0, 0.0]), 1e-3
    s = first_contact(r0, w, eps, 2e6)
    assert s is not None
    assert np.linalg.norm(r0 + s * w) == pytest.approx(eps, rel=1e-6)


def test_matches_dense_sampling():
    rng = np.random.default_rng(12345)
    for _ in range(2000):
        r0 = rng.uniform(-5, 5, 2)
        w = rng.uniform(-3, 3, 2)
        eps = rng.uniform(0.1, 2)
        dt = rng.uniform(0.1, 5)
        s = first_contact(r0, w, eps, dt)
        grid = np.linspace(0, dt, 4001)
        dist = np.linalg.norm(r0[None] + grid[:, None] * w[None], axis=1)
        inside = np.nonzero(dist <= eps - 1e-9)[0]
        if len(inside):
            assert s is not None and s <= grid[inside[0]] + 1e-12
        if s is not None:
            assert np.linalg.norm(r0 + s * w) <= eps + 1e-9
            # nothing strictly earlier is inside
            early = grid < s - 1e-9
            assert np.all(dist[early] >= eps - 1e-9)
        else:
            assert np.all(dist > eps - 1e-9)


def test_min_separation():
    s, dmin = min_separation([-10, 1], [1, 0], 100.0)
    assert s == pytest.approx(10) and dmin == pytest.approx(1)
    s, dmin = min_separation([-10, 1], [1, 0], 4.0)  # clipped to interval end
    assert s == 4.0 and dmin == pytest.approx(math.hypot(6, 1))


def test_almost_immediate_contact():
    # starts 1e-12 outside the disk, closing at unit speed
    s = first_contact([1 + 1e-12, 0], [-1, 0], 1.0, 1.0)
    assert s == pytest.approx(1e-12, rel=1e-3)
