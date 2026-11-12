import dataclasses
import math
from fractions import Fraction as F

import numpy as np
import pytest

from tagsim import AgentSpec, BestResponseVsPP, Scripted, pure_pursuit, simulate
from tagsim.best_response import advance, chaser_decisions
from test_strategies import make_obs


def engine_min_sep(res):
    r, t = res.x_E - res.x_C, res.times
    best = np.linalg.norm(r[0])
    for i in range(len(t) - 1):
        if t[i + 1] > t[i]:
            w = (r[i + 1] - r[i]) / (t[i + 1] - t[i])
            s = np.clip(-(r[i] @ w) / (w @ w), 0, t[i + 1] - t[i]) if w @ w > 0 else 0.0
            best = min(best, np.linalg.norm(r[i] + s * w))
    return best


@pytest.mark.parametrize("tau_C,tau_E,phi_C", [("1", "1/4", "0"), ("7/5", "1/2", "3/10"), ("3/2", "1", "1/4")])
def test_rollout_matches_engine(tau_C, tau_E, phi_C):
    # Same open-loop runner plans through advance() and through the engine.
    R_C, R_E, eps, legs = 1.5, 1.0, 0.1, 12
    rng = np.random.default_rng(1)
    N = 40
    ang = rng.uniform(0, 2 * np.pi, (N, legs))
    sp = rng.uniform(0, 1, (N, legs))
    V = R_E * sp[..., None] * np.stack([np.cos(ang), np.sin(ang)], axis=-1)
    tau_C, tau_E, phi_C = F(tau_C), F(tau_E), F(phi_C)
    vc0 = np.array([0.0, R_C])
    C = AgentSpec(R_C, tau_C, first_decision=phi_C, initial_velocity=vc0)
    E = AgentSpec(R_E, tau_E)

    e = np.tile([3.0, 1.0], (N, 1))
    c = np.zeros((N, 2))
    vc = np.tile(vc0, (N, 1))
    hit = np.full(N, np.inf)
    ctimes = chaser_decisions(phi_C, tau_C, legs * tau_E)
    for j in range(legs):
        e, c, vc, h, _ = advance(e, c, vc, V[:, j], j * tau_E, (j + 1) * tau_E, ctimes, R_C, eps)
        hit = np.minimum(hit, h)

    for i in range(N):
        res = simulate(C, E, [0, 0], [3, 1], eps, legs * tau_E, pure_pursuit, Scripted(V[i]))
        if res.captured:
            assert hit[i] == pytest.approx(res.capture_time, abs=1e-12)
        else:
            assert np.isinf(hit[i])
            np.testing.assert_allclose(e[i], res.x_E[-1], atol=1e-12)
            np.testing.assert_allclose(c[i], res.x_C[-1], atol=1e-12)
    assert np.isfinite(hit).any() and np.isinf(hit).any()  # both outcomes exercised


def test_plan_prediction_matches_engine():
    # Execute the planner's own best open-loop plan in the engine: the predicted
    # survival and min separation must be what actually happens.
    br = BestResponseVsPP(n_dirs=16, beam=16, depth=8)
    o = make_obs([2.5, 0.5], [0, 0], vel_opp=[1.6, 0], R=1.0, period="1/2", R_opp=1.6,
                 period_opp="6/5", next_opp="2/5", eps=0.5)
    plan, survived, msep = br.plan(o)
    C = AgentSpec(1.6, "6/5", first_decision="2/5", initial_velocity=[1.6, 0])
    res = simulate(C, AgentSpec(1.0, "1/2"), [0, 0], [2.5, 0.5], 0.5, 4, pure_pursuit, Scripted(plan))
    assert res.captured != survived
    if survived:
        assert engine_min_sep(res) == pytest.approx(msep, abs=1e-12)


def test_simultaneous_decision_ignores_stale_chaser_velocity():
    # Chaser decides now (next_opp == t): its old velocity is irrelevant to the
    # future, so it must not affect the plan. When it's mid-commitment it must.
    br = BestResponseVsPP(n_dirs=16, beam=8, depth=4)
    kw = dict(R=1.0, period="1/2", R_opp=1.5, period_opp=1, eps=0.3)
    a = br(make_obs([2, 1], [0, 0], vel_opp=[1.5, 0], next_opp=0, **kw))
    b = br(make_obs([2, 1], [0, 0], vel_opp=[0, -1.5], next_opp=0, **kw))
    np.testing.assert_array_equal(a, b)
    c = br(make_obs([2, 1], [0, 0], vel_opp=[1.5, 0], next_opp="1/2", **kw))
    d = br(make_obs([2, 1], [0, 0], vel_opp=[0, -1.5], next_opp="1/2", **kw))
    assert not np.allclose(c, d)


def test_deterministic_admissible_and_stateless():
    br = BestResponseVsPP(n_dirs=12, speeds=(1.0, 0.5, 0.0), beam=8, depth=4)
    o = make_obs([1, 2], [0, 0], vel_opp=[1, 1], R=0.9, period="1/3", R_opp=1.3, period_opp=1,
                 next_opp="1/7", eps=0.2)
    v = br(o)
    assert np.linalg.norm(v) <= 0.9 + 1e-12
    v[:] = 7
    np.testing.assert_array_equal(br(o), br(dataclasses.replace(o)))
    assert not np.allclose(br(o), 7)


