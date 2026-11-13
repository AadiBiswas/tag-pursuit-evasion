# How to Win a Game of Tag — Stage 4C: Optimality of Two-Leg Evasion

*2026-11-13. This document builds on `theory/stage4_multidecision_analysis.md` (cited as "4B") and `theory/stage4_viability_analysis.md` (cited as "4A").*

**Numbering.** New results are 4C.x, plus **Theorem 10**.

**Units.** $R_E = \tau_C = 1$, so $\varepsilon = 1/\alpha_C$.

**Setting.** The runner decides at the start and at the middle of each chaser period, with aligned clocks; this is the class $\mathcal R_2$ of 4B.

## Contents

1. Summary
2. Audit of the Stage 4B certificates
3. Formulation and optimisation structure
4. The translation lemma
5. Theorem 10: Conjecture 4B.1 for $s = 3/2$ and $s = 2$
6. The optimal orbit: active set and exact characterisation
7. Equality at the threshold
8. Unresolved lemmas
9. What this says about speed and agility
10. Recommendation

Appendix: reproduction.

---

## 1. Summary

1. **Conjecture 4B.1 is proved for $s = 3/2$ and $s = 2$** (Theorem 10). The proof is computer-assisted and has two parts:
   - **Translation lemma (Lemma 4C.2, any $m$, any $s$).** Shifting a whole period's start along the line of sight changes no control. Each leg's clearance then moves at least at rate $x_j/c_j$, where $x_j$ is the x-coordinate of that leg's closest point. Leg 1's closest point always has $x_1 > 0$ (Lemma 4C.1). So a maximiser of $G_{\rm up}$ that does not close can only exist if some binding leg has its closest point on or behind the chaser's line, $x_j \le 0$.
   - **Exact localization certificate.** Every non-decreasing two-leg period whose clearance is at least the certified orbit's clearance lies in an explicit box $N$. On all of $N$, leg 2's closest point has $x_2 > 0$.

   Together these force every maximiser to be closing. For other $s$ the conjecture **remains open**, and the method applies one value of $s$ at a time.
2. **Exact threshold for $s \in \{3/2, 2\}$.**
   - $\kappa_{\rm PP}(s;\mathcal R_2) = G_{\rm lev}(s,2)^{-1/2}$ exactly. The supremum defining it is the best *closing* two-leg orbit.
   - **Rigorous enclosure:** $[1.568873,\ 1.5695293557]$ for $s = 3/2$, and $[1.700102,\ 1.7008681679]$ for $s = 2$. The upper ends are within $10^{-14}$ of the true values.
   - **Numerical values (80-digit Newton):** 1.56952935572498083415… and 1.70086816790105068696….
3. **Active set at the optimum** (numerical, 80 digits; §6):
   - both legs at full speed;
   - the period closes;
   - **only leg 2 binds**, tangent at an interior point (parameter 0.138 or 0.119) in front of the chaser ($x_2 = 0.330$ or $0.219$);
   - leg 1 has slack: its closest point is the midpoint $\mathbf r(1/2)$, with clearance 0.6506 against 0.6371.

   The reduced two-variable objective has a nondegenerate maximum there. It is therefore an algebraic number, but the minimal polynomial has not been computed.
4. **At the threshold** $\alpha_C = \kappa$:
   - **Proven:** every eventually-periodic run is captured (Theorem 8(c) with Theorem 10).
   - **Proven under hypothesis (R):** non-periodic survival exists (Prop. 4C.5). (R) is regularity of the optimal-orbit family, and is verified numerically but not certified.
   - So the Stage 4A boundary phenomenon carries over, through a different mechanism: translation gain rather than $D\sin\theta$ scaling.
5. **Audit (§2).** No error was found in the Stage 4B certificates. The coverage argument is now stated explicitly, separately from the exactness of the arithmetic.

**Recommendation (§10).** The two-leg problem is resolved at the two speed ratios that matter for the paper. A proof for all $s$ would need one new analytic lemma (§8, U1). Further computation is not justified. **Move to the optimal-chaser problem.**

