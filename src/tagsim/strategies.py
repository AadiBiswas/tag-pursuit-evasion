"""Stage 2 baseline strategies.

Every policy here is a stateless function of the Observation, so it sees only
what the engine hands it at its own decision time. At a simultaneous decision
that means the opponent's *old* committed velocity.

Zero separation can't actually occur at a decision (eps > 0 ends the game
first); policies return a zero velocity there rather than dividing by zero.
"""

import math

import numpy as np


def _unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else np.zeros_like(v)


def pure_pursuit(obs):
    """Full speed at the runner's current position (the Proposition 1 strategy)."""
    return obs.spec_self.max_speed * _unit(obs.pos_opp - obs.pos_self)


def braking_pursuit(obs):
    """Pure pursuit, but slow to min(R, d / tau) so the chaser lands on the
    observed runner position at its next decision instead of flying past it.
    Not admissible in exact-speed mode once d < R tau."""
    d = obs.pos_opp - obs.pos_self
    dist = np.linalg.norm(d)
    if dist == 0:
        return np.zeros_like(d)
    # we're deciding now, so the next decision is exactly one period away
    speed = min(obs.spec_self.max_speed, dist / float(obs.spec_self.period))
    return speed * d / dist


def contact_time(p0, v, R, eps):
    """Earliest t >= 0 with |p0 + v t| <= R t + eps, or None.

    This is condition (★) of spec §B.1a: a target at relative position p0
    moving with constant velocity v can be brought within eps by time t by a
    chaser of speed R iff it holds. Both sides are >= 0, so square them and
    solve the quadratic. (Same |p0|^2 - eps^2 cancellation caveat as the old
    capture check; harmless at the scales a predictor runs at.)
    """
    a = v @ v - R * R
    b = 2 * (p0 @ v - eps * R)
    c = p0 @ p0 - eps * eps
    if c <= 0:
        return 0.0
    if a == 0:
        return -c / b if b < 0 else None
    disc = b * b - 4 * a * c
    if disc < 0:
        return None
    # c > 0 so q != 0. With a < 0 the roots straddle 0 and the positive one is
    # the entry; with a > 0 both roots share the sign of -b.
    q = -0.5 * (b + math.copysign(math.sqrt(disc), b))
    roots = [r for r in (q / a, c / q) if r >= 0]
    return min(roots) if roots else None


class Intercept:
    """Aim at the earliest predicted contact point.

    Prediction: the runner keeps its currently committed velocity for
    `horizon` time units (None = forever). That velocity is real information
    only until the runner's next decision; past that it's an extrapolation.
    A runner that hasn't committed yet (fresh start) is treated as stationary.
    If no contact is predicted within the horizon -- e.g. a faster runner
    heading away -- fall back to pure pursuit.

    The aim is always full speed toward p0 + v t*, which reaches the
    eps-ball exactly at t* if the prediction holds (spec §B.1a).
    """

    def __init__(self, horizon=None):
        self.horizon = horizon

    def __call__(self, obs):
        R = obs.spec_self.max_speed
        p0 = obs.pos_opp - obs.pos_self
        v = np.zeros_like(p0) if obs.vel_opp is None else obs.vel_opp
        t = contact_time(p0, v, R, obs.eps)
        if t is None or (self.horizon is not None and t > self.horizon):
            return pure_pursuit(obs)
        return R * _unit(p0 + v * t)


def flee(obs):
    """Full speed directly away from the chaser's current position."""
    return obs.spec_self.max_speed * _unit(obs.pos_self - obs.pos_opp)


class Perpendicular:
    """Full speed perpendicular to the chaser->runner line. 2D only.

    side=+1 rotates the line of sight 90 degrees counterclockwise, side=-1
    clockwise. Fixed per instance, so runs are reproducible; every chaser
    here is reflection-equivariant, so the two sides give mirror-image games.
    """

    def __init__(self, side=1):
        if side not in (1, -1):
            raise ValueError("side must be +1 or -1")
        self.side = side

    def __call__(self, obs):
        u = _unit(obs.pos_self - obs.pos_opp)
        if u.shape != (2,):
            raise ValueError("perpendicular evasion is 2D-only (not unique in 3D)")
        return obs.spec_self.max_speed * self.side * np.array([-u[1], u[0]])


class PredictiveEvasion:
    """Full-speed heading that maximizes predicted minimum separation. 2D only.

    Chaser model -- an assumption about the opponent, not knowledge of it:
    it keeps its committed velocity until its next decision (which the runner
    can see), then plays full-speed pure pursuit at each of its decision
    times. Against braking or intercepting chasers the model is wrong after
    the chaser's next decision, by design.

    The runner assumes it holds the candidate velocity for the lookahead
    L = max(own period, time to chaser's next decision). The second term is
    what lets an agile runner see a whole committed pass coming (spec §B.3).

    Candidates are n_dirs headings ordered 0, +d, -d, +2d, ... from straight
    away (CCW first). The earliest candidate within 1e-9 of the best wins, so
    when nothing threatens within L every candidate ties at the current
    separation and the runner simply flees.
    """

    def __init__(self, n_dirs=180):
        if n_dirs < 2 or n_dirs % 2:
            raise ValueError("n_dirs must be a positive even number")
        k = np.arange(1, n_dirs // 2)
        step = 2 * np.pi / n_dirs
        self.offsets = np.concatenate([[0.0], np.column_stack([k * step, -k * step]).ravel(), [np.pi]])

    def __call__(self, obs):
        if obs.pos_self.shape != (2,):
            raise ValueError("predictive evasion is 2D-only for now")
        Rc, tau_C = obs.spec_opp.max_speed, float(obs.spec_opp.period)
        t_dec = float(obs.next_opp - obs.t)  # 0 at a simultaneous decision
        L = max(float(obs.spec_self.period), t_dec)

        away = obs.pos_self - obs.pos_opp
        ang = math.atan2(away[1], away[0]) + self.offsets
        V = obs.spec_self.max_speed * np.column_stack([np.cos(ang), np.sin(ang)])

        e = np.tile(obs.pos_self, (len(V), 1))
        c = np.tile(obs.pos_opp, (len(V), 1))
        vc = np.zeros_like(V) if obs.vel_opp is None else np.tile(obs.vel_opp, (len(V), 1))
        worst = np.full(len(V), np.inf)
        t = 0.0
        while True:
            t_end = min(t_dec, L)
            if t_end > t:
                dt = t_end - t
                r, w = e - c, V - vc
                ww = np.einsum("ij,ij->i", w, w)
                s = np.divide(-np.einsum("ij,ij->i", r, w), ww, out=np.zeros(len(V)), where=ww > 0)
                s = np.clip(s, 0.0, dt)
                worst = np.minimum(worst, np.linalg.norm(r + s[:, None] * w, axis=1))
                e += V * dt
                c += vc * dt
                t = t_end
            if t_dec >= L:
                break
            gap = e - c
            n = np.linalg.norm(gap, axis=1, keepdims=True)
            vc = Rc * np.divide(gap, n, out=np.zeros_like(gap), where=n > 0)
            t_dec += tau_C

        return V[np.argmax(worst >= worst.max() - 1e-9)].copy()
