# Stage 2 preliminary experiment — research note (2026-11-12)

Regenerate with `python experiments/stage2.py run` followed by `python experiments/stage2.py figures`. The configuration is `configs/stage2.json`. Two runs produced byte-identical `runs.csv`.

## Setup

- **Model.** 2D, bounded-speed model. Units: $\varepsilon = R_E = 1$, so $\alpha_C = \tau_C$ and $a = \tau_E/\tau_C$.
  - $D_0 = 10$.
  - $s \in \{1.2, 1.5, 2\}$.
  - $\alpha_C \in \{1/2, 4/5, 1, 5/4, 8/5, 5/2, 4\}$.
  - $a \in \{1/4, 1, 4\}$, where $a = 1/4$ means the runner decides 4× as often as the chaser.
- **Initial states.** 40 paired states, the *same* 40 for every cell and every strategy pair. Each state has:
  - a uniform line-of-sight angle;
  - uniform initial headings, at full speed;
  - phases $\varphi_i = j/32 \cdot \tau_i$.
- **Horizon.** $H = 2 \times$ the Proposition 1 time bound at the worst phase, i.e. $2\,(3\tau_C + (D_0 + \tau_C)/(R_C - R_E))$, which is 22 to 204 time units.
  - This is a guarantee horizon only for $\alpha_C \le 1$. Above that it is just a long look.
- **Size.** 22,680 runs. The sweep takes about 5 s on 16 cores.
- **Strategies** (`src/tagsim/strategies.py`):
  - Chasers: pure pursuit (PP); braking pursuit (BP); intercept, which uses the (★) contact time against the runner's committed velocity extrapolated indefinitely, and falls back to PP when no contact is predicted.
  - Runners: flee; perpendicular, CCW side; predictive, a 180-heading search maximizing predicted min separation under a "chaser plays PP after its next decision" model.
  - The CW perpendicular variant is the mirror image. Every chaser is reflection-equivariant and the state distribution is reflection-invariant, so its outcome *distribution* is identical. It was not run separately.

"Captured" below means **captured within H** against **that specific runner**. A non-capture is an observed failure under these conditions, not a proof of escape.

## Capture frequency by strategy pair

Pooled over $s$ and the listed $\alpha_C$ values. The $\alpha_C \le 1$ column also pools over $a$.

| pair | $\alpha_C \le 1$ | $\alpha_C > 1$, $a=1/4$ | $\alpha_C > 1$, $a=1$ | $\alpha_C > 1$, $a=4$ |
|---|---|---|---|---|
| PP vs flee | 1.00 (1080/1080) | 1.00 (480/480) | 1.00 (480/480) | 1.00 (480/480) |
| PP vs perpendicular | 1.00 (1080/1080) | 0.55 (263/480) | 0.78 (373/480) | 0.97 (468/480) |
| PP vs predictive | 1.00 (1080/1080) | 0.61 (294/480) | 0.66 (319/480) | 0.81 (388/480) |
| BP vs flee | 0.98 (1061/1080)\* | 0.00 (0/480) | 0.00 (1/480) | 0.09 (43/480) |
| BP vs perpendicular | 1.00 (1080/1080) | 0.50 (240/480) | 0.25 (122/480) | 0.33 (160/480) |
| BP vs predictive | 0.99 (1067/1080)\* | 0.00 (0/480) | 0.00 (0/480) | 0.35 (167/480) |
| intercept vs flee | 1.00 (1080/1080) | 1.00 (480/480) | 1.00 (480/480) | 1.00 (480/480) |
| intercept vs perpendicular | 1.00 (1080/1080) | 1.00 (480/480) | 0.98 (472/480) | 1.00 (480/480) |
| intercept vs predictive | 1.00 (1080/1080) | 0.60 (287/480) | 0.81 (387/480) | 1.00 (480/480) |

\* All 32 BP misses at $\alpha_C \le 1$ are at $\alpha_C = 1$ exactly. Their minimum separation is $1 \pm 10^{-14}$. They are exact ties broken by rounding (see below), not strategy failures.

The per-cell breakdown with Wilson 95% CIs is in `summary.csv` and `figures/stage2/capture_vs_alpha.png`. With n = 40 per point, a CI is about ±0.15 near 0.5, and an observed 1.00 has a lower bound of 0.91.

## Checks against theory

- **Proposition 1 (PP, $\alpha_C \le 1$).** 3,240/3,240 runs were captured, all within the proven bound. The largest ratio of capture time to bound was 0.9998, so on these states the bound is nearly tight.
- **Braking pursuit.** The experiment led to a new, proven result (spec §B.2a, Rev 2). BP satisfies Proposition 1, and $\alpha_C \le 1$ is *sharp* for it. A runner fleeing in a straight line keeps the separation pinned at $R_E\tau_C$ forever, at every speed ratio.
  - Numerically, all 1,396 BP-vs-flee non-captures at $\alpha_C > 1$ have late separation equal to $\alpha_C$, to a relative precision of $1.5 \times 10^{-11}$.
