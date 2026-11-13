# How to Win a Game of Tag — Stage 4A: Viability Analysis of the Aligned One-Decision Game

*2026-11-12. This document is meant to be read on its own; it builds on `theory/stage3_mathematical_review.md` (the review).*

- Notation follows the review. Its Theorems 1–5 and Lemmas M and S are cited by those names.
- New results are numbered 4A.x, plus **Theorems 6 and 7**.

## Contents

1. Summary
2. The game $\mathcal G_1$ and its reduction to the separation $D$
3. Exact one-period geometry
4. The viability formulation
5. Main results: Theorems 6 and 7
6. Numerical experiments and validation
7. Agreement with existing theorems
8. Literature status
9. Open questions and the next problem

Appendix: reproduction.

---

## 1. Summary

**The game.** In the game $\mathcal G_1$:
- The chaser plays full-speed pure pursuit (PP) with period $\tau_C$.
- The runner decides **exactly once per chaser period, at the chaser's decision instants**.
- Capture is the closed $\varepsilon$-ball, checked continuously.

In this game the relative path over one period is a single straight segment. The state at decision times reduces exactly to the separation $D$.

**Proven.**

1. **Exact one-period map (Prop. 4A.5).**
   - The full-speed runner actions are parametrised by the separation $y$ they would hold fixed.
   - Action $y$ sends $D$ to $T_y(D) = \sqrt{D^2 - (s^2-1)(D-y)/(s-y)}$.
   - Its closest approach is $D\sin\theta_y$, or $T_y(D)$ when $D \ge 2y$.
   - Every safe end-separation either is reached by a full-speed action, or is reached while still closing in (a "plateau" interval in closed form).
2. **Up-step bound (Lemma 4A.7).** Call a period an **up-step** if it does not decrease $D$.
   - The closest approach during an up-step from $D$ is at most $\Psi(D)$.
   - $\Psi(D) = D/s$ for $D \le s/2$, $\Psi(D) = \sqrt{g(D)}$ for $s/2 \le D \le y^\*$, and $\Psi(D) \le \sqrt G$ always.
   - So up-steps are never safer than the best period-1 orbit.
3. **Theorem 6 — exact threshold for $\mathcal G_1$.** Here $\alpha_{\rm sym}(s) = G(s)^{-1/2}$ is the Theorem 2 threshold.
   - **(a)** For $\alpha_C > \alpha_{\rm sym}(s)$, indefinite evasion exists (Theorem 2).
   - **(b)** For $\alpha_C < \alpha_{\rm sym}(s)$, PP captures **every** runner of $\mathcal G_1$ from **every** initial state, within a finite number of periods bounded on bounded sets.
   - **(c)** At $\alpha_C = \alpha_{\rm sym}(s)$, the outcome is subtler:
     - Indefinite evasion **is possible**, but only by **non-periodic** strategies.
     - Along every surviving run, $D_k$ decreases strictly to $y^\*$.
     - Every runner whose separation sequence is eventually periodic, the period-1 orbit included, is captured.
   - Hence $\kappa_{\rm PP}(s;\mathcal R^{\rm al}_1,\mathcal I_{\rm all}) = \alpha_{\rm sym}(s)$ **exactly**. PP's guarantee set is the **open** interval $(0, \alpha_{\rm sym}(s))$.
   - The capture–escape gap for this runner class is **closed**. For example, the proven guarantee rises from $2s/(1+s) = 1.2$ to $\alpha_{\rm sym} = 1.6301$ at $s = 1.5$.
4. **Finite versus infinite horizon.**
   - **At the threshold.** At $\alpha_C = \alpha_{\rm sym}$, the point $y^\*$ survives every finite horizon but has no infinite survival: $y^\* \in \bigcap_n\mathcal V_n \setminus \mathcal V_\infty^{\rm true}$.
   - **Theorem 7.** For $\alpha_{\rm sym} < \alpha_C \le 2$:
     - the kernel below the period-1 set's upper end is exactly the open period-1 set $(y_-, y_+)$;
     - for $\alpha_C < 2$, its lower end $y_-$ again survives every finite horizon but not forever.
   - So $\bigcap_n \mathcal V_n$ and the true survival set differ **generically**. The difference is caused by the strict (closed-ball) capture rule.

**Answers to the Stage 4A objectives.**

| # | Objective | Result |
|---|---|---|
| 1 | Necessary and sufficient condition for indefinite evasion in $\mathcal G_1$ | $\alpha_C \ge \alpha_{\rm sym}(s)$: some initial state survives. **Proven.** |
| 2 | Exact viability kernel | On $(0, y_+)$, proven for $\alpha_C \in (\alpha_{\rm sym}, 2]$. Above $y_+$: conjectured, with numerical support. |
| 3 | Optimality of periodic strategies | Periodic strategies are optimal for $\alpha_C \ne \alpha_{\rm sym}$, and **not** optimal at $\alpha_C = \alpha_{\rm sym}$. **Proven.** |
| 4 | Stronger PP capture bound | For $\mathcal R^{\rm al}_1$: capture for all $\alpha_C < \alpha_{\rm sym}(s)$. **Proven.** For general runners, Theorem 1 is unchanged. |
| 5 | Non-periodic strategy outperforming periodic evasion | Yes, but **only at the single parameter value** $\alpha_C = \alpha_{\rm sym}$. **Proven.** |

**Numerical support.**
- A grid prototype for $s \in \{1.5, 2\}$ agrees with all of the above.
- It also shows that grid estimates of the kernel **do not converge reliably** near the threshold. This is the predicted consequence of clearance margins that vanish along the boundary chain.

**Literature.** None of the material overlaps found so far is resolved; see §8. **Nothing is claimed as novel.**
- The closest prior construction is a circling evasion of a greedy discrete-time pursuer (Bopardikar–Bullo–Hespanha, Prop. III.4), in an equal-speed, alternating-move, point-capture model.
- Alonso–Goldstein–Reingold (1992) could not be read: bot protection blocked the full text.

---

## 2. The game $\mathcal G_1$ and its reduction to the separation $D$

### 2.1 Game

$\mathcal G_1$ is the model of review §2.1, with these restrictions:
- **Space.** $\mathbb R^d$, $d \ge 2$, unbounded and without obstacles.
- **Speeds.** $s = R_C/R_E > 1$.
- **Chaser.** PP with period $\tau_C$ and phase 0.
- **Runner.** Period $\tau_E = \tau_C$ and phase 0, so both agents decide at $t_k = k\tau_C$ and neither is pre-committed.
- **Speed model.** Bounded speed, $\|\mathbf v_E\| \le R_E$. The exact-speed variant is covered where stated.
- **Capture.** The closed ball of radius $\varepsilon$, checked continuously.

