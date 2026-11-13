# tag-pursuit-evasion

How to Win a Game of Tag: a two-player pursuit–evasion game with unequal speeds
and asynchronous, periodic decision clocks, in 2D/3D.

- `stage0_spec.md`: formal model, proofs, conjectures (with revision log)
- `NOTES.md`: research and implementation decisions
- `src/tagsim/`: event-driven simulator
  - `kinematics.py`: exact first-contact / closest approach on an interval
  - `engine.py`: clocks, simultaneous-move protocol, event log, trajectories
  - `policies.py`: scripted policies
  - `strategies.py`: baseline chasers (pure pursuit, braking, hybrid, intercept) and runners (flee, perpendicular, predictive)
  - `best_response.py`: best-response planner against pure pursuit; the closed-form symmetric-pass orbit
  - `viability.py`: exact one-period geometry of the aligned one-decision game
- `tests/`: pytest suite, including consistency checks against the spec's propositions
- `experiments/stage2.py`, `configs/stage2.json`: preliminary sweep; outputs in `results/stage2/` (incl. `note.md`)
  and `figures/stage2/`
- `experiments/stage3.py`, `experiments/policy_separation.py`, `configs/stage3.json`: Stage 3 orbits, certificates,
  sweeps, figures; outputs in `results/stage3/` and `figures/stage3/`
- `experiments/stage4a.py`, `experiments/stage4b.py`: Stage 4A viability prototype and Stage 4B two-leg analysis;
  outputs in `results/stage4a/`, `results/stage4b/`
- `theory/`: mathematics
  - `stage3_mathematical_review.md`: full proofs (Theorems 1-5, Lemmas M and S), thresholds, gaps
  - `stage4_viability_analysis.md`: Stage 4A viability kernels; exact threshold for the aligned one-decision game
  - `stage4_multidecision_analysis.md`: Stage 4B two-decision runners; certified threshold bracket
  - `theorem_register.md`: index of results, assumptions, proofs and tests
  - `certificates/`: exact escape certificates with a standalone verifier (`python theory/certificates/verify.py`), and the
    exact two-leg up-step bound (`two_leg_upper_bound.py`)
  - `literature_review.md`, with entries in `references.bib`

## Setup

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e '.[test,experiments]'
.venv/bin/python -m pytest
.venv/bin/python experiments/stage2.py run && .venv/bin/python experiments/stage2.py figures
```

## Minimal example

```python
from tagsim import AgentSpec, Constant, simulate

res = simulate(AgentSpec(1.5, "1/3"), AgentSpec(1.0, "1/2"),
               x_C0=[0, 0], x_E0=[10, 0], eps=1.0, horizon=40,
               chaser_policy=Constant([1.5, 0]), runner_policy=Constant([1.0, 0]))
res.capture_time   # 18.0
```

Clock periods and phases are exact rationals (`"1/3"`, `Fraction`, int, or decimal float).
