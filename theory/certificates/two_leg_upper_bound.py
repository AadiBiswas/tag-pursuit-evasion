"""Exact upper bound on the up-step clearance of the aligned two-leg game (Stage 4B).

Standard library only (fractions); imports nothing from tagsim or experiments.

Claim certified: for speed ratio s, every one-period two-leg runner action
(u1, u2 in the closed unit disk, each held for half a chaser period) started at
separation y with end separation |r(1)| >= y has closest approach <= T.
Units R_E = tau_C = 1; the chaser runs along +x at speed s for the whole period.

    python theory/certificates/two_leg_upper_bound.py 3/2 0.6421    # s, T
    python theory/certificates/two_leg_upper_bound.py 2 0.5929

Method: exhaustive branch-and-bound over boxes in (y, a1, b1, a2, b2), where
u_j = (a_j, b_j). Every decision is made in exact rational arithmetic. A box is
discarded only if one of these holds for EVERY point in it:
  * u1 or u2 lies outside the unit disk;
  * the step is strictly decreasing (|r(1)|^2 < y^2), by interval arithmetic;
  * the closest approach is <= T: the distance from the origin to a segment
    moves by at most the larger endpoint displacement (Hausdorff distance), so
    dist <= dist(at box centre) + Lipschitz slack. Also used: closest approach
    <= y (the start point) and <= |r(1/2)|.
Otherwise it is bisected. If every box is discarded, the claim is proven.

Domain: y in [0, (s+1)/2] suffices: an up-step needs y <= D*(average velocity),
and D* <= (s+1)/2 (theory/stage4_viability_analysis.md, Lemma 4A.7 /
stage4_multidecision_analysis.md, Lemma 4B.2). b1 >= 0 by reflection symmetry.
"""

import sys
from fractions import Fraction as Fr


def _minsq(lo, hi):
    return 0 if lo <= 0 <= hi else min(lo * lo, hi * hi)


def _maxsq(lo, hi):
    return max(lo * lo, hi * hi)


def _seg_dist2(px, py, dx, dy):
    a = dx * dx + dy * dy
    t = 0 if a == 0 else min(max(-(px * dx + py * dy) / a, Fr(0)), Fr(1))
    x, y = px + t * dx, py + t * dy
    return x * x + y * y


def _le_after_slack(d2, slack, T):
    """sqrt(d2) + slack <= T, exactly."""
    return slack <= T and d2 <= (T - slack) ** 2


def certify(s, T, max_nodes=50_000_000):
    """Returns (proven, leaves, nodes). proven=False means the node budget ran out."""
    s, T = Fr(s), Fr(T)
    W = (Fr(1), Fr(1, 2), Fr(1, 2), Fr(1, 2), Fr(1, 2))     # Lipschitz weights of y, a1, b1, a2, b2
    stack = [((Fr(0), Fr(-1), Fr(0), Fr(-1), Fr(-1)), ((s + 1) / 2, Fr(1), Fr(1), Fr(1), Fr(1)))]
    leaves = nodes = 0
    while stack:
        lo, hi = stack.pop()
        nodes += 1
        if nodes > max_nodes:
            return False, leaves, nodes
        (yl, a1l, b1l, a2l, b2l), (yh, a1h, b1h, a2h, b2h) = lo, hi
        # infeasible: speed or strictly decreasing step
        if _minsq(a1l, a1h) + _minsq(b1l, b1h) > 1 or _minsq(a2l, a2h) + _minsq(b2l, b2h) > 1:
            leaves += 1
            continue
        if _maxsq(yl + (a1l + a2l) / 2 - s, yh + (a1h + a2h) / 2 - s) + _maxsq((b1l + b2l) / 2, (b1h + b2h) / 2) < yl * yl:
            leaves += 1
            continue
        if yh <= T:                                             # closest approach <= start separation
            leaves += 1
            continue
        y, a1, b1, a2, b2 = [(l + h) / 2 for l, h in zip(lo, hi)]
        hy, ha1, hb1, ha2, hb2 = [(h - l) / 2 for l, h in zip(lo, hi)]
        p1x, p1y = y + (a1 - s) / 2, b1 / 2
        d2x, d2y = (a2 - s) / 2, b2 / 2
        L1 = hy + (ha1 + hb1) / 2                              # endpoint displacement bound, leg 1
        L2 = L1 + (ha2 + hb2) / 2                              # leg 2 (its end point moves most)
        if (_le_after_slack(_seg_dist2(y, Fr(0), (a1 - s) / 2, b1 / 2), L1, T)
                or _le_after_slack(p1x * p1x + p1y * p1y, L1, T)
                or _le_after_slack(_seg_dist2(p1x, p1y, d2x, d2y), L2, T)):
            leaves += 1
            continue
        k = max(range(5), key=lambda i: (hi[i] - lo[i]) * W[i])
        m = (lo[k] + hi[k]) / 2
        hi1 = hi[:k] + (m,) + hi[k + 1:]
        lo2 = lo[:k] + (m,) + lo[k + 1:]
        stack.append((lo, hi1))
        stack.append((lo2, hi))
    return True, leaves, nodes


if __name__ == "__main__":
    s, T = Fr(sys.argv[1]), Fr(sys.argv[2])
    ok, leaves, nodes = certify(s, T)
    verdict = "PROVEN" if ok else "NOT PROVEN (node budget exhausted)"
    print(f"s = {s}, T = {T}: up-step clearance <= T {verdict}; {leaves} leaf boxes, {nodes} nodes")
    sys.exit(0 if ok else 1)
