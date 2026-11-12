"""Write orbits/*.json from results/stage3/certified_orbits.json.

The Stage 3 file holds the primary data (s, m, rational leg velocities, D*,
alpha_c). This adds everything a reader needs to check a certificate by hand:
clock schedule, chaser velocity, per-leg relative motion, per-leg minimum and
the closure vector. verify.py recomputes all of it and must not import this.
"""

import json
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "results/stage3/certified_orbits.json"


def pair(p):
    return [str(p[0]), str(p[1])]


def build(row):
    s, m = Fr(row["s_exact"]), row["m"]
    h = Fr(1, m)
    D = Fr(row["D_star_exact"])
    V = [(Fr(a), Fr(b)) for a, b in row["velocities_exact"]]
    vc = (s, Fr(0))
    e, c = (D, Fr(0)), (Fr(0), Fr(0))
    legs, worst = [], None
    for j, v in enumerate(V):
        r = (e[0] - c[0], e[1] - c[1])
        w = (v[0] - vc[0], v[1] - vc[1])
        a = w[0] ** 2 + w[1] ** 2
        t = min(max(-(r[0] * w[0] + r[1] * w[1]) / a, Fr(0)), h)
        d2 = (r[0] + t * w[0]) ** 2 + (r[1] + t * w[1]) ** 2
        worst = d2 if worst is None else min(worst, d2)
        legs.append(dict(index=j, t_start=str(j * h), duration=str(h), runner_velocity=pair(v),
                         chaser_velocity=pair(vc), r0=pair(r), w=pair(w), t_min=str(t), min_sq_sep=str(d2)))
        e = (e[0] + h * v[0], e[1] + h * v[1])
        c = (c[0] + h * vc[0], c[1] + h * vc[1])
    r_end = (e[0] - c[0], e[1] - c[1])
    unit = all(v[0] ** 2 + v[1] ** 2 == 1 for v in V)
    return dict(
        s=str(s), m=m,
        speed_model="exact" if unit else "bounded",
        units="R_E = tau_C = 1, so rho = 1 and eps = 1/alpha_C",
        frame="per chaser period: chaser at origin, runner at (D0, 0); x along the line of sight, "
              "y = x rotated +90 degrees; runner leg velocities are given in this frame",
        clocks=dict(tau_C="1", tau_E=str(h), phi_C="0", phi_E="0",
                    note="runner decides at j/m; every chaser decision (integers) is a runner decision"),
        D0=str(D),
        alpha_c=row["alpha_c"],
        claim=f"For every alpha_C >= {row['alpha_c']} (equivalently eps^2 <= 1/alpha_c^2 in these units), "
              f"pure pursuit at speed ratio s = {s} never captures this runner from this state. "
              "Both clocks aligned, runner period tau_C/m.",
        legs=legs,
        closure=dict(r_end=pair(r_end), r_end_norm_sq=str(r_end[0] ** 2 + r_end[1] ** 2)),
        min_sq_clearance=str(worst),
    )


def main():
    for row in json.loads(SRC.read_text()):
        cert = build(row)
        s = Fr(cert["s"])
        name = f"s{s.numerator}-{s.denominator}_m{cert['m']:02d}.json"
        (HERE / "orbits" / name).write_text(json.dumps(cert, indent=1) + "\n")
        print(name)


if __name__ == "__main__":
    main()
