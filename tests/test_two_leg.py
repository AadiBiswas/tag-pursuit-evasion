"""Stage 4B: the aligned two-leg game. Checks of the statements in
theory/stage4_multidecision_analysis.md that can be tested directly."""

import importlib.util
import json
import math
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, "experiments")
import stage4b  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CERT_DIR = ROOT / "theory/certificates"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, CERT_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


verify = _load("verify")
bound = _load("two_leg_upper_bound")


def test_pathwise_monotonicity_counterexample_exact():
    cx = stage4b.counterexample()
    c_lo, up_lo = cx["at_3_10"]
    c_ds, up_ds = cx["at_D_star"]
    assert up_ds == 0 and up_lo > 0                   # y = 3/10 is a strict up-step, D* closes
    assert c_lo > 100 * c_ds                          # and it has far more clearance than the closing start
    assert cx["D_star"] == F(1913, 3064)


def test_upper_bound_certificate_coarse():
    ok, leaves, nodes = bound.certify(F(3, 2), F(6571, 10000))
    assert ok and leaves > 0


def test_upper_bound_cannot_cut_below_a_certified_orbit():
    # T below the certified m=2 orbit's clearance must NOT be provable (the orbit is a level step)
    c = json.loads((CERT_DIR / "orbits/s3-2_m02.json").read_text())
    clearance = math.sqrt(float(F(c["min_sq_clearance"])))
    T = F(math.floor(clearance * 10**4), 10**4)        # just below
    ok, _, _ = bound.certify(F(3, 2), T, max_nodes=20_000)
    assert not ok


@pytest.mark.parametrize("name", ["s3-2_m01.json", "s2-1_m01.json"])
def test_nesting_m1_orbit_is_an_m2_orbit(name):
    # R_1 ⊆ R_2: repeating each leg velocity gives a valid 2-leg certificate with the same orbit
    sys.path.insert(0, str(CERT_DIR))
    import build
    c = json.loads((CERT_DIR / "orbits" / name).read_text())
    row = dict(s_exact=c["s"], m=2, D_star_exact=c["D0"], alpha_c=c["alpha_c"],
               velocities_exact=[c["legs"][0]["runner_velocity"]] * 2)
    assert verify.check(build.build(row)) == F(c["min_sq_clearance"])


def _flatten_leg2(rh, w3, S):
    """Lemma 4B.4 construction: a planar w with |w + S e1| <= 1, w.rh = w3.rh, |w|^2 = |w3|^2.
    Points of the chord {w in the disk : w.rh = P} are mid + lam*t, lam in [-h, h]; |w|^2 is a
    convex quadratic in lam, and its value at the chord end with the smaller x-coordinate
    is >= |w3|^2, so a root exists between the chord's argmin and that end."""
    P, Q = rh @ w3[:2], w3 @ w3
    n = rh / np.linalg.norm(rh)
    t = np.array([-n[1], n[0]])
    foot = n * P / np.linalg.norm(rh)
    c = np.array([-S, 0.0])
    mid = foot + t * (t @ (c - foot))
    h = math.sqrt(max(1 - np.sum((mid - c) ** 2), 0.0))
    f = lambda lam: np.sum((mid + lam * t) ** 2)
    end = max((-h, h), key=lambda lam: -(mid + lam * t)[0])       # smaller x-coordinate
    lam_min = min(max(-(mid @ t), -h), h)
    lo, hi = lam_min, end
    assert f(lo) <= Q + 1e-12 and f(hi) >= Q - 1e-12
    for _ in range(200):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if (f(m) < Q) == (f(lo) < Q) else (lo, m)
    return mid + (lo + hi) / 2 * t


def test_two_leg_dimension_reduction_bounded_speed():
    rng = np.random.default_rng(4)
    S = 1.5
    for _ in range(500):
        rh = np.array([rng.uniform(-1, 2), rng.uniform(0.01, 1)])          # r(1/2) after a planar leg 1
        u = rng.normal(size=3)
        u *= rng.random() ** (1 / 3) / np.linalg.norm(u)                    # 3D leg-2 velocity, |u| <= 1
        w3 = u - np.array([S, 0, 0])
        w = _flatten_leg2(rh, w3, S)
        assert np.linalg.norm(w + [S, 0]) <= 1 + 1e-9                       # planar velocity admissible
        assert w @ rh == pytest.approx(w3[:2] @ rh, abs=1e-9)
        assert w @ w == pytest.approx(w3 @ w3, abs=1e-9)                     # same leg-2 distances and end point


@pytest.mark.parametrize("s,cert", [(1.5, "s3-2_m02.json"), (2.0, "s2-1_m02.json")])
def test_engine_replays_certified_two_leg_orbit(s, cert):
    assert stage4b.engine_check(s, cert, "1001/1000", periods=60) == (False, None)
    assert stage4b.engine_check(s, cert, "999/1000", periods=60)[0]
