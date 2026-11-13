# Theorem register

*Stage 3.5, 2026-11-12. Updated in Stage 4A (Theorems 6, 7) and Stage 4B (Theorems 8, 9).*

This file indexes every result, giving its assumptions, where its proof is, and which tests check it.

**Abbreviations.**
- **Review** = `theory/stage3_mathematical_review.md`.
- **Spec** = `stage0_spec.md`.
- **Tests** are in `tests/`: TS = `test_theory_scenarios.py`, BR = `test_best_response.py`, CP = `test_certificate_package.py`, CE = `test_certificates.py`.

**Notation** (Review §2):
- $s = R_C/R_E$
- $\alpha_C = R_E\tau_C/\varepsilon$
- $L = R_C\tau_C$
- $\rho = R_E\tau_C$

**Shared assumptions.** Capture is the closed $\varepsilon$-ball, checked continuously in time. Unless stated otherwise, the runner class is $\mathcal R_{\rm all}$ or larger and the initial-state class is $\mathcal I_{\rm all}$. The runner classes are defined in Review §2.4.

## Proven

| ID | Statement | Assumptions | Proof | Tests |
|---|---|---|---|---|
| Escape lemma | If $R_E \ge R_C$, a runner that flees at every decision is never caught. | Unbounded space; any chaser | Spec §B.1 | TS `test_escape_lemma` |
| Interception lemma | Capture by time $T$ is feasible iff $\exists\, t \le T$ with $\lVert \mathbf e(t) - \mathbf c_0 \rVert \le R_C t + \varepsilon$. | Known constant runner velocity | Spec §B.1a/b | TS `test_interception_*` |
| Lemma A | The runner's displacement over time $\sigma$ is at most $R_E\sigma$. | — | Review §3.2 | — |
| Lemma B | (i) If $D_k \ge L$: $D_{k+1} \le D_k - (L-\rho)$. (ii) If $D_k < L$: the separation is $\le D_k/s$ at $t_k + D_k/R_C$, and $D_{k+1} \le L + \rho - D_k$. | PP | Review §3.2 | TS `test_tangent_sidestep_min_distance` |
| Prop 1 | PP captures every runner if $\alpha_C \le 1$. | Either speed model; any $d$ | Spec §B.2 | TS `test_prop1_*` |
| **Thm 1** | PP captures every runner if $\alpha_C \le 2s/(1+s)$, by $\varphi_C + (K+2)\tau_C$. Capture is strict at equality. | $s > 1$; either speed model; any runner schedule, phase or information; any $d$ | Review §3 | TS `test_extended_threshold`; BR `test_never_escapes_below_extended_threshold` |
| BP threshold | Braking pursuit captures every runner iff $\alpha_C \le 1$. | Bounded-speed model | Spec §B.2a | TS `test_braking_*` |
| BP is not dominated by PP | There is a runner that BP catches and PP misses. | One explicit instance | Spec §B.2a | TS `test_braking_beats_pure_pursuit_on_a_specific_runner` |
| **Thm 2** | For $\alpha_C > \alpha_{\rm sym}(s)$, an explicit symmetric-pass runner evades PP forever. The relative state recurs exactly. | Runner decides at every chaser decision ($\mathcal R^{\rm al}_1$); specific initial state; both speed models; $d \ge 2$ | Review §4 | BR `test_symmetric_pass_*`, `test_best_pass_matches_grid` |
| **Thm 3** | The hybrid chaser $H$ (brake while $D > s\varepsilon$, then PP) captures every runner iff $\alpha_C \le s$. | Bounded-speed model; $H$ knows $\varepsilon$ | Review §3.4 and §3.5(b) | TS `test_hybrid_*` |
| **Thm 4** (computer-assisted) | For 15 pairs $(s, m)$ with $s \in \{6/5, 3/2, 2\}$ and $m \in \{1, 2, 4, 8, 16\}$, an aligned runner with $\tau_E = \tau_C/m$ evades PP forever iff $\alpha_C > \hat\alpha(s,m)$, for that particular orbit. The certified rational $\alpha_c \ge \hat\alpha$ admits equality. | $\mathcal R^{\rm al}_m$; specific initial state; both speed models; $d \ge 2$ | Review §7.2–7.3; `theory/certificates/README.md` | CE; CP (15/15 verified, negative tests) |
| **Lemma M** | For fixed speeds, clocks, phases and initial-state class, capture guarantees are monotone in $\alpha_C$: true at $\alpha'$ implies true at every $\alpha \le \alpha'$. This holds for $\varepsilon$-free chasers and for the best chaser. | Runner class closed under open-loop replay | Review §2.4 | — |
| **Lemma S** | $2s/(1+s) \le \alpha_{\rm sym}(s) < 2$. | $s > 1$ | Review §3.5 | TS `test_lemma_s_bounds` |
| **Thm 5** | **Policy separation.** For $\alpha_{\rm sym}(s) < \alpha_C \le s$, PP admits an indefinitely evading runner, while $H$ captures every runner. So $\kappa_{\rm PP} < \kappa^\*$. The interval is non-empty for all $s \ge 2$. | Bounded-speed model; $\mathcal R \supseteq \mathcal R^{\rm al}_1$; $\mathcal I_{\rm all}$ | Review §3.5 | TS `test_policy_separation_instance_exact`, `test_hybrid_captures_up_to_alpha_s`; figure `figures/stage3/policy_separation` |
| Cor 5.1 | The instance $s = 2$, $\alpha_C = 19/10$, with $y = 6/5$. The runner's frame velocity is $(1/8,\ 3\sqrt7/8)\,R_E$. | as Thm 5 | Review §3.5 | TS `test_policy_separation_instance_exact` |
| Rotation equivariance | PP and the orbit runners commute with orientation-preserving isometries. One period's state therefore maps to the next by a fixed rotation plus translation. | — | Review §4.2, step 5 | CP (3-period exact recurrence) |
| Scale invariance | With $\varepsilon$-free policies, the outcome depends on $\alpha_C$ only through a scale-free closest approach. | $\varepsilon$-free policies | Review §5.1 | — |

