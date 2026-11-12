"""Stage 3: how far beyond alpha_C = 1 does pure pursuit's guarantee extend?

    python experiments/stage3.py orbits    # periodic-orbit optimization -> results/stage3/orbits.json
    python experiments/stage3.py sweep     # best-response vs heuristics -> results/stage3/sweep.csv
    python experiments/stage3.py sweep_original   # same sweep, pre-fix planner -> sweep_original_planner.csv
    python experiments/stage3.py certify   # exact-rational certification of optimized orbits
    python experiments/stage3.py closure   # closure residuals / clearances of float orbits
    python experiments/stage3.py ablation  # planner fixes on/off, started on known escape orbits
    python experiments/stage3.py phase     # does clock alignment unlock escapes the sweep missed?
    python experiments/stage3.py figures

Units throughout: R_E = 1, tau_C = 1 for the orbit problem (lengths in R_E tau_C);
eps = R_E = 1 for the sweep (so alpha_C = tau_C).

Orbit problem. A runner whose clock contains the chaser's (a = 1/m, aligned) re-plans
at every chaser decision, where PP's future depends only on the separation D. A
period-P orbit is P consecutive chaser periods, each a "pass" from separation D_i to
D_{i+1} (indices mod P) with m straight runner legs, every leg clear of the eps-ball.
Rotation invariance of PP makes any such cycle an exact infinite evasion. We maximize
the worst closest approach M over the cycle; the orbit then escapes iff
alpha_C > 1/M (eps = R_E tau_C / alpha_C = 1/alpha_C in these units).
"""

import csv
import json
import math
import sys
import time
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tagsim import (AgentSpec, BestResponseVsPP, Perpendicular, PredictiveEvasion, flee,  # noqa: E402
                    min_separation, pure_pursuit, simulate)
from tagsim.best_response import SymmetricPass, best_pass  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "configs/stage3.json").read_text())
OUT = ROOT / "results/stage3"
FIG = ROOT / "figures/stage3"


# --- periodic orbits

def pass_geometry(d0, ph, q, s):
    """One chaser period in its own frame: chaser from origin along +x at speed s,
    runner from (d0, 0) on m equal legs. Returns (closest approach per leg, end separation)."""
    m = len(ph)
    h = 1.0 / m
    p = np.array([d0, 0.0])
    seps = np.empty(m)
    for j in range(m):
        c = np.array([s * j * h, 0.0])
        v = q[j] * np.array([math.cos(ph[j]), math.sin(ph[j])])
        seps[j] = min_separation(p - c, v - np.array([s, 0.0]), h)[1]
        p = p + v * h
    return seps, float(np.linalg.norm(p - np.array([s, 0.0])))


def unpack(x, P, m):
    D = x[:P]
    rest = x[P:].reshape(P, 2, m)
    return D, rest[:, 0], rest[:, 1]


def cycle(x, s, P, m):
    D, ph, q = unpack(x, P, m)
    seps, ends = [], []
    for i in range(P):
        sp, end = pass_geometry(D[i], ph[i], q[i], s)
        seps.append(sp)
        ends.append(end - D[(i + 1) % P])
    return np.concatenate(seps), np.array(ends)


def optimize_orbit(s, P, m, x0):
    from scipy.optimize import minimize
    X0 = np.concatenate([x0, [0.05]])
    cons = [{"type": "ineq", "fun": lambda X: cycle(X[:-1], s, P, m)[0] - X[-1]},
            {"type": "eq", "fun": lambda X: cycle(X[:-1], s, P, m)[1]}]
    bounds = [(1e-3, s + 1)] * P + ([(None, None)] * m + [(0, 1)] * m) * P + [(0, None)]
    r = minimize(lambda X: -X[-1], X0, method="SLSQP", bounds=bounds, constraints=cons,
                 options={"maxiter": 1000, "ftol": 1e-13})
    seps, ends = cycle(r.x[:-1], s, P, m)
    if np.abs(ends).max() > 1e-9:
        return -1.0, r.x[:-1]
    return float(seps.min()), r.x[:-1]


def random_start(rng, s, P, m):
    D = rng.uniform(0.3, 1.0, P) * s
    return np.concatenate([D] + [np.concatenate([rng.uniform(-np.pi, np.pi, m), np.ones(m)]) for _ in range(P)])