- **α_C = 1 boundary.** PP captures strictly inside the interval, but BP only touches the ε-ball at the endpoint. So the grid point $\alpha_C = 1$ is numerically undetermined for BP. These points should be read as "captured in exact arithmetic".
- **Escape lemma / Case 4.** Not exercised; this sweep has $s > 1$ only.

## Patterns

1. **Braking is never better than pure pursuit here.** On paired states with $\alpha_C > 1$, BP never captured where PP failed, against any runner. PP captured where BP failed in 1,396 / 582 / 834 states against flee / perpendicular / predictive.
   - The mechanism is the one in §B.2a. Overshoot is what lets PP close the final gap; braking removes it.
   - This answers the question of whether braking helps: on this evidence, no. Against flee the answer is proven.
2. **Intercept is the strongest chaser tested, but it doesn't dominate PP.**
   - Paired, at $\alpha_C > 1$: intercept captured where PP didn't in 330 states against perpendicular and 165 against predictive. PP captured where intercept didn't in 2 and 12 states.
   - The advantage is largest against runners whose velocity stays predictable: perpendicular, and a sluggish predictive runner ($a = 4$: 1.00 vs 0.81).
   - Against an agile predictive runner ($a = 1/4$) there is no advantage (0.60 vs 0.61). Its extrapolation is wrong within one runner period.
3. **The heuristic runners only beat PP well above the threshold.**
   - No runner evaded PP at $\alpha_C = 5/4$, for any $s$ or $a$.
   - The first PP failures appear at $\alpha_C = 8/5$ against perpendicular (5 runs), and at $5/2$ against predictive.
   - So these runners do *not* reveal a sharp transition at $\alpha_C = 1$.
4. **Runner agility helps evasion, and the effect is large.** Against PP at $\alpha_C > 1$, perpendicular evasion succeeds in 45% / 22% / 3% of runs for $a = 1/4 / 1 / 4$.
5. **Evasion against PP looks like hovering, not escaping.**
   - All 775 uncaptured PP runs end with separation ≤ 5.05, against $D_0 = 10$. Their minimum separation gets as low as 1.0012.
   - The perpendicular runner settles into a near-periodic orbit around the chaser, which keeps overshooting (`figures/stage2/trajectories.png`, middle row). That orbit is a natural candidate for the invariant set an H1 proof would need. It is only observed so far, not analysed.
6. **Results are not strongly horizon-limited.** Only 35 of 8,304 captures at $\alpha_C > 1$ happen after $H/2$. Doubling $H$ would probably change little, but that has not been tested.
7. **The "smarter" runner is not uniformly better.** Against PP with $a = 1/4$, perpendicular evasion beats predictive evasion (55% vs 61% captured overall, and 0.00 vs 0.03 at $\alpha_C = 4$). Predictive's objective is myopic: it maximizes min separation over one lookahead window, with no value placed on the position it ends in.

## Relevance to hypotheses

These are observations only; nothing below establishes a hypothesis.

- **H1** (the PP threshold is sharp at $\alpha_C = 1$). These heuristics evade PP only from $\alpha_C \ge 8/5$. That is consistent with H1 and equally consistent with a higher true threshold. It neither supports nor refutes H1 near $\alpha_C = 1$; testing H1 needs a best-response runner (Stage 3). The BP result shows what a proven sharp threshold looks like for a *different* chaser.
- **H2** (smarter chasers beat the PP threshold). Intercept captures strictly more than PP against these runners, but it is not a guarantee against all runners. Against an agile predictive runner it gains nothing.
- **H3** (agility and schedule effects). Only $a \in \{1/4, 1, 4\}$ were tested, all nested schedules. Monotone in $a$, as the refinement argument predicts. Says nothing about non-nested clocks.
- **H4, H5.** Not tested: there was no $s \le 1$ and no 3D.

## Limitations

- 40 states per cell, and a coarse $\alpha_C$ grid. Wide CIs at intermediate frequencies.
- One $D_0/\varepsilon = 10$.
- Fixed horizon; no runs with $H \to \infty$.
- Runner heuristics are weak opponents. Failure to evade is not evidence that evasion is impossible.
- Intercept extrapolates the runner's velocity forever. The `horizon` option exists but was not swept.
- Predictive evasion assumes the chaser plays PP, so it is misspecified against BP and intercept by construction.
