"""Re-check the committed orbit certificates from the JSON alone.

Deliberately shares no code with experiments/stage3.py:certify(), so a bug
there can't certify itself. Everything is exact rational arithmetic. Units:
R_E = tau_C = 1, eps = 1/alpha_c; chaser runs from the origin along +x at
speed s for the whole period, runner starts at (D*, 0) and plays m legs.
"""

import json
from fractions import Fraction as Fr
from pathlib import Path

import pytest

CERTS = Path(__file__).resolve().parents[1] / "results/stage3/certified_orbits.json"


@pytest.mark.skipif(not CERTS.exists(), reason="run experiments/stage3.py certify first")
def test_certificates_hold_exactly():
    certs = json.loads(CERTS.read_text())
    assert len(certs) == 15
    for c in certs:
        s, m = Fr(c["s_exact"]), c["m"]
        h = Fr(1, m)
        V = [(Fr(a), Fr(b)) for a, b in c["velocities_exact"]]
        D = Fr(c["D_star_exact"])
        eps2 = 1 / Fr(c["alpha_c"]) ** 2
        assert len(V) == m and D > 0
        assert all(vx * vx + vy * vy <= 1 for vx, vy in V)  # bounded-speed model, exactly
        px, py = D, Fr(0)
        for j, (vx, vy) in enumerate(V):
            rx, ry, wx, wy = px - s * j * h, py, vx - s, vy
            a, b = wx * wx + wy * wy, rx * wx + ry * wy
            t = min(max(-b / a, Fr(0)), h)  # minimizer of the convex quadratic |r + t w|^2 on [0, h]
            assert (rx + t * wx) ** 2 + (ry + t * wy) ** 2 > eps2
            px, py = px + vx * h, py + vy * h
        assert (px - s) ** 2 + py ** 2 == D * D  # closure: separation returns to D* exactly
