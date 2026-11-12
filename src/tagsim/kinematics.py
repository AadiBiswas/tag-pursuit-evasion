"""Exact relative kinematics on one inter-event interval.

Between events both velocities are constant, so the relative position
r(s) = r0 + s*w is affine and |r(s)|^2 is a quadratic in s. Everything here
is closed form; nothing is time-stepped.
"""

import math

import numpy as np


def first_contact(r0, w, eps, dt):
    """Earliest s in [0, dt] with |r0 + s*w| <= eps, or None.

    r0: relative position (runner minus chaser) at the start of the interval.
    w:  relative velocity (v_E - v_C), constant over the interval.
    """
    r0 = np.asarray(r0, dtype=float)
    w = np.asarray(w, dtype=float)
    n = float(np.linalg.norm(r0))
    if n <= eps:
        return 0.0
    a = float(w @ w)
    p = float(r0 @ w)
    # a == 0: zero relative velocity, separation is constant (and > eps here).
    # p >= 0: separation non-decreasing from s = 0, so no future contact.
    if a == 0.0 or p >= 0.0:
        return None
    # Don't use the textbook discriminant: |r0|^2 - eps^2 drops eps entirely
    # once |r0|/eps ~ 1e8. Go through the closest approach instead, whose
    # perpendicular distance is accurate to ~ulp(|r0|).
    s_min = -p / a
    dp = float(np.linalg.norm(r0 + s_min * w))
    if dp > eps:
        return None
    h = math.sqrt((eps - dp) * (eps + dp) / a)  # half-chord, in time
    # Entry root = (product of roots) / (exit root); avoids s_min - h cancelling
    # when contact is almost immediate.
    s = (n - eps) * (n + eps) / (a * (s_min + h))
    return s if s <= dt else None


def min_separation(r0, w, dt):
    """(s*, |r(s*)|): closest approach over [0, dt]. Diagnostics/tests only."""
    r0 = np.asarray(r0, dtype=float)
    w = np.asarray(w, dtype=float)
    a = float(w @ w)
    s = 0.0 if a == 0.0 else min(max(-float(r0 @ w) / a, 0.0), dt)
    return s, float(np.linalg.norm(r0 + s * w))
