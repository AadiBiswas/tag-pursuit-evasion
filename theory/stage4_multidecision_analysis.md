# How to Win a Game of Tag — Stage 4B: Multi-Decision Evasion

*2026-11-12. This document builds on `theory/stage3_mathematical_review.md` (cited as "the review") and `theory/stage4_viability_analysis.md` (cited as "4A").*

**Numbering.** New results are 4B.x, plus **Theorems 8 and 9**.

**Units.** $R_E = \tau_C = 1$. So $\rho = R_E\tau_C = 1$, $R_C\tau_C = s$, and $\varepsilon = 1/\alpha_C$.

## Contents

1. Summary
2. Audit of the Stage 4A boundary results
3. Nested runner classes
4. The $m$-leg period: structure, reduction, dimension
5. Level and up-step clearance; Theorem 8 (any $m$)
6. The two-leg game: Theorem 9, counterexample, numerics
7. Is periodic escape optimal?
8. Generalising to arbitrary $m$
9. Literature
10. Open questions and the next problem

Appendix: reproduction.

---

## 1. Summary

**Proven results.**

| Result | Statement | Assumptions |
|---|---|---|
| **Audit of 4A** (§2) | No mathematical gap was found. Two wordings were imprecise and are now clarified, not changed. | — |
| **Lemma 4B.1** (§3) | $\mathcal R_{m_1} \subseteq \mathcal R_{m_2}$ whenever $m_1 \mid m_2$. So guarantees and thresholds are monotone along divisibility. | Bounded-speed and exact-speed models, each separately. Nothing is claimed for non-nested schedules. |
| **Theorem 8** (§5) | For aligned $m$-decision runners, let $G_{\rm lev}(m)$ be the best squared clearance of a *closing* period and $G_{\rm up}(m)$ that of a *non-decreasing* period. Both suprema are attained. PP guarantees capture, with a uniform decrement and a finite period bound, when $\alpha_C < G_{\rm up}^{-1/2}$. A periodic orbit escapes when $\alpha_C > G_{\rm lev}^{-1/2}$. So $G_{\rm up}^{-1/2} \le \kappa_{\rm PP}(s;\mathcal R^{\rm al}_m) \le G_{\rm lev}^{-1/2}$. | Any $m$. |
| **Theorem 9** (§6) | Rigorous bracket for $m = 2$: $1.56690 < \kappa_{\rm PP}(3/2;\mathcal R^{\rm al}_2) \le 1.5695294$ and $1.69779 < \kappa_{\rm PP}(2;\mathcal R^{\rm al}_2) \le 1.7008682$. | Both speed models; every $d \ge 2$. |
| **Prop 4B.4** (§4.3) | The two-leg one-period problem in $\mathbb R^d$ reduces exactly to the plane. With exact speed, $d \ge 3$ adds options, but only ones already available to planar bounded-speed runners. | Bounded-speed model for the exact reduction. |

**How Theorem 9 is proven.**
- The **lower bound** on $\kappa$ comes from an exact-rational branch-and-bound certificate covering *every* non-decreasing two-leg period ($G_{\rm up}(2) \le T^2$).
- The **upper bound** comes from the Stage 3 exact orbit certificates.
- Compared with $m = 1$ ($\alpha_{\rm sym} = 1.6301$ and $1.7806$), the second decision per period strictly lowers PP's threshold.

**Counterexample (§6.2, exact).** The Stage 4A proof mechanism does **not** generalise.
- For $m = 1$, along any fixed action the closest approach increases with the starting separation over the up-step range. So the best up-step for that action is the closing one.
- For $m = 2$ this fails. At $s = 3/2$, a fixed control pair started at $y = 3/10$ (a strict up-step) has clearance 0.1638. The same pair started at its closing separation $D^\* = 1913/3064$ has clearance 0.0098.
- About 25% of random control pairs show some non-monotonicity.

**Numerical results (not proofs).**
- 300-start optimisation over all five parameters finds the best up-step equal to the best closing orbit, to 7 digits: $G_{\rm up}(2) = G_{\rm lev}(2)$.
- The optimiser is at full speed on both legs, and only leg 2 touches the clearance.
- **Conjecture 4B.1:** $G_{\rm up}(2) = G_{\rm lev}(2)$. This would make $\kappa_{\rm PP}(s;\mathcal R^{\rm al}_2) = G_{\rm lev}(2)^{-1/2}$ exactly: 1.5695294 at $s = 3/2$ and 1.7008682 at $s = 2$.

**Open.**
- Conjecture 4B.1 itself, which needs a global argument.
- Whether non-periodic survival exists at the $m = 2$ threshold.
- For $m \ge 4$, only the certified upper bounds and Theorem 1's lower bound are available.

