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

## 2026-11-12 — Stage 3

- H1 was false as stated. PP's guarantee extends to alpha_C <= 2s/(1+s). The proof is pathwise; the key is the overshoot inequality D_k + D_{k+1} <= L + rho.
- The symmetric-pass orbit (exact, closed form) bounds PP's threshold from above for aligned runners. Multi-leg orbits do better. Once the legs are fixed their closure equation is *linear* in D, so they can be certified in exact rationals. 15 certificates are in results/stage3/certified_orbits.json, with an independent checker in tests/test_certificates.py.
- Auditing which properties of PP the capture proof uses led to the hybrid chaser: brake while D > s*eps, PP below that. It captures iff alpha_C <= s, and is bounded-speed only.
- Best-response planner: beam search with an exact PP rollout. Two defects were found by starting it on states where escape provably exists:
  - no "hold velocity" action, because headings are relative to the rotating line of sight;
  - ranking partial plans by their prefix.
  Both are fixed, with switches kept for the ablation. The rollout ranking is the main fix. Even fixed, the planner fails at about 2% margins with small search settings, so it is a lower bound on the runner and never evidence of capture.
- as_time now forces Python ints: numpy-int Fractions overflowed silently (separate commit).
- Ties at thresholds (BP at alpha = 1, hybrid at alpha = s) are exact tangencies, so the float engine can go either way there and tests avoid those exact points. Thm 1's own threshold is *not* a tie: its capture is strict.
- Clock phase is first-order. The same states gave 12/12 escapes with aligned clocks and 0/12 with random phases.

## Open questions for Stage 4
- One-pass reachability / viability kernel in D for aligned runners. This would close or shrink [2s/(1+s), alpha_c(s, m)].
- Any escape from PP for runners whose clock is not aligned with the chaser's?
- Is kappa* (best chaser) finite?

## Open questions for Stage 3 (as posed after Stage 2; answered above)
- Best-response runner against PP near alpha_C = 1 (H1). The perpendicular orbit seen in Stage 2 is the
  obvious first candidate for an invariant evasion set.
- Is intercept's edge over PP a guarantee-level improvement anywhere, or only against predictable runners?
