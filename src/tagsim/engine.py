"""Event-driven two-agent pursuit-evasion engine.

Model (see stage0_spec.md, Revision 1):
  * each agent i has max speed R_i and a periodic decision clock
    t = phi_i + k * tau_i, k = 0, 1, ...
  * at a decision time it picks a velocity v with |v| <= R_i ("max" mode) or
    |v| == R_i ("exact" mode), held constant until its next decision
  * capture: first t in [0, H] with |x_C(t) - x_E(t)| <= eps, found exactly
    on every inter-event interval

Clock times are exact Fractions. With floats, 3 * 0.1 != 0.3 and two clocks
that "should" coincide drift apart by an ulp, which silently turns a
simultaneous move into a sequential one (and hands someone information).
Positions and capture offsets are float64.
"""

import json
import math
from dataclasses import dataclass
from fractions import Fraction

import numpy as np

from .kinematics import first_contact

ROLES = ("C", "E")
# Slack for R * unit_vector rounding: relative for R >= 1, absolute 1e-12 below.
SPEED_TOL = 1e-12


def as_time(x):
    """Exact time from int / Fraction / str ("1/3", "0.1") / float.

    Floats go through their shortest repr, so 0.1 means 1/10 rather than the
    binary approximation. Pass strings like "1/3" for non-terminating values.
    """
    if isinstance(x, float):
        if not math.isfinite(x):
            raise ValueError(f"time must be finite, got {x}")
        return Fraction(repr(x))
    return Fraction(x)


def _readonly(v):
    a = np.array(v, dtype=float)
    a.setflags(write=False)
    return a


@dataclass(frozen=True)
class AgentSpec:
    """Static description of one agent.

    first_decision: time of the agent's first decision (phi). 0 = fresh
    start, the agent picks its velocity at t = 0. If > 0 the agent is
    precommitted to initial_velocity on [0, first_decision).
    """
    max_speed: float
    period: Fraction
    first_decision: Fraction = Fraction(0)
    initial_velocity: tuple | None = None

    def __post_init__(self):
        object.__setattr__(self, "period", as_time(self.period))
        object.__setattr__(self, "first_decision", as_time(self.first_decision))
        if self.max_speed < 0 or not math.isfinite(self.max_speed):
            raise ValueError("max_speed must be finite and >= 0")
        if self.period <= 0:
            raise ValueError("period must be > 0")
        if not (0 <= self.first_decision <= self.period):
            raise ValueError("first_decision must lie in [0, period]")
        if self.first_decision > 0 and self.initial_velocity is None:
            raise ValueError("precommitted agent (first_decision > 0) needs initial_velocity")
        if self.initial_velocity is not None:
            object.__setattr__(self, "initial_velocity",
                               tuple(float(c) for c in self.initial_velocity))


@dataclass(frozen=True)
class Observation:
    """What an agent sees at one of its decision times.

    Built from the state at t^- for *all* agents deciding at t before any of
    them is asked, so vel_opp is the opponent's committed velocity, never its
    new choice. At a simultaneous decision next_opp == t.
    vel_self / vel_opp are None for a fresh-start agent that hasn't moved yet.
    """
    t: Fraction
    role: str
    k: int  # this agent's decision index, 0-based
    pos_self: np.ndarray
    pos_opp: np.ndarray
    vel_self: np.ndarray | None
    vel_opp: np.ndarray | None
    next_opp: Fraction
    spec_self: AgentSpec
    spec_opp: AgentSpec
    eps: float


@dataclass
class Result:
    captured: bool
    capture_time: float | None
    stop_reason: str  # "capture" | "horizon" | "max_events"
    events: list
    # Knots of the piecewise-linear trajectories (every event time, plus the
    # capture/stop time). Linear interpolation between knots is exact.
    times: np.ndarray
    x_C: np.ndarray
    x_E: np.ndarray
    n_intervals: int = 0

    def positions_at(self, t):
        t = float(t)
        if not (self.times[0] <= t <= self.times[-1]):
            raise ValueError("t outside simulated range")

        def interp(X):
            return np.array([np.interp(t, self.times, X[:, j]) for j in range(X.shape[1])])

        return interp(self.x_C), interp(self.x_E)

    def log_json(self):
        return json.dumps(self.events, sort_keys=True)


class _Agent:
    """Mutable per-run state. Position is stored as an anchor at the agent's
    last decision, so rounding error accumulates per decision, not per event."""

    def __init__(self, role, spec, x0):
        self.role = role
        self.spec = spec
        self.anchor_t = Fraction(0)
        self.anchor_x = np.array(x0, dtype=float)
        self.vel = None if spec.initial_velocity is None else np.array(spec.initial_velocity)
        self.next = spec.first_decision
        self.k = 0

    def pos(self, t):
        if self.vel is None:
            return self.anchor_x.copy()
        return self.anchor_x + self.vel * float(t - self.anchor_t)