### Stage 4A: the aligned one-decision game $\mathcal G_1$

All proofs are in `theory/stage4_viability_analysis.md` (V). The tests are in `tests/test_viability.py`.

| ID | Statement | Assumptions | Proof | Tests |
|---|---|---|---|---|
| Prop 4A.2 | The state at decision times reduces exactly to the separation $D$; open-loop strategies suffice; $\mathbb R^d$ reduces to the plane. | $\mathcal G_1$: aligned clocks, one runner decision per chaser period, PP, unbounded space | V §2 | — |
| Prop 4A.5 | Exact safe reachable set: the plateau interval (end point inside the disk on diameter $[0, (D,0)]$) together with the full-speed images $T_y(D)$ satisfying $C_y(D) > \varepsilon$. | Bounded-speed model | V §3.3 | `test_reachable_set_formula`, `test_heading_parametrization` |
| Lemma 4A.6 | $y^\*$ is the unique maximiser of $g$. Every action's level-step clearance is at most $G$, with equality only at full speed and $y^\*$. | — | V §3.4 | `test_y_star_is_unique_maximizer` |
| Lemma 4A.7 | Up-step bound: any step with $D' \ge D$ has closest approach $\le \Psi(D) \le \sqrt G$. | — | V §3.4 | `test_up_steps_bounded_by_psi` |
| Lemma 4A.8 | Compactness: for the **non-strict** relation, survival for every finite horizon is equivalent to infinite survival. | — | V §4 | — |
| **Thm 6** | $\kappa_{\rm PP}(s;\mathcal R^{\rm al}_1,\mathcal I_{\rm all}) = \alpha_{\rm sym}(s)$ exactly. The guarantee set is the **open** interval $(0,\alpha_{\rm sym})$. At $\alpha_{\rm sym}$, evasion is possible but **only non-periodically**: $D_k \downarrow y^\*$. Also $y^\* \in \bigcap_n\mathcal V_n \setminus \mathcal K_\infty$. | $\mathcal G_1$; both speed models; $d \ge 2$ | V §5.1 | `test_below_threshold_every_safe_step_goes_down`, `test_boundary_chain_*` |
| **Thm 7** | For $\alpha_{\rm sym} < \alpha_C \le 2$: $\mathcal K_\infty \cap (0,y_+) = (y_-,y_+)$. For $\alpha_C < 2$: $y_- \in \bigcap_n\mathcal V_n \setminus \mathcal K_\infty$. For every $\alpha_C > \alpha_{\rm sym}$: $\mathcal K_\infty \subseteq (\Psi^{-1}(\varepsilon), \infty)$. | $\mathcal G_1$ | V §5.2 | `test_period_one_set_matches_g`; high-precision chains in V §5.2 |

