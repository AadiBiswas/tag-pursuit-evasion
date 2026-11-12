import dataclasses
import math
from fractions import Fraction as F

import numpy as np
import pytest

from tagsim import (AgentSpec, Constant, Intercept, Observation, Perpendicular, PredictiveEvasion,
                    Scripted, braking_pursuit, contact_time, flee, pure_pursuit, simulate)


def make_obs(pos_self, pos_opp, vel_opp=None, R=1.0, period=1, R_opp=1.0, period_opp=1,
             t=0, next_opp=None, eps=0.1):
    def ro(v):
        if v is None:
            return None
        a = np.array(v, dtype=float)
        a.setflags(write=False)
        return a

    t = F(t)
    return Observation(t=t, role="X", k=0, pos_self=ro(pos_self), pos_opp=ro(pos_opp), vel_self=None,
                       vel_opp=ro(vel_opp), next_opp=t + F(period_opp) if next_opp is None else F(next_opp),
                       spec_self=AgentSpec(R, period), spec_opp=AgentSpec(R_opp, period_opp), eps=eps)


def speeds(res, agent):
    return [np.linalg.norm(e["velocity"]) for e in res.events
            if e["kind"] == "decision" and e["agent"] == agent]


def test_pure_pursuit_and_flee_directions():
    o = make_obs([1, 1], [4, 5], R=2.0)
    np.testing.assert_allclose(pure_pursuit(o), [1.2, 1.6])
    np.testing.assert_allclose(flee(o), [-1.2, -1.6])


def test_zero_separation_gives_zero_velocity():
    o = make_obs([1, 1], [1, 1], vel_opp=[0, 0])
    for pol in (pure_pursuit, braking_pursuit, Intercept(), flee):
        np.testing.assert_array_equal(pol(o), [0, 0])


def test_braking_speed():
    # far: R*tau = 2 < d = 5 -> full speed; near: d = 0.5 -> 0.5 / tau
    np.testing.assert_allclose(braking_pursuit(make_obs([0, 0], [5, 0], R=2.0, period=1)), [2, 0])
    np.testing.assert_allclose(braking_pursuit(make_obs([0, 0], [0.5, 0], R=2.0, period=1)), [0.5, 0])
    np.testing.assert_allclose(braking_pursuit(make_obs([0, 0], [0.5, 0], R=2.0, period="1/4")), [2, 0])


def test_overshoot_vs_braking():
    # One chaser interval, runner sidesteps at unit speed; nobody gets within eps.
    # PP flies to (4, 0), well past where it saw the runner; braking stops on (1, 0).
    C, E = AgentSpec(2.0, 2), AgentSpec(1.0, 2)
    ends = {}
    for name, pol in [("pp", pure_pursuit), ("brake", braking_pursuit)]:
        res = simulate(C, E, [0, 0], [1, 0], 0.01, 2, pol, Constant([0, 1]))
        assert not res.captured
        ends[name] = res.x_C[-1]
    np.testing.assert_allclose(ends["pp"], [4, 0])
    np.testing.assert_allclose(ends["brake"], [1, 0])


def test_braking_uses_own_period_under_async_clocks():
    C = AgentSpec(2.0, "1/3")
    E = AgentSpec(1.0, "1/2", first_decision="1/4", initial_velocity=[0, 1])
    rng = np.random.default_rng(0)
    ang = rng.uniform(0, 2 * np.pi, 40)
    res = simulate(C, E, [0, 0], [1.5, 0], 0.05, 6, braking_pursuit,
                   Scripted(np.c_[np.cos(ang), np.sin(ang)]))
    for e in (e for e in res.events if e["kind"] == "decision" and e["agent"] == "C"):
        xc, xe = res.positions_at(F(e["t"]))
        d = np.linalg.norm(xe - xc)
        assert np.linalg.norm(e["velocity"]) == pytest.approx(min(2.0, d * 3))
    assert min(speeds(res, "C")) < 2.0  # braking actually engaged


