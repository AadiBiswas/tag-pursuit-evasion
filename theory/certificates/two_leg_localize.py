"""Exact localization certificate for the aligned two-leg game (Stage 4C).

Standard library only. Shares its conventions (units, frame, domain, reflection)
with two_leg_upper_bound.py, but imports nothing.

Certifies two facts for a speed ratio s, a rational c_L and a box N in the
parameters (y, a1, b1, a2, b2), where u_j = (a_j, b_j):
  (L) every non-decreasing two-leg period (|r(1)| >= y, |u_j| <= 1, b1 >= 0) whose
      closest approach is >= c_L lies in N;
  (X) at every point of N, the closest point of leg 2 to the chaser has x > 0.
With c_L <= sqrt(G_lev(2)) (from an orbit certificate), (L) puts every maximizer of
G_up(2) in N, and (X) is the hypothesis of the translation lemma
(theory/stage4_two_leg_optimality.md, Lemma 4C.2), which then forces every maximizer
to be a closing period: G_up(2) = G_lev(2).

    python theory/certificates/two_leg_localize.py 3/2
    python theory/certificates/two_leg_localize.py 2

(L) is an exhaustive branch-and-bound over the same domain as two_leg_upper_bound.py.
A box is discarded if every point in it is infeasible, or has closest approach
< c_L (strict), or the box lies inside N. (X) is checked by exact interval arithmetic
on bisected sub-boxes of N.
"""

import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Box centres: the numerically optimal two-leg orbit, reflected so b1 >= 0
# (results/stage4b/two_leg_optima.json). They only need to be roughly right:
# both certified facts are checked exactly for whatever box is given.
CENTRES = {
    Fr(3, 2): (Fr("1.04267"), Fr("0.29958"), Fr("0.95407"), Fr("-0.13848"), Fr("0.99036")),
    Fr(2): (Fr("1.25717"), Fr("0.20169"), Fr("0.97945"), Fr("-0.33934"), Fr("0.94067")),
}
CERTS = {Fr(3, 2): "orbits/s3-2_m02.json", Fr(2): "orbits/s2-1_m02.json"}
HALF_WIDTH = Fr(3, 100)


def _minsq(lo, hi):
    return 0 if lo <= 0 <= hi else min(lo * lo, hi * hi)


def _maxsq(lo, hi):
    return max(lo * lo, hi * hi)


def _seg_dist2(px, py, dx, dy):
    a = dx * dx + dy * dy
    t = 0 if a == 0 else min(max(-(px * dx + py * dy) / a, Fr(0)), Fr(1))
    x, y = px + t * dx, py + t * dy
    return x * x + y * y


def _lt_after_slack(d2, slack, c):
    """sqrt(d2) + slack < c, exactly."""
    return slack < c and d2 < (c - slack) ** 2


