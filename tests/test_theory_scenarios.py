"""Representative scenarios for the Stage 0 propositions.

These are consistency checks between the engine and the proofs in
stage0_spec.md. Passing them proves nothing universal; failing one means
either the engine or the proof is wrong.

"""

import math
import zlib
from fractions import Fraction as F

import numpy as np
import pytest

from tagsim import (AgentSpec, Constant, Perpendicular, PredictiveEvasion, Scripted, braking_pursuit, hybrid_pursuit,
                    flee, min_separation, pure_pursuit, simulate)


def separation(res, t):
    xc, xe = res.positions_at(t)
    return np.linalg.norm(xe - xc)


def random_script(rng, R, n, full_speed=False):
    ang = rng.uniform(0, 2 * np.pi, n)
    sp = R if full_speed else R * rng.uniform(0, 1, n)
    return Scripted(np.c_[sp * np.cos(ang), sp * np.sin(ang)])


def prop1_bound(res, R_C, R_E, tau_C, phi_C):
    """phi_C + (K+1) tau_C, K = ceil((D1 - R_C tau_C)^+ / ((R_C - R_E) tau_C))."""
    t1 = float(phi_C)
    if res.capture_time <= t1:
        return t1
    K = math.ceil(max(separation(res, t1) - R_C * tau_C, 0.0) / ((R_C - R_E) * tau_C))
    return t1 + (K + 1) * tau_C


# Proposition 1: R_C > R_E and R_E * tau_C <= eps  =>  PP captures within the bound.
# Several of these have R_C * tau_C > eps, i.e. the overshoot regime that the
# original R_C tau_C <= eps hypothesis excluded.
@pytest.mark.parametrize("R_C,tau_C", [(1.5, "1"), (1.5, "4/5"), (1.1, "1"), (3.0, "1/2"), (1.2, "1/4")])
@pytest.mark.parametrize("tau_E", ["1/20", "1/7", "3/10", "2"])
def test_prop1_pure_pursuit_captures_within_bound(R_C, tau_C, tau_E):
    R_E, eps = 1.0, 1.0
    tau_Cf = float(F(tau_C))
    assert R_E * tau_Cf <= eps
    rng = np.random.default_rng(zlib.crc32(repr((R_C, tau_C, tau_E)).encode()))
    for trial in range(15):
        phi_C = F(rng.integers(0, 8), 8) * F(tau_C)
        ang = rng.uniform(0, 2 * np.pi)
        C = AgentSpec(R_C, tau_C, first_decision=phi_C,
                      initial_velocity=[R_C * math.cos(ang), R_C * math.sin(ang)] if phi_C else None)
        phi_E = F(rng.integers(0, 8), 8) * F(tau_E)
        E = AgentSpec(R_E, tau_E, first_decision=phi_E,
                      initial_velocity=[R_E, 0.0] if phi_E else None)
        D0 = rng.uniform(1.5, 20)
        x_E0 = D0 * np.array([math.cos(ang + 1), math.sin(ang + 1)])
        H = float(phi_C) + (D0 + (R_C + R_E) * float(phi_C)) / (R_C - R_E) + 5 * tau_Cf + 5
        n_E = int(H / float(F(tau_E))) + 3
        runners = [flee, random_script(rng, R_E, n_E), random_script(rng, R_E, n_E, True),
                   Constant([0.0, R_E]), Constant([0.0, 0.0])]
        for runner in runners:
            res = simulate(C, E, [0, 0], x_E0, eps, H, pure_pursuit, runner)
            assert res.captured, (trial, runner)
            assert res.capture_time <= prop1_bound(res, R_C, R_E, tau_Cf, phi_C) + 1e-9


