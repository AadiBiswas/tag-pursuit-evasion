"""Stage 4A prototype: finite-horizon viability of the aligned one-decision game
against full-speed pure pursuit. Theory: theory/stage4_viability_analysis.md.

    .venv/bin/python experiments/stage4a.py horizons    # grid survival horizons, s = 1.5 and 2
    .venv/bin/python experiments/stage4a.py chain       # Theorem 6(c) boundary chain: high precision + engine
    .venv/bin/python experiments/stage4a.py all

Units R_E = tau_C = 1, eps = 1/alpha_C. Everything here is a numerical
*estimate*; the proven statements are in the theory file, and nothing below is
used in their proofs.

Grid survival horizon. V_0 = (eps, inf), V_{n+1} = {D : R(D) meets V_n}, where R(D)
is the exact safe reachable set: the plateau interval (end points reached while
still closing in, closest approach = end separation) plus full-speed actions
y with C_y(D) > eps. The state is discretized to a grid; the controls y to a grid.
A landing point between two grid nodes counts as "in V_n" if BOTH neighbours are
(pessimistic estimate) or if EITHER is (optimistic estimate). The gap between the
two, and its change under refinement, is the reported discretization error. It
is not a certified bound: V_n need not be an interval at the grid scale.
"""

import json
import math
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path

import numpy as np

from tagsim import AgentSpec, pure_pursuit, simulate
from tagsim.viability import C, T, alpha_sym, g, heading, plateau_interval, y_star

OUT = Path(__file__).resolve().parents[1] / "results/stage4a"

S_VALUES = (1.5, 2.0)
ALPHA_FACTORS = (0.9, 0.99, 0.999, 1.0, 1.001, 1.01)
GRIDS = ((750, 300), (1500, 600), (3000, 1200))   # (state nodes, control values)
N_MAX = 200


def horizons(s, alpha, n_state, n_ctrl, n_max=N_MAX):
    """Grid estimates of N(D) = sup{n : D in V_n} (capped at n_max), pessimistic and optimistic."""
    eps = 1 / alpha
    D_max = s + 2.0
    Dg = np.linspace(eps, D_max, n_state + 1)[1:]          # nodes strictly above eps
    h = Dg[1] - Dg[0]
    ys = np.linspace((s - 1) / 2, (s + 1) / 2, n_ctrl)
    TT = T(Dg[:, None], ys[None, :], s)
    ok = C(Dg[:, None], ys[None, :], s) > eps
    k = np.floor((TT - Dg[0]) / h).astype(int)             # left neighbour node of each landing
    below = TT <= eps                                        # can't happen when ok, kept for safety
    kL, kR = np.clip(k, 0, n_state - 1), np.clip(k + 1, 0, n_state - 1)
    left_off = k < 0                                         # landing in (eps, first node): only right neighbour

    # plateau intervals as node ranges: pessimistic = nodes inside, optimistic = one node of slack each side
    pin, pout = np.zeros((n_state, 2), int), np.zeros((n_state, 2), int)
    for i, D in enumerate(Dg):
        p = plateau_interval(D, s)
        if p is None or p[1] <= eps:
            pin[i] = pout[i] = (1, 0)                        # empty range
            continue
        lo, hi = max(p[0], eps), p[1]
        a, b = math.ceil((lo - Dg[0]) / h - 1e-12), math.floor((hi - Dg[0]) / h + 1e-12)
        pin[i] = (max(a, 0), min(b, n_state - 1))
        pout[i] = (max(a - 1, 0), min(b + 1, n_state - 1))

    out = {}
    for mode in ("pess", "opt"):
        V = np.ones(n_state, bool)
        N = np.full(n_state, n_max)
        rng = pin if mode == "pess" else pout
        for n in range(1, n_max + 1):
            if mode == "pess":
                land = V[kL] & V[kR] & ~left_off
            else:
                land = V[kL] | V[kR]
            via_fs = (ok & land & ~below).any(axis=1)
            cs = np.concatenate([[0], np.cumsum(V)])
            via_pl = (rng[:, 1] >= rng[:, 0]) & (cs[np.minimum(rng[:, 1], n_state - 1) + 1] - cs[rng[:, 0]] > 0)
            Vn = via_fs | via_pl
            N[V & ~Vn] = n - 1
            V = Vn
            if not V.any():
                break
        surv = Dg[V]
        out[mode] = dict(max_horizon=int(N.max()), argmax_D=float(Dg[N.argmax()]),
                         survivors=int(V.sum()),
                         survivor_range=[float(surv.min()), float(surv.max())] if surv.size else None)
    return out


def fixed_point_interval(s, alpha):
    """{y : g(y) > alpha^-2}: the exact set of separations with a safe period-1 orbit."""
    ys, eps2 = y_star(s), 1 / alpha ** 2
    if g(ys, s) <= eps2:
        return None

    def root(lo, hi, increasing):
        for _ in range(200):
            m = (lo + hi) / 2
            if (g(m, s) > eps2) == increasing:
                hi = m
            else:
                lo = m
        return (lo + hi) / 2
    return root((s - 1) / 2, ys, True), root(ys, (s + 1) / 2, False)