---

## 2. Audit of the Stage 4A boundary results

Each delicate claim of 4A was re-derived from scratch.

| Claim (4A) | Verdict | Notes |
|---|---|---|
| Indefinite evasion at $\alpha_C = \alpha_{\rm sym}$ (Thm 6(c2)) | **Correct.** | See A1 below. |
| Strict clearance at every finite time | **Correct.** | Each period's closest approach is $C_y(D) = \sqrt G\,e^{A(a_k)} > \sqrt G = \varepsilon$. The infimum over all time equals $\varepsilon$ and is never attained, so no capture occurs (the capture set is $\{\lVert r\rVert \le \varepsilon\}$). |
| Eventually periodic escape is impossible at equality (Thm 6(c1)) | **Correct, and stronger than stated.** | See A2. |
| Uniform decrease below the threshold (Thm 6(b)) | **Correct.** | See A3. |
| Finite versus infinite horizon (Thm 6(c3), Thm 7(b), Lemma 4A.8) | **Correct.** | See A4. |
| Thm 7(b) needs $y_- > s/2$ | **Correct as stated.** | It is stated for $\alpha_C < 2$, which is equivalent: $\varepsilon > 1/2 = \sqrt{g(s/2)}$. |

**A1. Existence at the threshold.**
- *Quantifiers:* $\exists\,a_0 > 0$, $\forall D_0 \in (y^\*, y^\* + a_0)$, $\exists$ a runner policy, $\forall k$: the closest approach in period $k$ is $> \varepsilon$.
- *The limits used:*
  - $A'(0) = (1-\beta)/y^\* > 0$, which uses $g'(y^\*) = 0$;
  - $B'(0) = r \in [1/2, 1)$, using $k(y^\*)/(2y^\*) = 2c^2$.

  Both functions are $C^1$ on a neighbourhood of 0. Here $g$ is rational and positive near $y^\*$, and the square root's argument is near $y^{\*2} > 0$.
- *Consequence:* $a_0$ exists and $a_k$ stays in $(0, a_0)$.
- *Other conditions:* $y \in \operatorname{int} Y_s$ and $D < 2y$ hold for small $a$.
- *Checks:* re-checked in 400-digit arithmetic and in the engine (4A §6.2).

**A2. Trajectory versus policy (clarification).**
- *What (c1) proves.* It is a statement about **runs**: every surviving run has a strictly decreasing separation sequence. So no surviving run is eventually periodic in $D$, whatever policy produced it.
- *The surviving policy is stationary.* The construction in (c2) is a **stationary state-feedback** policy, $y(D) = y^\* + \beta(D - y^\*)$; the engine runner `BoundaryChain` is exactly this map. A stationary policy thus generates a non-periodic separation sequence.
- *Corrections to the wording.*
  - The 4A wording "only by non-periodic strategies" should read: "only by runs whose separation sequence is not eventually periodic; such runs are produced by a stationary feedback policy".
  - The remark "the only parameter value at which non-periodic strategies do strictly better than periodic ones" means precisely this: the set of $\alpha_C$ admitting some surviving run that is eventually periodic in $D$ is $(\alpha_{\rm sym}, \infty)$, while the set admitting any surviving run is $[\alpha_{\rm sym}, \infty)$.
- *Where recorded.* Both clarifications are added to 4A as a revision note. No statement there is altered.

