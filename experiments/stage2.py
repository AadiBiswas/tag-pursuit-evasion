"""Stage 2 preliminary sweep: baseline chasers vs baseline runners.

    python experiments/stage2.py run       # sweep -> results/stage2/{runs,summary}.csv
    python experiments/stage2.py figures   # figures/stage2/*, results/stage2/trajectories.npz

Units: eps = R_E = 1, so alpha_C = R_E tau_C / eps is just tau_C, and
a = A_C / A_E = tau_E / tau_C. Every (config, chaser, runner) cell uses the
same initial states, so strategy comparisons are paired.
"""

import csv
import json
import math
import sys
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tagsim import (AgentSpec, Intercept, Perpendicular, PredictiveEvasion, braking_pursuit,  # noqa: E402
                    flee, min_separation, pure_pursuit, simulate)

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "configs/stage2.json").read_text())
OUT = ROOT / "results/stage2"
FIG = ROOT / "figures/stage2"

CHASERS = {"pure_pursuit": pure_pursuit, "braking": braking_pursuit, "intercept": Intercept()}
RUNNERS = {"flee": flee, "perpendicular": Perpendicular(1), "predictive": PredictiveEvasion()}


def initial_states():
    rng = np.random.default_rng(CFG["seed"])
    n, g = CFG["n_states"], CFG["phase_grid"]
    return [dict(los=rng.uniform(0, 2 * np.pi), head_C=rng.uniform(0, 2 * np.pi),
                 head_E=rng.uniform(0, 2 * np.pi), jC=int(rng.integers(g)), jE=int(rng.integers(g)))
            for _ in range(n)]


def configs():
    for s in CFG["speed_ratios"]:
        for alpha in CFG["alpha_C"]:
            for a in CFG["agility_ratio_a"]:
                yield s, alpha, a


def horizon(s, tau_C):
    # 2x the Prop 1 time bound at the worst chaser phase: 3 tau_C + (D0 + R_E tau_C)/(R_C - R_E).
    # Only a guarantee for alpha_C <= 1; above that it's just "long enough to look".
    R_C = Fraction(str(s)) * Fraction(str(CFG["R_E"]))
    R_E = Fraction(str(CFG["R_E"]))
    B = 3 * tau_C + (Fraction(str(CFG["D0"])) + R_E * tau_C) / (R_C - R_E)
    return Fraction(str(CFG["horizon_factor"])) * B


def min_sep(res, t_from=0.0):
    """Exact min separation over [t_from, end]; trajectories are linear between knots."""
    t, r = res.times, res.x_E - res.x_C
    best = math.inf
    for i in range(len(t) - 1):
        if t[i + 1] < t_from or t[i + 1] == t[i]:
            continue
        w = (r[i + 1] - r[i]) / (t[i + 1] - t[i])
        start = max(t[i], t_from)
        r0 = r[i] + (start - t[i]) * w
        best = min(best, min_separation(r0, w, t[i + 1] - start)[1])
    return best


def prop1_bound(res, R_C, R_E, tau_C, phi_C):
    t1 = float(phi_C)
    if res.capture_time is not None and res.capture_time <= t1:
        return t1
    xc, xe = res.positions_at(t1)
    D1 = np.linalg.norm(xe - xc)
    K = math.ceil(max(D1 - R_C * tau_C, 0.0) / ((R_C - R_E) * tau_C))
    return t1 + (K + 1) * tau_C


def setup(s, alpha, a, st):
    eps, R_E, D0 = CFG["eps"], CFG["R_E"], CFG["D0"]
    R_C = s * R_E
    tau_C = Fraction(alpha) * Fraction(str(eps)) / Fraction(str(R_E))
    tau_E = Fraction(a) * tau_C
    g = CFG["phase_grid"]
    phi_C, phi_E = Fraction(st["jC"], g) * tau_C, Fraction(st["jE"], g) * tau_E
    C = AgentSpec(R_C, tau_C, first_decision=phi_C,
                  initial_velocity=[R_C * math.cos(st["head_C"]), R_C * math.sin(st["head_C"])])
    E = AgentSpec(R_E, tau_E, first_decision=phi_E,
                  initial_velocity=[R_E * math.cos(st["head_E"]), R_E * math.sin(st["head_E"])])
    x_E0 = [D0 * math.cos(st["los"]), D0 * math.sin(st["los"])]
    return C, E, x_E0, horizon(s, tau_C)