def test_braking_not_admissible_in_exact_mode():
    with pytest.raises(ValueError):
        simulate(AgentSpec(2.0, 1), AgentSpec(1.0, 1), [0, 0], [1, 0], 0.1, 1,
                 braking_pursuit, Constant([0, 1]), speed_mode="exact")


def test_contact_time_cases():
    assert contact_time(np.array([10.0, 0]), np.array([-1.0, 0]), 1.0, 1.0) == pytest.approx(4.5)
    assert contact_time(np.array([0.5, 0]), np.array([5.0, 0]), 1.0, 1.0) == 0.0
    # |v| == R: linear case
    assert contact_time(np.array([3.0, 0]), np.array([-1.0, 0]), 1.0, 0.0) == pytest.approx(1.5)
    assert contact_time(np.array([3.0, 0]), np.array([0.0, 1]), 1.0, 0.0) is None
    # faster target: catchable only if it comes toward us
    assert contact_time(np.array([-10.0, 0]), np.array([2.0, 0]), 1.0, 1.0) == pytest.approx(3.0)
    assert contact_time(np.array([10.0, 0]), np.array([2.0, 0]), 1.0, 1.0) is None


def test_intercept_with_stationary_or_uncommitted_runner_is_pure_pursuit():
    for vel in (None, [0, 0]):
        o = make_obs([0, 0], [3, 4], vel_opp=vel, R=1.5)
        np.testing.assert_allclose(Intercept()(o), pure_pursuit(o))


def test_intercept_hits_predicted_contact_time():
    # Runner committed to (0, 0.8) for the whole game; chaser re-solves every 1/4
    # and should keep aiming at the same contact point.
    vE = np.array([0.0, 0.8])
    t_star = contact_time(np.array([3.0, 0]), vE, 0.9, 0.6)
    E = AgentSpec(1.0, 100, first_decision=100, initial_velocity=vE)
    res = simulate(AgentSpec(0.9, "1/4"), E, [0, 0], [3, 0], 0.6, 20, Intercept(), Constant([0, 0]))
    assert res.capture_time == pytest.approx(t_star, abs=1e-9)
    pp = simulate(AgentSpec(0.9, "1/4"), E, [0, 0], [3, 0], 0.6, 20, pure_pursuit, Constant([0, 0]))
    assert not pp.captured or pp.capture_time > t_star


def test_intercept_falls_back_when_impossible_or_beyond_horizon():
    # faster runner heading straight away
    o = make_obs([0, 0], [5, 0], vel_opp=[2, 0], R=1.0)
    np.testing.assert_allclose(Intercept()(o), pure_pursuit(o))
    # catchable at t = 4.5-ish, but not within a horizon of 1
    o = make_obs([0, 0], [5, 0], vel_opp=[0, 0.5], R=1.0, eps=0.1)
    t = contact_time(o.pos_opp - o.pos_self, o.vel_opp, 1.0, 0.1)
    assert t > 1
    np.testing.assert_allclose(Intercept(horizon=1)(o), pure_pursuit(o))
    assert Intercept(horizon=t + 1)(o)[1] > 0  # leads the target


def test_intercept_does_not_see_simultaneous_choice():
    seen = []

    def chaser(obs):
        seen.append(obs)
        return Intercept()(obs)

    E = AgentSpec(1.0, 1, first_decision=1, initial_velocity=[0, 1])
    res = simulate(AgentSpec(1.5, 1), E, [0, 0], [5, 0], 0.1, 2, chaser, Scripted([[0, -1]]))
    at_one = [o for o in seen if o.t == 1][0]
    np.testing.assert_array_equal(at_one.vel_opp, [0, 1])  # old commitment, not the new (0, -1)
    chosen = [e["velocity"] for e in res.events if e.get("agent") == "C" and e["t"] == "1"][0]
    np.testing.assert_allclose(chosen, Intercept()(at_one))
    leaked = Intercept()(dataclasses.replace(at_one, vel_opp=np.array([0.0, -1.0])))
    assert not np.allclose(chosen, leaked)