@pytest.mark.parametrize("R_C,tau_C,tau_E", [(1.5, "1", "1/7"), (1.2, "1/4", "1/20"), (3.0, "1/2", "2")])
def test_prop1_against_stage2_runners(R_C, tau_C, tau_E):
    R_E, eps = 1.0, 1.0
    rng = np.random.default_rng(zlib.crc32(repr(("stage2", R_C, tau_C, tau_E)).encode()))
    for _ in range(4):
        phi_C = F(rng.integers(0, 8), 8) * F(tau_C)
        ang = rng.uniform(0, 2 * np.pi)
        C = AgentSpec(R_C, tau_C, first_decision=phi_C,
                      initial_velocity=[R_C * math.cos(ang), R_C * math.sin(ang)] if phi_C else None)
        E = AgentSpec(R_E, tau_E)
        D0 = rng.uniform(1.5, 20)
        x_E0 = D0 * np.array([math.cos(ang + 1), math.sin(ang + 1)])
        H = float(phi_C) + (D0 + (R_C + R_E) * float(phi_C)) / (R_C - R_E) + 5 * float(F(tau_C)) + 5
        for runner in (Perpendicular(1), Perpendicular(-1), PredictiveEvasion()):
            res = simulate(C, E, [0, 0], x_E0, eps, H, pure_pursuit, runner)
            assert res.captured
            assert res.capture_time <= prop1_bound(res, R_C, R_E, float(F(tau_C)), phi_C) + 1e-9


# Spec §B.2a: braking pursuit satisfies Prop 1 with the same bound...
# Not at alpha_C = 1 exactly: there braking only *touches* the eps-ball (see
# test_braking_at_alpha_one_is_a_tie), so float rounding decides the outcome.
@pytest.mark.parametrize("R_C,tau_C", [(1.5, "9/10"), (1.2, "3/4"), (3.0, "1/2")])
def test_braking_satisfies_prop1(R_C, tau_C):
    R_E, eps = 1.0, 1.0
    rng = np.random.default_rng(zlib.crc32(repr(("brake", R_C, tau_C)).encode()))
    for _ in range(10):
        tau_E = rng.choice(["1/20", "1/3", "2"])
        D0 = rng.uniform(1.5, 20)
        x_E0 = D0 * np.array([math.cos(rng.uniform(0, 7)), math.sin(rng.uniform(0, 7))])
        H = (D0 + (R_C + R_E) * float(F(tau_C))) / (R_C - R_E) + 5 * float(F(tau_C)) + 5
        n_E = int(H / float(F(tau_E))) + 3
        for runner in (flee, Perpendicular(), random_script(rng, R_E, n_E)):
            res = simulate(AgentSpec(R_C, tau_C), AgentSpec(R_E, tau_E), [0, 0], x_E0, eps, H,
                           braking_pursuit, runner)
            assert res.captured
            assert res.capture_time <= prop1_bound(res, R_C, R_E, float(F(tau_C)), 0) + 1e-9


# ...and the condition is sharp for it: a collinear constant-velocity runner
# keeps separation >= min(D0, R_E tau_C) forever whenever R_E tau_C > eps,
# for any speed ratio. Pure pursuit catches the same runner.
@pytest.mark.parametrize("R_C,tau_C", [(1.2, "5/4"), (2.0, "5/4"), (5.0, "4"), (1.5, "1001/1000")])
def test_braking_sharpness_counterexample(R_C, tau_C):
    R_E, eps, D0 = 1.0, 1.0, 10.0
    C, E = AgentSpec(R_C, tau_C), AgentSpec(R_E, 1000)
    res = simulate(C, E, [0, 0], [D0, 0], eps, 300, braking_pursuit, Constant([R_E, 0]))
    assert not res.captured
    # collinear and linear between knots, so the minimum sits on a knot
    seps = np.linalg.norm(res.x_E - res.x_C, axis=1)
    assert seps.min() == pytest.approx(R_E * float(F(tau_C)), rel=1e-9)
    assert simulate(C, E, [0, 0], [D0, 0], eps, 300, pure_pursuit, Constant([R_E, 0])).captured


def test_braking_at_alpha_one_is_a_tie():
    # R_E tau_C == eps: separation bottoms out at exactly eps (capture in exact
    # arithmetic, a coin flip in floats). Pure pursuit captures strictly inside.
    C, E = AgentSpec(1.5, 1), AgentSpec(1.0, 1000)
    res = simulate(C, E, [0, 0], [10, 0], 1.0, 300, braking_pursuit, Constant([1, 0]))
    seps = np.linalg.norm(res.x_E - res.x_C, axis=1)
    assert seps.min() == pytest.approx(1.0, abs=1e-12)


