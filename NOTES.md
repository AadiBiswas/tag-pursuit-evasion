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
  First version used the textbook discriminant; a test with `|r0|/eps = 1e9` showed `|r0|^2 - eps^2`
  loses eps entirely. Now computed via closest approach (perpendicular distance accurate to ~ulp(|r0|))
  and the entry root as `(n-eps)(n+eps) / (a (s_min + h))`. Grazing contact (closest approach exactly eps)
  counts as capture in exact arithmetic but is floating-point sensitive — measure zero, accepted.
- **Simultaneous moves.** All deciders' observations are frozen (read-only array copies) from the t^- state
  before any policy is called; then chaser is queried, then runner; then both velocities are applied.
  Policies that share hidden mutable state could still collude — not guarded against, not our threat model.
- **Position anchoring.** Each agent's position is `anchor + v * (t - t_anchor)` with the anchor reset at its
  own decisions; error accumulates per decision, not per event.
- **Speed validation.** Velocities above `R` by more than 1e-12 relative raise (no silent clipping — that
  would change the model). Within tolerance they are used as given.
- **Precommitment.** `first_decision` (phi) allowed in `[0, period]`; phi > 0 requires `initial_velocity`.
  Spec §A.2 had `[0, tau)`; phi = tau is "decided at 0^-", harmless and convenient.
- **Horizon.** Closed: capture exactly at H counts. No decisions are taken at t = H.
- **Termination guard.** `max_events` (default 1e6) with `stop_reason="max_events"`; needed once
  reactive policies can produce long games.

## Open questions for Stage 2
- See the Stage 1 report: which reactive baselines first, and whether to run the F experiment before or
  after a runner best-response (Stage 3).
