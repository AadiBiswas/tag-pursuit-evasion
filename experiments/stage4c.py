"""Stage 4C: structure of the optimal two-leg orbit (theory/stage4_two_leg_optimality.md).

    .venv/bin/python experiments/stage4c.py

Writes results/stage4c/optimum.txt. Everything here is high-precision NUMERICS
(80-digit Decimal), used to identify the active set and to illustrate
Proposition 4C.5. The proven statements rest on the exact certificates in
theory/certificates/.

Units R_E = tau_C = 1. Full-speed leg velocities are parametrized rationally,
u(t) = ((1 - t^2)/(1 + t^2), 2t/(1 + t^2)), so no trigonometry is involved. The
start separation of a closing period is fixed by the mean velocity (Lemma 4B.2).
"""

from decimal import Decimal as Dc, getcontext
from pathlib import Path

getcontext().prec = 80
OUT = Path(__file__).resolve().parents[1] / "results/stage4c"
STARTS = {Dc(3) / 2: ("0.734", "1.150"), Dc(2): ("0.815", "1.424")}


def unit(t):
    return (1 - t * t) / (1 + t * t), 2 * t / (1 + t * t)


def closing(t1, t2, s):
    """(y, d1, d2, p1, p2) of the closing full-speed period with parameters t1, t2."""
    u1, u2 = unit(t1), unit(t2)
    ux, uy = (u1[0] + u2[0]) / 2, (u1[1] + u2[1]) / 2
    y = ((ux - s) ** 2 + uy ** 2) / (2 * (s - ux))
    d1, d2 = ((u1[0] - s) / 2, u1[1] / 2), ((u2[0] - s) / 2, u2[1] / 2)
    p1 = (y + d1[0], d1[1])
    return y, d1, d2, p1, (p1[0] + d2[0], p1[1] + d2[1])


def leg(px, py, dx, dy):
    """(clearance^2, unclamped foot parameter, x of the closest point) of one leg."""
    a = dx * dx + dy * dy
    t = -(px * dx + py * dy) / a
    tc = min(max(t, Dc(0)), Dc(1))
    return (px + tc * dx) ** 2 + (py + tc * dy) ** 2, t, px + tc * dx


def F(t1, t2, s):
    """Leg-2 interior-tangency clearance^2 of the closing period: the reduced objective."""
    y, d1, d2, p1, p2 = closing(t1, t2, s)
    cr = p1[0] * d2[1] - p1[1] * d2[0]
    return cr * cr / (d2[0] ** 2 + d2[1] ** 2)


def _grad(f, t1, t2, h=Dc(10) ** -30):
    return ((f(t1 + h, t2) - f(t1 - h, t2)) / (2 * h), (f(t1, t2 + h) - f(t1, t2 - h)) / (2 * h))


def _hess(f, t1, t2, h=Dc(10) ** -15):
    a11 = (_grad(f, t1 + h, t2)[0] - _grad(f, t1 - h, t2)[0]) / (2 * h)
    a12 = (_grad(f, t1, t2 + h)[0] - _grad(f, t1, t2 - h)[0]) / (2 * h)
    a22 = (_grad(f, t1, t2 + h)[1] - _grad(f, t1, t2 - h)[1]) / (2 * h)
    return a11, a12, a22


def optimum(s):
    """Newton's method on grad F = 0 from a rough start; returns the critical point and diagnostics."""
    f = lambda a, b: F(a, b, s)
    t1, t2 = (Dc(x) for x in STARTS[s])
    for _ in range(60):
        g1, g2 = _grad(f, t1, t2)
        a11, a12, a22 = _hess(f, t1, t2)
        det = a11 * a22 - a12 * a12
        d1, d2 = (a22 * g1 - a12 * g2) / det, (-a12 * g1 + a11 * g2) / det
        t1, t2 = t1 - d1, t2 - d2
        if abs(d1) + abs(d2) < Dc(10) ** -28:
            break
    y, dd1, dd2, p1, p2 = closing(t1, t2, s)
    c1, f1, x1 = leg(y, Dc(0), *dd1)
    c2, f2, x2 = leg(p1[0], p1[1], *dd2)
    return dict(t1=t1, t2=t2, y=y, c=F(t1, t2, s).sqrt(), grad=_grad(f, t1, t2), hess=_hess(f, t1, t2),
                leg1=(c1.sqrt(), f1, x1), leg2=(c2.sqrt(), f2, x2), cos_psi=p2[0] / y)


