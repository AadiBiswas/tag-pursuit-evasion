from fractions import Fraction as F

import numpy as np
import pytest

from tagsim import AgentSpec, Constant, Scripted, as_time, simulate


def decisions(res, agent):
    return [e for e in res.events if e["kind"] == "decision" and e["agent"] == agent]


class Recorder:
    """Scripted policy that also keeps every observation it was shown."""

    def __init__(self, velocities):
        self.inner = Scripted(velocities)
        self.seen = []

    def __call__(self, obs):
        self.seen.append(obs)
        return self.inner(obs)


# --- time handling --------------------------------------------------------

def test_as_time_reads_floats_as_decimals():
    assert as_time(0.1) == F(1, 10)
    assert 3 * as_time(0.1) == as_time(0.3)
    assert as_time("1/3") == F(1, 3)
    with pytest.raises(ValueError):
        as_time(float("inf"))


# --- movement ---------------------------------------------------------------

def test_straight_line_motion_is_exact():
    C = AgentSpec(1.0, "1/3")
    E = AgentSpec(1.0, "1/2")
    vc, ve = np.array([0.6, 0.8]), np.array([-1.0, 0.0])
    res = simulate(C, E, [0, 0], [100, 0], 0.5, 4, Constant(vc), Constant(ve))
    assert res.stop_reason == "horizon"
    for t, xc, xe in zip(res.times, res.x_C, res.x_E):
        np.testing.assert_allclose(xc, vc * t, atol=1e-13)
        np.testing.assert_allclose(xe, [100, 0] + ve * t, atol=1e-13)
    pc, pe = res.positions_at(2.25)
    np.testing.assert_allclose(pc, vc * 2.25, atol=1e-13)
    np.testing.assert_allclose(pe, [100 - 2.25, 0], atol=1e-13)


def test_velocity_changes_only_at_decisions():
    C = AgentSpec(2.0, 1)
    E = AgentSpec(1.0, 10)
    res = simulate(C, E, [0, 0], [100, 100], 0.1, 3,
                   Scripted([[1, 0], [0, 1], [-2, 0]]), Constant([0, 0]))
    np.testing.assert_allclose(res.positions_at(1)[0], [1, 0], atol=1e-14)
    np.testing.assert_allclose(res.positions_at(2)[0], [1, 1], atol=1e-14)
    np.testing.assert_allclose(res.positions_at(3)[0], [-1, 1], atol=1e-14)
    np.testing.assert_allclose(res.positions_at(1.5)[0], [1, 0.5], atol=1e-14)


def test_stationary_agents():
    C, E = AgentSpec(1.0, 1), AgentSpec(1.0, 1)
    res = simulate(C, E, [0, 0], [3, 0], 1.0, 5, Constant([0, 0]), Constant([0, 0]))
    assert not res.captured and res.stop_reason == "horizon"
    np.testing.assert_array_equal(res.x_E[-1], [3, 0])


def test_zero_relative_velocity():
    C, E = AgentSpec(1.0, "1/3"), AgentSpec(1.0, "1/2")
    res = simulate(C, E, [0, 0], [3, 0], 1.0, 5, Constant([1, 0]), Constant([1, 0]))
    assert not res.captured
    seps = np.linalg.norm(res.x_E - res.x_C, axis=1)
    np.testing.assert_allclose(seps, 3.0, atol=1e-13)


def test_dimension_agnostic_3d_head_on():
    C, E = AgentSpec(1.0, 1), AgentSpec(1.0, 1)
    res = simulate(C, E, [0, 0, 0], [0, 0, 10], 1.0, 20, Constant([0, 0, 1]), Constant([0, 0, -1]))
    assert res.capture_time == pytest.approx(4.5)


# --- clocks ---------------------------------------------------------------

def test_asynchronous_clock_lattices():
    C, E = AgentSpec(1.0, "1/3"), AgentSpec(1.0, "1/2")
    res = simulate(C, E, [0, 0], [100, 0], 0.5, 2, Constant([0, 0]), Constant([0, 0]))
    assert [e["t"] for e in decisions(res, "C")] == ["0", "1/3", "2/3", "1", "4/3", "5/3"]
    assert [e["t"] for e in decisions(res, "E")] == ["0", "1/2", "1", "3/2"]
    # decision at the horizon itself is not taken
    assert all(F(e["t"]) < 2 for e in res.events if e["kind"] == "decision")


def test_float_periods_still_coincide():
    # 0.1 and 0.3 as floats would never land on the same instant
    C, E = AgentSpec(1.0, 0.1), AgentSpec(1.0, 0.3)
    res = simulate(C, E, [0, 0], [100, 0], 0.5, 1, Constant([0, 0]), Constant([0, 0]))
    tc = {e["t"] for e in decisions(res, "C")}
    te = {e["t"] for e in decisions(res, "E")}
    assert te <= tc and "3/10" in te


