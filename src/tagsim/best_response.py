"""Approximate best-response runner against full-speed pure pursuit.

Pure pursuit is deterministic and depends only on positions, so once the
runner knows the chaser plays it, the chaser's whole future is a function of
the runner's own future path. Best response is then a single-agent planning
problem. We solve it approximately with a beam search over the runner's next
`depth` decisions, re-planned at every decision (receding horizon).

Information: everything comes from the Observation -- positions, the chaser's
committed velocity, its exact next decision time and both periods. At a
simultaneous decision the chaser's new velocity is *inferred* from the PP rule
and current positions, never observed.

Ranking (lexicographic, so a large separation can't buy back a capture):
    1. survived the whole planning horizon
    2. later predicted capture time (only matters if everything dies)
    3. larger minimum separation over the horizon
Partial plans are ranked the same way after completing them by holding their
last velocity to the end of the horizon. Ranking on the partial prefix alone
prunes exactly the plans that head *toward* a close tangent pass -- they look
worse than fleeing right up until the pass that saves them.
Ties keep the earlier candidate (stable sort), so results are deterministic.
"""

import math

import numpy as np


def _first_contact(r, w, eps, dt):
    """Row-wise kinematics.first_contact: earliest hit time in [0, dt] or inf."""
    n = np.linalg.norm(r, axis=1)
    a = np.einsum("ij,ij->i", w, w)
    p = np.einsum("ij,ij->i", r, w)
    out = np.full(len(r), np.inf)
    out[n <= eps] = 0.0
    m = (n > eps) & (a > 0) & (p < 0)
    if m.any():
        s_min = -p[m] / a[m]
        dp = np.linalg.norm(r[m] + s_min[:, None] * w[m], axis=1)
        ok = dp <= eps
        h = np.sqrt(np.clip((eps - dp) * (eps + dp), 0, None) / a[m])
        s = (n[m] - eps) * (n[m] + eps) / (a[m] * (s_min + h))
        s = np.where(ok & (s <= dt), s, np.inf)
        out[m] = s
    return out


def _min_sep(r, w, dt):
    a = np.einsum("ij,ij->i", w, w)
    s = np.divide(-np.einsum("ij,ij->i", r, w), a, out=np.zeros(len(r)), where=a > 0)
    s = np.clip(s, 0.0, dt)
    return np.linalg.norm(r + s[:, None] * w, axis=1)


def advance(e, c, vc, ve, t0, t1, chaser_times, R_C, eps):
    """Move N runner/chaser pairs from t0 to t1 (exact Fractions) with fixed runner
    velocities ve; the chaser re-aims by PP at each time in chaser_times within
    [t0, t1). Returns (e, c, vc, hit_time, min_sep) with hit_time = inf if no capture.
    """
    hit = np.full(len(e), np.inf)
    msep = np.full(len(e), np.inf)
    t = t0
    for tc in [x for x in chaser_times if t0 <= x < t1] + [t1]:
        if tc > t:
            dt = float(tc - t)
            r, w = e - c, ve - vc
            s = _first_contact(r, w, eps, dt)
            new = np.isinf(hit) & np.isfinite(s)
            hit[new] = float(t) + s[new]
            msep = np.minimum(msep, _min_sep(r, w, dt))
            e, c = e + ve * dt, c + vc * dt
            t = tc
        if tc < t1:  # chaser decision at tc: full speed at the runner
            gap = e - c
            n = np.linalg.norm(gap, axis=1, keepdims=True)
            vc = R_C * np.divide(gap, n, out=np.zeros_like(gap), where=n > 0)
    return e, c, vc, hit, msep


def chaser_decisions(next_opp, tau_C, t_end):
    out, t = [], next_opp
    while t < t_end:
        out.append(t)
        t += tau_C
    return out