**A3. Uniform decrease.**
- *The argument.* Compactness of $\{(D, \mathbf v) : D \in [\varepsilon, s+1],\ \lVert\mathbf v\rVert \le 1\}$, together with continuity of $(D, \mathbf v) \mapsto (\text{closest approach}, D')$, turns a sequence of safe steps with vanishing decrease into a level step with closest approach $\ge \varepsilon > \sqrt G$. That contradicts Lemma 4A.7.
- *Two caveats:*
  - $\delta(\alpha_C)$ is **not constructive**;
  - the count of periods uses $D' \le D - (s-1)$ for $D \ge s$.
- *Why this matters.* Strictly decreasing separations alone would not prove capture, because they could converge to a positive limit. The compactness step is what excludes that.

**A4. Finite versus infinite horizon.**
- For each $n$, the chain witnessing $y^\* \in \mathcal V_n$ uses a first step of size $\eta_n \to 0$. No single policy survives every $n$, and that is exactly the content of $y^\* \notin \mathcal K_\infty$.
- Lemma 4A.8 (compactness) holds for the **non-strict** relation only. 4A never applies it to the strict relation.

---

## 3. Nested runner classes

**Definition.** $\mathcal R^{\rm al}_m$ (written $\mathcal R_m$ below) is the class of runners that decide at every time $k\tau_C + j\tau_C/m$ ($k \ge 0$, $0 \le j < m$). Each velocity is held until the next decision, and the runner observes the full state, as in review §2.1.
- **Bounded-speed model:** $\lVert\mathbf u\rVert \le 1$.
- **Exact-speed model:** $\lVert\mathbf u\rVert = 1$, written $\mathcal R^{=}_m$.

> **Lemma 4B.1 (nesting).** If $m_1 \mid m_2$, then $\mathcal R_{m_1} \subseteq \mathcal R_{m_2}$ and $\mathcal R^{=}_{m_1} \subseteq \mathcal R^{=}_{m_2}$. Consequently:
> - **Guarantee sets.** $A_{\rm PP}(\mathcal R_{m_2}) \subseteq A_{\rm PP}(\mathcal R_{m_1})$, and so $\kappa_{\rm PP}(s;\mathcal R_{m_2}) \le \kappa_{\rm PP}(s;\mathcal R_{m_1})$. The same holds for $\kappa^\*$, and within each speed model.
> - **Clearance constants (§5).** $G_{\rm lev}$ and $G_{\rm up}$ are non-decreasing along divisibility.

*Proof.*
- **Decision times.** The decision times of $\mathcal R_{m_1}$ form a subset of those of $\mathcal R_{m_2}$.
- **Simulation.** An $m_2$-runner can reproduce any $m_1$-runner by re-selecting its current velocity at the additional times. Re-selection preserves the speed, so this works in both models.
- **Information.** The $m_2$-runner observes at least as much at each common time.
- **Consequences.** A guarantee against a larger class implies one against a smaller class. Every period available to an $m_1$-runner is available to an $m_2$-runner. ∎

**Strictness.** Strictness is proven for the pair $1 \mid 2$:
- $G_{\rm lev}(2) \ge c_{\rm cert}(2)^2 > G = G_{\rm lev}(1)$. Here $c_{\rm cert}(2)^2 = 0.40594$ against $G = 0.37634$ at $s = 3/2$, and $0.34567$ against $0.31540$ at $s = 2$.
- With Theorem 6, this gives $\kappa_{\rm PP}(s;\mathcal R_2) \le \hat\alpha(s,2) < \alpha_{\rm sym}(s) = \kappa_{\rm PP}(s;\mathcal R_1)$.

**Non-nested schedules are not compared.** $\mathcal R_2$ and $\mathcal R_3$ are not nested, since $1/2 \notin \{0, 1/3, 2/3\}$. Nothing is claimed about their order. Only the chain $1 \mid 2 \mid 4 \mid 8 \mid 16$, used by the certificates, is ordered.

---

## 4. The $m$-leg period

### 4.1 Structure

Fix a chaser decision at which the separation is $y$, and use the period frame:
- $\mathbf r(0) = (y, 0)$;
- the chaser velocity is $s\mathbf e_x$ for the whole period;
- runner leg $j$ uses $\mathbf u_j$ on $[(j-1)/m,\ j/m]$.

> **Lemma 4B.2.** The relative path has the form $\mathbf r(t) = (y, 0) + \mathbf P_U(t)$.
> - **Translation.** $\mathbf P_U$ is piecewise linear and **does not depend on $y$**, so changing $y$ translates the whole path.
> - **End point.** $\mathbf P_U(1) = (\bar u_x - s,\ \bar u_y)$, where $\bar{\mathbf u}$ is the mean leg velocity. Hence:
>   - $\lVert\mathbf r(1)\rVert \ge y$ iff $y \le D^\*(\bar{\mathbf u}) := \lVert\bar{\mathbf u} - s\mathbf e_x\rVert^2/(2(s - \bar u_x))$;
>   - $D^\* \le (s+1)/2$;
>   - $\lVert\mathbf r(1)\rVert \le |y - s| + 1$.
> - **Reduction.** As in 4A, Prop. 4A.2(i)–(ii), the state at chaser decisions reduces to $D$, and open-loop leg sequences suffice. The runner's extra decisions inside a period do not enter the state, because they are aligned with that period's grid.

*Proof.*
- The chaser does not re-aim inside a period, and every displacement is a fixed multiple of a leg velocity.
- $\lVert(y + p_x,\ p_y)\rVert^2 \ge y^2$ iff $y \le \lVert\mathbf p\rVert^2/(-2p_x)$, with $p_x = \bar u_x - s < 0$.
- The bound $D^\* \le (s+1)/2$ is the bound $F \le (s+1)/2$ of Lemma 4A.7, applied to the admissible velocity $\bar{\mathbf u}$.
- The remaining claims follow as in 4A. ∎

### 4.2 Closest approach for two legs

Let $\mathbf d_j = (\mathbf u_j - s\mathbf e_x)/2$, $\mathbf p_1 = (y, 0) + \mathbf d_1$ and $\mathbf p_2 = \mathbf p_1 + \mathbf d_2$. The closest approach is
$$c(y, U) = \min\big(\operatorname{dist}(0, [(y,0), \mathbf p_1]),\ \operatorname{dist}(0, [\mathbf p_1, \mathbf p_2])\big).$$
Each term is given exactly by the clamped projection of 4A, Prop. 4A.3. This is continuous-time and includes the endpoints.

**How each term depends on $y$** (from Lemma 4B.2, translation):
- $\frac{d}{dy}\operatorname{dist}(0, \text{leg } j) = x_j/\operatorname{dist}$, where $x_j$ is the $x$-coordinate of that leg's closest point. This holds wherever the closest point is unique.
- Leg 1 starts on the positive axis and heads left, so its closest point has $x_1 \ge 0$. **Leg 1's clearance is non-decreasing in $y$**, as in 4A.
- Leg 2 can have its closest point at $x_2 < 0$. Then its clearance **decreases** as $y$ grows. This is the source of the counterexample in §6.2.

### 4.3 Dimension

> **Proposition 4B.4 (two legs in $\mathbb R^d$).**
> - **(i) Bounded speed.** For every $d \ge 2$, the set of pairs (closest approach, end separation) achievable in one two-leg period from separation $y$ is the same as in the plane.
> - **(ii) Exact speed.** For $d \ge 3$, the achievable set **contains** the planar exact-speed one, and is **contained in** the planar bounded-speed one. The first containment is strict in general.

*Proof of (i).*
1. **Leg 1.** By rotation about $\mathbf e_x$, put $\mathbf u_1$ in the plane spanned by $\mathbf e_x$ and $\mathbf e_y$. Leg 1 depends only on $(u_{1x}, \lVert\mathbf u_{1\perp}\rVert)$.
2. **Leg 2 data.** With $\mathbf r_h = \mathbf p_1$ planar, leg 2's distances and $\lVert\mathbf r(1)\rVert$ depend only on $P = \mathbf r_h\cdot\mathbf w$ and $Q = \lVert\mathbf w\rVert^2$, where $\mathbf w = \mathbf u_2 - s\mathbf e_x$ ranges over the ball $\bar B^d((-s, 0, \ldots), 1)$.
3. **The image at fixed $P$.**
   - In the plane: $\mathbf w$ ranges over a chord of the disk, and the image is the set of values of $\lVert\mathbf w\rVert^2$ on that chord. This is an interval, because the chord is connected.
   - In $\mathbb R^d$: the extra coordinates $z$ keep $P$ fixed and add $\lVert z\rVert^2 \le 1 - (x+s)^2 - y^2$. So $Q$ ranges over $[x^2 + y^2,\ 1 - 2sx - s^2]$ for each chord point $(x, y)$.
4. **Comparison.** The upper end $1 - 2sx - s^2$ is linear along the chord, so its maximum is at a chord end. There it equals $x^2 + y^2$, because chord ends lie on the circle. The minimum is a planar value. Hence the $d$-dimensional image lies inside the planar interval. ∎

*Proof of (ii).*
- On the sphere, $Q = 1 - 2sx - s^2$ exactly. As $(x, y)$ ranges over the chord (with $z \ne 0$ in the interior), this fills an interval.
- In the planar exact-speed model only the two chord ends are available.
- The upper containment follows from step 4 of (i). ∎

**Consequences.**
- Every two-leg bound below holds verbatim for $d \ge 2$ in the bounded-speed model.
- In the exact-speed model, upper bounds on clearance come from the planar bounded-speed analysis. Lower bounds (orbits) come from unit-speed planar constructions.
- For $m \ge 3$ no reduction is proven. The path depends on the Gram matrix of $(\mathbf r_0, \mathbf w_1, \ldots, \mathbf w_m)$, which can have rank 3. A non-planar three-leg path is **not** assumed to have a planar equivalent.

The constructive step of (i) is tested in `test_two_leg_dimension_reduction_bounded_speed` (500 random 3D leg-2 velocities).

---

## 5. Level and up-step clearance; Theorem 8

**Definitions.** For aligned $m$-leg periods, with $c$ the closest approach over the period:
$$G_{\rm lev}(m) = \sup\{c(y,U)^2 : \lVert\mathbf r(1)\rVert = y\}, \qquad G_{\rm up}(m) = \sup\{c(y,U)^2 : \lVert\mathbf r(1)\rVert \ge y\},$$
with $y > 0$ and $U \in \bar B^m$, so $G_{\rm lev} \le G_{\rm up}$. This $G_{\rm up}(2)$ is the brief's $G_2(s)$. For $m = 1$, Lemma 4A.7 gives $G_{\rm up}(1) = G_{\rm lev}(1) = G$.

> **Lemma 4B.5 (attainment).** Both suprema are attained.

*Proof.*
- Up-steps need $y \le D^\* \le (s+1)/2$ (Lemma 4B.2), and $c \le y$.
- So both suprema are taken over closed subsets of the compact set $[0, (s+1)/2] \times \bar B^m$, on which $c$ is continuous.
- Points with $y = 0$ give $c = 0$ and do not affect the supremum. ∎

**Attained does not mean closing.** For $m = 2$, the numerics locate the $G_{\rm up}$ optimiser at a closing period (§6.3), but that is not proven. §6.2 shows that, for a *fixed* control, the best up-step need not be the closing one.

> **Theorem 8 (aligned $m$-decision game; any $m \ge 1$).** In $\mathcal R_m$, against PP, with $\varepsilon = 1/\alpha_C$:
> - **(a) Escape.** If $\varepsilon < \sqrt{G_{\rm lev}(m)}$, a closing period $(y_L, U_L)$ with clearance $> \varepsilon$ exists. Replaying $U_L$ in each period's frame from separation $y_L$ never gets captured. The relative state and both clocks recur exactly.
> - **(b) Capture.** If $\varepsilon > \sqrt{G_{\rm up}(m)}$, every safe period strictly decreases $D$. There is a $\delta > 0$ such that every safe period starting with $D \le s+1$ decreases $D$ by at least $\delta$. PP captures every runner in $\mathcal R_m$ from separation $D_0$ within $\lceil (D_0 - \varepsilon)/\min(\delta, s-1)\rceil + 1$ periods.
> - **(c) At the threshold.** If $\varepsilon = \sqrt{G_{\rm up}(m)}$, every surviving run has strictly decreasing $D_k$, converging to the start $L$ of a closing period whose clearance equals $\sqrt{G_{\rm up}}$. In particular:
>   - if $G_{\rm lev}(m) < G_{\rm up}(m)$, PP also captures every runner at this $\alpha_C$;
>   - in every case, no surviving run is eventually periodic in $D$.
>
> Hence
> $$G_{\rm up}(m)^{-1/2} \le \kappa_{\rm PP}(s;\mathcal R_m,\mathcal I_{\rm all}) \le G_{\rm lev}(m)^{-1/2},$$
> with equality throughout if $G_{\rm up}(m) = G_{\rm lev}(m)$.

*Proof.*

**(a)** This is the recurrence argument of review §4.2, step 5, and `theory/certificates/README.md`:
- PP and the rotated leg schedule are equivariant under rotations and translations;
- both agents decide at every $t_k$;
- the period returns to separation $y_L$.

**(b) Steps go down.** A period with $\lVert\mathbf r(1)\rVert \ge y$ has $c^2 \le G_{\rm up} < \varepsilon^2$, so it is a capture.

**(b) A uniform decrease.**
1. Suppose safe periods $(y_j, U_j)$ with $y_j \in [\varepsilon, s+1]$ had $y_j - \lVert\mathbf r_j(1)\rVert \to 0$.
2. Compactness gives a limit $(y^\circ, U^\circ)$ that is a closing period with $c \ge \varepsilon$.
3. So $c^2 \ge \varepsilon^2 > G_{\rm up} \ge G_{\rm lev}$, a contradiction.

**(b) The period count.** For $D \ge s$, every period has $D' \le D - (s-1)$ (Lemma 4B.2). Each safe period therefore decreases $D$ by at least $\min(\delta, s-1)$ while $D$ stays above $\varepsilon$. This gives the bound.

**(c)**
1. Non-decreasing periods have $c \le \sqrt{G_{\rm up}} = \varepsilon$, so they are captures. Surviving runs therefore strictly decrease.
2. The limit of such a run is a closing period with $c \ge \varepsilon = \sqrt{G_{\rm up}}$. So $G_{\rm lev} = G_{\rm up}$, and $L$ starts an optimal closing period.
3. If $G_{\rm lev} < G_{\rm up}$, no run survives.

**Bracket.** The escape statement (a) holds for every $\alpha_C > G_{\rm lev}^{-1/2}$. The capture statement (b) holds for every $\alpha_C < G_{\rm up}^{-1/2}$. ∎

**Remarks.**
- **For $m = 1$**, Theorem 8 together with Lemma 4A.7 recovers Theorem 6(a)–(c1).
- **The boundary construction of Theorem 6(c2) is not covered.** Survival at the threshold needs the clearance to *gain*, to first order, when starting slightly above the optimal orbit's start.
  - For $m = 1$ this gain came from $c = D\sin\theta_y$ being linear in $D$.
  - For $m \ge 2$ this is open; see §7.
- **The decrement needs compactness.** $\delta$ comes from compactness, not from strict decrease alone, which would not exclude a positive limit (A3).
- **Strict versus non-strict capture.** (b) uses strict safety, $c > \varepsilon$, for the runner. (c) is where the two notions part.

---

## 6. The two-leg game

### 6.1 Theorem 9: rigorous bracket for $m = 2$

**Certificate.** `theory/certificates/two_leg_upper_bound.py` uses the Python standard library only.
- **Search space.** It runs a branch-and-bound over boxes in $(y, a_1, b_1, a_2, b_2) \in [0, (s+1)/2] \times [-1,1] \times [0,1] \times [-1,1]^2$. Here $\mathbf u_j = (a_j, b_j)$, and $b_1 \ge 0$ by reflection.
- **Exactness.** Every decision is made in exact rational arithmetic.
- **When a box is discarded.** A box is discarded only if, at every point of the box, one of the following holds:
  - a speed exceeds 1;
  - the period is strictly decreasing, by interval arithmetic on $\lVert\mathbf r(1)\rVert^2 - y^2$;
  - the closest approach is $\le T$.
- **How the clearance bound is certified.** The test "closest approach $\le T$" is certified by:
  - the distance at the box centre, plus a Lipschitz slack, since a segment's distance from the origin moves by at most the larger displacement of its endpoints;
  - or $c \le y$;
  - or $c \le \lVert\mathbf r(1/2)\rVert$.
- **Conclusion.** If every box is discarded, then $G_{\rm up}(2) \le T^2$.

**Lower bounds** come from the Stage 3 exact orbit certificates `s3-2_m02` and `s2-1_m02`. Both have unit-speed legs and pass the standalone verifier.

> **Theorem 9 (two-leg bracket).** In the aligned two-decision game, in both speed models and every $d \ge 2$:
>
> | $s$ | Certified $\sqrt{G_{\rm up}(2)} \le T$ | Capture for $\alpha_C <$ | Certified closing orbit $\sqrt{G_{\rm lev}(2)} \ge$ | Escape for $\alpha_C >$ | $m = 1$ threshold $\alpha_{\rm sym}$ |
> |---|---|---|---|---|---|
> | 3/2 | 3191/5000 = 0.6382 | 1/T = 1.566907 | 0.6371337 | $\hat\alpha = 1.5695294$ (and every $\alpha_C \ge 981/625$) | 1.6300837 |
> | 2 | 589/1000 = 0.5890 | 1/T = 1.697793 | 0.5879350 | $\hat\alpha = 1.7008682$ (and every $\alpha_C \ge 17009/10000$) | 1.7806141 |
>
> So $\kappa_{\rm PP}(3/2;\mathcal R_2) \in [1.566907,\ 1.569530]$ and $\kappa_{\rm PP}(2;\mathcal R_2) \in [1.697793,\ 1.700869]$.

*Proof.*
- The capture side is Theorem 8(b), with $G_{\rm up}(2) \le T^2$ certified as above. The runs took 2,351,423 and 3,942,403 nodes, and every box was discarded.
- The escape side is Theorem 8(a), with the certified orbits.
- Prop. 4B.4 extends both to $d \ge 2$. In the exact-speed model the orbits are admissible, being unit speed, and the upper bound still applies by Prop. 4B.4(ii). ∎

**Consistency check.** The certificate correctly *fails* to prove any $T$ below a certified closing orbit's clearance (`test_upper_bound_cannot_cut_below_a_certified_orbit`).

**Tighter runs.** A tighter pair of runs is in `results/stage4b/two_leg_upper_bound_tight.txt` if it completed. The bracket above uses only the runs in `results/stage4b/two_leg_upper_bound.txt`.

### 6.2 Counterexample: the Stage 4A mechanism fails for two legs

In 4A, an up-step from $D$ under a fixed action had closest approach $D\sin a$. That is increasing in $D$ up to the action's closing separation, so the closing period was the best up-step for that action. For two legs this is false:

> **Proposition 4B.6 (exact).** Take $s = 3/2$, $\mathbf u_1 = (12/13, -5/13)$ and $\mathbf u_2 = (-7/25, 24/25)$, both of unit speed. Then $D^\*(\bar{\mathbf u}) = 1913/3064 \approx 0.6243$.
> - **Start at $y = 3/10$.** This is a strict up-step: $\lVert\mathbf r(1)\rVert^2 - y^2 \approx 0.7645$. Its closest approach squared is $4635409/172802500$, so the closest approach is 0.16378.
> - **Start at the closing separation $y = D^\*$.** The closest approach squared is $97752769/1013929036900$, so the closest approach is 0.00982.

*Verification.* Exact rational arithmetic, in `experiments/stage4b.py` and `test_pathwise_monotonicity_counterexample_exact`.

**What this refutes.** The *pathwise* statement "for every control, the best non-decreasing start is the closing one". About 25% of random two-leg controls show some non-monotonicity in $y$ on $(0, D^\*]$; this was also seen at $s = 1.2$ and $3$.

**What it does not refute.** The *global* statement $G_{\rm up}(2) = G_{\rm lev}(2)$. The counterexample's controls are far from optimal.

**Mechanism.** Leg 2's closest point lies behind the chaser ($x_2 < 0$) here, so its clearance falls as the start moves out (§4.2).

### 6.3 Numerical optimisation (not certified)

The search used SLSQP from 300 random starts over $(y, \mathbf u_1, \mathbf u_2)$, with the closing constraint either as an equality (level) or an inequality (up-step). The results are in `results/stage4b/two_leg.txt`.

| $s$ | Best level $c$ | Best up-step $c$ | Optimiser | Leg clearances | Leg-2 closest point $x$ |
|---|---|---|---|---|---|
| 3/2 | 0.6371337 | 0.6371337 (it is the level one) | $y = 1.04267$, both legs at unit speed | 0.650644 / **0.637134** | +0.3296 |
| 2 | 0.5879350 | 0.5879350 (it is the level one) | $y = 1.25717$, both legs at unit speed | 0.606636 / **0.587935** | +0.2193 |

**Agreement with earlier results.**
- The values agree with the Stage 3 certified $\hat\alpha(s,2)$ to 7 digits.
- A $721^2$ grid over full-speed headings gives the same values.
- At the optimum the binding leg has its closest point *in front of* the chaser ($x > 0$). So along the optimal control the clearance increases with $y$ up to the closing value. The up-step constraint is active, as in 4A, and the counterexample's mechanism does not operate there.

**Engine replay of the certified orbits.** Each certified two-leg orbit was run, with the runner deciding twice per period:

| $\alpha_C$ | Result |
|---|---|
| $1.001\,\alpha_c$ | No capture in 200 periods. |
| $0.999\,\alpha_c$ | Captured at 0.55 periods, during leg 2. |

> **Conjecture 4B.1.** $G_{\rm up}(2) = G_{\rm lev}(2)$ for every $s > 1$, attained only by closing periods. Equivalently $\kappa_{\rm PP}(s;\mathcal R_2) = G_{\rm lev}(2)^{-1/2}$.
>
> **Status.** Numerically supported at $s = 3/2$ and $2$ (7 digits), and rigorously true to within $1.1\times10^{-3}$ in clearance (Theorem 9). Not proven.

---

## 7. Is periodic escape optimal?

**$m = 2$, away from the threshold.**
- By Theorem 8, if Conjecture 4B.1 holds, then for $\alpha_C \ne G_{\rm lev}^{-1/2}$ a surviving initial state exists iff a period-1 (closing) orbit survives.
- Unconditionally, this is proven outside the interval in Theorem 9. Below it every runner is captured; above it a closing orbit survives.
- Inside that interval (width about 0.003), it is not known whether some non-periodic run survives where no closing orbit does.

**Increasing separation within a period is not advantageous at the global optimum** (numerically), even though for a fixed control it can be (§6.2).

**At the threshold**, assuming 4B.1:
- **Proven.** Theorem 8(c): every surviving run strictly decreases to an optimal orbit's start, so no eventually-periodic run survives.
- **Not settled.** Whether such a run exists. Theorem 6(c2)'s construction needs the clearance to increase to first order with the start separation, using controls near the optimal ones.
- **The obstacle, concretely.** For $m = 1$ the gain came from a closed form. For $m = 2$:
  - the clearance near the optimum is the *minimum* of the two legs' clearances;
  - the optimal start is pinned by the closing constraint;
  - the needed one-sided derivative depends on how the optimal controls move with $y$.

  A computation along these lines is the natural first step of Stage 4C.

---

## 8. Generalising to arbitrary $m$

**What extends unchanged, for all $m$:**
- nesting along divisibility (Lemma 4B.1);
- reduction of the state to $D$ (Lemma 4B.2);
- attainment of both suprema (Lemma 4B.5);
- Theorem 8 in full.

So **for every $m$ the problem reduces to one question: is $G_{\rm up}(m) = G_{\rm lev}(m)$?** That is, can the best non-decreasing period always be taken to be closing?

**What does not extend:**
1. **The pathwise mechanism.** Monotonicity of clearance in $y$ along a fixed control fails already at $m = 2$ (Prop. 4B.6). Any proof of $G_{\rm up} = G_{\rm lev}$ must be global, comparing different controls. This is the essential new difficulty, and it does not shrink as $m$ grows.
2. **The exhaustive certificate's cost.**
   - The parameter space has dimension $2m + 1$. At $m = 2$, tolerance $10^{-3}$ needed about $3\times10^6$ boxes.
   - First-order bounds in dimension 9 ($m = 4$) are out of reach. Going further would need second-order bounds, or symmetry reductions such as the optimal orbits' reflection symmetry. Neither is proven to be without loss of generality.
3. **Dimension.** The planar reduction is proven only for $m \le 2$ (Prop. 4B.4).

**Comparison with the certified $m = 4, 8, 16$ orbits.**
- They give upper bounds only: $\kappa_{\rm PP}(s;\mathcal R_m) \le \hat\alpha(s,m)$. For example, 1.5595, 1.5474 and 1.5396 at $s = 3/2$.
- These need not be optimal, and the Stage 3 optimiser was not converged in $m$.
- The only lower bound for $m \ge 4$ is Theorem 1's $2s/(1+s)$ (1.2 at $s = 3/2$), which holds for every runner class. So for $m \ge 4$ the gap is still about 0.34 at $s = 3/2$, against about 0.003 for $m = 2$.
- The nesting lemma makes $\kappa(\mathcal R_m)$ non-increasing along $1, 2, 4, 8, 16$. The certified upper bounds are consistent with this.

---

## 9. Literature

**Search.** One targeted search was run: evaders updating more often than the pursuer, multirate sampled pursuit, capture radius. It found nothing beyond the sources already reviewed. The closest is still Aleem–Nowzari–Pappas, which has a self-triggered pursuer and a continuous-time evader, and no evader decision schedule.

**Status.** Theorems 8 and 9 and Prop. 4B.4–4B.6 are **Potentially distinct**, with the coverage limits of `theory/literature_review.md` §3 and 4A §8. Alonso–Goldstein–Reingold is still unread.

**Not new.** The branch-and-bound certificate method is standard computer-assisted proof practice, and nothing about it is claimed.

---

## 10. Open questions and the next problem

1. **Conjecture 4B.1** ($G_{\rm up}(2) = G_{\rm lev}(2)$) needs a global proof. Two routes:
   - **Analytic:** reduce to closing periods by a variational argument at the constrained optimum, together with an exclusion of other local maxima.
   - **Computational:** a second-order certificate tight enough to isolate the optimum, combined with a local uniqueness argument near it. This would give *equality*, not just a bracket.
2. **Boundary survival for $m = 2$.** Does the analogue of Theorem 6(c2) hold? This is a first-order sensitivity computation at the optimal orbit (§7).
3. **$m \ge 3$.** The planar reduction, and any lower bound on $\kappa(\mathcal R_m)$ better than $2s/(1+s)$.

**Most promising next problem.** Prove Conjecture 4B.1 by showing that **at any non-closing local maximiser of clearance among non-decreasing two-leg periods, the closing constraint can be tightened without loss.**
- *Concretely:* characterise the KKT points of the five-parameter problem, using which legs and speed bounds are active, and show that none has $\lVert\mathbf r(1)\rVert > y$.
- *Why this is the right target:*
  - it would turn Theorem 9's numerical bracket into an exact threshold for $\mathcal R_2$;
  - the active-set analysis is finite;
  - the same method is the only visible route to general $m$, since the exhaustive certificate does not scale.

---

## Appendix: reproduction

| What | Command | Output |
|---|---|---|
| Tests | `python -m pytest tests/test_two_leg.py` | — |
| Optimisation, counterexample, engine replay | `python experiments/stage4b.py` | `results/stage4b/two_leg.txt`, `two_leg_optima.json` |
| Upper-bound certificate at $s = 3/2$ (about 1–2 CPU-minutes) | `python theory/certificates/two_leg_upper_bound.py 3/2 3191/5000` | `results/stage4b/two_leg_upper_bound.txt` |
| Upper-bound certificate at $s = 2$ (about 2 CPU-minutes) | `python theory/certificates/two_leg_upper_bound.py 2 589/1000` | same file |
| Orbit certificates (lower side) | `python theory/certificates/verify.py` | stdout |