def split_legs(x, P, m):
    """Same path with every leg cut in two: a feasible start for 2m legs with the same value."""
    D, ph, q = unpack(x, P, m)
    return np.concatenate([D] + [np.concatenate([np.repeat(ph[i], 2), np.repeat(q[i], 2)]) for i in range(P)])


def orbits():
    rng = np.random.default_rng(CFG["seed"])
    out = []
    for s in CFG["orbit_speed_ratios"]:
        for P in CFG["orbit_periods"]:
            prev = None
            for m in CFG["orbit_legs"]:
                t0 = time.perf_counter()
                starts = [random_start(rng, s, P, m) for _ in range(CFG["orbit_starts"])]
                if prev is not None and m == 2 * prev[0]:
                    starts.append(split_legs(prev[1], P, prev[0]))
                best = (-1.0, None)
                for x0 in starts:
                    val, x = optimize_orbit(s, P, m, x0)
                    if val > best[0]:
                        best = (val, x)
                prev = (m, best[1])
                D, ph, q = unpack(best[1], P, m)
                row = dict(s=s, P=P, m=m, M=best[0], alpha_star=1 / best[0], D=D.tolist(),
                           headings=ph.tolist(), speeds=q.tolist(), seconds=time.perf_counter() - t0)
                out.append(row)
                print(f"s={s} P={P} m={m}: M={best[0]:.6f} alpha*={1 / best[0]:.4f} D={np.round(D, 4)}", flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "orbits.json").write_text(json.dumps(out, indent=1))


