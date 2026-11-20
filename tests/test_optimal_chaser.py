"""Stage 5: the optimal-chaser problem (theory/stage5_optimal_chaser.md)."""

import math

import pytest

from tagsim import AgentSpec, Intercept, flee, simulate
from tagsim.best_response import SymmetricPass, best_pass
from tagsim.strategies import hybrid_pursuit


@pytest.mark.parametrize("s", [1.05, 1.5, 3.0])
@pytest.mark.parametrize("alpha", [5, 50, 500])
def test_intercept_beats_flee_at_large_alpha(s, alpha):
    # Proposition 11: reading the runner's velocity catches straight flight at any
    # alpha_C. H only reads position, and above alpha_C = s it brakes forever here.
    tau = alpha
    res = simulate(AgentSpec(s, tau), AgentSpec(1.0, 10_000), [0, 0], [1.5 * tau, 0], 1.0,
                   2000 * tau, Intercept(), flee)
    assert res.captured
    assert res.capture_time < 30 * alpha


@pytest.mark.parametrize("s,alpha", [(2.0, 1.801), (2.0, 1.99)])
def test_intercept_loses_to_symmetric_pass_below_s(s, alpha):
    # Inside H's guarantee region Intercept still loses to the symmetric pass: it
    # extrapolates a velocity the runner changes every period.
    assert alpha <= s
    tau = alpha
    sp = SymmetricPass(s, 1.0, tau)
    res_intercept = simulate(AgentSpec(s, tau), AgentSpec(1.0, tau), [0, 0], [sp.D, 0], 1.0,
                             400 * tau, Intercept(), sp)
    res_hybrid = simulate(AgentSpec(s, tau), AgentSpec(1.0, tau), [0, 0], [sp.D, 0], 1.0,
                          400 * tau, hybrid_pursuit, sp)
    assert res_hybrid.captured          # H's proven guarantee holds here (Thm 3)
    assert not res_intercept.captured   # Intercept fails on the same instance


def test_symmetric_pass_still_escapes_intercept_above_alpha_sym():
    # Above alpha_sym the orbit beats PP (Thm 2), and Intercept too.
    s = 1.5
    y, g = best_pass(s)
    alpha_sym = 1 / math.sqrt(g)
    alpha = alpha_sym + 0.02
    tau = alpha
    sp = SymmetricPass(s, 1.0, tau)
    res = simulate(AgentSpec(s, tau), AgentSpec(1.0, tau), [0, 0], [sp.D, 0], 1.0, 400 * tau,
                   Intercept(), sp)
    assert not res.captured
