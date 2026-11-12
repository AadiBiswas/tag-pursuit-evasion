"""theory/certificates/: the standalone verifier accepts every committed certificate
and rejects deliberately broken ones, for the reason it was broken."""

import copy
import importlib.util
import json
import os
import subprocess
import sys
from fractions import Fraction as Fr
from pathlib import Path

import pytest

CERT_DIR = Path(__file__).resolve().parents[1] / "theory/certificates"
ORBITS = sorted((CERT_DIR / "orbits").glob("*.json"))
HAND = CERT_DIR / "examples/s4-3_m01_hand.json"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, CERT_DIR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


verify = _load("verify")


def _cert(path):
    return json.loads(path.read_text())


def test_all_certificates_verify():
    assert len(ORBITS) == 15
    for f in ORBITS + [HAND]:
        verify.check(_cert(f))


def test_hand_example_values():
    # s = 4/3, runner runs perpendicular at full speed: closest approach 5/8 at t = 1/2.
    c = _cert(HAND)
    assert verify.check(c) == Fr(25, 64)
    assert c["legs"][0]["t_min"] == "1/2"


def test_rejects_overspeed():
    c = _cert(ORBITS[-1])
    vx, vy = (Fr(x) for x in c["legs"][3]["runner_velocity"])
    c["legs"][3]["runner_velocity"] = [str(vx * Fr(1001, 1000)), str(vy * Fr(1001, 1000))]
    with pytest.raises(verify.Rejected, match="speed"):
        verify.check(c)


def test_rejects_exact_speed_claim_with_slow_leg():
    c = _cert(HAND)
    c["legs"][0]["runner_velocity"] = ["0", "9/10"]
    with pytest.raises(verify.Rejected, match="exact-speed"):
        verify.check(c)


def test_rejects_non_closing_orbit():
    c = _cert(ORBITS[0])
    c["D0"] = str(Fr(c["D0"]) + Fr(1, 10**6))
    with pytest.raises(verify.Rejected, match="closure"):
        verify.check(c)


def test_rejects_entering_capture_radius():
    c = _cert(ORBITS[0])
    c["alpha_c"] = "1"  # eps = rho: far inside the clearance
    with pytest.raises(verify.Rejected, match="min squared separation"):
        verify.check(c)


def test_rejects_exact_touch_between_decisions():
    # alpha = 8/5 makes eps exactly the closest approach, reached mid-leg (t = 1/2).
    # A touch is a capture (closed ball), so this is not an escape certificate.
    c = _cert(HAND)
    c["alpha_c"] = "8/5"
    with pytest.raises(verify.Rejected, match="touches"):
        verify.check(c)
    c["alpha_c"] = "8001/5000"  # just above: escape
    verify.check(c)


@pytest.mark.parametrize("field,value", [("duration", "shift"), ("t_start", "1/3"), ("phi_E", "1/32"), ("tau_E", "1/8")])
def test_rejects_schedule_violations(field, value):
    c = _cert(ORBITS[4])  # m = 16
    m = c["m"]
    if field == "duration":  # lengthen leg 2 and shorten leg 3; total still tau_C
        c["legs"][2]["duration"] = str(Fr(1, m) + Fr(1, 100))
        c["legs"][3]["duration"] = str(Fr(1, m) - Fr(1, 100))
    elif field == "t_start":
        c["legs"][5]["t_start"] = value
    else:
        c["clocks"][field] = value
    with pytest.raises(verify.Rejected, match="clock|phase|schedule"):
        verify.check(c)


def test_rejects_tampered_record():
    c = _cert(ORBITS[2])
    c["legs"][1]["min_sq_sep"] = str(Fr(c["legs"][1]["min_sq_sep"]) + Fr(1, 10**30))
    with pytest.raises(verify.Rejected, match="recorded"):
        verify.check(c)


def test_cli_exit_code_on_bad_certificate(tmp_path):
    c = _cert(HAND)
    c["alpha_c"] = "8/5"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(c))
    r = subprocess.run([sys.executable, str(CERT_DIR / "verify.py"), str(bad)], capture_output=True, text=True)
    assert r.returncode == 1 and "REJECTED" in r.stdout


def test_verifier_output_identical_across_processes_and_hash_seeds():
    outs = []
    for seed in ("0", "1", "4242"):
        env = dict(os.environ, PYTHONHASHSEED=seed)
        r = subprocess.run([sys.executable, "-I", str(CERT_DIR / "verify.py")], capture_output=True, text=True, env=env)
        assert r.returncode == 0, r.stdout
        outs.append(r.stdout)
    assert outs[0] == outs[1] == outs[2]
    assert "15/15 certificates verified" in outs[0]


def test_committed_files_regenerate_from_stage3_data():
    build = _load("build")
    rows = json.loads(build.SRC.read_text())
    for row in rows:
        s = Fr(row["s_exact"])
        f = CERT_DIR / "orbits" / f"s{s.numerator}-{s.denominator}_m{row['m']:02d}.json"
        assert f.read_text() == json.dumps(build.build(row), indent=1) + "\n"


def test_verifier_is_standalone():
    src = (CERT_DIR / "verify.py").read_text()
    lines = [ln.strip() for ln in src.splitlines()]
    imports = {ln.split()[1] for ln in lines if ln.startswith(("import ", "from "))}
    assert imports == {"json", "math", "sys", "fractions", "pathlib", "decimal"}
