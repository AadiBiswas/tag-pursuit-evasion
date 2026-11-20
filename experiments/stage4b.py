"""Stage 4B: the aligned two-leg game (runner decides twice per chaser period).
Theory: theory/stage4_multidecision_analysis.md.

    .venv/bin/python experiments/stage4b.py

Writes results/stage4b/two_leg.txt. Numerical optima here are NOT proofs: the
rigorous statements come from the exact certificates
(theory/certificates/orbits/*_m02.json for the lower bound on the level-orbit
clearance; theory/certificates/two_leg_upper_bound.py for the upper bound on every
non-decreasing period).

Units R_E = tau_C = 1; the chaser runs along +x at speed s for the whole period;
leg j has runner velocity u_j and lasts 1/2.
"""

import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from tagsim import AgentSpec, pure_pursuit, simulate

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/stage4b"
CERTS = ROOT / "theory/certificates/orbits"
S_VALUES = (1.5, 2.0)


def seg_dist2(px, py, dx, dy):
    a = dx * dx + dy * dy
    t = min(max(-(px * dx + py * dy) / a, 0.0), 1.0) if a > 0 else 0.0
    return (px + t * dx) ** 2 + (py + t * dy) ** 2, t


def two_leg(y, u1, u2, s):
    """(leg-1 clearance^2, leg-2 clearance^2, r(1/2), r(1), leg-2 closest point)."""
    d1 = ((u1[0] - s) / 2, u1[1] / 2)
    d2 = ((u2[0] - s) / 2, u2[1] / 2)
    p1 = (y + d1[0], d1[1])
    p2 = (p1[0] + d2[0], p1[1] + d2[1])
    c1, _ = seg_dist2(y, 0.0, *d1)
    c2, t2 = seg_dist2(p1[0], p1[1], *d2)
    return c1, c2, p1, p2, (p1[0] + t2 * d2[0], p1[1] + t2 * d2[1])


def optimize(s, level, starts=300, seed=0):
    """Max closest approach over (y, u1, u2) with |r(1)| = y (level) or >= y (up-step).
    SLSQP multistart; returns the best local optimum found (not a certified global one)."""
    def parts(z):
        return two_leg(z[0], z[1:3], z[3:5], s)
    cons = [{"type": "ineq", "fun": lambda z: parts(z)[0] - z[5]},
            {"type": "ineq", "fun": lambda z: parts(z)[1] - z[5]},
            {"type": "ineq", "fun": lambda z: 1 - z[1] ** 2 - z[2] ** 2},
            {"type": "ineq", "fun": lambda z: 1 - z[3] ** 2 - z[4] ** 2},
            {"type": "eq" if level else "ineq",
             "fun": lambda z: parts(z)[3][0] ** 2 + parts(z)[3][1] ** 2 - z[0] ** 2}]
    rng = np.random.default_rng(seed)
    best = (0.0, None)
    for _ in range(starts):
        r, ph = np.sqrt(rng.random(2)), rng.uniform(-math.pi, math.pi, 2)
        z0 = [rng.uniform(0.3, (s + 1) / 2), r[0] * math.cos(ph[0]), r[0] * math.sin(ph[0]),
              r[1] * math.cos(ph[1]), r[1] * math.sin(ph[1]), 0.1]
        z = minimize(lambda z: -z[5], z0, constraints=cons, method="SLSQP",
                     options=dict(maxiter=500, ftol=1e-14)).x
        feasible = all(c["fun"](z) > -1e-9 for c in cons) and (not level or abs(cons[4]["fun"](z)) < 1e-8)
        val = min(parts(z)[:2])
        if feasible and val > best[0]:
            best = (val, z)
    return best


def counterexample():
    """Exact: same two-leg controls, a start below the closing separation D* beats D* itself."""
    F = Fraction
    s, u1, u2 = F(3, 2), (F(12, 13), F(-5, 13)), (F(-7, 25), F(24, 25))

    def sd(px, py, dx, dy):
        # seg_dist2 with Fraction clamps, so nothing turns into a float
        a = dx * dx + dy * dy
        t = min(max(-(px * dx + py * dy) / a, F(0)), F(1))
        return (px + t * dx) ** 2 + (py + t * dy) ** 2

    def clear2(y):
        d1 = ((u1[0] - s) / 2, u1[1] / 2)
        d2 = ((u2[0] - s) / 2, u2[1] / 2)
        p1 = (y + d1[0], d1[1])
        p2 = (p1[0] + d2[0], p1[1] + d2[1])
        return min(sd(y, F(0), *d1), sd(*p1, *d2)), p2[0] ** 2 + p2[1] ** 2 - y * y
    X, Y = (u1[0] + u2[0]) / 2, (u1[1] + u2[1]) / 2
    Ds = ((X - s) ** 2 + Y ** 2) / (2 * (s - X))
    return dict(s=s, u1=u1, u2=u2, D_star=Ds, at_D_star=clear2(Ds), at_3_10=clear2(F(3, 10)))