def _check_velocity(v, spec, mode, d, who):
    # Copy: the committed velocity must not alias the policy's array, or an
    # in-place edit later rewrites the agent's path, past included.
    v = np.array(v, dtype=float)
    if v.shape != (d,) or not np.all(np.isfinite(v)):
        raise ValueError(f"{who}: velocity must be a finite vector of shape ({d},), got {v!r}")
    speed = float(np.linalg.norm(v))
    R = spec.max_speed
    tol = SPEED_TOL * max(1.0, R)
    if mode == "max" and speed > R + tol:
        raise ValueError(f"{who}: |v| = {speed!r} exceeds max speed {R!r}")
    if mode == "exact" and abs(speed - R) > tol:
        raise ValueError(f"{who}: |v| = {speed!r} != required speed {R!r}")
    return v


def simulate(chaser, runner, x_C0, x_E0, eps, horizon, chaser_policy, runner_policy,
             speed_mode="max", max_events=1_000_000):
    """Run one game. Policies are callables Observation -> velocity.

    Deterministic given deterministic policies: event order, simultaneous
    resolution (both observe t^-, then chaser is queried, then runner) and
    all arithmetic are fixed.
    """
    if speed_mode not in ("max", "exact"):
        raise ValueError("speed_mode must be 'max' or 'exact'")
    if not eps > 0:
        raise ValueError("eps must be > 0")
    H = as_time(horizon)
    if H < 0:
        raise ValueError("horizon must be >= 0")

    x_C0 = np.asarray(x_C0, dtype=float)
    x_E0 = np.asarray(x_E0, dtype=float)
    if x_C0.shape != x_E0.shape or x_C0.ndim != 1:
        raise ValueError("initial positions must be 1-D vectors of equal length")
    d = x_C0.shape[0]

    agents = {"C": _Agent("C", chaser, x_C0), "E": _Agent("E", runner, x_E0)}
    policies = {"C": chaser_policy, "E": runner_policy}
    for a in agents.values():
        if a.vel is not None:
            a.vel = _check_velocity(a.vel, a.spec, speed_mode, d, f"{a.role} initial")

    events = []
    knots_t, knots_C, knots_E = [], [], []

    def knot(t):
        knots_t.append(float(t))
        knots_C.append(agents["C"].pos(t))
        knots_E.append(agents["E"].pos(t))

    def finish(captured, t_cap, reason, n):
        return Result(captured, t_cap, reason, events, np.array(knots_t),
                      np.array(knots_C), np.array(knots_E), n)

    t = Fraction(0)
    knot(t)
    if np.linalg.norm(x_E0 - x_C0) <= eps:
        events.append({"t": "0", "kind": "capture", "offset": 0.0,
                       "x_C": x_C0.tolist(), "x_E": x_E0.tolist()})
        return finish(True, 0.0, "capture", 0)

    n = 0
    while t < H:
        if n >= max_events:
            events.append({"t": str(t), "kind": "stop", "reason": "max_events"})
            return finish(False, None, "max_events", n)

        deciders = [r for r in ROLES if agents[r].next == t]
        # Freeze every decider's view before anyone acts. This is the whole
        # simultaneous-move protocol; don't interleave observe/act.
        obs = {}
        for r in deciders:
            me, op = agents[r], agents["E" if r == "C" else "C"]
            obs[r] = Observation(
                t=t, role=r, k=me.k,
                pos_self=_readonly(me.pos(t)), pos_opp=_readonly(op.pos(t)),
                vel_self=None if me.vel is None else _readonly(me.vel),
                vel_opp=None if op.vel is None else _readonly(op.vel),
                next_opp=op.next, spec_self=me.spec, spec_opp=op.spec, eps=eps)
        chosen = {r: _check_velocity(policies[r](obs[r]), agents[r].spec, speed_mode, d,
                                     f"{r} decision {agents[r].k} at t={t}")
                  for r in deciders}
        for r in deciders:
            a = agents[r]
            a.anchor_x = a.pos(t)
            a.anchor_t = t
            a.vel = chosen[r]
            events.append({"t": str(t), "kind": "decision", "agent": r, "k": a.k,
                           "velocity": a.vel.tolist(), "pos": a.anchor_x.tolist()})
            a.k += 1
            a.next = t + a.spec.period
        if t > 0:  # t = 0 already has its knot
            knot(t)

        t_next = min(agents["C"].next, agents["E"].next, H)
        dt = t_next - t
        xc, xe = agents["C"].pos(t), agents["E"].pos(t)
        # Both velocities are set by now: AgentSpec forces fresh-start agents
        # to decide at t = 0, before the first interval.
        vc, ve = agents["C"].vel, agents["E"].vel
        n += 1
        s = first_contact(xe - xc, ve - vc, eps, float(dt))
        if s is not None:
            t_cap = float(t) + s
            pc, pe = xc + vc * s, xe + ve * s
            knots_t.append(t_cap)
            knots_C.append(pc)
            knots_E.append(pe)
            events.append({"t": repr(t_cap), "kind": "capture", "interval_start": str(t),
                           "offset": s, "x_C": pc.tolist(), "x_E": pe.tolist()})
            return finish(True, t_cap, "capture", n)
        t = t_next

    knot(t)
    events.append({"t": str(t), "kind": "stop", "reason": "horizon"})
    return finish(False, None, "horizon", n)