**Units.** $R_E = \tau_C = 1$. Then $\rho = 1$, $L = s$ and $\varepsilon = 1/\alpha_C$.

**Notation.** Write $\mathbf r_k = \mathbf x_E(t_k) - \mathbf x_C(t_k)$, $D_k = \|\mathbf r_k\|$ and $\hat{\mathbf u}_k = \mathbf r_k/D_k$.

> **Lemma 4A.1 (straight segment).** On $[t_k, t_{k+1}]$, $\mathbf r(t) = \mathbf r_k + (t - t_k)(\mathbf v_E - s\hat{\mathbf u}_k)$. The closest approach during the period is the Euclidean distance from $0$ to the segment $[\mathbf r_k, \mathbf r_{k+1}]$.

*Proof.* Both velocities are constant on the period. The distance from 0 to an affine segment is attained on the closed segment, endpoints included. ∎

### 2.2 Reduction

> **Proposition 4A.2 (reduction to $D$).** In $\mathcal G_1$:
> - **(i) Only $D$ matters.** Whether the runner can avoid capture forever (or for $n$ periods) from relative position $\mathbf r_0$ depends only on $D_0 = \|\mathbf r_0\|$.
> - **(ii) Feedback is unnecessary.** Such a strategy exists iff there is a sequence of runner velocities $(\mathbf v_k)$ with every period safe. Information and feedback add nothing.
> - **(iii) The planar problem suffices.** Survival from $D$ in $\mathbb R^d$, $d \ge 2$, is equivalent to survival from $D$ in the plane.

*Proof.*

**(i)** Let $\Phi$ be an orientation-preserving isometry of $\mathbb R^d$ with $\Phi(\mathbf r_0) = \mathbf r_0'$. Then:
- PP's velocity is $s\hat{\mathbf u}$, a function of the relative position that commutes with $\Phi$.
- The runner's admissible set, the ball of radius $R_E$, is $\Phi$-invariant.
- The capture set is $\Phi$-invariant.

So $\Phi$ maps safe runs from $\mathbf r_0$ onto safe runs from $\mathbf r_0'$. Translations act trivially, because only relative positions enter.

**(ii)** PP is deterministic. Each period starts with a fresh decision by both agents, so nothing committed earlier carries over. The run is therefore determined by $\mathbf r_0$ and the runner's velocity sequence. Any strategy, with any information, produces one such sequence, and conversely an open-loop sequence is admissible.

**(iii)** On each period, $\mathbf r$ moves in the plane spanned by $\hat{\mathbf u}_k$ and $\mathbf v_E$. Both the period's closest approach and $D_{k+1}$ depend only on:
- the component of $\mathbf v_E$ along $\hat{\mathbf u}_k$;
- the norm of its orthogonal component.

So every $d$-dimensional action has a planar equivalent and vice versa. ∎

**Reflections.** PP also commutes with reflections. So the side of the line of sight on which the runner passes is irrelevant; below we take $v_y \ge 0$.

**What breaks the reduction.**

| Change | Effect |
|---|---|
| Unaligned clocks, or a runner deciding at other times | At chaser decisions the runner may be mid-commitment. The state then also contains its committed velocity, relative to the line of sight, and its phase: at least 3 dimensions. |
| Runner with $m > 1$ aligned decisions per period | The state at chaser decisions **is still $D$**, but the period's relative path is piecewise linear. The one-period relation changes, and Lemma 4A.7 must be re-derived. This is the Stage 4B question (§9). |
| A chaser that is not a function of the current relative position only (memory, committed-velocity extrapolation, randomisation) | The state grows. Equivariance alone still holds for any feedback law of the relative position, e.g. braking or the hybrid chaser $H$. |
| A pre-committed first period ($\varphi_C > 0$ or $\varphi_E > 0$) | Only the first period differs. The reduction applies from $t_1$ on. |
| Bounded arenas, obstacles, or speed or clock rules depending on position | Translation and rotation invariance are lost. |
| Exact-speed model | The reduction is unchanged, but the action set becomes the unit circle. Proposition 4A.5 (the plateau part) changes; Theorems 6 and 7 do not (see the remarks after them). |
| $d = 1$ | The runner cannot sidestep: PP captures whenever capture is possible at all. Excluded. |

---

## 3. Exact one-period geometry

### 3.1 Coordinates

Work in the frame of one period: $\mathbf r_k = (D, 0)$, chaser velocity $(s, 0)$, runner velocity $\mathbf v$ with $\|\mathbf v\| \le 1$. Define:
- the relative velocity $\mathbf w = \mathbf v - (s, 0)$;
- $q = -w_x = s - v_x \in [s-1, s+1]$, so $q > 0$;
- $m = \|\mathbf w\|^2$.

> **Proposition 4A.3 (one period).** With the definitions above:
> - **End separation:** $D'^2 = \|\mathbf r_{k+1}\|^2 = D^2 - 2Dq + m$.
> - **Closest approach:** the unconstrained minimiser is $t^\* = Dq/m > 0$.
>   - If $Dq \ge m$: the closest approach is $D'$, attained at the end.
>   - If $Dq < m$: it is $D|w_y|/\sqrt m = D\sin a$, where $a \in [0, \pi/2)$ is the angle between $\mathbf w$ and $-\hat{\mathbf x}$.
> - **Thales disk.** $Dq \ge m$ iff the end point lies in the closed disk $\mathrm{Th}_D$ with diameter $[0, (D, 0)]$: the end point is reached "while still closing in".
> - **Fixed-point separation.** Define $F(\mathbf v) = m/(2q)$. Then $D' \gtreqless D$ iff $D \lesseqgtr F(\mathbf v)$.

*Proof.*
- The first three facts are the quadratic $\|(D,0) + t\mathbf w\|^2$ minimised over $t \in [0,1]$.
- For the Thales disk: the end point $P$ satisfies $P \in \mathrm{Th}_D$ iff $\|P\|^2 \le D P_x$. Here $P_x = D - q$ and $\|P\|^2 = D^2 - 2Dq + m$, so the condition reads $m \le Dq$.
- The last fact is the sign of $D'^2 - D^2 = m - 2Dq$. ∎

### 3.2 Full-speed actions

