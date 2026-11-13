"""Exact one-period geometry of the aligned, one-decision-per-period game
against full-speed pure pursuit (Stage 4A; theory/stage4_viability_analysis.md).

Units: R_E = tau_C = 1, so s = R_C and eps = 1/alpha_C. Frame of a period:
chaser at the origin, runner at (D, 0). Both velocities are constant for the
whole period, so the relative position r(t) = (D, 0) + t (v - (s, 0)) is a
straight segment, and the period's closest approach is the distance from the
origin to that segment (endpoints included).

Full-speed actions are parametrized by y in [(s-1)/2, (s+1)/2]: the velocity for
which D = y is a fixed point (Theorem 2's symmetric pass). From any D it gives
    T_y(D)^2 = D^2 - (s^2 - 1)(D - y)/(s - y)
    C_y(D)   = D sin(theta_y)  if D < 2y,  else T_y(D)
with cos^2 theta_y = (s^2 - 1)/(4 y (s - y)).
"""

import math

import numpy as np


def pass_step(D, v, s):
    """(closest approach over the period, separation at its end) for runner velocity v."""
    r0 = np.array([D, 0.0])
    w = np.asarray(v, dtype=float) - np.array([s, 0.0])
    a = w @ w
    t = 0.0 if a == 0 else min(max(-(r0 @ w) / a, 0.0), 1.0)
    return float(np.linalg.norm(r0 + t * w)), float(np.linalg.norm(r0 + w))


def g(y, s):
    """Squared closest approach of the y-fixed-point pass (review §4.1)."""
    return y * y - y * (s * s - 1) / (4 * (s - y))


def y_star(s):
    """Unique maximizer of g on [(s-1)/2, (s+1)/2]: the larger root of
    8 y (s - y)^2 = s (s^2 - 1). Bisection, so it never leaves the bracket."""
    lo, hi = s / 3, s
    for _ in range(200):
        m = (lo + hi) / 2
        if 8 * m * (s - m) ** 2 > s * (s * s - 1):
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def alpha_sym(s):
    return 1 / math.sqrt(g(y_star(s), s))


def cos2_theta(y, s):
    return (s * s - 1) / (4 * y * (s - y))


def heading(y, s, side=1):
    """Frame velocity (unit speed) of the full-speed action with fixed point y."""
    c2 = cos2_theta(y, s)
    return np.array([s - 2 * y * c2, side * 2 * y * math.sqrt(c2 * (1 - c2))])


def T(D, y, s):
    """Separation after one period from D under action y (vectorized)."""
    return np.sqrt(np.maximum(D * D - (s * s - 1) * (D - y) / (s - y), 0.0))


def C(D, y, s):
    """Closest approach during that period (vectorized)."""
    c2 = cos2_theta(y, s)
    return np.where(D < 2 * y, D * np.sqrt(1 - c2), T(D, y, s))


def plateau_interval(D, s):
    """Range of |P| over K ∩ Th, where K = {(D - s, 0) + v : |v| <= 1} is the set of
    reachable end points and Th is the disk on diameter [0, (D, 0)]. End points in Th
    are reached while still closing in, so their closest approach IS the end
    separation. Returns (lo, hi) or None if K ∩ Th is empty."""
    c1, r1 = np.array([D - s, 0.0]), 1.0
    c2, r2 = np.array([D / 2, 0.0]), D / 2

    def inside(p, c, r):
        return np.linalg.norm(p - c) <= r * (1 + 1e-12) + 1e-15

    cand = [0.0] if inside(np.zeros(2), c1, r1) else []   # origin lies on Th's boundary
    for c, r, oc, orr in ((c1, r1, c2, r2), (c2, r2, c1, r1)):
        n = np.linalg.norm(c)
        u = c / n if n > 0 else np.array([1.0, 0.0])
        for p in (c + r * u, c - r * u):           # nearest / farthest points from the origin
            if inside(p, oc, orr):
                cand.append(np.linalg.norm(p))
    d = abs(c2[0] - c1[0])                          # circle-circle intersections (centres on the x-axis)
    if abs(r1 - r2) <= d <= r1 + r2 and d > 0:
        x = (d * d + r1 * r1 - r2 * r2) / (2 * d)
        h = math.sqrt(max(r1 * r1 - x * x, 0.0))
        px = c1[0] + x * np.sign(c2[0] - c1[0])
        cand.append(math.hypot(px, h))
    if not cand:
        return None
    return min(cand), max(cand)