def test_never_escapes_below_extended_threshold():
    # Spec §B.2b: PP captures every runner when alpha_C <= 2s/(1+s). The planner
    # is the strongest runner we have; it must still lose, within the bound.
    s, eps = 1.5, 1.0
    alpha = F(2) * F(3, 2) / (1 + F(3, 2))  # = 6/5, exactly on the bound
    C, E = AgentSpec(s, alpha), AgentSpec(1.0, alpha / 4)
    res = simulate(C, E, [0, 0], [6, 2], eps, 60, pure_pursuit, BestResponseVsPP(beam=16))
    assert res.captured
    K = math.ceil(max(np.hypot(6, 2) - s * float(alpha), 0) / ((s - 1) * float(alpha)))
    assert res.capture_time <= (K + 2) * float(alpha) + 1e-9


def test_best_pass_matches_grid():
    from tagsim.best_response import best_pass, pass_margin
    for s in (1.05, 1.5, 2.0, 10.0):
        y, g = best_pass(s)
        grid = np.linspace(1e-6, s - 1e-6, 200001)
        assert g == pytest.approx(pass_margin(grid, s).max(), abs=1e-9)
    assert best_pass(2.0)[1] > 0.25 and best_pass(1e4)[1] == pytest.approx(0.25, abs=1e-4)


@pytest.mark.parametrize("s,alpha", [(1.5, "9/5"), (2.0, "2"), (1.2, "3/2")])
def test_symmetric_pass_evades_forever(s, alpha):
    # spec §B.3a: periodic orbit exists iff alpha_C > 1/sqrt(G(s)); here with >= 4% margin
    from tagsim.best_response import SymmetricPass
    tau = F(alpha)
    run = SymmetricPass(s, 1.0, float(tau))
    assert run.miss > 1.04  # eps = 1: not a near-tangency
    res = simulate(AgentSpec(s, tau), AgentSpec(1.0, tau), [0, 0], [run.D, 0], 1.0, 3000 * tau,
                   pure_pursuit, run)
    assert not res.captured and res.n_intervals == 3000
    seps = np.linalg.norm(res.x_E - res.x_C, axis=1)
    np.testing.assert_allclose(seps, run.D, rtol=1e-11)  # separation at every decision is D
    assert engine_min_sep(res) == pytest.approx(run.miss, rel=1e-9)


def test_symmetric_pass_below_its_threshold_is_caught():
    from tagsim.best_response import SymmetricPass, best_pass
    s = 1.5
    alpha = 0.98 / math.sqrt(best_pass(s)[1])
    tau = F(repr(alpha))
    run = SymmetricPass(s, 1.0, alpha)
    assert run.miss < 1.0
    res = simulate(AgentSpec(s, tau), AgentSpec(1.0, tau), [0, 0], [run.D, 0], 1.0, 10 * tau,
                   pure_pursuit, run)
    assert res.captured and res.capture_time < float(tau)


@pytest.mark.parametrize("hold,complete,escapes", [(False, False, False), (True, False, False),
                                                    (False, True, False), (True, True, True)])
def test_both_planner_fixes_needed_near_threshold(hold, complete, escapes):
    # Regression for the two Stage 3 planner defects, started on a verified escape
    # orbit (s = 1.5, a = 1/4, aligned clocks, alpha_C = 1.6 vs alpha*_4 ~ 1.5595).
    # At this (small) search size each fix alone still loses; with a larger search
    # (48 dirs, beam 64, 4 periods) rollout ranking alone does escape -- see
    # results/stage3/planner_ablation.txt.
    alpha = F(8, 5)
    D = 1.04 * float(alpha)  # the m = 4 orbit's separation, in units R_E tau_C
    res = simulate(AgentSpec(1.5, alpha), AgentSpec(1.0, alpha / 4), [0, 0], [D, 0], 1.0, 30 * alpha,
                   pure_pursuit, BestResponseVsPP(n_dirs=24, beam=32, hold_action=hold,
                                                  complete_partial_plans=complete))
    assert res.captured != escapes


def test_exact_certificate_reproduces_closed_form_orbit():
    # The symmetric pass as a 1-leg orbit row; exact certification must land on
    # alpha_sym(s) (to the 4 certified decimals) with exact closure (asserted inside).
    import sys
    sys.path.insert(0, "experiments")
    import stage3
    from tagsim.best_response import SymmetricPass, best_pass
    s = 1.5
    sp = SymmetricPass(s, 1.0, 1.0)
    w = 2 * sp.D * math.cos(sp.theta)
    v = np.array([-w * math.cos(sp.theta) + s, w * math.sin(sp.theta)])
    row = dict(s=s, m=1, headings=[[math.atan2(v[1], v[0])]], speeds=[[min(1.0, np.linalg.norm(v))]])
    c = stage3.certify(row)
    a_sym = 1 / math.sqrt(best_pass(s)[1])
    assert a_sym <= c["alpha_c_float"] <= a_sym + 2e-4
    assert c["clearance"] == pytest.approx(math.sqrt(best_pass(s)[1]), rel=1e-6)
