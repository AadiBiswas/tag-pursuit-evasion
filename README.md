# tag-pursuit-evasion

How to Win a Game of Tag: a two-player pursuit–evasion game with unequal speeds
and asynchronous, periodic decision clocks, in 2D/3D.

- `stage0_spec.md`: formal model, proofs, conjectures (with revision log)
- `NOTES.md`: research and implementation decisions
- `src/tagsim/`: event-driven simulator
  - `kinematics.py`: exact first-contact / closest approach on an interval
  - `engine.py`: clocks, simultaneous-move protocol, event log, trajectories
  - `policies.py`: scripted policies
  - `strategies.py`: baseline chasers (pure pursuit, braking, intercept) and runners (flee, perpendicular, predictive)
- `tests/`: pytest suite, including consistency checks against the spec's propositions
- `experiments/stage2.py`, `configs/stage2.json`: preliminary sweep; outputs in `results/stage2/` (incl. `note.md`)
  and `figures/stage2/`

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
