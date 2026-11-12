# Research notes

Running log of assumptions, decisions, failed approaches and open questions.
Theory lives in `stage0_spec.md`; this file records the *why* behind code and process.

## 2026-11-11 — Stage 0 → Rev 1

- Primary model switched to `|v| <= R` with velocity held between decisions; exact-speed kept as `speed_mode="exact"`.
- Proposition 1 re-verified under bounded speed (spec §B.2 Rev 1). Condition is `R_E tau_C <= eps`, weaker than the original `R_C tau_C <= eps`.
- New: interception lemma (★) and the complete s <= 1 outcome characterization (spec §B.1a/b).
- Open: H1 (PP threshold sharpness) — only single-interval evidence. H5 projection lemma still a sketch.

## 2026-11-11 — Stage 1 engine decisions

- **Exact clock arithmetic.** Decision times are `fractions.Fraction`. Floats would make `3*0.1 != 0.3`, so
  "simultaneous" decisions on commensurate clocks would silently become sequential by an ulp — i.e. one
  agent would get information it shouldn't. Float inputs are read via `repr` (0.1 → 1/10).
  Positions and capture offsets stay float64.
- **Capture check.** Closed-form earliest root of `|r0 + s w| = eps` on each inter-event interval.
  The textbook discriminant is unusable at large scale: `|r0|^2 - eps^2` rounds to `|r0|^2` once
  `|r0|/eps` is ~1e8 (caught by a test at 1e9). We go through the closest approach instead, whose
  perpendicular distance is accurate to ~ulp(|r0|), and get the entry root as `(n-eps)(n+eps) / (a(s_min+h))`
  so near-immediate contact doesn't cancel either. Grazing contact (closest approach exactly eps) counts
  as capture in exact arithmetic but is floating-point sensitive — measure zero, accepted.
- **Simultaneous moves.** All deciders' observations are frozen (read-only array copies) from the t^- state
  before any policy is called; then chaser is queried, then runner; then both velocities are applied.
  Policies that share hidden mutable state could still collude — not guarded against, not our threat model.
- **Position anchoring.** Each agent's position is `anchor + v * (t - t_anchor)` with the anchor reset at its
  own decisions; error accumulates per decision, not per event.
- **Speed validation.** Velocities above `R` by more than `1e-12 * max(1, R)` raise (no silent clipping —
  that would change the model). Within tolerance they are used as given.
- **Precommitment.** `first_decision` (phi) allowed in `[0, period]`; phi > 0 requires `initial_velocity`.
  Spec §A.2 had `[0, tau)`; phi = tau is "decided at 0^-", harmless and convenient.
- **Horizon.** Closed: capture exactly at H counts. No decisions are taken at t = H.
- **Termination guard.** `max_events` (default 1e6) with `stop_reason="max_events"`; needed once
  reactive policies can produce long games.

## Fixed issues

- **Velocity aliasing** (fixed 2026-11-11, after the style pass). The engine stored the array a policy
  returned without copying, and `Constant`/`Scripted` hand back their internal arrays, so an in-place edit
  by any policy rewrote an agent's committed velocity — and, through position anchoring, its past path.
  `_check_velocity` now copies. Regression test: `test_committed_velocity_does_not_alias_policy_array`.
  No existing run was affected (200-game log/trajectory hash unchanged).

## 2026-11-12 — Stage 2

- Strategies in `src/tagsim/strategies.py`, all stateless functions of the Observation; no engine changes.
  Exact decision rules are in the docstrings. Perpendicular is CCW by default; CW is a separate instance.
- Intercept extrapolates the runner's committed velocity with no horizon by default; past the runner's next
  decision that's a guess. Predictive evasion assumes the chaser plays PP after its next decision -- an
  opponent *model*, wrong by design against braking/intercept.
- Braking pursuit turned out to have a clean proven story (spec §B.2a): same guarantee as PP for
  alpha_C <= 1, sharp above it via a trivial straight-line runner. At alpha_C = 1 exactly braking only
  touches the eps-ball, so that grid point is decided by rounding -- don't read anything into BP at alpha = 1.
- Preliminary sweep + findings: `results/stage2/note.md`.

## Open questions for Stage 3
- Best-response runner against PP near alpha_C = 1 (H1). The perpendicular orbit seen in Stage 2 is the
  obvious first candidate for an invariant evasion set.
- Is intercept's edge over PP a guarantee-level improvement anywhere, or only against predictable runners?
