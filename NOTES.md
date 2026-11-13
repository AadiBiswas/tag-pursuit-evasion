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

## 2026-11-12 — Stage 3.5 (verification)

- **Certificates.** These are now one JSON file per orbit in theory/certificates/, with a stdlib-only verifier (no tagsim, no generator import). The verifier checks speed, schedule, the PP rule, exact closure, closed-interval clearance, 3-period exact recurrence and the recorded values. All 15 pass. Every leg is unit speed, so Theorem 4 holds in the exact-speed model too.
- **Hand-checkable example.** At s = 4/3, a perpendicular runner from D = 25/24 has closest approach exactly 5/8, so it escapes PP iff alpha > 8/5. It doubles as the "touch" negative test.
- **Monotonicity.** It was easy once phrased right: if the runner class is closed under open-loop replay, replay the eps-run's controls in the eps'-game. The sweeps are NOT such a family: D(0) = 10 eps moves with alpha in normalised units.
- **Policy separation.** At s = 2, alpha = 1.9, the symmetric pass beats PP while the hybrid captures everyone. alpha_sym < 2 always (g(s/2) = 1/4 and g'(s/2) = 1/s), so the separation interval is non-empty for all s >= 2.
- **Literature.** ANP (self-triggered ZOH PP) has endogenous sampling, so it never meets overshoot. Its App. B is our Lemma B(i). BBH: turn-based, equal steps, point capture. Yufereva: sampled simple pursuit with period = capture radius, but equal speeds and compact space. Alonso–Goldstein–Reingold is unread and is the top priority.

## 2026-11-12 — Stage 4A (viability, aligned one-decision game)

- **Key simplification.** With one decision each per period, the relative path over a period is ONE straight segment, so everything is plane geometry.
  - Parametrize full-speed actions by the separation y they hold fixed. Then T_y(D)^2 = D^2 - (s^2-1)(D-y)/(s-y), with clearance D sin(theta_y).
- **The whole game hangs on one inequality.** An up-step from D has clearance <= Psi(D) <= sqrt(G).
  - Below alpha_sym, D strictly decreases every period: capture.
  - Above it, the symmetric pass survives.
  - At alpha_sym, only a chain that creeps down onto y* survives. Every periodic strategy dies. A cute closed-vs-open-ball effect.
- **Finite vs infinite horizon really differ**, with explicit points: y* at alpha_sym, and y_- for alpha_sym < alpha < 2. Survival time from y_- grows like log(1/first step).
- **The grid DP is unreliable near the threshold**, in both directions. It is kept in the write-up as a cautionary result, not hidden.
- **Literature.**
  - BBH Prop III.4 is a circling evasion of greedy discrete pursuit: the nearest precedent for our periodic orbits. It is cited.
  - The AGR full text is blocked by bot protection. Someone needs to open RR-1700 in a browser.

## 2026-11-12 — Stage 4B (two runner decisions per chaser period)

- **Audit of 4A.** It holds up. The one real wording issue: the boundary survivor is a *stationary* feedback, y = y* + beta(D - y*), generating a non-periodic D sequence. Recorded as a revision note in the 4A file.
- **Theorem 8 for any m is formal.** Capture iff no safe non-decreasing period (G_up), escape iff a safe closing period (G_lev). The whole difficulty is whether G_up = G_lev.
- **The 4A trick dies at m = 2.** With leg 2's closest point behind the chaser, clearance falls as the start moves out, so for a fixed control the best up-step is not the closing one. Exact counterexample, s = 3/2: clearance 0.164 vs 0.0098.
- **Globally, the closing orbit still wins** (to 7 digits). An exact-rational branch-and-bound over all 5 parameters proves G_up^(1/2) <= 0.6382 / 0.5890 in 2-4M nodes. Tight runs (0.6374 / 0.5882, 10M / 17M nodes) give a bracket of width < 8e-4 around the certified m=2 orbits.
  - The Lipschitz bound "a segment's distance moves at most as much as its endpoints" makes the B&B cheap at 5D. It will not scale to m = 4 (9D).
- **Dimension.** Two legs in 3D flatten to the plane by an intermediate-value argument on a chord (bounded speed). With exact speed, 3D genuinely adds options, but only ones planar bounded-speed runners already have.

## Open questions for Stage 4
- One-pass reachability / viability kernel in D for aligned runners. This would close or shrink [2s/(1+s), alpha_c(s, m)].
- Any escape from PP for runners whose clock is not aligned with the chaser's?
- Is kappa* (best chaser) finite?

## Open questions for Stage 3 (as posed after Stage 2; answered above)
- Best-response runner against PP near alpha_C = 1 (H1). The perpendicular orbit seen in Stage 2 is the
  obvious first candidate for an invariant evasion set.
- Is intercept's edge over PP a guarantee-level improvement anywhere, or only against predictable runners?