def run_cell(task):
    s, alpha, a, i, st = task
    C, E, x_E0, H = setup(s, alpha, a, st)
    rows = []
    for cn, chaser in CHASERS.items():
        for rn, runner in RUNNERS.items():
            res = simulate(C, E, [0, 0], x_E0, CFG["eps"], H, chaser, runner, speed_mode=CFG["speed_mode"])
            Hf = float(H)
            final = None if res.captured else float(np.linalg.norm(res.x_E[-1] - res.x_C[-1]))
            rows.append(dict(
                s=s, alpha_C=alpha, a=a, state=i, chaser=cn, runner=rn,
                tau_C=str(C.period), tau_E=str(E.period), phi_C=str(C.first_decision),
                phi_E=str(E.first_decision), horizon=str(H),
                captured=int(res.captured), capture_time=res.capture_time,
                min_sep=min_sep(res), late_min_sep=None if res.captured else min_sep(res, 0.75 * Hf),
                final_sep=final, n_intervals=res.n_intervals,
                prop1_bound=prop1_bound(res, C.max_speed, E.max_speed, float(C.period), C.first_decision)
                if cn == "pure_pursuit" else None))
    return rows


def wilson(k, n, z=1.96):
    if n == 0:
        return math.nan, math.nan
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def run():
    states = initial_states()
    tasks = [(s, alpha, a, i, st) for s, alpha, a in configs() for i, st in enumerate(states)]
    with Pool() as pool:
        rows = [r for cell in pool.map(run_cell, tasks, chunksize=4) for r in cell]
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "runs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    groups = {}
    for r in rows:
        groups.setdefault((r["s"], r["alpha_C"], r["a"], r["chaser"], r["runner"]), []).append(r)
    with open(OUT / "summary.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["s", "alpha_C", "a", "chaser", "runner", "n", "captures", "freq", "ci_lo", "ci_hi",
                    "median_capture_time", "min_sep_uncaptured", "prop1_violations"])
        for key, rs in groups.items():
            k = sum(r["captured"] for r in rs)
            lo, hi = wilson(k, len(rs))
            times = [r["capture_time"] for r in rs if r["captured"]]
            unc = [r["min_sep"] for r in rs if not r["captured"]]
            viol = sum(1 for r in rs if r["prop1_bound"] is not None and r["s"] > 1
                       and Fraction(r["alpha_C"]) <= 1
                       and (not r["captured"] or r["capture_time"] > r["prop1_bound"] + 1e-9))
            w.writerow([*key, len(rs), k, k / len(rs), lo, hi,
                        float(np.median(times)) if times else "", min(unc) if unc else "",
                        viol if key[3] == "pure_pursuit" else ""])
    print(f"{len(rows)} runs -> {OUT}")