def test_prop1_collinear_flee_hits_lower_bound():
    # Runner flees along the LOS; any chaser needs >= (D0 - eps)/(R_C - R_E).
    R_C, R_E, eps, D0 = 1.5, 1.0, 1.0, 20.0
    res = simulate(AgentSpec(R_C, "1"), AgentSpec(R_E, "1"), [0, 0], [D0, 0], eps, 100,
                   pure_pursuit, Constant([R_E, 0]))
    lower = (D0 - eps) / (R_C - R_E)
    assert lower <= res.capture_time <= prop1_bound(res, R_C, R_E, 1.0, 0)
    assert res.capture_time == pytest.approx(lower)  # collinear: PP is exactly optimal here


# B.3 matador geometry: one PP commitment, runner takes the tangent sidestep.
# Min separation is exactly D/s at sigma = D/R_C. This is a single-interval
# fact, not an escape theorem.
@pytest.mark.parametrize("R_C,R_E,D", [(2.0, 1.0, 4.0), (1.3, 1.0, 5.0)])
def test_tangent_sidestep_min_distance(R_C, R_E, D):
    s = R_C / R_E
    v_tan = [R_E**2 / R_C, R_E * math.sqrt(R_C**2 - R_E**2) / R_C]
    assert np.linalg.norm(v_tan) == pytest.approx(R_E)
    tau = 1.5 * D / R_C  # long commitment: R_E tau > eps for the eps used below
    sig, dmin = min_separation([D, 0], np.array(v_tan) - [R_C, 0], tau)
    assert sig == pytest.approx(D / R_C) and dmin == pytest.approx(D / s)

    C, E = AgentSpec(R_C, tau), AgentSpec(R_E, tau)
    for eps, hit in [(D / s * (1 - 1e-6), False), (D / s * (1 + 1e-6), True)]:
        assert R_E * tau > eps
        res = simulate(C, E, [0, 0], [D, 0], eps, tau, pure_pursuit, Constant(v_tan))
        assert res.captured == hit
        if hit:
            assert res.capture_time == pytest.approx(D / R_C, rel=1e-2)


# B.1 escape lemma: R_E >= R_C, runner flees from its first decision with D > eps.
@pytest.mark.parametrize("R_C", [1.0, 0.8])
def test_escape_lemma(R_C):
    R_E, eps, D0 = 1.0, 1.0, 1.2
    rng = np.random.default_rng(3)
    E = AgentSpec(R_E, "1/3")
    for chaser_period in ["1/10", "1/3", "7/9"]:
        C = AgentSpec(R_C, chaser_period)
        n = int(30 / float(F(chaser_period))) + 2
        for pol in [pure_pursuit, random_script(rng, R_C, n), random_script(rng, R_C, n, True)]:
            res = simulate(C, E, [0, 0], [D0, 0], eps, 30, pol, flee)
            assert not res.captured
            # separation at runner decision times is non-decreasing
            seps = [separation(res, F(e["t"]))
                    for e in res.events if e["kind"] == "decision" and e["agent"] == "E"]
            assert all(b >= a - 1e-12 for a, b in zip(seps, seps[1:]))


# Interception lemma (Case 4 window): runner on a known line until T,
# chaser free at t=0. Capture by T iff exists t in [0,T]:
#     |e0 + v_E t - c0| <= R_C t + eps.
def earliest_root(e0, vE, R_C, eps, T):
    """Earliest t in [0,T] where the condition holds (squared quadratic), or None."""
    a = vE @ vE - R_C**2
    b = 2 * (e0 @ vE - eps * R_C)
    c = e0 @ e0 - eps**2
    if c <= 0:
        return 0.0
    roots = np.roots([a, b, c]) if a != 0 else np.array([-c / b])
    ok = sorted(r.real for r in np.atleast_1d(roots) if abs(r.imag) < 1e-12 and 0 <= r.real <= T)
    return ok[0] if ok else None


def test_interception_constructive_capture():
    e0, vE, R_C, R_E, T = np.array([3.0, 0.0]), np.array([0.0, 0.8]), 0.9, 1.0, 5.0
    eps = 0.6
    t_star = earliest_root(e0, vE, R_C, eps, T)
    assert t_star is not None
    p = e0 + vE * t_star
    v_C = R_C * p / np.linalg.norm(p)
    C = AgentSpec(R_C, 10)
    E = AgentSpec(R_E, 5, first_decision=5, initial_velocity=vE)
    res = simulate(C, E, [0, 0], e0, eps, 5, Constant(v_C), Constant([0, 0]))
    assert res.captured and res.capture_time == pytest.approx(t_star, abs=1e-9)
    assert res.capture_time <= T