### Stage 4B: aligned multi-decision runners

Proofs are in `theory/stage4_multidecision_analysis.md` (M). Tests are in `tests/test_two_leg.py`.

| ID | Statement | Assumptions | Proof | Tests / certificate |
|---|---|---|---|---|
| Lemma 4B.1 | Nesting: $\mathcal R_{m_1} \subseteq \mathcal R_{m_2}$ when $m_1 \mid m_2$, in each speed model, so $\kappa$ is non-increasing along divisibility. Strict for $1 \mid 2$. | Aligned clocks. Nothing claimed for non-nested schedules. | M §3 | `test_nesting_m1_orbit_is_an_m2_orbit` |
| Lemma 4B.2 | The $m$-leg period is a translate of a path independent of $y$. It is non-decreasing iff $y \le D^\*(\bar{\mathbf u}) \le (s+1)/2$. The state reduces to $D$. | — | M §4.1 | — |
| Prop 4B.4 | Two legs in $\mathbb R^d$: same one-period options as the plane (bounded speed). Exact-speed options in $d \ge 3$ lie between the planar exact-speed and planar bounded-speed options. | $m \le 2$ | M §4.3 | `test_two_leg_dimension_reduction_bounded_speed` |
| Lemma 4B.5 | $G_{\rm lev}(m)$ and $G_{\rm up}(m)$ are attained. | — | M §5 | — |
| **Thm 8** | $G_{\rm up}(m)^{-1/2} \le \kappa_{\rm PP}(s;\mathcal R_m) \le G_{\rm lev}(m)^{-1/2}$. Capture below the lower bound comes with a uniform decrement and a finite period bound. At the threshold, no eventually-periodic run survives. | Any $m$; aligned clocks | M §5 | — |
| **Thm 9** | $\kappa_{\rm PP}(3/2;\mathcal R_2) \in [1.568873, 1.569530]$ and $\kappa_{\rm PP}(2;\mathcal R_2) \in [1.700102, 1.700869]$. | Both speed models; $d \ge 2$ | M §6.1 | `theory/certificates/two_leg_upper_bound.py` (exact branch-and-bound) plus orbit certificates `*_m02`; `test_upper_bound_*` |
| Prop 4B.6 | Exact counterexample: for a fixed two-leg control, a strict up-step can have far more clearance than the closing period, so the Stage 4A pathwise mechanism fails for $m = 2$. | $s = 3/2$ | M §6.2 | `test_pathwise_monotonicity_counterexample_exact` |

## Thresholds currently known

Notation is from Review §2.5. Unless stated otherwise, these bounds are for $\mathcal R_{\rm all}$, $\mathcal I_{\rm all}$, and both speed models.

| $s$ | $2s/(1+s) \le \kappa_{\rm PP}$ | $\kappa_{\rm PP} \le \alpha_{\rm sym}(s)$ (closed form) | $\kappa_{\rm PP} \le \hat\alpha(s,16)$ | $\kappa^\*$ (bounded-speed) $\ge s$ |
|---|---|---|---|---|
| 6/5 | 1.0909 | 1.4342676433 | 1.3889168761 | 1.2 |
| 3/2 | 1.2000 | 1.6300837216 | 1.5396185998 | 1.5 |
| 2 | 1.3333 | 1.7806140964 | 1.6539612377 | 2 (so $\kappa_{\rm PP} < \kappa^\*$) |

**At $\hat\alpha$ itself the orbit is captured.** The upper-bound columns therefore bound only the supremum, and they hold for any runner class that contains $\mathcal R^{\rm al}_m$.

## Numerically supported (not proven)