def figures():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with open(OUT / "summary.csv") as f:
        summ = list(csv.DictReader(f))
    # first three slots of the reference categorical palette, fixed order; line style
    # carries a, so identity never rests on color alone
    colors = {"pure_pursuit": "#2a78d6", "braking": "#eb6834", "intercept": "#1baf7a"}
    styles = {"1/4": "-", "1": "--", "4": ":"}
    labels = {"1/4": "a = 1/4 (runner 4x more agile)", "1": "a = 1", "4": "a = 4 (runner 4x less agile)"}

    fig, axes = plt.subplots(3, 3, figsize=(11, 9), sharex=True, sharey=True)
    for i, rn in enumerate(CFG["runners"]):
        for j, s in enumerate(CFG["speed_ratios"]):
            ax = axes[i, j]
            for cn in CFG["chasers"]:
                for a in CFG["agility_ratio_a"]:
                    rs = [r for r in summ if r["runner"] == rn and r["chaser"] == cn
                          and float(r["s"]) == s and r["a"] == a]
                    x = [float(Fraction(r["alpha_C"])) for r in rs]
                    y = [float(r["freq"]) for r in rs]
                    ax.plot(x, y, styles[a], color=colors[cn], marker="o", ms=3, lw=1.3)
                    if a == "1/4":
                        ax.fill_between(x, [float(r["ci_lo"]) for r in rs], [float(r["ci_hi"]) for r in rs],
                                        color=colors[cn], alpha=0.12, lw=0)
            ax.axvline(1, color="0.5", lw=0.8)
            ax.set_xscale("log")
            ax.set_xticks([0.5, 1, 2, 4], ["1/2", "1", "2", "4"])
            ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
            ax.set_ylim(-0.03, 1.03)
            ax.grid(alpha=0.25)
            if i == 0:
                ax.set_title(f"s = R_C/R_E = {s}")
            if j == 0:
                ax.set_ylabel(f"runner: {rn}\ncapture frequency")
            if i == 2:
                ax.set_xlabel(r"$\alpha_C = R_E\tau_C/\varepsilon$")
    handles = [plt.Line2D([], [], color=c, lw=2, label=f"chaser: {n}") for n, c in colors.items()]
    handles += [plt.Line2D([], [], color="k", ls=ls, label=labels[a]) for a, ls in styles.items()]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False)
    fig.suptitle(f"Capture within horizon, {CFG['n_states']} paired initial states per point "
                 "(shaded: 95% Wilson CI, a = 1/4)", y=0.995)
    fig.tight_layout(rect=(0, 0.06, 1, 0.98))
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / "capture_vs_alpha.png", dpi=160)
    fig.savefig(FIG / "capture_vs_alpha.pdf")

    trajectories(plt)


# Representative cases: chosen after looking at runs.csv; see results/stage2/note.md.
REPRESENTATIVE = [
    dict(s=1.5, alpha="5/2", a="1/4", state=0, runner="flee"),
    dict(s=1.5, alpha="5/2", a="1/4", state=0, runner="perpendicular"),
    dict(s=1.5, alpha="5/2", a="1", state=2, runner="predictive"),
]


def trajectories(plt):
    states = initial_states()
    saved = {}
    fig, axes = plt.subplots(len(REPRESENTATIVE), 3, figsize=(11, 3.7 * len(REPRESENTATIVE)))
    axes = np.atleast_2d(axes)
    for row, case in enumerate(REPRESENTATIVE):
        C, E, x_E0, H = setup(case["s"], case["alpha"], case["a"], states[case["state"]])
        for col, (cn, chaser) in enumerate(CHASERS.items()):
            res = simulate(C, E, [0, 0], x_E0, CFG["eps"], H, chaser, RUNNERS[case["runner"]])
            tag = f"case{row}_{case['runner']}_{cn}"
            saved[f"{tag}_t"], saved[f"{tag}_xC"], saved[f"{tag}_xE"] = res.times, res.x_C, res.x_E
            ax = axes[row, col]
            ax.plot(*res.x_C.T, color="#eb6834", lw=1.1, label="chaser")
            ax.plot(*res.x_E.T, color="#2a78d6", lw=1.1, label="runner")
            dec = [ev for ev in res.events if ev["kind"] == "decision" and ev["agent"] == "C"]
            ax.plot(*np.array([d["pos"] for d in dec]).T, "o", color="#eb6834", ms=2.5, label="chaser decision")
            ax.plot(*res.x_C[0], "s", color="#eb6834", ms=5)
            ax.plot(*res.x_E[0], "s", color="#2a78d6", ms=5)
            if res.captured:
                ax.add_patch(plt.Circle(res.x_E[-1], CFG["eps"], fill=False, color="k", lw=0.8))
            outcome = (f"captured at t = {res.capture_time:.1f}" if res.captured
                       else f"no capture by H = {float(H):.0f}")
            ax.set_title(f"{cn} vs {case['runner']}\n{outcome}", fontsize=9)
            ax.set_aspect("equal", adjustable="datalim")
            ax.grid(alpha=0.25)
        axes[row, 0].set_ylabel(f"s={case['s']}, alpha_C={case['alpha']}, a={case['a']}", fontsize=9)
    axes[0, 0].legend(fontsize=8, loc="best")
    fig.tight_layout()
    fig.savefig(FIG / "trajectories.png", dpi=160)
    fig.savefig(FIG / "trajectories.pdf")
    np.savez(OUT / "trajectories.npz", **saved)


if __name__ == "__main__":
    {"run": run, "figures": figures}[sys.argv[1]]()