def test_interception_infeasible_window():
    # eps = 0.4: |e(t)| - 0.9 t - 0.4 is decreasing and still 0.1 > 0 at t = T = 5
    e0, vE, R_C, R_E, T, eps = np.array([3.0, 0.0]), np.array([0.0, 0.8]), 0.9, 1.0, 5, 0.4
    assert earliest_root(e0, vE, R_C, eps, T) is None
    rng = np.random.default_rng(11)
    E = AgentSpec(R_E, 5, first_decision=5, initial_velocity=vE)
    p = e0 + vE * T
    candidates = [Constant(R_C * p / np.linalg.norm(p))]
    candidates += [random_script(rng, R_C, 60) for _ in range(100)]
    for period in ["1/10", "5"]:
        for pol in candidates:  # Scripted is stateless (indexes by obs.k), safe to reuse
            res = simulate(AgentSpec(R_C, period), E, [0, 0], e0, eps, T, pol, Constant([0, 0]))
            assert not res.captured


def test_braking_beats_pure_pursuit_on_a_specific_runner():
    # PP is not universally better than braking; it only won every paired state
    # in the Stage 2 sweep. Here the runner jinks up, then cuts back across the
    # braking chaser's path: braking (speed d/tau = 1) meets it, PP (speed 4)
    # has long gone past.
    C, E = AgentSpec(4.0, 1), AgentSpec(2.0, "1/4")
    runner = Scripted([[0, 2]] + [[-0.5, -1]] * 3)
    pp = simulate(C, E, [0, 0], [1, 0], 0.1, 1, pure_pursuit, runner)
    bp = simulate(C, E, [0, 0], [1, 0], 0.1, 1, braking_pursuit, runner)
    assert not pp.captured
    # PP's closest approach is at t = 0.2 on the first runner leg: |(1 - 0.8, 0.4)| = sqrt(0.2)
    assert min_separation([1, 0], [-4, 2], 0.25)[1] == pytest.approx(math.sqrt(0.2))
    # braking chaser at (t, 0) vs runner (1.125 - t/2, 0.75 - t): they coincide at
    # t = 0.75, so first eps-contact is 0.1/|(1.5, 1)| earlier
    assert bp.captured and bp.capture_time == pytest.approx(0.75 - 0.1 / math.hypot(1.5, 1), abs=1e-12)


# Spec §B.2b: PP captures every runner when alpha_C <= 2s/(1+s), within
# phi_C + (K+2) tau_C. Checked on the boundary itself and just inside it.
@pytest.mark.parametrize("s", [F(6, 5), F(3, 2), F(3)])
@pytest.mark.parametrize("shrink", [F(1), F(97, 100)])
def test_extended_threshold(s, shrink):
    from tagsim import BestResponseVsPP
    R_C, R_E, eps = float(s), 1.0, 1.0
    tau_C = shrink * 2 * s / (1 + s)
    rng = np.random.default_rng(zlib.crc32(repr(("ext", s, shrink)).encode()))
    for _ in range(3):
        phi_C = F(rng.integers(0, 8), 8) * tau_C
        a = F(rng.choice(["1/4", "1", "2"]))
        tau_E = a * tau_C
        ang = rng.uniform(0, 2 * np.pi)
        C = AgentSpec(R_C, tau_C, first_decision=phi_C,
                      initial_velocity=[R_C * math.cos(ang), R_C * math.sin(ang)] if phi_C else None)
        E = AgentSpec(R_E, tau_E)
        D0 = rng.uniform(2, 12)
        x_E0 = D0 * np.array([math.cos(ang + 2), math.sin(ang + 2)])
        H = float(phi_C) + (D0 + (R_C + R_E) * float(phi_C)) / (R_C - R_E) + 6 * float(tau_C) + 5
        n_E = int(H / float(tau_E)) + 3
        runners = [flee, Perpendicular(), PredictiveEvasion(), random_script(rng, R_E, n_E),
                   BestResponseVsPP(n_dirs=16, beam=12)]
        for runner in runners:
            res = simulate(C, E, [0, 0], x_E0, eps, H, pure_pursuit, runner)
            assert res.captured, runner
            t1 = float(phi_C)
            if res.capture_time > t1:
                K = math.ceil(max(separation(res, t1) - R_C * float(tau_C), 0) / ((R_C - R_E) * float(tau_C)))
                assert res.capture_time <= t1 + (K + 2) * float(tau_C) + 1e-9