class OrbitRunner:
    """Replays an optimized orbit: at each chaser decision (every m-th own decision,
    aligned clocks) rotate the stored pass into the current line of sight."""

    def __init__(self, row):
        self.P, self.m = row["P"], row["m"]
        self.ph, self.q = np.array(row["headings"]), np.array(row["speeds"])

    def __call__(self, obs):
        k = obs.k
        i, j = (k // self.m) % self.P, k % self.m
        if j == 0:
            u = obs.pos_self - obs.pos_opp
            self.frame = math.atan2(u[1], u[0])
        a = self.frame + self.ph[i, j]
        v = self.q[i, j] * np.array([math.cos(a), math.sin(a)])
        n = np.linalg.norm(v)
        return v / n if n > 1 else v


def verify_orbit(row, alpha, periods=2000):
    """Run an optimized orbit in the engine at alpha_C (eps = 1/alpha in units tau_C = R_E = 1)."""
    s, m = row["s"], row["m"]
    tau = Fraction(1)
    res = simulate(AgentSpec(s, tau), AgentSpec(1.0, tau / m), [0, 0], [row["D"][0], 0], 1 / alpha,
                   periods * tau, pure_pursuit, OrbitRunner(row))
    return res


# --- best-response sweep

def initial_states():
    rng = np.random.default_rng(CFG["seed"])
    g = CFG["phase_grid"]
    return [dict(los=rng.uniform(0, 2 * np.pi), head_C=rng.uniform(0, 2 * np.pi),
                 head_E=rng.uniform(0, 2 * np.pi), jC=int(rng.integers(g)), jE=int(rng.integers(g)))
            for _ in range(CFG["n_states"])]


def setup(s, alpha, a, st):
    R_C = s
    tau_C = Fraction(alpha)
    tau_E = Fraction(a) * tau_C
    g = CFG["phase_grid"]
    phi_C, phi_E = Fraction(st["jC"], g) * tau_C, Fraction(st["jE"], g) * tau_E
    C = AgentSpec(R_C, tau_C, first_decision=phi_C,
                  initial_velocity=[R_C * math.cos(st["head_C"]), R_C * math.sin(st["head_C"])])
    E = AgentSpec(1.0, tau_E, first_decision=phi_E,
                  initial_velocity=[math.cos(st["head_E"]), math.sin(st["head_E"])])
    D0 = CFG["D0"]
    x_E0 = [D0 * math.cos(st["los"]), D0 * math.sin(st["los"])]
    # approach phase (Prop 1 case (i)) plus a long look at whatever happens after
    H = Fraction(str(round((D0 + float(tau_C)) / (s - 1) + 3 * float(tau_C), 6))) + CFG["extra_periods"] * tau_C
    return C, E, x_E0, H


def runners(original=False):
    if original:  # the pre-fix planner, for the before/after comparison only
        return {name: BestResponseVsPP(hold_action=False, complete_partial_plans=False, **kw)
                for name, kw in CFG["planner_configs"].items()}
    rs = {"flee": flee, "perpendicular": Perpendicular(1), "predictive": PredictiveEvasion()}
    for name, kw in CFG["planner_configs"].items():
        rs[name] = BestResponseVsPP(**kw)
    return rs


def min_sep_after(res, t_from):
    t, r = res.times, res.x_E - res.x_C
    best = math.inf
    for i in range(len(t) - 1):
        if t[i + 1] <= t_from or t[i + 1] == t[i]:
            continue
        w = (r[i + 1] - r[i]) / (t[i + 1] - t[i])
        start = max(t[i], t_from)
        best = min(best, min_separation(r[i] + (start - t[i]) * w, w, t[i + 1] - start)[1])
    return best


def run_cell(task):
    s, alpha, a, i, st, original = task
    C, E, x_E0, H = setup(s, alpha, a, st)
    rows = []
    for name, runner in runners(original).items():
        t0 = time.perf_counter()
        res = simulate(C, E, [0, 0], x_E0, 1.0, H, pure_pursuit, runner)
        rows.append(dict(s=s, alpha_C=alpha, a=a, state=i, runner=name, horizon=str(H),
                         captured=int(res.captured), capture_time=res.capture_time,
                         min_sep=min_sep_after(res, 0.0),
                         late_min_sep=None if res.captured else min_sep_after(res, float(H) / 2),
                         n_intervals=res.n_intervals, seconds=round(time.perf_counter() - t0, 3)))
    return rows


def sweep(original=False):
    name = "sweep_original_planner" if original else "sweep"
    states = initial_states()
    tasks = [(s, alpha, a, i, st, original) for s in CFG["speed_ratios"] for alpha in CFG["alpha_C"]
             for a in CFG["agility_ratio_a"] for i, st in enumerate(states)]
    with Pool() as pool:
        rows = [r for cell in pool.imap(run_cell, tasks, chunksize=1) for r in cell]
    OUT.mkdir(parents=True, exist_ok=True)
    fields = [k for k in rows[0] if k != "seconds"]
    with open(OUT / f"{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    total = sum(r["seconds"] for r in rows)
    (OUT / f"{name}_cost.txt").write_text(f"{len(rows)} games, {total:.0f} CPU-seconds (not reproducible)\n")
    print(f"{len(rows)} games, {total:.0f} CPU-s")



# --- exact certification of optimized orbits
#
# With the m runner legs fixed (as velocities in the chaser-line frame), the end
# point is (D + X, Y) with X, Y independent of D, so the closure condition
# |(D + X - s, Y)|^2 = D^2 is *linear* in D:  D* = ((X - s)^2 + Y^2) / (2 (s - X)).
# Rational leg velocities with |v|^2 <= 1 (checked exactly) give a rational D*,
# and every leg's closest approach squared is rational too. So an orbit is
# certified in exact arithmetic: no tolerances, no interval bounds.

def _rational_velocity(phi, q, den=10**9):
    t = Fraction(math.tan(phi / 2)).limit_denominator(den)  # Pythagorean parametrization: exact unit vector
    u = ((1 - t * t) / (1 + t * t), 2 * t / (1 + t * t))
    q = min(Fraction(q).limit_denominator(den), Fraction(1))
    return q * u[0], q * u[1]


def certify(row, digits=4):
    """Exact closure D* and certified escape threshold for one P = 1 orbit.
    Returns dict with D*, exact min clearance^2 (as float and str), and a
    rational alpha_c such that the orbit escapes PP for every alpha_C >= alpha_c."""
    s = Fraction(str(row["s"]))
    m = row["m"]
    h = Fraction(1, m)
    V = [_rational_velocity(ph, q) for ph, q in zip(row["headings"][0], row["speeds"][0])]
    assert all(vx * vx + vy * vy <= 1 for vx, vy in V)
    X = sum(vx for vx, _ in V) * h
    Y = sum(vy for _, vy in V) * h
    assert X < s
    D = ((X - s) ** 2 + Y ** 2) / (2 * (s - X))
    px, py = D, Fraction(0)
    worst = None
    for j, (vx, vy) in enumerate(V):
        rx, ry = px - s * j * h, py
        wx, wy = vx - s, vy
        a = wx * wx + wy * wy
        sig = min(max(-(rx * wx + ry * wy) / a, Fraction(0)), h)
        d2 = (rx + sig * wx) ** 2 + (ry + sig * wy) ** 2
        worst = d2 if worst is None or d2 < worst else worst
        px, py = px + vx * h, py + vy * h
    assert (px - s) ** 2 + py ** 2 == D * D  # closure, exactly
    # smallest decimal alpha_c with eps^2 = 1/alpha_c^2 < worst
    alpha_c = Fraction(math.ceil(10 ** digits / math.sqrt(float(worst))), 10 ** digits)
    while 1 / alpha_c ** 2 >= worst:
        alpha_c += Fraction(1, 10 ** digits)
    return dict(s=row["s"], s_exact=str(s), m=m, D_star=float(D), clearance=math.sqrt(float(worst)),
                alpha_c=str(alpha_c), alpha_c_float=float(alpha_c), D_star_exact=str(D),
                clearance_sq_exact=str(worst),
                velocities_exact=[[str(vx), str(vy)] for vx, vy in V])


def certify_all():
    orb = json.loads((OUT / "orbits.json").read_text())
    out = []
    for row in orb:
        if row["P"] != 1:
            continue
        c = certify(row)
        c["alpha_star_float_opt"] = row["alpha_star"]
        res = verify_orbit(dict(row, D=[c["D_star"]]), 1.001 * c["alpha_c_float"], periods=500)
        c["engine_500_periods_at_1.001_alpha_c"] = "no capture" if not res.captured else "captured"
        out.append(c)
        print(f"s={c['s']} m={c['m']}: D*={c['D_star']:.6f} clearance={c['clearance']:.6f} "
              f"alpha_c={c['alpha_c']} (float optimum {row['alpha_star']:.5f}) engine: {c['engine_500_periods_at_1.001_alpha_c']}")
    (OUT / "certified_orbits.json").write_text(json.dumps(out, indent=1))


def closure_table():
    """Float orbits as optimized: closure residual, clearance, engine check."""
    orb = json.loads((OUT / "orbits.json").read_text())
    lines = ["| s | P | m | runner period | alpha* (opt) | D_i / (R_E tau_C) | closure residual | "
             "clearance at 1.01 alpha*, eps units | 2000 periods at 1.01 alpha* | 0.99 alpha* |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for row in orb:
        x = np.concatenate([row["D"]] + [np.concatenate([h, q]) for h, q in zip(row["headings"], row["speeds"])])
        seps, ends = cycle(x, row["s"], row["P"], row["m"])
        hi = verify_orbit(row, 1.01 * row["alpha_star"], periods=2000)
        lo = verify_orbit(row, 0.99 * row["alpha_star"], periods=2000)
        clear = min_sep_after(hi, 0.0) * 1.01 * row["alpha_star"]
        lines.append(f"| {row['s']} | {row['P']} | {row['m']} | tau_C/{row['m']} | {row['alpha_star']:.5f} | "
                     f"{', '.join(f'{d:.4f}' for d in row['D'])} | {np.abs(ends).max():.1e} | {clear:.5f} | "
                     f"{'no capture' if not hi.captured else 'CAPTURED'} | "
                     f"{'captured t=%.2f' % lo.capture_time if lo.captured else 'no capture'} |")
    (OUT / "orbit_table.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


ABLATION_CONFIGS = {"small (24 dirs, beam 32, 2 periods)": dict(n_dirs=24, beam=32),
                    "large (48 dirs, beam 64, 4 periods)": dict(n_dirs=48, beam=64, horizon_chaser_periods=4,
                                                                max_depth=16)}


def _ablation_cell(task):
    s, m, alpha, hold, complete, cname = task
    orb = json.loads((OUT / "orbits.json").read_text())
    if m == "sym":
        D, a = SymmetricPass(s, 1.0, float(alpha)).D, Fraction(1)
    else:
        row = next(r for r in orb if r["s"] == s and r["P"] == 1 and r["m"] == m)
        D, a = row["D"][0] * float(alpha), Fraction(1, m)
    res = simulate(AgentSpec(s, alpha), AgentSpec(1.0, alpha * a), [0, 0], [D, 0], 1.0, 60 * alpha, pure_pursuit,
                   BestResponseVsPP(hold_action=hold, complete_partial_plans=complete, **ABLATION_CONFIGS[cname]))
    return task, ("escaped 60 periods" if not res.captured else f"caught t={res.capture_time:.2f}")


def ablation():
    """Planner started on known escape orbits' own states (aligned clocks).
    Escape exists by construction there, so 'caught' is a planner failure."""
    orb = json.loads((OUT / "orbits.json").read_text())
    cases = []
    for s in (1.2, 1.5, 2.0):
        a4 = next(r for r in orb if r["s"] == s and r["P"] == 1 and r["m"] == 4)["alpha_star"]
        asym = 1 / math.sqrt(best_pass(s)[1])
        for f in (Fraction(102, 100), Fraction(105, 100), Fraction(115, 100), Fraction(130, 100)):
            cases.append((s, 4, Fraction(repr(round(a4 * float(f), 6))), f, a4))
            cases.append((s, "sym", Fraction(repr(round(asym * float(f), 6))), f, asym))
    tasks = [(s, m, al, hold, comp, cname) for s, m, al, f, _ in cases
             for hold, comp in [(False, False), (True, False), (False, True), (True, True)] for cname in ABLATION_CONFIGS]
    with Pool() as pool:
        res = dict(pool.map(_ablation_cell, tasks))
    lines = ["Planner started on a known escape orbit's own state (aligned clocks; escape exists by construction).",
             "orbit 'sym' = Prop 3 symmetric pass (runner a = 1); orbit 4 = optimized 4-leg orbit (runner a = 1/4).",
             "columns: hold_action / complete_partial_plans", ""]
    for s, m, al, f, ath in cases:
        lines.append(f"s={s} orbit={m} alpha_C={float(al):.4f} (= {float(f):.2f} x threshold {ath:.4f})")
        for cname in ABLATION_CONFIGS:
            cells = [f"{'on' if h else 'off'}/{'on' if c else 'off'}: {res[(s, m, al, h, c, cname)]}"
                     for h, c in [(False, False), (True, False), (False, True), (True, True)]]
            lines.append(f"    {cname}: " + " | ".join(cells))
    (OUT / "planner_ablation.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def _phase_cell(task):
    s, alpha, i, aligned = task
    C, E, x0, H = setup(s, alpha, "1/4", initial_states()[i])
    phi_E = C.first_decision % E.period if aligned else E.first_decision
    E = AgentSpec(1.0, E.period, first_decision=phi_E, initial_velocity=E.initial_velocity)
    res = simulate(C, E, [0, 0], x0, 1.0, H, pure_pursuit, BestResponseVsPP(**CFG["planner_configs"]["br_h4_b64_d48"]))
    return s, alpha, aligned, not res.captured


def phase():
    """Same states as the sweep at a = 1/4, but with the runner's clock aligned to the chaser's."""
    cases = [(1.5, "8/5"), (1.2, "7/5"), (2.0, "8/5")]
    tasks = [(s, al, i, ali) for s, al in cases for i in range(CFG["n_states"]) for ali in (False, True)]
    with Pool() as pool:
        out = pool.map(_phase_cell, tasks)
    lines = ["a=1/4, planner br_h4_b64_d48, sweep initial states; escapes out of %d" % CFG["n_states"]]
    for s, al in cases:
        for ali in (False, True):
            n = sum(o[3] for o in out if o[:3] == (s, al, ali))
            lines.append(f"s={s} alpha_C={al} runner clock {'aligned' if ali else 'random '}: {n}")
    (OUT / "phase_alignment_check.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


# --- figures

COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # reference categorical slots 1-4


def pp_series(res):
    """Separation at each chaser decision."""
    ts = [Fraction(e["t"]) for e in res.events if e.get("agent") == "C"]
    return np.array([np.linalg.norm(np.subtract(*res.positions_at(float(t))[::-1])) for t in ts])


def _escape_counts(path, planners_only=True):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    out = {}
    for r in rows:
        if planners_only and not r["runner"].startswith("br_"):
            continue
        k = (float(r["s"]), r["a"], float(Fraction(r["alpha_C"])), r["state"])
        out[k] = out.get(k, False) or r["captured"] == "0"
    return out


def figures():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import stage2
    FIG.mkdir(parents=True, exist_ok=True)
    orb = json.loads((OUT / "orbits.json").read_text())
    cert = json.loads((OUT / "certified_orbits.json").read_text())
    with open(OUT / "sweep.csv") as f:
        rows = list(csv.DictReader(f))
    planners = sorted(CFG["planner_configs"])
    alphas = [float(Fraction(a)) for a in CFG["alpha_C"]]

    # 1. threshold map: proofs vs certificates vs numerics
    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    ss = np.linspace(1.001, 3, 400)
    asym = np.array([1 / math.sqrt(best_pass(x)[1]) for x in ss])
    ax.plot(ss, np.ones_like(ss), color="0.6", lw=1, ls=":", label=r"Prop 1: capture proven for $\alpha_C\leq 1$")
    ax.plot(ss, 2 * ss / (1 + ss), color="k", lw=2, label=r"Thm 1: capture proven for $\alpha_C\leq 2s/(1+s)$")
    ax.plot(ss, asym, color=COLORS[1], lw=2, label=r"Thm 2: escape proven for $\alpha_C>\alpha_{sym}(s)$ (aligned, $a=1$)")
    ax.fill_between(ss, 2 * ss / (1 + ss), asym, color="0.88", lw=0, label="not settled by Thm 1/2")
    pts = [(c["s"], c["alpha_c_float"]) for c in cert if c["m"] == 16]
    ax.plot(*zip(*pts), "*", color=COLORS[0], ms=12,
            label=r"exact-rational certified escape, 16 runner legs/period (aligned, $a=1/16$)")
    for m in (2, 4, 8):
        p2 = [(c["s"], c["alpha_c_float"]) for c in cert if c["m"] == m]
        ax.plot(*zip(*p2), "o", color=COLORS[0], ms=3, alpha=0.5, label="certified, m = 2, 4, 8" if m == 2 else None)
    esc = _escape_counts(OUT / "sweep.csv")
    for s_ in CFG["speed_ratios"]:
        hit = sorted({k[2] for k, v in esc.items() if v and k[0] == s_})
        ax.plot([s_], [hit[0]], "v", color=COLORS[2], ms=8, label="planner: smallest swept $\\alpha_C$ with an escape" if s_ == 1.2 else None)
        below = max(x for x in alphas if x < hit[0])
        ax.plot([s_], [below], "^", color=COLORS[2], ms=8, mfc="white",
                label="planner: next swept $\\alpha_C$ below, no escape (random phases)" if s_ == 1.2 else None)
    ax.set_xlabel(r"speed ratio $s=R_C/R_E$")
    ax.set_ylabel(r"$\alpha_C=R_E\tau_C/\varepsilon$")
    ax.set_xlim(1, 3)
    ax.set_ylim(0.9, 2.1)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7, loc="lower right")
    ax.set_title("Full-speed pure pursuit: proven capture, proven/certified escape, numerical evidence", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "threshold_map.png", dpi=170)
    fig.savefig(FIG / "threshold_map.pdf")
    plt.close(fig)

    # 2. escape fraction vs alpha_C (markers only: the alpha grid is sparse)
    fig, axes = plt.subplots(3, 3, figsize=(11, 8.5), sharex=True, sharey=True)
    for i, a in enumerate(CFG["agility_ratio_a"]):
        for j, s_ in enumerate(CFG["speed_ratios"]):
            ax = axes[i, j]
            cell = [r for r in rows if float(r["s"]) == s_ and r["a"] == a]
            series = [("best response (any of 3 planner configs)", None, "o", 7),
                      ("perpendicular", "perpendicular", "s", 5), ("predictive", "predictive", "D", 5),
                      ("flee", "flee", "x", 6)]
            for k, ((label, name, mk, ms), col) in enumerate(zip(series, COLORS)):
                y = []
                for al in CFG["alpha_C"]:
                    rs = [r for r in cell if r["alpha_C"] == al]
                    states = sorted({r["state"] for r in rs})
                    if name is None:
                        n = sum(any(r["captured"] == "0" for r in rs if r["state"] == st and r["runner"] in planners)
                                for st in states)
                    else:
                        n = sum(r["captured"] == "0" for r in rs if r["runner"] == name)
                    y.append(n / len(states))
                xs = np.array(alphas) * (1 + 0.012 * (k - 1.5))  # small dodge so markers don't hide each other
                ax.plot(xs, y, mk, color=col, ms=ms, label=label, mfc=col if mk != "s" else "white")
            ax.axvline(2 * s_ / (1 + s_), color="k", lw=1)
            ax.axvline(1 / math.sqrt(best_pass(s_)[1]), color=COLORS[1], lw=1, ls="--")
            ax.set_ylim(-0.05, 1.05)
            ax.grid(alpha=0.25)
            if i == 0:
                ax.set_title(f"s = {s_}", fontsize=10)
            if j == 0:
                ax.set_ylabel(f"a = {a}\\nfraction of 12 states,\\nno capture within H")
            if i == 2:
                ax.set_xlabel(r"$\alpha_C$ (swept values only)")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    handles += [plt.Line2D([], [], color="k", lw=1), plt.Line2D([], [], color=COLORS[1], lw=1, ls="--")]
    labels += [r"$2s/(1+s)$: capture proven at or below", r"$\alpha_{sym}(s)$: escape proven above (aligned $a=1$)"]
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=8.5)
    fig.suptitle("No capture within horizon H vs full-speed pure pursuit; random clock phases, paired initial states", y=0.995)
    fig.tight_layout(rect=(0, 0.07, 1, 0.98))
    fig.savefig(FIG / "escape_vs_alpha.png", dpi=160)
    fig.savefig(FIG / "escape_vs_alpha.pdf")
    plt.close(fig)

    # 3. original vs corrected planner, same states
    old, new = _escape_counts(OUT / "sweep_original_planner.csv"), _escape_counts(OUT / "sweep.csv")
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6), sharey=True)
    for ax, s_ in zip(axes, CFG["speed_ratios"]):
        for k, (a, col) in enumerate(zip(CFG["agility_ratio_a"], COLORS)):
            yo = [sum(old.get((s_, a, al, str(i)), False) for i in range(CFG["n_states"])) for al in alphas]
            yn = [sum(new.get((s_, a, al, str(i)), False) for i in range(CFG["n_states"])) for al in alphas]
            xs = np.array(alphas) * (1 + 0.015 * (k - 1))
            ax.plot(xs, yo, "o", mfc="white", color=col, ms=6)
            ax.plot(xs, yn, "o", color=col, ms=4, label=f"a = {a}")
        ax.axvline(2 * s_ / (1 + s_), color="k", lw=1)
        ax.set_title(f"s = {s_}", fontsize=10)
        ax.set_xlabel(r"$\alpha_C$ (swept values only)")
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("states (of 12) with an escape")
    h, l = axes[0].get_legend_handles_labels()
    h += [plt.Line2D([], [], marker="o", ls="", color="0.3", mfc="white"), plt.Line2D([], [], marker="o", ls="", color="0.3")]
    l += ["original planner (hollow)", "corrected planner (filled)"]
    fig.legend(h, l, loc="lower center", ncol=5, frameon=False, fontsize=8.5)
    fig.suptitle("Best-response planner before/after the two Stage 3 fixes (same states, same 3 configs)", y=0.99)
    fig.tight_layout(rect=(0, 0.1, 1, 0.95))
    fig.savefig(FIG / "planner_comparison.png", dpi=160)
    fig.savefig(FIG / "planner_comparison.pdf")
    plt.close(fig)

    # 4. escape trajectories, world frame
    s_, alpha = 1.5, 1.8
    tau = Fraction(repr(alpha))
    sp = SymmetricPass(s_, 1.0, alpha)
    res_sym = simulate(AgentSpec(s_, tau), AgentSpec(1.0, tau), [0, 0], [sp.D, 0], 1.0, 8 * tau, pure_pursuit, sp)
    row = next(r for r in orb if r["s"] == 1.5 and r["P"] == 1 and r["m"] == 16)
    c16 = next(c for c in cert if c["s"] == 1.5 and c["m"] == 16)
    a16 = 1.01 * c16["alpha_c_float"]
    res_m = verify_orbit(dict(row, D=[c16["D_star"]]), a16, periods=8)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
    for ax, res, title in [(axes[0], res_sym, f"Thm 2 symmetric pass, s=1.5, $\\alpha_C$={alpha}, a=1"),
                           (axes[1], res_m, f"certified 16-leg orbit, s=1.5, $\\alpha_C$={a16:.3f}, a=1/16")]:
        ax.plot(*res.x_C.T, color=COLORS[1], lw=1.2, label="chaser (PP)")
        ax.plot(*res.x_E.T, color=COLORS[0], lw=1.2, label="runner")
        ax.plot(*res.x_C[0], "s", color=COLORS[1], ms=5)
        ax.plot(*res.x_E[0], "s", color=COLORS[0], ms=5)
        ax.set_aspect("equal", adjustable="datalim")
        ax.grid(alpha=0.25)
        ax.set_xlabel(r"$x / \varepsilon$")
        ax.set_ylabel(r"$y / \varepsilon$")
        ax.set_title(title + "\n8 chaser periods; squares = start", fontsize=9)
    axes[0].legend(fontsize=8)
    ax = axes[2]
    for (lab, s2, al, a2, st_i), col in zip([("s=1.5, $\\alpha_C$=5/2, a=1/4, state 0", 1.5, "5/2", "1/4", 0),
                                             ("s=1.5, $\\alpha_C$=5/2, a=1/4, state 5", 1.5, "5/2", "1/4", 5),
                                             ("s=1.2, $\\alpha_C$=5/2, a=1/4, state 0", 1.2, "5/2", "1/4", 0)], COLORS):
        C, E, x0, H = stage2.setup(s2, al, a2, stage2.initial_states()[st_i])
        res = simulate(C, E, [0, 0], x0, 1.0, H + 60 * C.period, pure_pursuit, Perpendicular(1))
        ax.plot(pp_series(res) / float(C.period), "o", color=col, ms=2.5, label=lab)
    ax.set_xlabel("chaser decision index k")
    ax.set_ylabel(r"$D_k / (R_E\tau_C)$")
    ax.set_ylim(0, 6)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
    ax.set_title("perpendicular runner vs PP (Stage 2 states):\nseparation at chaser decisions settles to a fixed point", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "escape_orbits.png", dpi=170)
    fig.savefig(FIG / "escape_orbits.pdf")
    plt.close(fig)

    # 5. separation over continuous time, in units of eps
    def sep_curve(res, n=4000):
        t = np.linspace(res.times[0], res.times[-1], n)
        return t, np.array([np.linalg.norm(np.subtract(*res.positions_at(x)[::-1])) for x in t])

    cases = []
    res = simulate(AgentSpec(s_, tau), AgentSpec(1.0, tau), [0, 0], [sp.D, 0], 1.0, 6 * tau, pure_pursuit, sp)
    cases.append((f"Thm 2 symmetric pass (s=1.5, $\\alpha_C$={alpha})", res, float(tau)))
    res = verify_orbit(dict(row, D=[c16["D_star"]]), a16, periods=6)
    cases.append((f"certified 16-leg orbit (s=1.5, $\\alpha_C$={a16:.3f})", res, 1.0))  # tau_C = 1, eps = 1/alpha
    C, E, x0, H = setup(1.2, "8/5", "1/4", initial_states()[0])
    res = simulate(C, E, [0, 0], x0, 1.0, H, pure_pursuit, BestResponseVsPP(**CFG["planner_configs"]["br_h4_b64_d48"]))
    cases.append(("best-response planner, sweep state 0 (s=1.2, $\\alpha_C$=8/5, a=1/4)", res, float(C.period)))
    res = simulate(C, E, [0, 0], x0, 1.0, H, pure_pursuit, PredictiveEvasion())
    cases.append(("predictive heuristic, same state (captured)", res, float(C.period)))
    fig, axes = plt.subplots(len(cases), 1, figsize=(9, 2.1 * len(cases)), sharey=False)
    for ax, (lab, res, tc), col in zip(axes, cases, COLORS):
        t, d = sep_curve(res)
        eps = 1.0 if tc != 1.0 else 1 / a16
        ax.plot(t / tc, d / eps, color=col, lw=1)
        ax.axhline(1, color="k", lw=0.8)
        ax.set_ylabel(r"$|x_E-x_C|/\varepsilon$")
        ax.set_title(lab + ("" if not res.captured else f" -- captured at t/tau_C = {res.capture_time / tc:.2f}"), fontsize=9)
        ax.set_ylim(0, min(12, d.max() / eps * 1.05))
        ax.grid(alpha=0.25)
    axes[-1].set_xlabel(r"$t / \tau_C$")
    fig.tight_layout()
    fig.savefig(FIG / "separation_vs_time.png", dpi=160)
    fig.savefig(FIG / "separation_vs_time.pdf")
    plt.close(fig)


if __name__ == "__main__":
    {"orbits": orbits, "sweep": sweep, "sweep_original": lambda: sweep(original=True), "phase": phase,
     "certify": certify_all, "closure": closure_table, "ablation": ablation, "figures": figures}[sys.argv[1]]()