def boundary_chain(s, steps=150, a0=Dc("0.01")):
    """Prop. 4C.5 illustration at alpha_C = 1/c*: from D = y_L + a, play the closing orbit whose
    start is y_L + beta*a (found along the line t* + lam * grad(y)/|grad(y)|^2), so this period
    starts (1 - beta) a beyond that orbit's own start. Returns min(clearance^2 - c*^2), final a,
    and the contraction range."""
    opt = optimum(s)
    t1s, t2s, yL, cs = opt["t1"], opt["t2"], opt["y"], opt["c"]
    yf = lambda a, b: closing(a, b, s)[0]
    gy = _grad(yf, t1s, t2s)
    n2 = gy[0] ** 2 + gy[1] ** 2
    v = (gy[0] / n2, gy[1] / n2)
    beta = (1 + (-opt["cos_psi"]) / (1 - opt["cos_psi"])) / 2
    a, worst, ratios = a0, None, []
    for _ in range(steps):
        target, lam = yL + beta * a, beta * a
        for _ in range(40):                                   # solve y(t* + lam v) = target
            r = yf(t1s + lam * v[0], t2s + lam * v[1]) - target
            dr = (yf(t1s + (lam + Dc(10) ** -30) * v[0], t2s + (lam + Dc(10) ** -30) * v[1])
                  - yf(t1s + (lam - Dc(10) ** -30) * v[0], t2s + (lam - Dc(10) ** -30) * v[1])) / (2 * Dc(10) ** -30)
            lam -= r / dr
        t1, t2 = t1s + lam * v[0], t2s + lam * v[1]
        yc, d1, d2, p1, p2 = closing(t1, t2, s)
        D = yL + a
        b = D - yc                                            # translation beyond the orbit's own start
        q1 = (p1[0] + b, p1[1])
        c1 = leg(D, Dc(0), *d1)[0]
        c2 = leg(q1[0], q1[1], *d2)[0]
        margin = min(c1, c2) - cs * cs
        Dn = ((p2[0] + b) ** 2 + p2[1] ** 2).sqrt()
        an = Dn - yL
        ratios.append(an / a)
        worst = margin if worst is None else min(worst, margin)
        assert margin > 0 and 0 < an < a, (margin, an, a)
        a = an
    return worst, a, (float(min(ratios)), float(max(ratios))), beta


def main():
    lines = ["Optimal closing two-leg orbit: critical point of the reduced objective F_s(t1, t2) (80-digit Newton).",
             "Numerics, not a certificate; see theory/stage4_two_leg_optimality.md.", ""]
    for s in STARTS:
        o = optimum(s)
        lines += [f"s = {s}:",
                  f"  t1 = {str(o['t1'])[:40]}, t2 = {str(o['t2'])[:40]}",
                  f"  start/closing separation y_L = {str(o['y'])[:40]}",
                  f"  clearance c* = {str(o['c'])[:40]}",
                  f"  alpha* = 1/c* = {str(1 / o['c'])[:40]}",
                  f"  |grad F| = {float(abs(o['grad'][0]) + abs(o['grad'][1])):.1e}; Hessian of F (t1,t2) = "
                  f"{[round(float(x), 6) for x in o['hess']]} (negative definite)",
                  f"  leg 1: clearance {float(o['leg1'][0]):.10f}, foot parameter {float(o['leg1'][1]):.6f} "
                  f"(> 1: closest point is the midpoint r(1/2)), x = {float(o['leg1'][2]):.6f}",
                  f"  leg 2: clearance {float(o['leg2'][0]):.10f} (binding), foot parameter {float(o['leg2'][1]):.6f} "
                  f"(interior tangency), x = {float(o['leg2'][2]):.6f} > 0",
                  f"  rotation per period: cos(psi) = P_x / y_L = {float(o['cos_psi']):.6f}"]
        worst, a, (rmin, rmax), beta = boundary_chain(s)
        lines.append(f"  boundary chain at alpha = alpha*: 150 steps from a = 0.01, beta = {float(beta):.4f}: "
                     f"min(clearance^2 - c*^2) = {float(worst):.3e} > 0, final a = {float(a):.3e}, "
                     f"a_(k+1)/a_k in [{rmin:.4f}, {rmax:.4f}]")
        lines.append("")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "optimum.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