---

## 2. Audit of the Stage 4B certificates

The certificate is `theory/certificates/two_leg_upper_bound.py`. **Exact arithmetic does not by itself make it a proof.** It is one only together with the coverage invariant (item 6) and the soundness of each discard rule (item 3). Both are checked below.

1. **Search domain.** Boxes in $(y, a_1, b_1, a_2, b_2)$ with:
   - $y \in [0, (s+1)/2]$;
   - $a_1 \in [-1, 1]$, $b_1 \in [0, 1]$, $a_2 \in [-1, 1]$, $b_2 \in [-1, 1]$;
   - $\mathbf u_j = (a_j, b_j)$.
2. **The domain contains every admissible non-decreasing period.**
   - $\lVert\mathbf u_j\rVert \le 1$ gives $|a_j|, |b_j| \le 1$.
   - Reflecting the whole period in the line of sight ($b_j \mapsto -b_j$) preserves every distance. So $b_1 \ge 0$ loses nothing.
   - Non-decreasing periods have $y \le D^\*(\bar{\mathbf u})$ (Lemma 4B.2). The bound $D^\* \le (s+1)/2$ is the $F \le (s+1)/2$ bound of Lemma 4A.7, valid for all admissible velocities, not only unit ones. Its proof bounds $F = \lVert\mathbf w\rVert/(2\cos a)$ by the far chord point in the same direction.
   - $y = 0$ is included harmlessly.
3. **Discard rules.** Each is a valid statement about *every* point of a box.
   - *Speed.* $\min_{\rm box}(a^2 + b^2) = \operatorname{minsq}(a) + \operatorname{minsq}(b) > 1$ means no admissible point.
   - *Strictly decreasing.* $p_{2x} = y + (a_1 + a_2)/2 - s$ is increasing in each variable, so its range over the box comes from the corner values. The same holds for $p_{2y}$. Then $\max_{\rm box}\lVert\mathbf p_2\rVert^2 < y_{\rm lo}^2 \le \min_{\rm box} y^2$ means every point has $\lVert\mathbf r(1)\rVert < y$.
   - *Start point.* $c \le \lVert\mathbf r(0)\rVert = y \le y_{\rm hi}$.
   - *Lipschitz bound.* $c \le \operatorname{dist}(0, \text{leg}_j) \le \operatorname{dist}(0, \text{leg}_j(\text{centre})) + \max(|\Delta A|, |\Delta B|)$, where $A, B$ are the leg's endpoints.
     - This holds because corresponding points $A + t(B - A)$ move by at most $(1-t)|\Delta A| + t|\Delta B|$, and distance to a set is 1-Lipschitz.
     - Endpoint displacements are bounded with the $\ell^1$ norm, which dominates the Euclidean one: $|\Delta\mathbf r(0)| \le h_y$, $|\Delta\mathbf r(1/2)| \le h_y + (h_{a_1} + h_{b_1})/2 = L_1$, and $|\Delta\mathbf r(1)| \le L_1 + (h_{a_2} + h_{b_2})/2 = L_2$.
     - The point bound $c \le \lVert\mathbf r(1/2)\rVert$ uses slack $L_1$.
4. **Continuous-time closest approach.** Each leg's distance is the exact minimum of the quadratic $\lVert\mathbf p + t\mathbf d\rVert^2$ over the **closed** interval $t \in [0, 1]$, found by clamping the vertex. There is no sampling.
5. **Rounding.** None. Every quantity is a `Fraction`, and the test "$\sqrt{d} + L \le T$" is decided exactly as $L \le T$ and $d \le (T - L)^2$.
6. **Coverage invariant.** At all times, the stack together with the discarded boxes covers the domain:
   - each split replaces a box by its two closed halves;
   - every popped box is either discarded or split.

   So an empty stack means every point lies in some discarded box. This is what makes the computation a **global** certificate.
