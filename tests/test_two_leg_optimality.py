"""Stage 4C: translation lemma, localization certificate pieces, optimum structure
(theory/stage4_two_leg_optimality.md)."""

import importlib.util
import json
import math
import sys
from decimal import Decimal as Dc
from fractions import Fraction as F
from pathlib import Path

import numpy as np

sys.path.insert(0, "experiments")
import stage4b  # noqa: E402
import stage4c  # noqa: E402

CERT_DIR = Path(__file__).resolve().parents[1] / "theory/certificates"
spec = importlib.util.spec_from_file_location("two_leg_localize", CERT_DIR / "two_leg_localize.py")
loc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loc)


def _closest_x(px, py, dx, dy):
    a = dx * dx + dy * dy
    t = min(max(-(px * dx + py * dy) / a, 0.0), 1.0)
    return px + t * dx


def _random_period(rng, s):
    r, ph = np.sqrt(rng.random(2)), rng.uniform(-math.pi, math.pi, 2)
    u1 = (r[0] * math.cos(ph[0]), r[0] * math.sin(ph[0]))
    u2 = (r[1] * math.cos(ph[1]), r[1] * math.sin(ph[1]))
    return rng.uniform(0.05, s + 1), u1, u2


def test_leg1_closest_point_is_in_front():
    # Lemma 4C.1(ii): leg 1 starts on the positive axis and heads left, so its closest point has x > 0
    rng = np.random.default_rng(1)
    for s in (1.2, 1.5, 2.0, 3.0):
        for _ in range(5000):
            y, u1, _ = _random_period(rng, s)
            x1 = _closest_x(y, 0.0, (u1[0] - s) / 2, u1[1] / 2)
            c1 = math.sqrt(stage4b.seg_dist2(y, 0.0, (u1[0] - s) / 2, u1[1] / 2)[0])
            assert c1 < 1e-12 or x1 > 0


def test_translation_lemma_tangent_bound():
    # Lemma 4C.2: translating the period start by b >= 0 moves each leg's clearance by at least
    # b * x_j / c_j (the distance to a segment is convex in the translation)
    rng = np.random.default_rng(2)
    s = 1.5
    for _ in range(3000):
        y, u1, u2 = _random_period(rng, s)
        b = rng.uniform(0, 0.3)
        legs0 = [(y, 0.0, (u1[0] - s) / 2, u1[1] / 2)]
        legs0.append((y + legs0[0][2], legs0[0][3], (u2[0] - s) / 2, u2[1] / 2))
        for px, py, dx, dy in legs0:
            c0 = math.sqrt(stage4b.seg_dist2(px, py, dx, dy)[0])
            cb = math.sqrt(stage4b.seg_dist2(px + b, py, dx, dy)[0])
            if c0 > 1e-9:
                assert cb >= c0 + b * _closest_x(px, py, dx, dy) / c0 - 1e-12


def test_leg2_in_front_on_localization_box():
    for s in (F(3, 2), F(2)):
        ok, n = loc.leg2_front(s, *loc.box(s))
        assert ok and n >= 1


def test_localization_is_not_vacuous():
    # a box that misses the optimal orbit cannot be certified: the orbit itself is a counterexample
    s = F(3, 2)
    lo, hi = loc.box(s)
    shifted = (tuple(x + F(1, 5) for x in lo), tuple(x + F(1, 5) for x in hi))
    ok, _, _ = loc.localize(s, loc.c_lower(s), *shifted, max_nodes=20_000)
    assert not ok


def test_c_lower_below_certified_orbit():
    for s in (F(3, 2), F(2)):
        q = F(json.loads((CERT_DIR / loc.CERTS[s]).read_text())["min_sq_clearance"])
        cL = loc.c_lower(s)
        assert cL * cL <= q and q - cL * cL < F(1, 10**8)


def test_optimum_structure_and_certificate_agreement():
    for s, cert in ((Dc(3) / 2, "s3-2_m02.json"), (Dc(2), "s2-1_m02.json")):
        o = stage4c.optimum(s)
        a11, a12, a22 = o["hess"]
        assert abs(o["grad"][0]) + abs(o["grad"][1]) < Dc(10) ** -40
        assert a11 < 0 and a11 * a22 - a12 * a12 > 0             # strict local maximum
        assert o["leg1"][0] > o["leg2"][0] + Dc("0.01")          # leg 1 slack
        assert 0 < o["leg2"][1] < 1 and o["leg2"][2] > 0         # interior tangency, in front of the chaser
        q = json.loads((CERT_DIR / "orbits" / cert).read_text())["min_sq_clearance"]
        num, den = (int(x) for x in q.split("/"))
        c_cert = (Dc(num) / Dc(den)).sqrt()
        assert c_cert <= o["c"] and o["c"] - c_cert < Dc(10) ** -13


def test_boundary_chain_short():
    worst, a, (rmin, rmax), _ = stage4c.boundary_chain(Dc(2), steps=40)
    assert worst > 0 and a < Dc(10) ** -12 and 0 < rmin <= rmax < 1


def test_upper_bound_node_count_reproducible():
    # Stage 4B audit: the branch-and-bound is deterministic; the coarse run's counts are fixed
    spec_b = importlib.util.spec_from_file_location("two_leg_upper_bound", CERT_DIR / "two_leg_upper_bound.py")
    ub = importlib.util.module_from_spec(spec_b)
    spec_b.loader.exec_module(ub)
    assert ub.certify(F(3, 2), F(6571, 10000)) == (True, 27379, 54757)
