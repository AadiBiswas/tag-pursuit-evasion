"""Standalone verifier for the periodic escape certificates (Theorem 4).

Standard library only. Imports nothing from tagsim, experiments/ or build.py,
so a bug in the generator can't vouch for itself.

    python theory/certificates/verify.py                 # verify every orbits/*.json
    python theory/certificates/verify.py --summary FILE  # also write the summary table
    python theory/certificates/verify.py some.json ...

Units (README.md): R_E = tau_C = 1, so rho = R_E tau_C = 1 and eps = 1/alpha_C.
Local frame of a chaser period: chaser at the origin, runner at (D, 0), so
pure pursuit plays (s, 0). Runner leg j runs on [j/m, (j+1)/m] at velocity V_j.

Checks, in order. A certificate is accepted only if all pass:
  1. speed      |V_j|^2 <= 1, and == 1 if the certificate claims the exact-speed model
  2. schedule   m legs of duration exactly tau_E = 1/m, starting at j/m, runner and
                chaser phases 0, so every chaser decision is a runner decision
  3. pursuit    chaser velocity on every leg is s * (e - c)/|e - c| at the period start
  4. integrate  relative position r_j at each leg start, recomputed from 1-3
  5. closure    |r_m|^2 == D^2 exactly
  6. clearance  min over the CLOSED leg interval of |r_j + t w_j|^2 > 1/alpha_c^2
  7. recurrence the runner policy below is run in absolute coordinates, exactly, for
                several periods; at every chaser decision the state must be the
                image of the initial state under a rotation + translation
  8. record     every derived quantity written in the certificate equals the recomputed one
Runner policy for 7: at chaser decision t_k, with u_k = (e - c)/|e - c| and
n_k = u_k rotated by +90 degrees, play V_j[0] u_k + V_j[1] n_k on leg j of that period.
"""

import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
RECURRENCE_PERIODS = 3


class Rejected(Exception):
    pass


def _fr(x):
    return Fr(x) if isinstance(x, str) else Fr(x)


def _vec(p):
    return (_fr(p[0]), _fr(p[1]))


def _exact_sqrt(q):
    """sqrt of a non-negative rational if it is rational, else None."""
    n, d = q.numerator, q.denominator
    rn, rd = math.isqrt(n), math.isqrt(d)
    return Fr(rn, rd) if rn * rn == n and rd * rd == d else None


def _leg_min(r, w, h):
    """Exact min of |r + t w|^2 over the closed interval t in [0, h]: the quadratic's
    vertex clamped to the interval (clamping is what puts the endpoints in)."""
    a = w[0] * w[0] + w[1] * w[1]
    t = Fr(0) if a == 0 else min(max(-(r[0] * w[0] + r[1] * w[1]) / a, Fr(0)), h)
    x, y = r[0] + t * w[0], r[1] + t * w[1]
    return t, x * x + y * y


def check(cert):
    """Raise Rejected(reason) unless the certificate proves what it claims.
    Returns the exact minimum squared clearance."""
    s, m = _fr(cert["s"]), cert["m"]
    if not (isinstance(m, int) and m >= 1):
        raise Rejected("m must be a positive integer")
    if not s > 1:
        raise Rejected("needs s > 1")
    D = _fr(cert["D0"])
    alpha = _fr(cert["alpha_c"])
    if D <= 0 or alpha <= 0:
        raise Rejected("D0 and alpha_c must be positive")
    eps2 = 1 / alpha ** 2
    legs = cert["legs"]
    if len(legs) != m:
        raise Rejected(f"{len(legs)} legs for m = {m}")
    V = [_vec(leg["runner_velocity"]) for leg in legs]

    # 1. speed
    for j, (vx, vy) in enumerate(V):
        q = vx * vx + vy * vy
        if q > 1:
            raise Rejected(f"leg {j}: runner speed^2 = {float(q)} > 1")
        if cert["speed_model"] == "exact" and q != 1:
            raise Rejected(f"leg {j}: exact-speed model claimed but speed^2 = {float(q)}")
    if cert["speed_model"] not in ("exact", "bounded"):
        raise Rejected("speed_model must be 'exact' or 'bounded'")

    # 2. schedule
    clk = cert["clocks"]
    if _fr(clk["tau_C"]) != 1 or _fr(clk["tau_E"]) != Fr(1, m):
        raise Rejected("clock periods must be tau_C = 1, tau_E = 1/m")
    if _fr(clk["phi_C"]) != 0 or _fr(clk["phi_E"]) != 0:
        raise Rejected("both phases must be 0 (aligned clocks)")
    for j, leg in enumerate(legs):
        if _fr(leg["t_start"]) != Fr(j, m) or _fr(leg["duration"]) != Fr(1, m):
            raise Rejected(f"leg {j}: [t_start, duration] = [{leg['t_start']}, {leg['duration']}] "
                           f"violates the runner clock (expected [{Fr(j, m)}, {Fr(1, m)}])")

    # 3-6 in the local frame
    h = Fr(1, m)
    e, c = (D, Fr(0)), (Fr(0), Fr(0))
    gap = (e[0] - c[0], e[1] - c[1])
    n = _exact_sqrt(gap[0] ** 2 + gap[1] ** 2)
    vc = (s * gap[0] / n, s * gap[1] / n)          # pure pursuit, from positions alone
    worst, derived = None, []
    for j, v in enumerate(V):
        r = (e[0] - c[0], e[1] - c[1])
        w = (v[0] - vc[0], v[1] - vc[1])
        t, d2 = _leg_min(r, w, h)
        if d2 <= eps2:
            raise Rejected(f"leg {j}: min squared separation {float(d2):.6g} <= eps^2 = {float(eps2):.6g}"
                           + (" (touches: capture)" if d2 == eps2 else ""))
        worst = d2 if worst is None else min(worst, d2)
        derived.append(dict(chaser_velocity=vc, r0=r, w=w, t_min=t, min_sq_sep=d2))
        e = (e[0] + h * v[0], e[1] + h * v[1])
        c = (c[0] + h * vc[0], c[1] + h * vc[1])
    r_end = (e[0] - c[0], e[1] - c[1])
    if r_end[0] ** 2 + r_end[1] ** 2 != D * D:
        raise Rejected(f"closure fails: |r(tau_C)|^2 - D^2 = {float(r_end[0] ** 2 + r_end[1] ** 2 - D * D):.3g}")

    # 7. recurrence, in absolute coordinates, exactly
    _recurrence(s, m, D, V, eps2, RECURRENCE_PERIODS)

    # 8. recorded values
    for j, (leg, dv) in enumerate(zip(legs, derived)):
        for key, val in dv.items():
            rec = leg[key]
            rec = _vec(rec) if isinstance(val, tuple) else _fr(rec)
            if rec != val:
                raise Rejected(f"leg {j}: recorded {key} does not match the recomputed value")
    cl = cert["closure"]
    if _vec(cl["r_end"]) != r_end or _fr(cl["r_end_norm_sq"]) != D * D:
        raise Rejected("recorded closure data does not match")
    if _fr(cert["min_sq_clearance"]) != worst:
        raise Rejected("recorded min_sq_clearance does not match")
    return worst