def test_phases():
    C = AgentSpec(1.0, 1, first_decision="1/4", initial_velocity=[1, 0])
    E = AgentSpec(1.0, 1, first_decision="3/4", initial_velocity=[0, 1])
    res = simulate(C, E, [0, 0], [50, 0], 0.5, 3, Constant([0, 0]), Constant([0, 0]))
    assert [e["t"] for e in decisions(res, "C")] == ["1/4", "5/4", "9/4"]
    assert [e["t"] for e in decisions(res, "E")] == ["3/4", "7/4", "11/4"]
    np.testing.assert_allclose(res.positions_at(1)[0], [0.25, 0], atol=1e-14)
    np.testing.assert_allclose(res.positions_at(1)[1], [50, 0.75], atol=1e-14)


# --- initialization -------------------------------------------------------

def test_fresh_start_vs_precommitted():
    rec = Recorder([[0, 0]])
    C = AgentSpec(1.0, 1, first_decision="1/2", initial_velocity=[1, 0])
    E = AgentSpec(1.0, 1)  # fresh start
    simulate(C, E, [0, 0], [50, 0], 0.5, "1/2", rec, Constant([0, 0]))
    assert rec.seen == []  # chaser never got to decide before t = 1/2

    rec = Recorder([[0, 0]])
    res = simulate(C, E, [0, 0], [50, 0], 0.5, "3/4", rec, Constant([0, 0]))
    (obs,) = rec.seen
    assert obs.t == F(1, 2) and obs.k == 0
    np.testing.assert_array_equal(obs.vel_self, [1, 0])
    np.testing.assert_allclose(obs.pos_self, [0.5, 0])
    np.testing.assert_allclose(res.x_C[-1], [0.5, 0])


def test_fresh_start_observation_has_no_velocities():
    rc, re = Recorder([[0, 0]]), Recorder([[0, 0]])
    simulate(AgentSpec(1.0, 1), AgentSpec(1.0, 1), [0, 0], [5, 0], 0.5, "1/2", rc, re)
    assert rc.seen[0].vel_opp is None and re.seen[0].vel_opp is None
    assert rc.seen[0].next_opp == 0  # opponent decides now too


def test_bad_specs():
    with pytest.raises(ValueError):
        AgentSpec(1.0, 1, first_decision="1/2")  # precommitted but no velocity
    with pytest.raises(ValueError):
        AgentSpec(1.0, 1, first_decision=2, initial_velocity=[0, 0])
    with pytest.raises(ValueError):
        AgentSpec(1.0, 0)
    with pytest.raises(ValueError):
        AgentSpec(-1.0, 1)


# --- information / simultaneity ---------------------------------------------

def test_simultaneous_decisions_do_not_leak():
    # C every 1/3, E every 1/2 -> both decide at t = 0 and t = 1.
    c_vel = [[0.1 * k, 0] for k in range(10)]
    rc, re = Recorder(c_vel), Recorder([[0, 0.1 * k] for k in range(10)])
    simulate(AgentSpec(1.0, "1/3"), AgentSpec(1.0, "1/2"), [0, 0], [100, 0], 0.5, 2, rc, re)
    at_one = [o for o in re.seen if o.t == 1][0]
    # chaser's decision 3 happens at t = 1 too; runner must see decision 2's velocity
    np.testing.assert_array_equal(at_one.vel_opp, c_vel[2])
    assert at_one.next_opp == 1
    c_at_one = [o for o in rc.seen if o.t == 1][0]
    np.testing.assert_array_equal(c_at_one.vel_opp, [0, 0.1])  # runner's decision 1 (t=1/2)


def test_sequential_decision_sees_latest_commitment():
    c_vel = [[0.1 * k, 0] for k in range(10)]
    rc, re = Recorder(c_vel), Recorder([[0, 0]] * 10)
    simulate(AgentSpec(1.0, "1/3"), AgentSpec(1.0, "1/2"), [0, 0], [100, 0], 0.5, 2, rc, re)
    half = [o for o in re.seen if o.t == F(1, 2)][0]
    np.testing.assert_array_equal(half.vel_opp, c_vel[1])  # chosen at t = 1/3
    assert half.next_opp == F(2, 3)


def test_observation_is_read_only():
    def vandal(obs):
        obs.pos_opp[0] = 0.0
        return [0, 0]

    with pytest.raises(ValueError):
        simulate(AgentSpec(1.0, 1), AgentSpec(1.0, 1), [0, 0], [5, 0], 0.5, 1,
                 vandal, Constant([0, 0]))


# --- speed constraints ------------------------------------------------------