7. **Extension beyond the planar bounded-speed model.**
   - Prop. 4B.4(i): in the bounded-speed model in $\mathbb R^d$, the one-period options are exactly the planar ones.
   - Prop. 4B.4(ii): in the exact-speed model, the options lie inside the planar bounded-speed ones.
   - So the planar bounded-speed upper bound covers all four variants.
   - The audit re-checked the key step: the maximum of the linear function $1 - 2sx - s^2$ along a chord is attained at a chord end, where it equals $x^2 + y^2$.
8. **Reproducibility.** The search is deterministic (depth-first, with a fixed split rule). Re-running reproduces identical node counts; `test_upper_bound_node_count_reproducible` checks the coarse run's count exactly.

**Verdict.** No error was found. The Stage 4B results stand as stated.

---

## 3. Formulation and optimisation structure

**The period.** Fix a chaser decision with separation $D = y$. Let $\mathbf d_j = (\mathbf u_j - s\mathbf e_x)/2$, $\mathbf r_0 = (y, 0)$, $\mathbf r_{1/2} = \mathbf r_0 + \mathbf d_1$ and $\mathbf r_1 = \mathbf r_{1/2} + \mathbf d_2$.

**Each leg's squared separation is a quadratic in time.** On leg $j$, with local time $\sigma \in [0, 1]$ (real time $\sigma/2$) and leg start $\mathbf p_j$:
$$\lVert\mathbf p_j + \sigma\mathbf d_j\rVert^2 = \lVert\mathbf p_j\rVert^2 + 2\sigma\,\mathbf p_j\cdot\mathbf d_j + \sigma^2\lVert\mathbf d_j\rVert^2.$$
Its vertex is at $\sigma_j^\* = -\mathbf p_j\cdot\mathbf d_j/\lVert\mathbf d_j\rVert^2$, so:
$$c_j^2 = \begin{cases} \lVert\mathbf p_j\rVert^2, & \sigma_j^\* \le 0 \quad\text{(the leg starts moving away)},\\[2pt] \dfrac{(\mathbf p_j \times \mathbf d_j)^2}{\lVert\mathbf d_j\rVert^2}, & 0 < \sigma_j^\* < 1 \quad\text{(interior tangency)},\\[6pt] \lVert\mathbf p_j + \mathbf d_j\rVert^2, & \sigma_j^\* \ge 1 \quad\text{(still closing in at the leg's end)}.\end{cases}$$
The period's closest approach is $c^2 = \min(c_1^2, c_2^2)$.

**Constraints.**
- **Speed:** $\lVert\mathbf u_j\rVert \le 1$; in the exact-speed model, $= 1$.
- **Non-decreasing:** $\lVert\mathbf r_1\rVert^2 \ge y^2$, i.e. $y \le D^\*(\bar{\mathbf u})$.

**Symmetries.**
- **Reflection** in the line of sight. This gives $b_1 \ge 0$, the only symmetry used.
- **Translation** of the start along the line of sight, $y \mapsto y + b$ with the controls fixed. This is not a symmetry, but it is the key *monotone* deformation (§4).
- **Rotation** is already removed by the frame.

**Full speed.**
- *Numerically:* both legs are at speed 1 at the optimum (4B §6.3, 300 starts; §6 here).
- *Proven:* only for non-decreasing periods whose binding leg is leg 1, by the argument of Lemma 4A.6(ii) applied to leg 1. For leg 2 it is **not proven**; see U2.
- *Not needed:* Theorem 10 does not use full speed.

**Reducing the variables.**
- Under full speed and closing, $y$ is eliminated: $y = D^\*(\bar{\mathbf u})$.
- With the rational parametrisation $\mathbf u(t) = ((1 - t^2)/(1 + t^2),\ 2t/(1 + t^2))$, the closing period becomes a two-variable rational problem in $(t_1, t_2)$.
- With the active set of §6 (leg 2 interior tangency), the objective is the explicit rational function
  $$F_s(t_1, t_2) = \frac{(\mathbf r_{1/2} \times \mathbf d_2)^2}{\lVert\mathbf d_2\rVert^2}.$$

---

## 4. The translation lemma

> **Lemma 4C.1 (leg 1 is in front).** For any $y > 0$ and any admissible $\mathbf u_1$ with $c_1 > 0$, the closest point of leg 1 to the chaser has $x_1 > 0$.

*Proof.*
- $d_{1x} = (u_{1x} - s)/2 < 0$, and the vertex parameter is $\sigma^\* = y|d_{1x}|/\lVert\mathbf d_1\rVert^2 > 0$.
- **Interior case** ($\sigma^\* < 1$). The closest point has $x = y - y\,d_{1x}^2/\lVert\mathbf d_1\rVert^2 = y\,d_{1y}^2/\lVert\mathbf d_1\rVert^2$. This is $> 0$ unless $d_{1y} = 0$, in which case the leg passes through the origin and $c_1 = 0$.
- **End case** ($\sigma^\* \ge 1$). Then $y|d_{1x}| \ge \lVert\mathbf d_1\rVert^2 \ge d_{1x}^2$, so $x = y + d_{1x} \ge 0$. Equality forces $d_{1y} = 0$ and the end point to be the origin, so again $c_1 = 0$. ∎

> **Lemma 4C.2 (translation; any number of legs $m$, any $s$).** Translate a period's start from $y$ to $y + b$ with the controls fixed. Then:
> - **(i) Monotone translate.** Every leg translates by $(b, 0)$. Its clearance $c_j(b)$ is convex in $b$, and satisfies
>   $$c_j(b) \ge c_j(0) + b\,x_j/c_j(0),$$
>   where $x_j$ is the x-coordinate of leg $j$'s closest point (when $c_j(0) > 0$).
> - **(ii) Slack shrinks as the start moves out.** $\frac{d}{db}\big(\lVert\mathbf r_1 + b\mathbf e_x\rVert^2 - (y+b)^2\big) = 2(r_{1x} - y) \le 0$.
> - **(iii) Maximisers.** Let $Z$ be a maximiser of $G_{\rm up}(s, m)$. If every leg whose clearance equals $c(Z)$ has $x_j > 0$, then $Z$ closes.

*Proof.*

**(i)** $c_j(b)$ is the distance from the point $(-b, 0)$ to the fixed segment, and the distance to a convex set is convex. Its right derivative at $b = 0$ is the unit vector from the point to its nearest point, projected on $+\mathbf e_x$, which is $x_j/c_j$. A convex function lies above its tangent.

**(ii)** Direct computation, using $r_{1x} \le \lVert\mathbf r_1\rVert$ and $\lVert\mathbf r_1\rVert = y$ in the closing case. In general it is just the derivative.

**(iii)** Suppose $\lVert\mathbf r_1\rVert > y$ at $Z$. For small $b > 0$:
- the translated period is still non-decreasing (continuity);
- binding legs gain at least $b\,x_j/c > 0$ by (i);
- non-binding legs stay above $c(Z)$ by continuity.

So $c$ strictly increases, contradicting maximality. ∎

**Corollary 4C.3.** For $m = 2$, a non-closing maximiser of $G_{\rm up}$ must have **leg 2 binding with $x_2 \le 0$**: its closest point is on or behind the chaser's line.
- This is exactly the configuration in the Stage 4B counterexample (Prop. 4B.6), where $x_2 = -0.078$ at $y = 3/10$ and $-0.0047$ at $y = D^\*$.
- That counterexample is consistent with everything here: it shows that this configuration occurs, but not at a maximiser.

---

## 5. Theorem 10: Conjecture 4B.1 for $s = 3/2$ and $s = 2$

**Certificate.** `theory/certificates/two_leg_localize.py` uses the Python standard library only, with exact rationals, and independent code. Its inputs are:
- $c_L$, a rational with $c_L^2 \le$ the exact minimum squared clearance of the orbit certificate `s3-2_m02` or `s2-1_m02`. Hence $c_L \le \sqrt{G_{\rm lev}(2)}$.
  - $s = 3/2$: $c_L = 637133670/10^9$.
  - $s = 2$: $c_L = 587935043/10^9$.
- The box $N$: centre $\pm\,3/100$ in every coordinate. The centre is the numerical optimum (reflected so that $b_1 \ge 0$), rounded to 5 decimals.
  - $s = 3/2$: centre $(1.04267,\ 0.29958,\ 0.95407,\ -0.13848,\ 0.99036)$.
  - $s = 2$: centre $(1.25717,\ 0.20169,\ 0.97945,\ -0.33934,\ 0.94067)$.

It certifies two facts:

- **(L)** Every non-decreasing two-leg period with $b_1 \ge 0$ and $c \ge c_L$ lies in $N$.
  - Method: branch-and-bound as in §2, but a box is discarded when all its points have $c < c_L$ (**strict**), are infeasible, or lie in $N$.
  - The coverage invariant is as in §2, item 6.
- **(X)** Every point of $N$ has $x_2 > 0$.
  - Method: exact interval arithmetic, using $x_2 = p_{1x} + \sigma^\* d_{2x} \ge p_{1x,\rm lo} + \sigma^\*_{\rm hi}\,d_{2x,\rm lo}$ (valid since $d_{2x} < 0$ and $\sigma^\* \in [0, 1]$), on bisected sub-boxes.

> **Theorem 10.** For $s = 3/2$ and $s = 2$:
> - **(a)** Every maximiser of $G_{\rm up}(s, 2)$ is a closing period. Hence $G_{\rm up}(s, 2) = G_{\rm lev}(s, 2)$: Conjecture 4B.1 holds at these $s$.
> - **(b)** $\kappa_{\rm PP}(s;\mathcal R_2,\mathcal I_{\rm all}) = G_{\rm lev}(s, 2)^{-1/2}$ exactly, in both speed models and every $d \ge 2$, with
>   $$\kappa_{\rm PP}(3/2;\mathcal R_2) \in [1/0.6374,\ \hat\alpha] = [1.5688735,\ 1.5695293557],$$
>   $$\kappa_{\rm PP}(2;\mathcal R_2) \in [1/0.5882,\ \hat\alpha] = [1.7001020,\ 1.7008681679].$$
> - **(c)** At $\alpha_C = \kappa_{\rm PP}$, every surviving run has strictly decreasing separation, converging to the start of an optimal closing orbit. No eventually-periodic run survives.

*Proof.*

**(a)**
1. A maximiser $Z$ exists (Lemma 4B.5). After reflection, $b_1 \ge 0$.
2. $c(Z) = \sqrt{G_{\rm up}} \ge \sqrt{G_{\rm lev}} \ge c_L$, so $Z \in N$ by (L).
3. By (X), $x_2(Z) > 0$, and $x_1(Z) > 0$ by Lemma 4C.1. So every binding leg is in front of the chaser.
4. Lemma 4C.2(iii) then says $Z$ closes.

**(b)**
- *Equality.* Theorem 8 with (a).
- *Lower ends.* $1/T$ from the Stage 4B tight certificates ($T = 3187/5000$ and $2941/5000$).
- *Upper ends.* $\hat\alpha$ from the orbit certificates.
- *Other models and dimensions.* As in Theorem 9, via Prop. 4B.4.

**(c)** This is Theorem 8(c) with $G_{\rm lev} = G_{\rm up}$. ∎

**Certificate runs:** see §5.1 and `results/stage4c/two_leg_localize.txt`.

### 5.1 Certificate runs

| $s$ | $c_L$ | (X): leg 2 in front on all of $N$ | (L): every up-step with $c \ge c_L$ lies in $N$ | CPU time |
|---|---|---|---|---|
| 3/2 | 63713367/10^8 | **proven** (1 box) | **proven**: 14,801,431 nodes, 7,400,716 leaf boxes | 509 s |
| 2 | 587935043/10^9 | **proven** (1 box) | **proven**: 28,365,945 nodes, 14,182,973 leaf boxes | 991 s |

`test_localization_is_not_vacuous` shows that a box missing the optimum *cannot* be certified, as it must not be.

---

## 6. The optimal orbit: active set and exact characterisation

**Method.** Newton's method on $\nabla F_s = 0$ at 80 digits (`experiments/stage4c.py`, `results/stage4c/optimum.txt`).

| | $s = 3/2$ | $s = 2$ |
|---|---|---|
| $(t_1, t_2)$ | $(0.7341375037923629\ldots,\ 1.1495585410770672\ldots)$ | $(0.8150570703745211\ldots,\ 1.4238145622282894\ldots)$ |
| closing start $y_L$ | 1.0426737922203917260256… | 1.2571723775157850997390… |
| clearance $c^\*$ | 0.6371336709010391843248… | 0.5879350433338086721425… |
| $\alpha^\* = 1/c^\*$ | **1.5695293557249808341532…** | **1.7008681679010506869606…** |
| leg 1 | slack, $c_1 = 0.65064$; closest point $\mathbf r(1/2)$ (vertex parameter 1.065) | slack, $c_1 = 0.60664$; closest point $\mathbf r(1/2)$ (1.078) |
| leg 2 | **binding**, interior tangency at parameter 0.1378, $x_2 = 0.3296$ | **binding**, interior tangency at 0.1186, $x_2 = 0.2193$ |
| Hessian of $F_s$ | $\begin{pmatrix}-1.3403 & 0.1737\\ 0.1737 & -0.2449\end{pmatrix}$, negative definite | $\begin{pmatrix}-0.9494 & 0.0749\\ 0.0749 & -0.0990\end{pmatrix}$, negative definite |
| rotation per period | $\cos\psi = -0.3614$ | $\cos\psi = -0.6456$ |

**Consistency.** $c^\*$ exceeds the certified orbit's exact clearance by less than $10^{-13}$, and that orbit's clearance is a rigorous lower bound (`test_optimum_structure_and_certificate_agreement`).

**Active constraints at the optimum:**
- $\lVert\mathbf u_1\rVert = 1$ and $\lVert\mathbf u_2\rVert = 1$;
- closing ($\lVert\mathbf r_1\rVert = y$);
- leg-2 interior tangency.

Leg 1's clearance constraint is **inactive**. With full speed and closing, the problem has 2 free variables, and with one smooth binding constraint the maximiser is a smooth unconstrained critical point of $F_s$. The KKT system reduces to $\nabla F_s = 0$.

**What would make this an exact characterisation.** Suppose the global level maximiser has this active set. This is the unresolved lemma U2.
- Then $G_{\rm lev}(s, 2) = \max F_s = F_s(t^\*)$, where $t^\*$ is a nondegenerate critical point of a rational function with rational coefficients.
- Clearing denominators, $t^\*$ solves a polynomial system over $\mathbb Q$. By elimination, $G_{\rm lev}(s, 2)$ is an **algebraic number**.
- The minimal polynomial was **not computed**: no computer algebra system was available, and adding one was not justified for this stage.

**Which root is relevant.**
- Theorem 10's localization identifies the relevant critical point **geometrically**: the global maximiser lies in $N$.
- Within $N$, the numerical maximiser is a strict local maximum.
- **Not certified:** uniqueness of the critical point in $N$, and the active set being constant across $N$. Both are part of U2.

---

## 7. Equality at the threshold

Stage 4A's boundary survival came from $c = D\sin\theta_y$ being linear in $D$. For two legs the corresponding mechanism is translation.

> **Proposition 4C.5 (non-periodic survival at the threshold; conditional).** Let $G_2 = G_{\rm up}(s, 2) = G_{\rm lev}(s, 2)$ and $\varepsilon = \sqrt{G_2}$. Let $Z = (y_L, U^\*)$ be an optimal closing orbit whose binding legs all have $x_j > 0$. Assume
> - **(R)** there is a $C^1$ family $U(\lambda)$ of closing full-speed orbits with $U(0) = U^\*$, start $y(\lambda)$ with $y'(0) \ne 0$, and clearance $h(\lambda)$ differentiable at 0.
>
> Then there is an $a_0 > 0$ such that from every $D_0 \in (y_L, y_L + a_0)$ the runner survives forever. Its separation decreases strictly to $y_L$, and it can use a stationary feedback policy.

*Proof.*

**Rotation angle.** $\cos\psi := r_{1x}/y_L < 1$, because a period cannot return to its start: both legs move strictly left. Choose $\beta \in [0, 1)$ with $r := \beta + (1-\beta)\cos\psi \in (0, 1)$.

**The family.** Since $h \le \sqrt{G_2} = h(0)$ and $h$ is differentiable at 0, $h'(0) = 0$, so $h(\lambda) = \sqrt{G_2} - o(\lambda)$.

**One step.** Given a small $a > 0$:
1. Pick $\lambda = O(a)$ with $y(\lambda) = y_L + \beta a$ (implicit function theorem).
2. Play $U(\lambda)$ from $D = y_L + a$. This is the orbit's own start translated by $b = (1-\beta)a$.

**Clearance (Lemma 4C.2(i)).**
- Each leg binding at $Z$ has clearance $\ge h(\lambda) + b\,x_j(\lambda)/c_j(\lambda) \ge \sqrt{G_2} - o(a) + \tfrac12(1-\beta)a\,x_j/c$, which is $> \sqrt{G_2}$ for small $a$.
- Each leg not binding at $Z$ stays above $\sqrt{G_2}$ by continuity.

**Landing.**
$$D'^2 = y(\lambda)^2 + 2b\,r_{1x}(\lambda) + b^2, \qquad\text{so}\qquad D' - y_L = ra + O(a^2) \in (0, a)$$
for small $a$.

**Conclusion.** Induction on the periods. The policy $D \mapsto U(\lambda(D))$ is stationary. ∎

**Status for $s = 3/2$ and $s = 2$.**
- **Proven by Theorem 10 and (X):** the hypotheses $G_{\rm up} = G_{\rm lev}$ and $x_j > 0$ for the binding legs at the maximiser, since $Z \in N$.
- **Verified numerically, not certified:** hypothesis (R). With the active set of §6, $F_s$ is smooth, and $y(\cdot)$ has nonzero gradient at $t^\*$.

**High-precision illustration.** At $\alpha_C = \alpha^\*$, the chain was run for 150 steps from $a = 0.01$, using the line $t^\* + \lambda\,\nabla y/\lVert\nabla y\rVert^2$:

| $s$ | $\beta$ | $\min(\text{clearance}^2 - c^{\*2})$ | contraction ratio |
|---|---|---|---|
| 3/2 | 0.633 | $3.4\times10^{-48} > 0$ | 1/2 |
| 2 | 0.696 | $1.9\times10^{-48} > 0$ | 1/2 |

**What is new compared with 4A.** For $m = 2$ the period rotates the line of sight by more than $90°$ ($\cos\psi < 0$). So the optimal orbit's own controls, started slightly outside, would land *inside* $y_L$, from where survival is impossible. Mixing in a neighbouring orbit with a larger closing start ($\beta$) is necessary, not cosmetic.

---

## 8. Unresolved lemmas

**U1. Conjecture 4B.1 for all $s > 1$.**
- By Corollary 4C.3, it is equivalent to: *no maximiser of $G_{\rm up}(s, 2)$ has leg 2 binding with $x_2 \le 0$.*
- An analytic route: show that when leg 2's closest point is behind the chaser, rotating $\mathbf u_2$ toward the perpendicular of $\mathbf r_{1/2}$ raises $c_2$ faster than the accompanying translation lowers it.
- *Evidence:* Theorem 10 at two values of $s$, and 4B's 7-digit optimisation.
- *What a proof needs:* a first-order analysis of the case "leg 2 binding with $x_2 \le 0$" in which both legs' gradients are controlled simultaneously.

**U2. Structure and uniqueness in $N$.**
- The claim: the global closing maximiser is at full speed with leg-2 interior tangency, and $F_s$ has a unique critical point in the corresponding parameter region.
- This would give an exact algebraic characterisation and settle hypothesis (R).
- *Evidence:* the 80-digit Newton solution, a negative definite Hessian, and 300 local searches all reaching it.
- *What a proof needs:* exact interval bounds on the Hessian of $F_s$ over the image of $N$ (concavity implies uniqueness), plus exclusion of the other active sets in $N$, e.g. leg 1 binding or speed below 1. This is a small certificate, but it was not built in this stage.

**U3. Closed form.** The minimal polynomial of $G_{\rm lev}(s, 2)$. This needs computer algebra, and only becomes meaningful once U2 holds.

---

## 9. What this says about speed and agility

**Why two decisions beat one.**
- With one decision the relative path is a straight chord. The best period-1 orbit is a symmetric chord pass whose closest approach lies in its middle.
- With two decisions the runner bends the path once. The bend lets leg 2 graze the capture disk early in the leg ($\sigma^\* \approx 0.12$–$0.14$), with its closest point well in front of the chaser. Meanwhile leg 1 stays clear and ends at the midpoint.
- The chord's single tangency becomes one tangency plus slack, worth about 0.06 in $\alpha_C$ at $s = 3/2$, and 0.08 at $s = 2$.

**Locally greatest clearance versus infinite survival.**
- A period that ends *farther out* can have more clearance than the closing period with the same controls. The exact counterexample of Prop. 4B.6 shows this.
- That extra clearance does not help forever. A non-closing maximiser must have leg 2 behind the chaser (Corollary 4C.3), and at the actual optimum the closing orbit dominates (Theorem 10).
- Survival is decided by what can be **repeated** (closing orbits), together with a boundary limit of non-repeating runs (§7). It is not decided by one-period records.

**How capture and evasion interact.**
- The capture guarantee needs a bound on all non-decreasing periods ($G_{\rm up}$).
- Constructive evasion needs a single closing orbit ($G_{\rm lev}$).
- The threshold is exact exactly when these agree. That agreement is a statement about *where the chaser can be outrun* by geometry, not about the chaser's strategy.

**Dimension.**
- *Independent of $d \ge 2$:* Lemma 4C.1, Lemma 4C.2 (all $m$), Theorem 10, and Prop. 4C.5.
- *Why:* for two legs, the one-period problem in $\mathbb R^d$ equals the planar one (Prop. 4B.4).
- *Not implied for $m \ge 3$.*

**Full speed versus bounded speed.**
- Theorem 10 holds in both speed models: the optimal orbits are unit speed, and the upper bounds cover bounded speed.
- That the optimum is at full speed is numerical (U2).
- For $m = 1$ full speed was proven (Lemma 4A.6). For $m = 2$, slowing down never helped in any experiment.

---

## 10. Recommendation

**The two-leg problem is answered where it matters.** For the paper's speed ratios:
- the threshold is exact as a supremum over closing orbits;
- it is rigorously enclosed;
- it is known to 20+ digits numerically;
- its boundary behaviour is understood, up to a regularity hypothesis.

**What remains is a different kind of work.** U1 (all $s$) is a genuine analytic question. Extending the computation to more values of $s$, or to four legs, would not answer it, and the exhaustive certificate does not scale (4B §8).

**Recommendation.**
- Do **not** increase the numerical budget on two legs.
- Record U1 and U2 as open lemmas.
- **Move to the optimal-chaser problem.** $\kappa^\*$ is so far bounded only below, by $s$, through the hybrid chaser of Theorem 3, and nothing bounds it above. The policy-separation result already shows the chaser's strategy matters more than the runner's second decision: the hybrid chaser's guarantee reaches $\alpha_C = s$, while the runner's second decision moves PP's threshold by only about 0.06.

---

## Appendix: reproduction

| What | Command | Output |
|---|---|---|
| Tests | `python -m pytest tests/test_two_leg_optimality.py` | — |
| Optimum and boundary chain (80 digits, under a second) | `python experiments/stage4c.py` | `results/stage4c/optimum.txt` |
| Localization certificate | `python theory/certificates/two_leg_localize.py 3/2` (and `2`) | `results/stage4c/two_leg_localize.txt` |