def _recurrence(s, m, D, V, eps2, periods):
    h = Fr(1, m)
    c, e = (Fr(0), Fr(0)), (D, Fr(0))
    for k in range(periods):
        g = (e[0] - c[0], e[1] - c[1])
        n = _exact_sqrt(g[0] ** 2 + g[1] ** 2)
        if n != D:
            raise Rejected(f"recurrence: separation at chaser decision {k} is not D")
        u = (g[0] / n, g[1] / n)
        nn = (-u[1], u[0])
        vc = (s * u[0], s * u[1])                   # chaser re-aims at t_k; runner decides too
        for j, (a, b) in enumerate(V):
            v = (a * u[0] + b * nn[0], a * u[1] + b * nn[1])
            r, w = g, (v[0] - vc[0], v[1] - vc[1])
            _, d2 = _leg_min(r, w, h)
            if d2 <= eps2:
                raise Rejected(f"recurrence: period {k} leg {j} reaches the capture radius")
            e = (e[0] + h * v[0], e[1] + h * v[1])
            c = (c[0] + h * vc[0], c[1] + h * vc[1])
            g = (e[0] - c[0], e[1] - c[1])
    # Nothing else to compare: in the frame (u_k, n_k) the period starts with the chaser
    # at the origin and the runner at (|g|, 0) by construction, so |g| == D (checked at
    # the top of each period) plus both clocks deciding at the integer t_k IS the
    # initial state. The frames themselves are exact rational unit vectors.


def summarize(name, cert, clear_sq):
    """One summary row. alpha_hat = 1/sqrt(min clearance^2) is this orbit's own sharp
    threshold (it escapes iff alpha_C > alpha_hat); printed to 10 digits via Decimal."""
    from decimal import Decimal, getcontext
    getcontext().prec = 40
    a_hat = 1 / (Decimal(clear_sq.numerator) / Decimal(clear_sq.denominator)).sqrt()
    alpha = _fr(cert["alpha_c"])
    return (f"| {name} | {cert['s']} | {cert['m']} | {float(_fr(cert['D0'])):.6f} | "
            f"{math.sqrt(clear_sq):.6f} | {a_hat:.10f} | {alpha} | {cert['speed_model']} | verified |")


def main(argv):
    out = None
    if "--summary" in argv:
        i = argv.index("--summary")
        out = Path(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    files = [Path(a) for a in argv] or sorted((HERE / "orbits").glob("*.json"))
    rows, bad = [], 0
    for f in files:
        cert = json.loads(f.read_text())
        try:
            cl = check(cert)
        except (Rejected, KeyError, ValueError, ZeroDivisionError, TypeError) as ex:
            bad += 1
            print(f"REJECTED {f.name}: {type(ex).__name__}: {ex}")
            continue
        print(f"ok       {f.name}: s={cert['s']} m={cert['m']} alpha_c={cert['alpha_c']} "
              f"clearance^2={float(cl):.12f}")
        rows.append(summarize(f.stem, cert, cl))
    print(f"{len(files) - bad}/{len(files)} certificates verified")
    if out is not None:
        head = ["| certificate | s | m | D0 / (R_E tau_C) | min clearance / (R_E tau_C) | "
                "orbit's sharp threshold alpha_hat = 1/clearance | certified alpha_c | speed model | status |",
                "|---|---|---|---|---|---|---|---|---|"]
        out.write_text("\n".join(head + rows) + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