def c_lower(s):
    """Rational c_L with c_L^2 <= the certified orbit's exact min clearance^2 <= G_lev(2)."""
    q = Fr(json.loads((HERE / CERTS[s]).read_text())["min_sq_clearance"])
    c = Fr(math.isqrt(q.numerator * 10**18 // q.denominator), 10**9)
    assert c * c <= q
    return c


def localize(s, cL, N_lo, N_hi, max_nodes=100_000_000):
    """(L): returns (proven, leaves, nodes)."""
    W = (Fr(1), Fr(1, 2), Fr(1, 2), Fr(1, 2), Fr(1, 2))
    stack = [((Fr(0), Fr(-1), Fr(0), Fr(-1), Fr(-1)), ((s + 1) / 2, Fr(1), Fr(1), Fr(1), Fr(1)))]
    leaves = nodes = 0
    while stack:
        lo, hi = stack.pop()
        nodes += 1
        if nodes > max_nodes:
            return False, leaves, nodes
        if all(N_lo[i] <= lo[i] and hi[i] <= N_hi[i] for i in range(5)):
            leaves += 1
            continue
        (yl, a1l, b1l, a2l, b2l), (yh, a1h, b1h, a2h, b2h) = lo, hi
        if _minsq(a1l, a1h) + _minsq(b1l, b1h) > 1 or _minsq(a2l, a2h) + _minsq(b2l, b2h) > 1:
            leaves += 1
            continue
        if _maxsq(yl + (a1l + a2l) / 2 - s, yh + (a1h + a2h) / 2 - s) + _maxsq((b1l + b2l) / 2, (b1h + b2h) / 2) < yl * yl:
            leaves += 1
            continue
        if yh < cL:
            leaves += 1
            continue
        y, a1, b1, a2, b2 = [(l + h) / 2 for l, h in zip(lo, hi)]
        hy, ha1, hb1, ha2, hb2 = [(h - l) / 2 for l, h in zip(lo, hi)]
        p1x, p1y = y + (a1 - s) / 2, b1 / 2
        L1 = hy + (ha1 + hb1) / 2
        L2 = L1 + (ha2 + hb2) / 2
        if (_lt_after_slack(_seg_dist2(y, Fr(0), (a1 - s) / 2, b1 / 2), L1, cL)
                or _lt_after_slack(p1x * p1x + p1y * p1y, L1, cL)
                or _lt_after_slack(_seg_dist2(p1x, p1y, (a2 - s) / 2, b2 / 2), L2, cL)):
            leaves += 1
            continue
        k = max(range(5), key=lambda i: (hi[i] - lo[i]) * W[i])
        m = (lo[k] + hi[k]) / 2
        stack.append((lo, hi[:k] + (m,) + hi[k + 1:]))
        stack.append((lo[:k] + (m,) + lo[k + 1:], hi))
    return True, leaves, nodes


def _mul(a, b):
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return min(p), max(p)


def leg2_front(s, N_lo, N_hi, max_depth=40):
    """(X): every point of N has the closest point of leg 2 at x > 0. Returns (proven, boxes checked).
    Lower bound: x2 = p1x + t*d2x with t in [0, 1] and d2x < 0, so x2 >= p1x_lo + t_hi * d2x_lo."""
    stack, checked = [(tuple(N_lo), tuple(N_hi), 0)], 0
    while stack:
        lo, hi, depth = stack.pop()
        checked += 1
        p1x = (lo[0] + (lo[1] - s) / 2, hi[0] + (hi[1] - s) / 2)
        p1y = (lo[2] / 2, hi[2] / 2)
        d2x = ((lo[3] - s) / 2, (hi[3] - s) / 2)
        d2y = (lo[4] / 2, hi[4] / 2)
        assert d2x[1] < 0
        dot = tuple(sorted((-(_mul(p1x, d2x)[1] + _mul(p1y, d2y)[1]), -(_mul(p1x, d2x)[0] + _mul(p1y, d2y)[0]))))
        den = (_minsq(*d2x) + _minsq(*d2y), _maxsq(*d2x) + _maxsq(*d2y))
        t_hi = min(max(dot[1] / den[0] if dot[1] > 0 else dot[1] / den[1], Fr(0)), Fr(1))
        if p1x[0] + t_hi * d2x[0] > 0:
            continue
        if depth >= max_depth:
            return False, checked
        k = max(range(5), key=lambda i: hi[i] - lo[i])
        m = (lo[k] + hi[k]) / 2
        stack.append((lo, hi[:k] + (m,) + hi[k + 1:], depth + 1))
        stack.append((lo[:k] + (m,) + lo[k + 1:], hi, depth + 1))
    return True, checked


def box(s, half=HALF_WIDTH):
    c = CENTRES[s]
    return tuple(x - half for x in c), tuple(x + half for x in c)


if __name__ == "__main__":
    s = Fr(sys.argv[1])
    N_lo, N_hi = box(s)
    cL = c_lower(s)
    okx, nx = leg2_front(s, N_lo, N_hi)
    print(f"s = {s}: N = centre {[str(x) for x in CENTRES[s]]} +/- {HALF_WIDTH}; c_L = {cL}")
    print(f"  (X) leg-2 closest point has x > 0 on N: {'PROVEN' if okx else 'NOT PROVEN'} ({nx} sub-boxes)")
    okl, leaves, nodes = localize(s, cL, N_lo, N_hi)
    print(f"  (L) every up-step with clearance >= c_L lies in N: {'PROVEN' if okl else 'NOT PROVEN'} "
          f"({leaves} leaf boxes, {nodes} nodes)")
    sys.exit(0 if okx and okl else 1)