def test_speed_modes():
    C, E = AgentSpec(2.0, 1), AgentSpec(1.0, 1)
    run = lambda vc, mode: simulate(C, E, [0, 0], [50, 0], 0.5, 1, Constant(vc),
                                    Constant([1, 0]), speed_mode=mode)
    run([0, 0], "max")
    run([1.2, 1.6], "max")
    run([2 * (1 + 1e-13), 0], "max")  # rounding noise is tolerated
    with pytest.raises(ValueError):
        run([2.01, 0], "max")
    run([1.2, 1.6], "exact")
    with pytest.raises(ValueError):
        run([1, 0], "exact")


def test_precommitted_velocity_is_checked():
    C = AgentSpec(1.0, 1, first_decision="1/2", initial_velocity=[3, 0])
    with pytest.raises(ValueError):
        simulate(C, AgentSpec(1.0, 1), [0, 0], [5, 0], 0.5, 1, Constant([0, 0]), Constant([0, 0]))


def test_wrong_shape_velocity():
    with pytest.raises(ValueError):
        simulate(AgentSpec(1.0, 1), AgentSpec(1.0, 1), [0, 0], [5, 0], 0.5, 1,
                 Constant([0, 0, 0]), Constant([0, 0]))


# --- capture detection ------------------------------------------------------

def test_initial_capture():
    res = simulate(AgentSpec(1.0, 1), AgentSpec(1.0, 1), [0, 0], [0.5, 0], 1.0, 5,
                   Constant([0, 0]), Constant([1, 0]))
    assert res.captured and res.capture_time == 0.0 and res.n_intervals == 0


def test_capture_between_decisions():
    # chaser parked at origin; runner sweeps past it mid-interval
    res = simulate(AgentSpec(1.0, 10), AgentSpec(1.0, 10), [0, 0], [-5, 0.5], 1.0, 10,
                   Constant([0, 0]), Constant([1, 0]))
    assert res.captured
    assert res.capture_time == pytest.approx(5 - np.sqrt(0.75), abs=1e-14)
    cap = res.events[-1]
    assert cap["kind"] == "capture" and cap["interval_start"] == "0"
    np.testing.assert_allclose(np.linalg.norm(np.subtract(cap["x_E"], cap["x_C"])), 1.0)


def test_capture_on_decision_boundary_and_horizon():
    C, E = AgentSpec(1.0, "9/2"), AgentSpec(1.0, "9/2")
    args = ([0, 0], [10, 0], 1.0)
    res = simulate(C, E, *args, "9/2", Constant([1, 0]), Constant([-1, 0]))
    assert res.captured and res.capture_time == pytest.approx(4.5)
    res = simulate(C, E, *args, "4.4", Constant([1, 0]), Constant([-1, 0]))
    assert not res.captured and res.stop_reason == "horizon"


def test_horizon_zero():
    res = simulate(AgentSpec(1.0, 1), AgentSpec(1.0, 1), [0, 0], [5, 0], 1.0, 0,
                   Constant([1, 0]), Constant([0, 0]))
    assert not res.captured and res.n_intervals == 0


def test_script_exhaustion_raises():
    with pytest.raises(IndexError):
        simulate(AgentSpec(1.0, 1), AgentSpec(1.0, 1), [0, 0], [50, 0], 0.5, 3,
                 Scripted([[0, 0]]), Constant([0, 0]))


def test_max_events_stop():
    res = simulate(AgentSpec(1.0, "1/1000"), AgentSpec(1.0, 1), [0, 0], [50, 0], 0.5, 10,
                   Constant([0, 0]), Constant([0, 0]), max_events=100)
    assert res.stop_reason == "max_events" and res.n_intervals == 100


# --- reproducibility ----------------------------------------------------------

def random_game(seed):
    rng = np.random.default_rng(seed)

    def script(R, n):
        ang = rng.uniform(0, 2 * np.pi, n)
        sp = R * rng.uniform(0, 1, n)
        return Scripted(np.c_[sp * np.cos(ang), sp * np.sin(ang)])

    C = AgentSpec(1.3, "2/7", first_decision="1/7", initial_velocity=[0, 1.3])
    E = AgentSpec(1.0, "1/5")
    return simulate(C, E, [0, 0], [4, 1], 0.05, 20, script(1.3, 80), script(1.0, 110))


def test_runs_are_bitwise_reproducible():
    a, b = random_game(7), random_game(7)
    assert a.log_json() == b.log_json()
    np.testing.assert_array_equal(a.times, b.times)
    np.testing.assert_array_equal(a.x_C, b.x_C)
    np.testing.assert_array_equal(a.x_E, b.x_E)
    assert random_game(8).log_json() != a.log_json()
