"""Stage 4A: one-period geometry of the aligned one-decision game and the
statements of theory/stage4_viability_analysis.md that can be checked directly."""

import math
import sys
from fractions import Fraction as F

import numpy as np
import pytest

from tagsim import AgentSpec, min_separation, pure_pursuit, simulate
from tagsim.viability import C, T, alpha_sym, g, heading, pass_step, plateau_interval, y_star

sys.path.insert(0, "experiments")
import stage4a  # noqa: E402

S = (1.5, 2.0)


def test_pass_step_matches_engine_kinematics():
    rng = np.random.default_rng(11)
    for _ in range(200):
        s, D = rng.uniform(1.05, 3), rng.uniform(0.1, 5)
        r, ph = math.sqrt(rng.random()), rng.uniform(0, 2 * math.pi)
        v = np.array([r * math.cos(ph), r * math.sin(ph)])
        cl, Dp = pass_step(D, v, s)
        assert cl == pytest.approx(min_separation([D, 0], v - [s, 0], 1.0)[1], abs=1e-12)
        assert Dp == pytest.approx(np.linalg.norm(np.array([D - s, 0]) + v), abs=1e-12)


@pytest.mark.parametrize("s", S)
def test_heading_parametrization(s):
    # y is the fixed point of the action; T_y and C_y are its exact one-period map and clearance
    for y in np.linspace((s - 1) / 2 + 1e-6, (s + 1) / 2 - 1e-6, 15):
        v = heading(y, s)
        assert np.linalg.norm(v) == pytest.approx(1, abs=1e-12)
        assert pass_step(y, v, s)[1] == pytest.approx(y, abs=1e-12)
        for D in (0.3 * y, y, 1.7 * y, 2.4 * y):
            cl, Dp = pass_step(D, v, s)
            assert Dp == pytest.approx(T(D, y, s), abs=1e-12)
            assert cl == pytest.approx(C(D, y, s), abs=1e-12)


@pytest.mark.parametrize("s", S)
def test_y_star_is_unique_maximizer(s):
    ys = y_star(s)
    grid = np.linspace((s - 1) / 2, (s + 1) / 2, 20001)
    vals = g(grid, s)
    assert vals.max() <= g(ys, s) + 1e-15
    assert abs(grid[vals.argmax()] - ys) < 1e-3
    assert g((s - 1) / 2, s) == pytest.approx(0, abs=1e-12) and g((s + 1) / 2, s) == pytest.approx(0, abs=1e-12)


@pytest.mark.parametrize("s", (1.2, 1.5, 2.0, 3.0))
def test_up_steps_bounded_by_psi(s):
    # Lemma U*: any step with D' >= D has closest approach <= Psi(D) <= sqrt(G)
    rng = np.random.default_rng(int(10 * s))
    ys, G = y_star(s), g(y_star(s), s)

    def psi(D):
        return D / s if D <= s / 2 else math.sqrt(max(g(D, s), 0.0))
    for _ in range(20000):
        r, ph = math.sqrt(rng.random()), rng.uniform(0, 2 * math.pi)
        D = rng.uniform(0.01, s + 1)
        cl, Dp = pass_step(D, [r * math.cos(ph), r * math.sin(ph)], s)
        if Dp >= D:
            assert D <= (s + 1) / 2 + 1e-12
            assert cl <= psi(min(D, ys)) + 1e-12 and cl <= math.sqrt(G) + 1e-12


@pytest.mark.parametrize("s", S)
def test_reachable_set_formula(s):
    # Proposition R: every safe end separation is a plateau value or a full-speed T_y(D)
    rng = np.random.default_rng(7)
    ys = np.linspace((s - 1) / 2, (s + 1) / 2, 20001)
    for _ in range(60):
        D, eps = rng.uniform(0.3, 2 * s), rng.uniform(0.25, 0.8)
        r, ph = np.sqrt(rng.random(20000)), rng.random(20000) * 2 * np.pi
        V = np.stack([r * np.cos(ph), r * np.sin(ph)], 1)
        w = V - [s, 0]
        t = np.clip(-(D * w[:, 0]) / (w * w).sum(1), 0, 1)
        safe = np.hypot(D + w[:, 0], w[:, 1])[np.hypot(D + t * w[:, 0], t * w[:, 1]) > eps]
        pl = plateau_interval(D, s)
        fs = T(D, ys, s)[C(D, ys, s) > eps]
        for x in safe[::25]:
            in_pl = pl is not None and pl[0] - 1e-9 <= x <= pl[1] + 1e-9
            assert in_pl or (fs.size and np.abs(fs - x).min() < 1e-3)


@pytest.mark.parametrize("s", S)
def test_below_threshold_every_safe_step_goes_down(s):
    # Theorem 6(b): for alpha < alpha_sym no safe step keeps or raises D
    eps = 1 / (0.99 * alpha_sym(s))
    ys = np.linspace((s - 1) / 2, (s + 1) / 2, 4001)
    for D in np.linspace(eps * 1.0001, s + 1, 400):
        ok = C(D, ys, s) > eps
        assert np.all(T(D, ys[ok], s) < D)


@pytest.mark.parametrize("s", ("3/2", "2"))
def test_boundary_chain_high_precision(s):
    # Theorem 6(c): at alpha = alpha_sym the chain stays strictly safe and contracts to y*
    worst, a, (rmin, rmax) = stage4a.chain_decimal(F(s), steps=150, prec=160)
    assert worst > 0 and 0 < a < F(1, 10**40)
    assert 0.45 < rmin <= rmax < 0.55


def test_boundary_chain_in_engine():
    s = 2.0
    a_s = alpha_sym(s)
    for f, caught in ((1.0, False), (0.999, True)):
        tau = F(repr(a_s * f))
        res = simulate(AgentSpec(s, tau), AgentSpec(1.0, tau), [0, 0], [(y_star(s) + 0.01) * float(tau), 0], 1.0,
                       25 * tau, pure_pursuit, stage4a.BoundaryChain(s, tau))
        assert res.captured == caught


def test_period_one_set_matches_g():
    s = 2.0
    lo, hi = stage4a.fixed_point_interval(s, 1.01 * alpha_sym(s))
    eps2 = 1 / (1.01 * alpha_sym(s)) ** 2
    assert g(lo, s) == pytest.approx(eps2, abs=1e-12) and g(hi, s) == pytest.approx(eps2, abs=1e-12)
    assert stage4a.fixed_point_interval(s, 0.999 * alpha_sym(s)) is None