hybrid_chaser = hybrid_pursuit  # review §3.4


@pytest.mark.parametrize("s,alpha", [(F(2), F(19, 10)), (F(3, 2), F(147, 100)), (F(6, 5), F(119, 100))])
def test_hybrid_captures_up_to_alpha_s(s, alpha):
    # alpha_C <= s: every runner caught within phi_C + (K+2) tau_C. (Not tested at
    # alpha_C = s itself: there straight flee makes the last step an exact tangency,
    # capture in exact arithmetic but decided by rounding in floats.) Includes the
    # symmetric-pass runner, which provably beats pure pursuit when alpha > alpha_sym(s).
    from tagsim.best_response import SymmetricPass, best_pass
    R_C, eps = float(s), 1.0
    tau = alpha
    sp = SymmetricPass(R_C, 1.0, float(tau))
    rng = np.random.default_rng(zlib.crc32(repr(("hyb", s, alpha)).encode()))
    runners = [flee, Perpendicular(), PredictiveEvasion(), random_script(rng, 1.0, 400), sp]
    if float(alpha) > 1 / math.sqrt(best_pass(R_C)[1]):
        assert not simulate(AgentSpec(R_C, tau), AgentSpec(1.0, tau), [0, 0], [sp.D, 0], eps, 200 * tau,
                            pure_pursuit, sp).captured
    for runner in runners:
        for x0 in ([sp.D, 0], [7, 3]):
            res = simulate(AgentSpec(R_C, tau), AgentSpec(1.0, tau / 2 if runner is not sp else tau),
                           [0, 0], x0, eps, 400 * tau, hybrid_chaser, runner)
            assert res.captured, runner
            L, rho = R_C * float(tau), float(tau)
            K = math.ceil(max(np.hypot(*x0) - L, 0) / (L - rho))
            assert res.capture_time <= (K + 2) * float(tau) + 1e-9


def test_hybrid_sharp_above_alpha_s():
    # alpha_C > s: collinear straight flee pins separation at R_E tau_C > s eps, braking forever.
    s, tau = 2.0, F(21, 10)
    res = simulate(AgentSpec(s, tau), AgentSpec(1.0, 1000), [0, 0], [10, 0], 1.0, 400, hybrid_chaser, Constant([1, 0]))
    assert not res.captured
    assert np.linalg.norm(res.x_E - res.x_C, axis=1).min() == pytest.approx(float(tau), rel=1e-9)


def test_policy_separation_instance_exact():
    # Review §3.5, Corollary 5.1: s = 2, alpha_C = 19/10, y = 6/5. All exact.
    s, alpha, y = F(2), F(19, 10), F(6, 5)
    g = y * y - y * (s * s - 1) / (4 * (s - y))
    assert g == F(63, 200) and g > 1 / alpha ** 2          # Theorem 2 applies: PP is evaded
    cos2 = (s * s - 1) / (4 * y * (s - y))
    assert cos2 == F(25, 32) and 0 < cos2 < 1
    # frame velocity (1/8, 3 sqrt7 / 8): |v|^2 = 1/64 + 63/64, and it is the Theorem 2 rule
    assert F(1, 64) + F(9 * 7, 64) == 1
    assert s - 2 * y * cos2 == F(1, 8)                      # R_C - (2 D cos theta) cos theta, tau_C = R_E = 1
    assert (2 * y) ** 2 * cos2 * (1 - cos2) == F(63, 64)    # squared n-component
    assert alpha <= s                                       # Theorem 3: the hybrid chaser captures everyone


def test_lemma_s_bounds():
    from tagsim.best_response import best_pass
    for s in (1.01, 1.2, 1.5, 1.7, 2.0, 3.0, 10.0, 100.0):
        a_sym = 1 / math.sqrt(best_pass(s)[1])
        assert 2 * s / (1 + s) <= a_sym < 2
    # the witness in the proof: g(s/2) = 1/4 exactly, g'(s/2) = 1/s
    for s in (F(6, 5), F(2), F(7)):
        y = s / 2
        assert y * y - y * (s * s - 1) / (4 * (s - y)) == F(1, 4)
        assert 2 * y - s * (s * s - 1) / (4 * (s - y) ** 2) == 1 / s