class BestResponseVsPP:
    """Beam-search runner. Actions are n_dirs headings spaced evenly from
    straight-away-from-the-chaser, times each fraction in `speeds` of R_E,
    plus "hold the current velocity".
    depth=None plans ceil(horizon_chaser_periods * tau_C / tau_E) runner legs,
    capped at max_depth."""

    def __init__(self, n_dirs=24, speeds=(1.0,), beam=32, depth=None,
                 horizon_chaser_periods=2, max_depth=12):
        self.offsets = 2 * np.pi * np.arange(n_dirs) / n_dirs
        self.speeds = np.asarray(speeds, dtype=float)
        self.beam, self.depth = beam, depth
        self.horizon_chaser_periods, self.max_depth = horizon_chaser_periods, max_depth

    def plan(self, obs):
        """Returns (velocities of the best plan, survived, predicted min separation)."""
        R_E, R_C = obs.spec_self.max_speed, obs.spec_opp.max_speed
        tau_E, tau_C = obs.spec_self.period, obs.spec_opp.period
        depth = self.depth or min(self.max_depth,
                                  max(1, math.ceil(self.horizon_chaser_periods * tau_C / tau_E)))
        t0 = obs.t
        ctimes = chaser_decisions(obs.next_opp, tau_C, t0 + depth * tau_E)

        e = obs.pos_self[None].astype(float)
        c = obs.pos_opp[None].astype(float)
        vc = np.zeros_like(e) if obs.vel_opp is None else obs.vel_opp[None].astype(float)
        hit = np.full(1, np.inf)
        msep = np.full(1, np.inf)
        plans = np.zeros((1, 0, 2))
        prev = None if obs.vel_self is None else obs.vel_self[None].astype(float)

        for j in range(depth):
            away = e - c
            base = np.arctan2(away[:, 1], away[:, 0])
            ang = base[:, None] + self.offsets[None, :]                     # (B, n_dirs)
            dirs = np.stack([np.cos(ang), np.sin(ang)], axis=-1)            # (B, n_dirs, 2)
            ve = (R_E * self.speeds[None, None, :, None] * dirs[:, :, None, :]).reshape(len(e), -1, 2)
            # Headings are relative to the *current* line of sight, which rotates, so
            # "keep going straight" is almost never on the grid. Without it a runner
            # with 4 decisions per chaser period can't even copy a 1-decision runner.
            if prev is not None:
                ve = np.concatenate([ve, prev[:, None, :]], axis=1)
            B, A = ve.shape[:2]

            def rep(x):
                return np.repeat(x, A, axis=0)

            ve = ve.reshape(B * A, 2)
            ta, tb = t0 + j * tau_E, t0 + (j + 1) * tau_E
            e2, c2, vc2, h, ms = advance(rep(e), rep(c), rep(vc), ve, ta, tb, ctimes, R_C, obs.eps)
            hit2 = np.minimum(rep(hit), h)
            msep2 = np.minimum(rep(msep), ms)
            plans2 = np.concatenate([np.repeat(plans, A, axis=0), ve[:, None, :]], axis=1)
            t_end = t0 + depth * tau_E
            if tb < t_end:
                _, _, _, hr, mr = advance(e2, c2, vc2, ve, tb, t_end, ctimes, R_C, obs.eps)
                score_hit, score_sep = np.minimum(hit2, hr), np.minimum(msep2, mr)
            else:
                score_hit, score_sep = hit2, msep2
            alive = np.isinf(score_hit)
            order = np.lexsort((-score_sep, -score_hit, ~alive))[: self.beam]
            e, c, vc, hit, msep, plans = e2[order], c2[order], vc2[order], hit2[order], msep2[order], plans2[order]
            prev = plans[:, -1]

        return plans[0], bool(np.isinf(hit[0])), float(msep[0])

    def __call__(self, obs):
        return self.plan(obs)[0][0].copy()


def pass_margin(y, s):
    """g(y) of spec §B.3a: squared closest approach of a one-leg symmetric pass, in units
    of (R_E tau_C)^2, at D = y R_E tau_C. Negative means the speed limit rules it out."""
    return y * y - y * (s * s - 1) / (4 * (s - y))


def best_pass(s, tol=1e-13):
    """argmax and max of pass_margin over 0 < y < s. g is unimodal there (g(0) = 0,
    g -> -inf at s, one interior critical point), so golden-section is enough."""
    lo, hi = 0.0, s
    k = (math.sqrt(5) - 1) / 2
    while hi - lo > tol * s:
        a, b = hi - k * (hi - lo), lo + k * (hi - lo)
        if pass_margin(a, s) < pass_margin(b, s):
            lo = a
        else:
            hi = b
    y = (lo + hi) / 2
    return y, pass_margin(y, s)


class SymmetricPass:
    """Constructive periodic evasion of pure pursuit (spec §B.3a).

    Must decide at every chaser decision (period tau_C, aligned phase). At each
    decision the chaser re-aims along u = (e - c)/|e - c|; the runner takes the
    one straight leg that makes the relative motion pass the chaser at angle
    theta and come back out to the same separation D exactly when the chaser
    next decides. By rotation invariance the next period is a rotated copy, so
    the orbit is periodic -- no numerics involved beyond rounding.

    Closest approach per pass is D sin(theta) = R_E tau_C sqrt(g(y)).
    """

    def __init__(self, R_C, R_E, tau_C, side=1):
        s = R_C / R_E
        self.y, g = best_pass(s)
        self.miss = R_E * tau_C * math.sqrt(g)
        self.D = self.y * R_E * tau_C
        cos2 = (s * s - 1) / (4 * self.y * (s - self.y))
        self.theta = math.acos(math.sqrt(cos2))
        self.R_C, self.R_E, self.tau_C, self.side = R_C, R_E, tau_C, side

    def __call__(self, obs):
        u = obs.pos_self - obs.pos_opp
        u = u / np.linalg.norm(u)
        perp = self.side * np.array([-u[1], u[0]])
        wn = 2 * self.D * math.cos(self.theta) / self.tau_C
        v = wn * (-math.cos(self.theta) * u + math.sin(self.theta) * perp) + self.R_C * u
        n = np.linalg.norm(v)
        # |v| = R_E exactly at the optimum; shave the last ulp or two
        return v * (self.R_E / n) if n > self.R_E else v