def run_horizons():
    rows, lines = [], ["Grid survival horizons N(D) = sup{n : D in V_n}, capped at %d periods." % N_MAX,
                       "pess/opt = pessimistic/optimistic landing rule (see module docstring). Estimates, not proofs.", ""]
    for s in S_VALUES:
        a_sym = alpha_sym(s)
        lines.append(f"s = {s}: y* = {y_star(s):.10f}, alpha_sym = {a_sym:.10f}")
        for f in ALPHA_FACTORS:
            alpha = a_sym * f
            fp = fixed_point_interval(s, alpha)
            fp_txt = ("empty (g touches alpha^-2 at y* only)" if f == 1.0 else
                      f"({fp[0]:.6f}, {fp[1]:.6f})" if fp else "empty")
            lines.append(f"  alpha = {f} alpha_sym = {alpha:.6f};  exact period-1 set {fp_txt}")
            for ns, nc in GRIDS:
                r = horizons(s, alpha, ns, nc)
                rows.append(dict(s=s, alpha_factor=f, alpha=alpha, n_state=ns, n_ctrl=nc, **r))
                fmt = lambda x: (f"max N = {x['max_horizon']:3d} at D = {x['argmax_D']:.4f}; "
                                 + (f"survive {N_MAX}: {x['survivors']} nodes in [{x['survivor_range'][0]:.4f}, "
                                    f"{x['survivor_range'][1]:.4f}]" if x['survivors'] else f"none survive {N_MAX}"))
                lines.append(f"    grid {ns:4d} x {nc:4d}  pess: {fmt(r['pess'])}")
                lines.append(f"    {'':15s}  opt:  {fmt(r['opt'])}")
        lines.append("")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "horizons.json").write_text(json.dumps(rows, indent=1) + "\n")
    (OUT / "horizons.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def chain_decimal(s, a0="0.01", steps=600, prec=400):
    """Theorem 6(c) construction in `prec`-digit Decimal arithmetic: D_k = y* + a_k,
    action y_k = y* + beta a_k. Returns (min clearance^2 - G, final a, contraction ratios)."""
    getcontext().prec = prec
    q = Fraction(s).limit_denominator(1000)
    s = Decimal(q.numerator) / Decimal(q.denominator)
    one = Decimal(1)
    gD = lambda y: y * y - y * (s * s - 1) / (4 * (s - y))
    lo, hi = s / 3, s
    for _ in range(4 * prec):
        m = (lo + hi) / 2
        if 8 * m * (s - m) ** 2 > s * (s * s - 1):
            lo = m
        else:
            hi = m
    ys = (lo + hi) / 2
    G = gD(ys)
    c2 = (s * s - 1) / (4 * ys * (s - ys))
    beta = max(Decimal(0), one - one / (4 * c2))
    a, worst, ratios = Decimal(a0), None, []
    for _ in range(steps):
        D, y = ys + a, ys + beta * a
        assert D < 2 * y
        margin = D * D * gD(y) / (y * y) - G           # closest approach^2 - eps^2 at alpha = alpha_sym
        Dn = (D * D - (s * s - 1) * (D - y) / (s - y)).sqrt()
        ratios.append((Dn - ys) / a)
        worst = margin if worst is None else min(worst, margin)
        a = Dn - ys
    return worst, a, (float(min(ratios)), float(max(ratios)))


class BoundaryChain:
    """Engine policy for the chain: at each decision, a = D - y* (normalized), play action
    y* + beta a in the period frame. Must decide at every chaser decision (aligned, a = 1)."""

    def __init__(self, s, tau):
        self.s, self.tau, self.ys = s, float(tau), y_star(s)
        c2 = (s * s - 1) / (4 * self.ys * (s - self.ys))
        self.beta = max(0.0, 1 - 1 / (4 * c2))

    def __call__(self, obs):
        u = obs.pos_self - obs.pos_opp
        D = np.linalg.norm(u) / self.tau
        u = u / np.linalg.norm(u)
        y = self.ys + self.beta * (D - self.ys)
        vx, vy = heading(y, self.s)
        v = vx * u + vy * np.array([-u[1], u[0]])
        n = np.linalg.norm(v)
        return v / n if n > 1 else v


def run_chain():
    lines = []
    for s in S_VALUES:
        worst, a, (rmin, rmax) = chain_decimal(s)
        lines.append(f"s = {s}: 600 steps from a_0 = 0.01 in 400-digit arithmetic: "
                     f"min (clearance^2 - G) = {float(worst):.3e} > 0, final a = {float(a):.3e}, "
                     f"a_(k+1)/a_k in [{rmin:.4f}, {rmax:.4f}]")
        a_s = alpha_sym(s)
        ys = y_star(s)
        for f, periods in ((1.0, 30), (1 - 1e-3, 30)):
            tau = Fraction(repr(a_s * f))
            res = simulate(AgentSpec(s, tau), AgentSpec(1.0, tau), [0, 0], [(ys + 0.01) * float(tau), 0], 1.0,
                           periods * tau, pure_pursuit, BoundaryChain(s, tau))
            r = res.x_E - res.x_C
            lines.append(f"  engine, alpha = {f} alpha_sym, start y* + 0.01: "
                         + (f"captured at t = {res.capture_time / float(tau):.3f} periods" if res.captured
                            else f"no capture in {periods} periods; final D - y* = "
                                 f"{np.linalg.norm(r[-1]) / float(tau) - ys:.3e}"))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "boundary_chain.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("chain", "all"):
        run_chain()
    if cmd in ("horizons", "all"):
        run_horizons()