> **Lemma 4A.4 (full-speed actions).**
> - **Parametrisation.** On the unit semicircle $\{\|\mathbf v\| = 1,\ v_y \ge 0\}$, the map $\mathbf v \mapsto F(\mathbf v)$ is a strictly increasing bijection, in the heading angle, onto $Y_s = [(s-1)/2,\ (s+1)/2]$.
> - **Formulas.** Writing $y = F(\mathbf v)$:
>   $$q_y = \frac{s^2-1}{2(s-y)}, \quad m_y = 2q_y y, \quad \cos^2\theta_y = \frac{s^2-1}{4y(s-y)},$$
>   where $\theta_y$ is the angle $a$ of Proposition 4A.3.
> - **The one-period map of action $y$:**
>   $$T_y(D)^2 = D^2 - \frac{(s^2-1)(D-y)}{s-y}, \qquad C_y(D) = \begin{cases} D\sin\theta_y, & D < 2y,\\ T_y(D), & D \ge 2y.\end{cases}$$
> - **Its fixed point.** $T_y(y) = y$, with closest approach $y\sin\theta_y = \sqrt{g(y)}$. This is Theorem 2's symmetric pass.

*Proof.*
- With $c = \cos\psi$: $q = s - c$ and $m = 1 + s^2 - 2sc$. So $F = (1 + s^2 - 2sc)/(2(s-c))$, and
  $$\frac{dF}{dc} = \frac{1 - s^2}{2(s-c)^2} < 0.$$
- The end values are $F(c = 1) = (s-1)/2$ and $F(c = -1) = (s+1)/2$.
- Eliminating $c$ gives $q_y$ and $m_y$, and $\cos^2\theta_y = q_y^2/m_y$.
- The formulas for $T_y$ and $C_y$ are Proposition 4A.3 with $m = 2q_y y$; the condition $Dq < m$ reads $D < 2y$. ∎

$g(y) = y^2\sin^2\theta_y$ is the review's pass profile. Its zeros $(s \pm 1)/2$ are the ends of $Y_s$, the straight-flee and straight-toward headings.

### 3.3 Exact safe reachable set

Write $K_D = \bar B((D - s, 0), 1)$ for the set of reachable end points.

> **Proposition 4A.5 (exact safe reachable set; bounded-speed model).** For $D > \varepsilon$, let
> $$\mathcal R(D) = \{D' : \text{some admissible } \mathbf v \text{ reaches } D' \text{ with closest approach} > \varepsilon\}.$$
> Then
> $$\mathcal R(D) = \Big(\{\|P\| : P \in K_D \cap \mathrm{Th}_D\} \;\cup\; \{T_y(D) : y \in Y_s,\ C_y(D) > \varepsilon\}\Big) \cap (\varepsilon, \infty).$$
> - **The plateau set.** The first set is a closed interval $[n_-(D), n_+(D)]$, possibly empty: it is the norm image of the intersection of two disks. Its end points are among:
>   - the points of each disk nearest to and farthest from the origin that lie in the other disk;
>   - the two circles' intersection points;
>   - the origin, if it lies in $K_D$.
> - **When $D \ge s$:** $\mathcal R(D) = [\max(0, D - s - 1),\ D - s + 1] \cap (\varepsilon, \infty)$.

*Proof.*

**"⊇".** Plateau points have closest approach equal to $D' > \varepsilon$. Full-speed points are safe by definition.