| Claim | Evidence | Location |
|---|---|---|
| $\hat\alpha(s,m)$ decreases slowly in $m$ and is not converged at $m = 16$. | Optimiser plus certificates | Review §7.1 |
| Period-2 orbit search returns period-1 solutions. | SLSQP, 40 starts | Review §7.1 |
| No escape found at $\alpha_C \le 7/5$ with random phases. | Planner sweep: 5,184 games | Review §6; `results/stage3/sweep.csv` |
| Clock alignment decides the outcome: 12/12 escapes aligned vs 0/12 at random phases. | Planner | `results/stage3/phase_alignment_check.txt` |
| The perpendicular runner converges to a fixed-point orbit. | Long runs | Review §5.3 |
| A less agile runner ($a = 2$) escapes PP at large $\alpha_C$. | Planner | Review §5.3 |
| $\alpha_{\rm sym}(s) < s$ iff $s > s_0 \approx 1.7078$. | Bisection on the closed form | Review §3.5 |

## Conjectures and open questions

| Item | Status |
|---|---|
| **Conjecture 4B.1**: $G_{\rm up}(2) = G_{\rm lev}(2)$, i.e. $\kappa_{\rm PP}(s;\mathcal R_2) = G_{\rm lev}(2)^{-1/2}$ (1.5695294 at $s = 3/2$, 1.7008682 at $s = 2$). | 7-digit numerical agreement; rigorous to within $2.7\times10^{-4}$ in clearance (Thm 9). |
| **Failed conjecture (kept)**: for every fixed $m$-leg control, clearance is non-decreasing in $y$ on $(0, D^\*]$. | True for $m = 1$; **false for $m = 2$** (Prop 4B.6). |
| **Conjecture 4A.1**: for $\alpha_{\rm sym} < \alpha_C \le 2$, $\mathcal K_\infty = (y_-, \infty)$ in $\mathcal G_1$. | Grid evidence at $s = 1.5$ and $2$ (V §6.1). |
| **Stage 4B question**: does Lemma 4A.7 extend to $m$-leg aligned runners, giving $\kappa_{\rm PP}(s;\mathcal R^{\rm al}_m) = G_m(s)^{-1/2}$? | **Partly answered (M):** the pathwise version fails at $m = 2$. The global version, $G_{\rm up} = G_{\rm lev}$, is Conjecture 4B.1, bracketed by Thm 9. |
| **H1′**: optimal evasion of PP by aligned runners is periodic, so $\kappa_{\rm PP}(s;\mathcal R^{\rm al}_m)$ tends to the limit of the periodic-orbit thresholds. | Conjecture |
| Exact value of $\kappa_{\rm PP}(s;\cdot)$ for any runner class. | **Solved for $\mathcal R^{\rm al}_1$** (Thm 6). Open for $\mathcal R^{\rm al}_m$ with $m \ge 2$ and for $\mathcal R_{\rm all}$; for $\mathcal R_{\rm all}$ the gap is about 0.30 at $s = 1.2, 1.5, 2$. |
| Any escape from PP for $\mathcal R_{a,\Phi}$ with $0 \notin \Phi$ (unaligned clocks only). | Open. There is planner evidence at $\alpha_C \ge 8/5$. |
| Escape from far initial states ($\mathcal I_{\rm far}$): can a runner reach an orbit's state? | Open |
| $\kappa^\* < \infty$ (H2, upper half). Is $\kappa^\* > s$? | Open |
| Policy separation in the exact-speed model. | Open, because $H$ is inadmissible there. |
| Exact-speed best chaser beyond $2s/(1+s)$. | Open |

## Falsified

| Hypothesis | By |
|---|---|
| H1: PP's threshold against agile runners is exactly $\alpha_C = 1$. | Thm 1 |
| "BP never beats PP." | BP not dominated (explicit instance) |
| "Stage 2 heuristics locate the escape boundary." | Thm 2, Thm 4, and the planner |

## Literature status

The literature status of each result is given in `theory/literature_review.md`, §2.
- Only Lemma B(i) is **previously established**.
- Theorems 1–5 are **potentially distinct**, subject to the unread sources listed there.
- **Nothing is claimed as novel.**