def test_perpendicular_sides():
    o = make_obs([1, 0], [0, 0], R=2.0)
    np.testing.assert_allclose(Perpendicular(1)(o), [0, 2])
    np.testing.assert_allclose(Perpendicular(-1)(o), [0, -2])
    o = make_obs([3, 4], [0, 0])
    assert Perpendicular()(o) @ np.array([3, 4]) == pytest.approx(0)
    with pytest.raises(ValueError):
        Perpendicular(0)


def test_predictive_evasion_flees_when_unthreatened():
    # Stationary chaser that won't move again within the lookahead: every
    # heading ties at the current separation, tie-break gives straight away.
    o = make_obs([3, 4], [0, 0], vel_opp=[0, 0], R=1.0, period="1/2", next_opp=10)
    np.testing.assert_allclose(PredictiveEvasion()(o), flee(o), atol=1e-12)


def test_predictive_evasion_against_stationary_then_pursuing_chaser():
    # Chaser at rest now, pure pursuit from t = 0.2 on: running straight away is best.
    o = make_obs([3, 0], [0, 0], vel_opp=[0, 0], R=1.0, period=2, R_opp=1.5, next_opp="0.2")
    np.testing.assert_allclose(PredictiveEvasion()(o), [1, 0], atol=1e-12)


def test_predictive_evasion_finds_tangent_sidestep():
    # Spec §B.3: chaser committed head-on at speed 2 for 3 time units, runner
    # (speed 1) at distance 4. Tangent heading is 60 deg off straight-away and
    # keeps min separation at exactly D/s = 2; fleeing drops to 1.
    o = make_obs([4, 0], [0, 0], vel_opp=[2, 0], R=1.0, period="1/10", R_opp=2.0, next_opp=3)
    v = PredictiveEvasion()(o)
    assert np.linalg.norm(v) == pytest.approx(1.0)
    assert math.degrees(math.atan2(v[1], v[0])) == pytest.approx(60, abs=1e-9)  # CCW wins the mirror tie

    C = AgentSpec(2.0, 3, first_decision=3, initial_velocity=[2, 0])
    E = AgentSpec(1.0, "1/10")
    res = simulate(C, E, [0, 0], [4, 0], 1.9, 3, Constant([0, 0]), PredictiveEvasion())
    assert not res.captured
    assert simulate(C, E, [0, 0], [4, 0], 1.9, 3, Constant([0, 0]), flee).captured


def test_predictive_evasion_is_deterministic_and_2d_only():
    o = make_obs([1, 2], [0, 0], vel_opp=[1, 1], R=1.0, period="1/3", R_opp=1.3, next_opp="1/7")
    np.testing.assert_array_equal(PredictiveEvasion()(o), PredictiveEvasion()(o))
    with pytest.raises(ValueError):
        PredictiveEvasion()(make_obs([1, 2, 3], [0, 0, 0]))
    with pytest.raises(ValueError):
        PredictiveEvasion(n_dirs=7)


@pytest.mark.parametrize("pol", [pure_pursuit, braking_pursuit, Intercept(), flee,
                                 Perpendicular(), PredictiveEvasion()])
def test_returned_velocity_is_a_fresh_array(pol):
    o = make_obs([1, 2], [-1, 0.5], vel_opp=[0.3, -0.2], R=0.9, R_opp=1.1, next_opp="1/2")
    v = pol(o)
    assert np.linalg.norm(v) <= 0.9 + 1e-12
    for arr in (o.pos_self, o.pos_opp, o.vel_opp):
        assert not np.shares_memory(v, arr)
    first = v.copy()
    v[:] = 99.0
    np.testing.assert_array_equal(pol(o), first)  # no hidden state to corrupt


def test_strategies_run_in_3d():
    C, E = AgentSpec(1.5, "1/3"), AgentSpec(1.0, "1/2")
    for chaser in (pure_pursuit, braking_pursuit, Intercept()):
        res = simulate(C, E, [0, 0, 0], [3, 4, 5], 0.5, 200, chaser, flee)
        assert res.captured