**"⊆".** Take an admissible $\mathbf v$ with end point $P$, $\|P\| = D'$, and closest approach $c > \varepsilon$.
- If $P \in \mathrm{Th}_D$, then $D'$ is in the plateau set.
- Otherwise $c$ is the distance from 0 to the line through $(D,0)$ and $P$:
  $$h(x)^2 = \frac{D^2 D'^2 (1 - x^2)}{D^2 + D'^2 - 2DD'x},$$
  where $x = \cos\varphi$ and $\varphi$ is the polar angle of $P$. Differentiating,
  $$\frac{d(h^2)}{dx} \propto (Dx - D')(D'x - D).$$

*Case $D' < D$.* $P \notin \mathrm{Th}_D$ means $x < D'/D$. There both factors are negative, so $h$ increases with $x$.
- Among the points of $K_D$ at radius $D'$ outside $\mathrm{Th}_D$, the clearance is largest at the largest admissible $x$.
- If some point of $K_D$ at radius $D'$ lies in $\mathrm{Th}_D$, then $D'$ is already in the plateau set.
- Otherwise the largest admissible $x$ lies on $\partial K_D$, i.e. at full speed, with clearance $\ge c$. So $D' = T_y(D)$ with $C_y(D) \ge c > \varepsilon$.

*Case $D' \ge D$.* $h^2$ peaks at $x = D/D'$, where the angle at $(D,0)$ is a right angle. That would need $w_x = 0$, which is impossible since $q \ge s - 1 > 0$. So the admissible $x$ lie on the increasing side, and again the maximum is on $\partial K_D$.

*The case $D \ge s$.* Every reachable radius in $[D-s-1, D-s+1]$ is attained by a radial point $(D - s + u, 0)$ with $u \in [-1, 1]$, and such a point lies in $\mathrm{Th}_D$.

*The plateau set.* $K_D \cap \mathrm{Th}_D$ is convex and compact, so its norm image is an interval. On a circle, the norm has exactly one local maximum and one local minimum (the points along the line through the origin), which gives the candidate list. ∎

**Structure.**
- **Interval property.** $\mathcal R(D)$ was an interval in all 643 random cases checked: $s \in \{1.5, 2\}$, $D \in (0.2, 2s + 1)$, $\varepsilon \in (0.2, 0.9)$, in `test_reachable_set_formula` and the Stage 4A check script. This is **not proven** and is not used below.
- **Openness.** $\mathcal R(D)$ is relatively open at any end where the safety constraint binds, because safety is a strict inequality.
- **Continuity.** The maps $(D, \mathbf v) \mapsto (\text{closest approach}, D')$ are continuous. This is the only continuity used below.

**Parameter dependence.**
- Only $s$ and $\varepsilon = 1/\alpha_C$ enter.
- $\mathcal R_\varepsilon(D)$ is decreasing in $\varepsilon$ (nested).
- The full-speed part does not depend on $\varepsilon$ except through the safety test.

### 3.4 Fixed-point profile and the up-step bound

> **Lemma 4A.6 (fixed-point profile).**
> - **(i)** $g$ has a unique maximiser $y^\* \in (s/2, (s+1)/2)$ on $Y_s$: the larger root of $8y(s-y)^2 = s(s^2-1)$. Moreover, $g$ is strictly increasing on $[(s-1)/2, y^\*]$, and $g(s/2) = 1/4$.
> - **(ii)** For an admissible $\mathbf v$ with $w_y \ne 0$, define its level-step clearance $f(\mathbf v) := F(\mathbf v)^2 w_y^2/m$, the closest approach squared of the step $F \to F$. Then $f(\mathbf v) \le G := g(y^\*)$, with equality iff $\|\mathbf v\| = 1$ and $F(\mathbf v) = y^\*$.

*Proof.*

**(i) Critical points.**
- $g'(y) = 2y - s(s^2-1)/(4(s-y)^2)$, so the critical points on $(0, s)$ solve $h(y) := 8y(s-y)^2 = s(s^2-1)$.
- $h$ increases on $(0, s/3)$ and decreases on $(s/3, s)$. Its maximum is $h(s/3) = 32s^3/27 > s(s^2-1)$, so there are exactly two roots, $r_1 < s/3 < r_2$.
- Since $g'(0) < 0$, $r_1$ is a local minimum and $r_2$ a local maximum.

**(i) The maximiser on $Y_s$.**
- On $Y_s$, $g \ge 0$, with zeros only at the ends, because $g(y) = y\,(4y(s-y) - (s^2-1))/(4(s-y))$. So $g$ has an interior maximum on $Y_s$.
- It must be $r_2 =: y^\*$. If $r_1$ lay inside $Y_s$, a second interior local maximum would be needed, and there is none.
- $g(s/2) = 1/4$ directly. Also $h(s/2) = s^3 > s(s^2-1)$ gives $s/2 < y^\*$, and since $r_1 < s/3$, $g$ is strictly increasing on $[(s-1)/2, y^\*]$.

**(ii)** Write $f = mw_y^2/(4q^2) = w_y^2/4 + w_y^4/(4q^2)$. At fixed $v_x$ (fixed $q$), $f$ strictly increases with $|w_y| = |v_y|$. So the maximum over the disk is attained only on the unit circle, where $f = g(F(\mathbf v))$ by Lemma 4A.4. Then apply (i). ∎

> **Lemma 4A.7 (up-step bound).** Suppose a step from $D$ under an admissible $\mathbf v$ has $D' \ge D$. Then:
> - $D \le F(\mathbf v) \le (s+1)/2$;
> - its closest approach is at most
>   $$\Psi(D) := \begin{cases} D/s, & D \le s/2,\\ \sqrt{g(D)}, & s/2 \le D \le (s+1)/2;\end{cases}$$
> - $\Psi \le \sqrt G$, and $\Psi$ is continuous and strictly increasing on $(0, y^\*]$.
>
> In particular, every up-step or level step has closest approach $\le \sqrt G$, with equality only for the level step at $y^\*$ under the action $y^\*$.

*Proof.*

**The closest approach.** By Proposition 4A.3, $D' \ge D$ means $D \le F$. Then $Dq \le m/2 < m$, so the closest approach is $D\sin a$, where $a$ is the direction of $\mathbf w$.

**Reduction to full speed.**
- $\mathbf w$ lies in the disk $\bar B((-s, 0), 1)$. In direction $a$, $\|\mathbf w\|$ is at most the far chord point $\rho_2(a)$, which corresponds to full speed.
- $F = \|\mathbf w\|/(2\cos a)$. So the full-speed action in the same direction has $y(a) := \rho_2(a)/(2\cos a) \ge F \ge D$, and $\theta_{y(a)} = a$.
- Hence the closest approach is $D\sin\theta_y$ for some $y \in [D, (s+1)/2]$. This also gives $F \le (s+1)/2$.

**Maximising over $y$.** $\sin^2\theta_y = 1 - (s^2-1)/(4y(s-y))$ increases on $y < s/2$ and decreases on $y > s/2$. Its maximum value is $1/s^2$, at $y = s/2$. So $\max_{y \in [D, (s+1)/2]} D\sin\theta_y = \Psi(D)$.

**Properties of $\Psi$.**
- It is continuous at $s/2$, since $\sqrt{g(s/2)} = 1/2$.
- It is strictly increasing on $(0, y^\*]$ by Lemma 4A.6(i).
- $\Psi \le \sqrt G$ since $\sqrt{g} \le \sqrt G$ and $D/s \le 1/2 \le \sqrt G$ (Lemma S).

**Equality case.** It follows from Lemma 4A.6(ii). ∎

**Exact-speed model.** Lemmas 4A.6(ii) and 4A.7 restrict to the unit circle unchanged.

---

## 4. The viability formulation

**Survival sets.** Let $\mathcal R = \mathcal R_\varepsilon$ be the strict-safety relation of Proposition 4A.5, and $\bar{\mathcal R}$ the same relation with closest approach $\ge \varepsilon$. Define
$$\mathcal V_0 = (\varepsilon, \infty), \qquad \mathcal V_{n+1} = \{D \in \mathcal V_0 : \mathcal R(D) \cap \mathcal V_n \ne \varnothing\},$$
and $\bar{\mathcal V}_n$ likewise with $\bar{\mathcal R}$.
- By induction, the sequence $\mathcal V_n$ is decreasing.
- $\mathcal V_n$ is exactly the set of separations from which the runner can survive $n$ full periods.

**Three different sets.**
- $\mathcal V_\infty := \bigcap_n \mathcal V_n$: finite-horizon survival for every $n$.
- $\mathcal K_\infty := \{D : \exists$ an infinite chain $D = D_0 \to D_1 \to \cdots$ with $D_{k+1} \in \mathcal R(D_k)\}$: true indefinite survival, i.e. a single admissible infinite policy, by Prop. 4A.2.
- $\bar{\mathcal K}_\infty$: the same with $\bar{\mathcal R}$.

$\mathcal K_\infty$ is the largest viable set, the **viability kernel**. Clearly $\mathcal K_\infty \subseteq \mathcal V_\infty \subseteq \bar{\mathcal V}_\infty$.

**Boundedness.** Since $D' \le |D - s| + 1$, every chain enters $[0, s+1]$ and stays there.
- If $D > s + 1$, then $D' \le D - (s-1)$.
- If $D \le s + 1$, then $D' \le s + 1$.

> **Lemma 4A.8 (compactness).** $\bar{\mathcal V}_\infty = \bar{\mathcal K}_\infty$. That is, for the **non-strict** relation, surviving every finite horizon is the same as surviving forever.

*Proof.*
1. Let $D \in \bar{\mathcal V}_n$ for all $n$. Choose an $n$-chain with actions $(\mathbf v^n_k)_{k<n}$.
2. All states lie in $[0, \max(D, s+1)]$, and all actions lie in the unit disk.
3. A diagonal subsequence gives $D^n_k \to D_k$ and $\mathbf v^n_k \to \mathbf v_k$ for every $k$.
4. By continuity, $D_{k+1}$ is the end separation of $(D_k, \mathbf v_k)$, and its closest approach is $\ge \varepsilon$ (a limit of numbers $> \varepsilon$). ∎

**Why the strict relation behaves differently.** The same argument for the **strict** relation yields only a $\bar{\mathcal R}$-chain: limits of strict inequalities are not strict. So for strict safety, which is the model's closed-ball capture, $\mathcal V_\infty$ can be strictly larger than $\mathcal K_\infty$. Theorems 6(c) and 7(b) show that it is, and say exactly where.

Numerical convergence of $\mathcal V_n$ therefore cannot establish $\mathcal K_\infty$. This is also visible in §6.

---

## 5. Main results

Let $\alpha_{\rm sym}(s) = G(s)^{-1/2}$. When $\varepsilon < \sqrt G$, i.e. $\alpha_C > \alpha_{\rm sym}$, let
$$\mathrm{Fix}_\varepsilon = \{y : g(y) > \varepsilon^2\} = (y_-, y_+),$$
an open interval around $y^\*$ by Lemma 4A.6.

### 5.1 Theorem 6: the exact threshold

> **Theorem 6 (exact threshold of $\mathcal G_1$).** In $\mathcal G_1$, in both speed models and every dimension $d \ge 2$:
> - **(a) Above the threshold.** If $\alpha_C > \alpha_{\rm sym}(s)$, then $\mathrm{Fix}_\varepsilon \subseteq \mathcal K_\infty$. Indefinite evasion is possible.
> - **(b) Below the threshold.** If $\alpha_C < \alpha_{\rm sym}(s)$, then:
>   - every safe step strictly decreases $D$;
>   - there is a $\delta(\alpha_C) > 0$ such that every safe step from $D \le s+1$ decreases $D$ by at least $\delta$;
>   - consequently $\mathcal K_\infty = \mathcal V_\infty = \varnothing$, and PP captures every runner of $\mathcal G_1$ from separation $D_0$ within
>     $$\left\lceil \frac{D_0 - \varepsilon}{\min(\delta, s-1)} \right\rceil + 1 \text{ periods}.$$
> - **(c) At the threshold**, $\alpha_C = \alpha_{\rm sym}(s)$, so $\varepsilon = \sqrt G$:
>   - **(c1)** Every surviving run has $D_k$ strictly decreasing with $D_k \downarrow y^\*$. In particular $\mathcal K_\infty \subseteq (y^\*, \infty)$, and no runner whose separation sequence is eventually periodic survives. The Theorem 2 orbit and every periodic orbit are captured.
>   - **(c2)** There is an $a_0 > 0$ with $(y^\*, y^\* + a_0) \subseteq \mathcal K_\infty$.
>   - **(c3)** $y^\* \in \mathcal V_\infty \setminus \mathcal K_\infty$.
>
> **Consequently:**
> - PP's guarantee set against $\mathcal R^{\rm al}_1$ (review §2.5) is the open interval $(0, \alpha_{\rm sym}(s))$, and $\kappa_{\rm PP}(s;\mathcal R^{\rm al}_1,\mathcal I_{\rm all}) = \alpha_{\rm sym}(s)$.
> - The guarantee **fails at** the threshold.
> - Indefinite evasion is possible from some initial state **iff** $\alpha_C \ge \alpha_{\rm sym}(s)$.

*Proof.*

**(a)** This is Theorem 2: $D = y \in \mathrm{Fix}_\varepsilon$ is a fixed point of action $y$, with closest approach $\sqrt{g(y)} > \varepsilon$.

**(b) Steps go down.** By Lemma 4A.7, an up-step or level step has closest approach $\le \sqrt G < \varepsilon$, so it is a capture. Hence every safe step has $D' < D$.

**(b) A uniform decrease.**
1. Suppose safe steps $(D_j, \mathbf v_j)$ with $D_j \le s + 1$ had $D_j - D'_j \to 0$.
2. A convergent subsequence $(D_j, \mathbf v_j) \to (D^\*, \mathbf v^\*)$ gives a level step at $D^\*$ with closest approach $\ge \varepsilon > \sqrt G$.
3. This contradicts Lemma 4A.7. So such a $\delta(\alpha_C) > 0$ exists.

**(b) The period count.** For $D > s + 1$, every step decreases $D$ by at least $s - 1$. Each safe step thus decreases $D$ by at least $\min(\delta, s-1)$, while $D$ must stay above $\varepsilon$. This gives the bound, and with it $\mathcal V_n = \varnothing$ for large $n$ on bounded sets.

**(c1) Survivors decrease strictly.** Up-steps and level steps have closest approach $\le \sqrt G = \varepsilon$, so they are captures. A surviving chain is therefore strictly decreasing, and converges to some $L \ge \varepsilon$.

**(c1) The limit is $y^\*$.**
1. Pass to a subsequence along which $\mathbf v_k \to \mathbf v^\*$.
2. The limit step is a level step at $L$ with closest approach $\ge \sqrt G$.
3. By the equality case of Lemma 4A.7, $L = y^\*$.
4. A strictly decreasing sequence with limit $y^\*$ stays above $y^\*$, and is not eventually periodic.

**(c2) Setup.** Let $c^2 = \cos^2\theta_{y^\*} \in (0, 1)$. Set
$$\beta = \max\big(0,\ 1 - 1/(4c^2)\big) \in [0, 1), \qquad r = 1 - 2(1-\beta)c^2 \in [\tfrac12, 1).$$
From $D = y^\* + a$, play the action $y = y^\* + \beta a$. For small $a > 0$ this is a valid choice: $y \in \operatorname{int} Y_s$ and $D < 2y$.

**(c2) Clearance.**
$$A(a) := \ln C_y(D) - \tfrac12\ln G = \ln\frac{y^\*+a}{y^\*+\beta a} + \tfrac12\ln\frac{g(y^\*+\beta a)}{G}.$$
$A$ is $C^1$, with $A(0) = 0$ and $A'(0) = (1 - \beta)/y^\* > 0$, using $g'(y^\*) = 0$.

**(c2) Landing.**
$$B(a) := T_y(D) - y^\* = \sqrt{(y^\*+a)^2 - k(y)(1-\beta)a} - y^\*, \qquad k(y) = \frac{s^2-1}{s-y}.$$
$B(0) = 0$ and $B'(0) = 1 - (1-\beta)k(y^\*)/(2y^\*) = r$, since $k(y^\*)/(2y^\*) = 2c^2$.

**(c2) Conclusion.**
- Choose $a_0 > 0$ such that, for every $a \in (0, a_0)$: $A(a) > 0$, $0 < B(a) < a$, $y \in \operatorname{int} Y_s$, and $D < 2y$.
- Then from any $D_0 \in (y^\*, y^\* + a_0)$, the chain $a_{k+1} = B(a_k)$ stays in $(0, a_0)$, and every period has closest approach $C_y(D) > \sqrt G = \varepsilon$.

**(c3) $y^\* \notin \mathcal K_\infty$.** This follows from (c1).

**(c3) $y^\* \in \mathcal V_n$ for every $n$: the first step.** From $D = y^\*$, play $y = y^\* - \eta$. Then
$$A_0(\eta) = -\ln(1 - \eta/y^\*) + \tfrac12\ln\big(g(y^\*-\eta)/G\big)$$
has $A_0(0) = 0$ and $A_0'(0) = 1/y^\* > 0$. So for small $\eta$ the step is safe, and it lands at $x_1 := y^\* - T_y(y^\*) \in (0, c_1\eta)$.

**(c3) Later steps.** From $D = y^\* - x$ with $x > 0$, play $y = y^\* - 2x$. Then
$$A_1(x) = \ln\frac{y^\*-x}{y^\*-2x} + \tfrac12\ln\big(g(y^\*-2x)/G\big)$$
has $A_1(0) = 0$ and $A_1'(0) = 1/y^\* > 0$, and the next value satisfies $x'/x \to 1 + 2c^2$. So there are $x_{\max} > 0$ and $\Lambda$ such that, for $x \in (0, x_{\max})$, the step is safe and $x < x' \le \Lambda x$.

**(c3) Conclusion.** Given $n$, choose $\eta$ so small that $\Lambda^n c_1\eta < x_{\max}$. The resulting chain survives $n + 1$ periods. ∎

**Remarks on Theorem 6.**

- **Exact-speed model.** Every construction above uses full-speed actions, and the bounds are restrictions of the bounded-speed ones. So Theorem 6 holds verbatim with $\|\mathbf v\| = R_E$.
- **Dimension.** Proposition 4A.2(iii) extends everything to $d \ge 2$.
- **Validation in exact and high-precision arithmetic (§6.2).**
  - The (c2) chain was run for 600 steps in 400-digit arithmetic from $a_0 = 0.01$, at $s = 1.5$ and $s = 2$.
  - Every period's (clearance² − G) was $\ge 7.9\times10^{-184} > 0$, and $a_{k+1}/a_k \in [0.497, 0.500]$.
  - This illustrates the proof; it does not replace it.
- **What (c) means.**
  - Closed-ball capture makes the period-1 orbit fail exactly at its own threshold.
  - A runner that keeps "spending" a vanishing amount of separation, by approaching the optimal orbit from above, survives there anyway.
  - This is the only parameter value at which non-periodic strategies do strictly better than periodic ones in $\mathcal G_1$.

### 5.2 Theorem 7: the kernel below $y_+$

> **Theorem 7 (kernel below $y_+$; $\alpha_{\rm sym}(s) < \alpha_C \le 2$, i.e. $1/2 \le \varepsilon < \sqrt G$).**
> - **(a)** $\mathcal K_\infty \cap (0, y_+) = (y_-, y_+) = \mathrm{Fix}_\varepsilon$.
> - **(b)** If moreover $\alpha_C < 2$, then $y_- \in \mathcal V_\infty \setminus \mathcal K_\infty$, and $\mathcal V_\infty \cap (0, y_+) = [y_-, y_+)$.
> - **(c) A weaker bound for every $\alpha_C > \alpha_{\rm sym}$:** $\mathcal K_\infty \subseteq (d_-(\varepsilon), \infty)$, where $d_-(\varepsilon) = \Psi^{-1}(\varepsilon) \in (0, y^\*)$. This equals $y_-$ for $\varepsilon \ge 1/2$, and $s\varepsilon$ for $\varepsilon \le 1/2$.

*Proof.*

**(c)**
1. Let $D \le d_-$. By Lemma 4A.7 every up-step or level step from $D$ has closest approach $\le \Psi(D) \le \Psi(d_-) = \varepsilon$, so it is a capture.
2. Hence a chain from $D$ is strictly decreasing. It converges to some $L < D \le d_-$, and the limit level step at $L$ has closest approach $\ge \varepsilon$.
3. But $\Psi(L) < \Psi(d_-) = \varepsilon$, a contradiction.
4. For $\varepsilon \in [1/2, \sqrt G)$: $\Psi = \sqrt g$ on $[s/2, y^\*]$ and $g(s/2) = 1/4 \le \varepsilon^2$, so $d_- = y_-$.

**(a)** This combines (c) with Theorem 6(a).

**(b) $y_- \notin \mathcal K_\infty$.** This is (c).

**(b) Points below $y_-$ are not in $\mathcal V_\infty$.**
1. Let $D < y_-$ and suppose $D \in \mathcal V_\infty \subseteq \bar{\mathcal V}_\infty$. By Lemma 4A.8 there is an infinite $\bar{\mathcal R}$-chain from $D$.
2. An up-step or level step from $D' \le D < y_-$ has closest approach $\le \Psi(D') < \varepsilon$, so it is not in $\bar{\mathcal R}$. Hence the chain strictly decreases.
3. The same limit argument as in (c) gives a contradiction.

**(b) $y_- \in \mathcal V_n$ for every $n$.**
- *Monotonicity.* Since $\varepsilon > 1/2$, we have $y_- > s/2$. On $(s/2, (s+1)/2)$, $\varphi(y) := \ln\sin^2\theta_y = \ln g(y) - 2\ln y$ is strictly decreasing, since
  $$\frac{d}{dy}\sin^2\theta_y = \frac{(s^2-1)(s-2y)}{4y^2(s-y)^2} < 0.$$
  Write $\mu = -\varphi'(y_-) > 0$.
- *First step.* From $y_-$, play $y = y_- - \eta$. The log clearance ratio is $\varphi(y_- - \eta) - \varphi(y_-) > 0$.
- *Later steps.* From $y_- - x$, play $y = y_- - x - Kx$ with $K = 2g'(y_-)/(g(y_-)\mu)$. The log clearance ratio divided by $x$ tends to $g'(y_-)/g(y_-) > 0$, and the next value grows geometrically, $x'/x \to 1 + K k(y_-)/(2y_-)$.
- *Conclusion.* The rest is as in Theorem 6(c3).

**(b) The remaining points.** $(y_-, y_+) \subseteq \mathcal K_\infty \subseteq \mathcal V_\infty$. ∎

**High-precision illustration (120 digits).** Starting from $y_-$ at $\alpha_C = 1.01\,\alpha_{\rm sym}$, a first step of size $\eta = 10^{-6}, 10^{-12}, 10^{-24}$ gives the following numbers of safe periods (before the next step would be unsafe):

| $s$ | $\eta = 10^{-6}$ | $\eta = 10^{-12}$ | $\eta = 10^{-24}$ |
|---|---|---|---|
| 1.5 | 14 | 30 | 62 |
| 2 | 11 | 24 | 50 |

The count grows like $\log(1/\eta)$: finite for each $\eta$, but unbounded.

**Above $y_+$.**

> **Conjecture 4A.1.** For $\alpha_{\rm sym}(s) < \alpha_C \le 2$, $\mathcal K_\infty = (y_-(\alpha_C), \infty)$.

- *Support.* The grid survival sets (§6.1) at $\alpha_C = 1.001$ and $1.01\,\alpha_{\rm sym}$, for $s = 1.5$ and $2$, consist of every node from about $y_-$ up to the grid's upper end, $s + 2$. Their lower edge converges to $y_-$ under refinement.
- *What is missing.* A proof that every $D > y_+$ can descend into $\mathrm{Fix}_\varepsilon$ with every step safe.
- *For $\alpha_C > 2$.* Only (c) is proven, and the band between $s\varepsilon$ and $y_-$ is undetermined.

---

## 6. Numerical experiments and validation

All outputs come from `experiments/stage4a.py` and are in `results/stage4a/`.

### 6.1 Grid survival horizons

**Method.** $N(D) = \sup\{n : D \in \mathcal V_n\}$, capped at 200 periods.
- **Transitions.** They come from the exact formulas: the plateau interval of Proposition 4A.5 plus a grid of full-speed actions $y$.
- **Discretisation.** States are discretised. A landing point between two nodes counts as surviving:
  - if **both** neighbours survive (**pessimistic**); or
  - if **either** does (**optimistic**).
- **Error tracking.** Three refinements, from 750 × 300 to 3000 × 1200 (state nodes × actions), and the pessimistic/optimistic gap.
- **Status.** None of this is a certified bound. $\mathcal V_n$ need not be an interval at grid scale.

**Maximum horizon below the threshold** (pessimistic / optimistic, finest grid):

| $\alpha_C/\alpha_{\rm sym}$ | $s = 1.5$ | $s = 2$ | Theorem 6(b) |
|---|---|---|---|
| 0.9 | 6 / 6 | 3 / 3 | finite ✓ |
| 0.99 | 13 / 13 | 8 / 9 | finite ✓ |
| 0.999 | 28 / 40 | 21 / 27 | finite. At coarser grids the optimistic rule **falsely** reports ≥ 200-period survival. |

The horizon is reached from far starts ($D \approx 3$), which spend their first periods approaching.

**At the threshold**, $\alpha_C = \alpha_{\rm sym}$:
- The pessimistic estimate finds **no** 200-period survivor, at any refinement. Its maximum horizon keeps growing: 21 → 30 → 43 at $s = 1.5$, and 17 → 25 → 33 at $s = 2$.
- Theorem 6(c2), by contrast, proves an interval of indefinite survival.
- The grid cannot see this kernel, because the safety margin along the surviving chain tends to zero.
- The optimistic estimate "survives" from slightly **below** $y^\*$, by 0.008–0.019, which Theorem 6(c1) shows is false.

So both grid estimates are wrong at the threshold, in opposite directions.

**Above the threshold.** The lower edge of the 200-period survivor set tracks the exact $y_-$:

| $s$, $\alpha_C/\alpha_{\rm sym}$ | exact $y_-$ | pessimistic edge (750 / 1500 / 3000 nodes) | optimistic edge (3000 nodes) |
|---|---|---|---|
| 1.5, 1.01 | 0.969847 | 0.9738 / 0.9719 / 0.9709 | 0.9699 |
| 2, 1.01 | 1.156485 | 1.1622 / 1.1576 / 1.1576 | 1.1564 |

- The node spacing at 3000 nodes is about 0.001.
- The upper edge is always the grid's end, $s + 2$, consistent with Conjecture 4A.1.

### 6.2 Boundary chain: high precision and engine

**High precision** (`results/stage4a/boundary_chain.txt`):
- The Theorem 6(c2) chain was run for 600 steps in 400-digit Decimal arithmetic.
- $\min(\text{clearance}^2 - G) = 1.4\times10^{-183}$ at $s = 1.5$, and $7.9\times10^{-184}$ at $s = 2$. Both are positive.
- The contraction ratio is 0.497–0.500, matching $r = 1/2$.

**Event-driven engine** (`BoundaryChain` runner, float64, start $y^\* + 0.01$):

| $\alpha_C$ | Result |
|---|---|
| $\alpha_{\rm sym}$ | No capture in 30 periods. $D - y^\*$ ends at $9\times10^{-12}$. |
| $0.999\,\alpha_{\rm sym}$ | The same runner is captured at $t \approx 2.5$ periods. |

### 6.3 Formula checks

`tests/test_viability.py` checks:
- **One-period values.** `pass_step` agrees with the engine's kinematics on 200 random states.
- **Full-speed map.** $T_y$ and $C_y$ agree with direct integration.
- **Reachable set.** Every brute-force safe end-separation lies in the Proposition 4A.5 set.
- **Up-steps.** No sampled up-step exceeds $\Psi(D)$, over 20,000 samples for each of 4 values of $s$.
- **$y^\*$.** It is the grid maximiser of $g$.
- **Below threshold.** At $\alpha_C = 0.99\,\alpha_{\rm sym}$, every safe full-speed step decreases $D$.
- **Boundary chain.** It passes in Decimal and in the engine.

---

## 7. Agreement with existing theorems

| Existing result | Relation to Stage 4A |
|---|---|
| **Theorem 1** (PP captures for $\alpha_C \le 2s/(1+s)$, any runner) | Consistent. For $\mathcal R^{\rm al}_1$ the exact threshold is $\alpha_{\rm sym} \ge 2s/(1+s)$ (Lemma S): 1.6301 vs 1.2 at $s = 1.5$, and 1.7806 vs 1.3333 at $s = 2$. Theorem 1 remains the best bound for general runner classes. |
| **Theorem 2** (period-1 escape) | It is Theorem 6(a), and is now known to be **sharp** for $\mathcal R^{\rm al}_1$, except at the threshold itself, where (c) applies. |
| **Theorem 4** (certified $m$-leg orbits) | Runners in $\mathcal R^{\rm al}_m$, $m \ge 2$, lie outside $\mathcal G_1$. Since $\hat\alpha(s,2) < \alpha_{\rm sym}(s)$, we get $\kappa_{\rm PP}(s;\mathcal R^{\rm al}_2) \le \hat\alpha(s,2) < \alpha_{\rm sym}(s) = \kappa_{\rm PP}(s;\mathcal R^{\rm al}_1)$. **A second decision per period strictly lowers PP's threshold.** |
| **Theorem 5** (policy separation) | Extends to the endpoint $\alpha_C = \alpha_{\rm sym}(s)$. For $\mathcal R \supseteq \mathcal R^{\rm al}_1$, PP fails there by 6(c2), while $H$ captures whenever $\alpha_{\rm sym}(s) \le s$, e.g. at $s = 2$. |
| **Lemma M and §2.5 of the review** | The guarantee set is an interval, as Lemma M requires. Theorem 6 shows the case **open at its supremum** really occurs. |
| **Stage 3 numerics** | The planner and sweeps used random phases or $m \ge 2$, so they are outside $\mathcal G_1$, and there is nothing to reconcile. The phase result (aligned clocks matter) is consistent with $\mathcal G_1$ being the aligned case. |

---

## 8. Literature status

This is an update to `theory/literature_review.md`. The labels are as defined there.

**Alonso, Goldstein, Reingold, "Lion and Man: Upper and lower bounds".**
- *Metadata verified via Crossref:* ORSA J. Computing 4(4):447–452, 1992, DOI 10.1287/ijoc.4.4.447. Also INRIA research report RR-1700, verified via the HAL API.
- *Full text **not read**:* INFORMS returned 403, and every HAL route was blocked by bot protection.
- *Secondary source only* (Zhou, Shewchuk, Stipanović, Huang, Tomlin, "Smarter Lions"; metadata not verified): an equal-speed lion and man in a disk of diameter $d$, capture radius $r$, a capture-time upper bound of $O(d\log(d/r))$ and a superlinear evasion lower bound.
- *Assessment:* no evidence that it treats a faster pursuer, fixed-period re-aiming, or overshoot. **Unresolved** until read.
- *Action needed:* the open-access PDF (`inria.hal.science/inria-00076937/file/RR-1700.pdf`) must be opened in a normal browser.

**Bopardikar, Bullo, Hespanha (T-RO 2008).**
- *Metadata:* the DOI 10.1109/TRO.2008.2006721 is now verified via Crossref and DOI resolution.
- *Exact statements recovered from page images of the author manuscript.* Write $\kappa = r_{\rm sens}/r_{\rm step}$.
  - **Theorem III.3 (GREEDY).** If $\kappa > \sqrt{2 + 2\cos\beta_c}$, the pursuer traps the evader, with an explicit trapping-time bound (their eq. 9). Here $\beta_c$ is an explicit function of $\kappa$ and $\mathrm{diam}(Q)/r_{\rm step}$ (their eq. 8).
  - **Proposition III.4 (evasion).** If $\kappa \le \sqrt{2 + 2\cos\beta_c}$ and $Q$ contains a circle of radius $r_{\rm step}/\sqrt{4 - \kappa^2}$, then the evader can step around that circle with the pursuer one step behind, landing exactly on the evader's previous position. GREEDY never traps it.
  - **Model:** alternating moves, equal step radii, capture is coincidence, bounded convex arena.
- **Relevance to Theorem 2 and Theorem 6(a).** Prop. III.4 is a **circling, periodic evasion of a sampled greedy pursuer**: the closest prior construction to our symmetric pass. The differences are:
  - our chaser is faster, and overshoots;
  - our moves are simultaneous, with continuous capture checking and a capture radius;
  - their evasion defeats *trapping within sensing range*, not capture.

  Theorem 2 stays **Potentially distinct**, with this precedent cited.
- **CDC 2008 range-only paper** (same authors). Capture radius 1, evader step $\beta < 1/2$, and capture within $\lceil 2(\|e_0 - p_0\| + 1 + 2\beta)/(1 - 2\beta)\rceil$ steps (their Thm III.2). This is a different information model.

**Stage 4A results.**
- *Theorem 6, Theorem 7, and the finite/infinite-horizon gap.* **Potentially distinct.** No source read treats viability of sampled pure pursuit with a capture radius.
- *Viability kernels and the finite-horizon recursion.* These are standard notions, and only elementary versions, proved here, are used. Nothing about them is claimed.
- *Search coverage.* Still incomplete, per `theory/literature_review.md` §3.

---

## 9. Open questions and the next problem

1. **Conjecture 4A.1**: the kernel above $y_+$. The open part is reachability of $\mathrm{Fix}_\varepsilon$ from far separations.
2. **The case $\alpha_C > 2$**: the band between $s\varepsilon$ and $y_-$ in Theorem 7(c).
3. **Capture-time asymptotics as $\alpha_C \uparrow \alpha_{\rm sym}$.** The grid horizons grow (6, 13, 28+ at $s = 1.5$). A saddle-node "ghost" heuristic suggests $N \sim (\alpha_{\rm sym} - \alpha_C)^{-1/2}$. This is not established; the grid estimates are not accurate enough near the threshold to test it.
4. **The precise next mathematical question (Stage 4B).**
   - *Setting:* runners in $\mathcal R^{\rm al}_m$ ($m \ge 2$ aligned decisions per chaser period). The state at chaser decisions is still $D$ (§2.2), so the problem stays one-dimensional.
   - *Question:* is every non-decreasing period's closest approach bounded by the best **period-1 $m$-leg orbit** clearance $\sqrt{G_m(s)}$? That is, does Lemma 4A.7 extend from straight segments to $m$-segment polygonal relative paths?
   - *If yes:* $\kappa_{\rm PP}(s;\mathcal R^{\rm al}_m) = G_m(s)^{-1/2}$ exactly, the certified $\hat\alpha(s,m)$ become two-sided once $G_m$ is known, and the same boundary phenomena follow.
   - *If no:* non-periodic multi-leg evasion beats every periodic orbit. That would refute H1′ (review §5.4) for $m \ge 2$.

---

## Appendix: reproduction

| What | Command | Output |
|---|---|---|
| Stage 4A tests | `python -m pytest tests/test_viability.py` | — |
| Boundary chain (Decimal and engine) | `python experiments/stage4a.py chain` | `results/stage4a/boundary_chain.txt` |
| Grid horizons (about 2 min) | `python experiments/stage4a.py horizons` | `results/stage4a/horizons.{txt,json}` |

Code: `src/tagsim/viability.py` (exact one-period formulas) and `experiments/stage4a.py` (prototype).