def engine_check(s, cert_name, factor, periods=200):
    """Replay the certified two-leg orbit (legs in each period's frame) in the engine."""
    c = json.loads((CERTS / cert_name).read_text())
    alpha = Fraction(c["alpha_c"]) * Fraction(factor)
    tau = alpha                                   # eps = R_E = 1, so alpha_C = tau_C
    D0 = float(Fraction(c["D0"])) * float(tau)
    legs = [(float(Fraction(a)), float(Fraction(b))) for a, b in (leg["runner_velocity"] for leg in c["legs"])]
    state = {}

    def runner(obs):
        k = obs.k
        if k % 2 == 0:                             # chaser decision: freeze this period's frame
            u = obs.pos_self - obs.pos_opp
            u = u / np.linalg.norm(u)
            state["frame"] = (u, np.array([-u[1], u[0]]))
        u, n = state["frame"]
        a, b = legs[k % 2]
        return a * u + b * n
    res = simulate(AgentSpec(s, tau), AgentSpec(1.0, tau / 2), [0, 0], [D0, 0], 1.0, periods * tau,
                   pure_pursuit, runner)
    return res.captured, (res.capture_time / float(tau) if res.captured else None)


def main():
    lines = ["Stage 4B two-leg game. Numerical optima are local-search results (300 SLSQP starts),",
             "not certified global optima; see theory/stage4_multidecision_analysis.md.", ""]
    rows = []
    for s in S_VALUES:
        for level in (True, False):
            v, z = optimize(s, level)
            c1, c2, p1, p2, q2 = two_leg(z[0], z[1:3], z[3:5], s)
            row = dict(s=s, kind="level" if level else "up-step", clearance=math.sqrt(v), alpha=1 / math.sqrt(v),
                       y=z[0], u1=list(z[1:3]), u2=list(z[3:5]),
                       speeds=[math.hypot(*z[1:3]), math.hypot(*z[3:5])],
                       end_minus_start=math.hypot(*p2) - z[0],
                       leg_clearances=[math.sqrt(c1), math.sqrt(c2)], leg2_closest_x=q2[0])
            rows.append(row)
            lines.append(f"s = {s} best {row['kind']:7s}: clearance {row['clearance']:.7f}  alpha {row['alpha']:.7f}  "
                         f"y = {z[0]:.5f}  speeds = ({row['speeds'][0]:.6f}, {row['speeds'][1]:.6f})  "
                         f"|r(1)| - y = {row['end_minus_start']:.1e}  leg clearances = "
                         f"({row['leg_clearances'][0]:.6f}, {row['leg_clearances'][1]:.6f})  "
                         f"x of leg-2 closest point = {q2[0]:.4f}")
    lines.append("")
    cx = counterexample()
    lines.append(f"Counterexample to pathwise monotonicity (exact): s = 3/2, u1 = (12/13, -5/13), u2 = (-7/25, 24/25), "
                 f"D* = {cx['D_star']}")
    for key, y in (("at_3_10", "3/10"), ("at_D_star", "D*")):
        c2, up = cx[key]
        lines.append(f"  start y = {y}: closest approach^2 = {c2} (= {math.sqrt(c2):.6f}), "
                     f"|r(1)|^2 - y^2 = {float(up):.6f}")
    lines.append("")
    for s, name in ((1.5, "s3-2_m02.json"), (2.0, "s2-1_m02.json")):
        for f in ("1001/1000", "999/1000"):
            cap, t = engine_check(s, name, f)
            lines.append(f"engine: certified m=2 orbit {name} at alpha = {f} * alpha_c: "
                         + (f"captured at {t:.3f} periods" if cap else "no capture in 200 periods"))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "two_leg.txt").write_text("\n".join(lines) + "\n")
    (OUT / "two_leg_optima.json").write_text(json.dumps(rows, indent=1) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
