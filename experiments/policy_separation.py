"""Policy separation at s = 2, alpha_C = 19/10 (review §3.5): the same runner, from the
same state, escapes pure pursuit forever and is caught by the hybrid chaser.

Two deterministic engine runs, nothing swept. The escape itself is Theorem 2
(and the exact certificate theory/certificates/orbits/s2-1_m01.json); this
script only draws it.

    .venv/bin/python experiments/policy_separation.py
"""

import math
from fractions import Fraction
from pathlib import Path

import numpy as np

from tagsim import AgentSpec, hybrid_pursuit, pure_pursuit, simulate
from tagsim.best_response import SymmetricPass, best_pass

ROOT = Path(__file__).resolve().parents[1]
OUT, FIG = ROOT / "results/stage3", ROOT / "figures/stage3"
COLORS = ["#2a78d6", "#eb6834"]  # same categorical slots as the Stage 3 figures

S, ALPHA, EPS, PERIODS = 2.0, Fraction(19, 10), 1.0, 40


def runs():
    tau = ALPHA  # R_E = eps = 1, so alpha_C = tau_C
    sp = SymmetricPass(S, 1.0, float(tau))
    C, E = AgentSpec(S, tau), AgentSpec(1.0, tau)
    x0 = [sp.D, 0.0]
    pp = simulate(C, E, [0, 0], x0, EPS, PERIODS * tau, pure_pursuit, sp)
    hy = simulate(C, E, [0, 0], x0, EPS, PERIODS * tau, hybrid_pursuit, sp)
    return sp, pp, hy


def separation(res, n_per_period=400):
    # Motion is affine between events, so linear interpolation of positions is exact.
    t = np.linspace(res.times[0], res.times[-1], int(n_per_period * res.times[-1] / float(ALPHA)) + 2)
    sep = np.array([np.linalg.norm(np.subtract(*res.positions_at(x))) for x in t])
    return t, sep


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sp, pp, hy = runs()
    assert not pp.captured and hy.captured
    tp, dp = separation(pp)
    th, dh = separation(hy)
    lines = [f"s = {S}, alpha_C = {ALPHA} (eps = R_E = 1, tau_C = tau_E = {ALPHA}, aligned clocks)",
             f"alpha_sym(2) = {1 / math.sqrt(best_pass(S)[1]):.10f} < alpha_C <= s = 2",
             f"runner: Theorem 2 symmetric pass, D = {sp.D:.6f}, predicted closest approach {sp.miss:.6f}",
             f"pure pursuit: no capture in {PERIODS} periods, min separation {dp.min():.6f} (> eps = 1)",
             f"hybrid chaser: captured at t = {hy.capture_time:.6f} = {hy.capture_time / float(ALPHA):.4f} tau_C "
             f"(Theorem 3 bound phi_C + (K+2) tau_C with K = 0: {2 * float(ALPHA):.4f})"]
    (OUT / "policy_separation.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw=dict(width_ratios=[1.6, 1]))
    show = 8 * float(ALPHA)
    k = tp <= show
    ax.plot(tp[k] / float(ALPHA), dp[k], color=COLORS[0], lw=2, label="pure pursuit: never captures")
    ax.plot(th / float(ALPHA), dh, color=COLORS[1], lw=2, label="hybrid chaser: captures")
    ax.plot(hy.capture_time / float(ALPHA), EPS, "o", color=COLORS[1], ms=8, mec="white", mew=2)
    ax.axhline(EPS, color="0.45", lw=1, ls="--")
    ax.text(8, EPS, r"capture radius $\varepsilon$", ha="right", va="bottom", color="0.35", fontsize=9)
    ax.set_xlabel(r"time / $\tau_C$")
    ax.set_ylabel(r"separation / $\varepsilon$")
    ax.set_xlim(0, 8)
    ax.set_ylim(0, None)
    ax.set_title(r"Same runner, same start: $s=2$, $\alpha_C=1.9$", fontsize=10)
    ax.legend(frameon=False, loc="lower right", fontsize=9)
    for a in (ax, bx):
        a.spines[["top", "right"]].set_visible(False)

    # absolute paths (runner), first 12 periods for PP, until capture for hybrid
    k = tp <= 12 * float(ALPHA)
    E_pp = np.array([pp.positions_at(x)[1] for x in tp[k]])
    C_pp = np.array([pp.positions_at(x)[0] for x in tp[k]])
    E_hy = np.array([hy.positions_at(x)[1] for x in th])
    bx.plot(C_pp[:, 0], C_pp[:, 1], color=COLORS[0], lw=1, alpha=0.45, label="pure pursuit (chaser)")
    bx.plot(E_pp[:, 0], E_pp[:, 1], color=COLORS[0], lw=2, label="runner vs pure pursuit")
    bx.plot(E_hy[:, 0], E_hy[:, 1], color=COLORS[1], lw=2, label="runner vs hybrid")
    bx.set_aspect("equal")
    bx.set_title("Absolute paths, 12 periods", fontsize=10)
    bx.legend(frameon=False, fontsize=8, loc="lower left")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"policy_separation.{ext}", dpi=160)


if __name__ == "__main__":
    main()
