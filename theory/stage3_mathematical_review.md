# How to Win a Game of Tag — Stage 3 Mathematical Review

*Status as of 2026-11-12. This document is meant to be read on its own. The code references at the end of each section are there for reproduction; they are not needed to follow the mathematics.*

**Revision history.**
- **Rev 1** (Stage 3): §§1–11 as first written.
- **Rev 2** (Stage 3.5, 2026-11-12): additions, each marked *Rev 2* where it appears. Rev 1 text is kept, and a note is added wherever Rev 2 supersedes it.
  - New §2.4: monotonicity in $\alpha_C$ (Lemma M).
  - New §2.5: precise threshold notation.
  - New §3.5: Lemma S and Theorem 5, the policy separation.
  - New §7.3: the independent certificate package and the threshold convention.
  - Status-table rows added.
  - Corrections, listed in §7.3.
  - §10 replaced by `theory/literature_review.md`.
  - The index of all results is in `theory/theorem_register.md`.

## Contents

1. Executive summary
2. Model and definitions
3. The improved capture theorem (Theorem 1), with complete proof
   - 2.4 Monotonicity in $\alpha_C$ (Lemma M), 2.5 Threshold notation — *Rev 2*
   - 3.4 A related guarantee for a hybrid chaser (Theorem 3)
   - 3.5 Policy separation (Lemma S, Theorem 5) — *Rev 2*
4. The period-1 escape orbit (Theorem 2), with complete proof
5. Theorem-status table
6. Numerical results and their limitations
7. Higher-period and multi-leg orbits; exact certification (Theorem 4); 7.3 certificate package — *Rev 2*
8. The remaining capture–escape gap
9. Implications for H1–H5
10. Literature status and search checklist
11. Recommended direction for Stage 4

Appendix A covers reproduction.

---

## 1. Executive summary

The question for Stage 3 was where the capture guarantee of full-speed **pure pursuit (PP)** ends. Write $s = R_C/R_E > 1$ for the speed ratio and $\alpha_C = R_E\tau_C/\varepsilon$ for the chaser's decision interval in units of the time the runner needs to cross the capture radius.

**What is proven.**
- **Theorem 1.** PP captures every runner whenever $\alpha_C \le 2s/(1+s)$. This holds for every runner decision schedule, every phase, every dimension, and both speed models. The earlier sufficient condition was $\alpha_C \le 1$, and $2s/(1+s) > 1$ for every $s > 1$. So the original hypothesis **H1, "the PP threshold is exactly $\alpha_C = 1$", is false.**
- **Theorem 2.** For $\alpha_C > \alpha_{\rm sym}(s)$ (explicit formula below; it lies in $(1,2)$), there is an exact periodic escape from PP. The runner needs only to decide at the chaser's decision times, so $a = 1$ with aligned clocks is enough.
- **Theorem 3.** A different chaser captures more: brake onto the observed point while $D > s\varepsilon$, then switch to full-speed pursuit. It captures every runner whenever $\alpha_C \le s$, and this bound is sharp for that chaser. This is new in this review; Section 3.4 explains how it came out of auditing Theorem 1. It needs the bounded-speed model.

**What is certified by exact computation.**
- **Theorem 4.** For $s \in \{6/5, 3/2, 2\}$, runners with $m \in \{1,2,4,8,16\}$ aligned decisions per chaser period escape PP exactly whenever $\alpha_C \ge \alpha_c(s,m)$.
- The certificate is a finite computation in exact rational arithmetic; no tolerance appears anywhere in it.
- The values $\alpha_c(s,16) = 1.3890,\ 1.5397,\ 1.6540$ improve on $\alpha_{\rm sym}(s) = 1.4343,\ 1.6301,\ 1.7806$.

**What is only numerical.**
- A corrected best-response planner never found an escape at a swept $\alpha_C \le 7/5$ when clock phases were random, for any $s$ or $a$.
- With clocks aligned, it escapes wherever a certified orbit exists. It also finds escapes at random phases and at $a = 2$ for large $\alpha_C$, but nothing proves those.
- Two defects in the planner were found and fixed by testing it against known orbits (Section 6.2).

**Added in Rev 2 (Stage 3.5).**
- **Theorem 5 (policy separation).** At $s = 2$ and $\alpha_C = 1.9$, a runner evades PP forever, yet the hybrid chaser captures every runner. A change of chaser strategy alone turns indefinite evasion into guaranteed capture, so PP is not optimal for guaranteed capture (§3.5).
- **Lemma M.** Capture guarantees are monotone in $\alpha_C$ whenever only $\varepsilon$ varies, so the thresholds are well defined (§2.4–2.5).
- **Certificates.** All 15 certificates pass a standalone exact verifier and hold in both speed models (§7.3).

**What is open.**
- For each $s$, the true PP threshold lies in $[\,2s/(1+s),\ \alpha_c(s,m)\,]$ for aligned runners. The remaining gap is about 0.30 at $s = 1.2, 1.5, 2$ (Section 8).
- For runners whose clock is not aligned with the chaser's, no escape is proven at any $\alpha_C$.

**Novelty.** No novelty is claimed. The closest prior work identified so far is a self-triggered sampled-pursuit paper. It differs in a material way, because there the pursuer chooses its own sampling times; Section 10 gives the comparison.

---

## 2. Model and definitions

### 2.1 Game

There are two agents in $\mathbb R^d$ ($d \ge 1$): a chaser $C$ and a runner $E$, with maximum speeds $R_C > R_E > 0$.

**Decision clocks.** Agent $i$ decides only at the times
$$\mathcal T_i = \{\varphi_i + k\tau_i : k \ge 0\},$$
with period $\tau_i > 0$ and phase $\varphi_i \in [0, \tau_i]$. If $\varphi_i > 0$, the agent is committed on $[0, \varphi_i)$ to a given initial velocity.

**Velocities.** At each of its decision times, agent $i$ chooses a velocity $\mathbf v_i$ and holds it constant until its next decision.
- *Bounded-speed model (primary):* $\|\mathbf v_i\| \le R_i$.
- *Exact-speed model (variant):* $\|\mathbf v_i\| = R_i$.

There is no other control: no acceleration, no turning-rate limit, no mid-interval change.

**Information.** At each of its decision times, an agent sees the full state at $t^-$: both positions, both committed velocities, and both clocks. When both agents decide at the same instant, neither sees the other's new velocity.

**Strategies** are nonanticipative maps from observed history to velocity.

**Capture** happens at the first $t$ with $\|\mathbf x_E(t) - \mathbf x_C(t)\| \le \varepsilon$. The capture radius $\varepsilon > 0$ defines a closed ball, and capture is tested continuously in time, not only at decision times.

### 2.2 Notation

Throughout:
- $s = R_C/R_E$
- $L = R_C\tau_C$, the chaser's travel in one period
- $\rho = R_E\tau_C$, the runner's travel in one chaser period
- $\alpha_C = \rho/\varepsilon$
- $t_k = \varphi_C + k\tau_C$ for the chaser's decision times, with $\mathbf c_k = \mathbf x_C(t_k)$ and $\mathbf e_k = \mathbf x_E(t_k)$
- $D_k = \|\mathbf e_k - \mathbf c_k\|$, and $\hat{\mathbf u}_k = (\mathbf e_k - \mathbf c_k)/D_k$

Two identities used repeatedly are $s\varepsilon = L/\alpha_C$ and $\rho = \alpha_C\varepsilon$.

**Pure pursuit (PP).** At each $t_k$, the chaser plays $\mathbf v_C = R_C\hat{\mathbf u}_k$. This is full speed toward the runner's *current* position, held for the whole period, and it is admissible in both speed models.

**Braking pursuit (BP).** At each $t_k$, the chaser plays $\mathbf v_C = \min(R_C, D_k/\tau_C)\,\hat{\mathbf u}_k$.

### 2.3 Quantifiers

**Uniform capture guarantee.** A chaser strategy $\sigma_C$ has one at parameters $(s, \alpha_C, \text{runner class } \mathcal R)$ if, for **every** initial state (positions, initial velocities, both phases) and **every** runner strategy in $\mathcal R$, capture happens in finite time.

**Escape construction.** This means **there exists** an initial state (phases included) and a runner strategy in $\mathcal R$ such that the given chaser *never* captures.

The two statements are not complementary. Between them lie parameters where neither has been established.

**Threshold.** For PP define
$$\kappa_{\rm PP}(s; \mathcal R) = \sup\{\alpha_C : \text{PP has a uniform capture guarantee against } \mathcal R \text{ for every } \alpha' \le \alpha_C\}.$$
Here $\mathcal R$ fixes the runner's speed bound, and its decision-period class: either a fixed ratio $a = \tau_E/\tau_C$, or "any period". Monotonicity of the guarantee in $\alpha_C$ has **not** been proven, which is why the definition takes the supremum over an initial interval.

> *Rev 2.* Monotonicity is now proven (Lemma M, §2.4) whenever only $\varepsilon$ varies and the runner class is closed under open-loop replay. The supremum over an initial interval therefore coincides with the plain supremum. The notation of §2.5 supersedes this definition.

### 2.4 Monotonicity in $\alpha_C$ — *Rev 2*

**Normalised game.** Use units with $R_E = \tau_C = 1$, so $\rho = 1$, $L = s$ and $\varepsilon = 1/\alpha_C$. A **configuration** fixes:
- $s$ and the speed model;
- a runner class $\mathcal R$;
- an initial-state class $\mathcal I$. Its states (positions, committed initial velocities, both phases) are given in these units.

With the configuration fixed, changing $\alpha_C$ changes **only** the capture radius.

**Runner classes used in this document.**

| Class | Definition |
|---|---|
| $\mathcal R_{\rm free}$ | Every measurable runner path with speed $\le R_E$. This is larger than the model, and it is the class Theorem 1 actually covers. |
| $\mathcal R_{\rm all}$ | Every model runner: any period $\tau_E > 0$, any phase, nonanticipative strategies. |
| $\mathcal R_{a,\Phi}$ | Model runners with $\tau_E = a\tau_C$ and phase offset $\varphi_E - \varphi_C \bmod \tau_E$ in $\Phi$. |
| $\mathcal R^{\rm al}_m$ | $\mathcal R_{1/m,\{0\}}$: aligned runners with $m$ decisions per chaser period. Every chaser decision is then also a runner decision. |

Inclusions: $\mathcal R^{\rm al}_m \subseteq \mathcal R^{\rm al}_{km} \subseteq \mathcal R_{\rm all} \subseteq \mathcal R_{\rm free}$, for every integer $k \ge 1$.

Strategies are deterministic and nonanticipative, and **may read $\varepsilon$**, since it is part of the observation.

**(R) Open-loop closure.** Each class above is defined only by restrictions on the runner's clock and speed. So it contains every *open-loop* runner, meaning a fixed sequence of velocities at its decision times, that respects those restrictions. A class such as "the Stage 3 planner with fixed settings" does **not** have this property.

**Definition (guarantee).** $G(\sigma_C;\alpha,\mathcal R,\mathcal I)$ holds if, for every $x_0 \in \mathcal I$ with $D(0) > 1/\alpha$ and every $\sigma_E \in \mathcal R$, the game started from $x_0$ ends in capture at a finite time.

> **Lemma M (monotonicity).** Fix a configuration whose $\mathcal R$ satisfies (R), and let $0 < \alpha \le \alpha'$.
> - (a) Let $\sigma_C$ be a chaser strategy that does not read $\varepsilon$, such as PP or BP. If $G(\sigma_C;\alpha',\mathcal R,\mathcal I)$ holds, then so does $G(\sigma_C;\alpha,\mathcal R,\mathcal I)$.
> - (b) If some admissible chaser strategy guarantees capture at $\alpha'$, then some admissible chaser strategy guarantees capture at $\alpha$.

*Proof.* Write $\varepsilon = 1/\alpha \ge \varepsilon' = 1/\alpha'$.
1. **The chaser.** Let $\sigma'_C$ guarantee capture at $\alpha'$. Define $\sigma_C$ as $\sigma'_C$ with the constant $\varepsilon'$ substituted wherever $\sigma'_C$ reads the capture radius. For (a), $\sigma_C = \sigma'_C$.
   - Admissibility means the speed bound and the decision clock. Neither involves $\varepsilon$, so $\sigma_C$ is admissible at radius $\varepsilon$.
2. **The run at radius $\varepsilon$.** Take $x_0 \in \mathcal I$ with $D(0) > \varepsilon$, so also $D(0) > \varepsilon'$, and any $\sigma_E \in \mathcal R$.
   - The dynamics do not depend on the capture radius. Only the stopping rule does.
   - So let $\xi$ be the trajectory that $(\sigma_C, \sigma_E)$ generates from $x_0$ at radius $\varepsilon$, continued for all $t \ge 0$ while ignoring the stopping rule.
   - Let $u$ be the sequence of velocities $\sigma_E$ chooses along $\xi$, and let $\tilde\sigma_E$ be the open-loop runner that plays $u$. By (R), $\tilde\sigma_E \in \mathcal R$.
3. **The run at radius $\varepsilon'$.** Here $(\sigma_C, \tilde\sigma_E)$ from $x_0$ generates exactly $\xi$:
   - $\sigma_C$ receives the same histories, because it uses $\varepsilon'$ in both games;
   - $\tilde\sigma_E$ ignores its observations.
4. **Conclusion.** By the guarantee at $\alpha'$, $\xi$ enters the closed $\varepsilon'$-ball at some finite $T'$. That ball lies inside the $\varepsilon$-ball. So the game at radius $\varepsilon$ ends in capture by $T'$. ∎

**Corollary M.** For a configuration satisfying (R):
- The sets $A_{\rm PP} = \{\alpha : G({\rm PP};\alpha,\mathcal R,\mathcal I)\}$ and $A^\* = \{\alpha : \exists\,\sigma_C,\ G(\sigma_C;\alpha,\mathcal R,\mathcal I)\}$ are intervals of the form $(0,\kappa)$ or $(0,\kappa]$.
- So the clause "for every $\alpha' \le \alpha_C$" in the §2.3 definition is redundant, and $\kappa = \sup A$.
- Enlarging $\mathcal R$ or $\mathcal I$ can only lower $\kappa$.

**What Lemma M does not cover.** It concerns families in which only $\varepsilon$ varies. The Stage 2 and Stage 3 sweeps are not such families:
- **Initial distance.** They fix $\varepsilon = R_E = 1$ and set $\tau_C = \alpha_C$, with $D(0) = 10\varepsilon$. In normalised units the initial distance is $10/\alpha_C$, so the initial state moves with $\alpha_C$.
- **Horizon.** The finite horizon also changes with $\alpha_C$.
- **Runner.** The runner is a single fixed heuristic, so (R) fails.

The corrected-planner escape counts happen to be non-decreasing in $\alpha_C$ in every $(s, a)$ cell, but nothing guarantees that. Changing the agility ratio $a$ or the phase class $\Phi$ changes $\mathcal R$, which is a different axis altogether.

### 2.5 Threshold notation — *Rev 2*

All of the following are defined for a configuration, written $(s;\ \mathcal R,\ \mathcal I)$ together with the speed model, and none is a function of $s$ alone.

- **PP threshold:** $\kappa_{\rm PP}(s;\mathcal R,\mathcal I) = \sup\{\alpha : G({\rm PP};\alpha,\mathcal R,\mathcal I)\}$.
  - PP is admissible in both speed models.
  - Every bound proven so far holds in both, so the speed model is suppressed here.
- **Best-chaser threshold:** $\kappa^\*(s;\mathcal R,\mathcal I,\text{model}) = \sup\{\alpha : \exists$ admissible $\sigma_C$ with $G(\sigma_C;\alpha,\mathcal R,\mathcal I)\}$.
- **Aligned thresholds:** $\kappa_{\rm PP}(s;\mathcal R^{\rm al}_m,\mathcal I)$.
- **Agility thresholds:** $\kappa_{\rm PP}(s;\mathcal R_{a,\Phi},\mathcal I)$.
- **Initial-state classes.**
  - The default is $\mathcal I_{\rm all}$: all states.
  - Every escape construction uses one specific state. So it bounds $\kappa$ only for classes $\mathcal I$ that contain that state.
  - For $\mathcal I_{\rm far}(d_0) = \{D(0) \ge d_0\}$, no escape is proven. Reaching an orbit's state from far away has not been shown.
- **Shorthand.** $\kappa_{\rm PP}(s)$ means $\kappa_{\rm PP}(s;\mathcal R_{\rm all},\mathcal I_{\rm all})$, and is used only when that is what is meant.

**Proven relations.**
1. **Theorem 1.** $2s/(1+s) \le \kappa_{\rm PP}(s;\mathcal R,\mathcal I)$ for every $\mathcal R \subseteq \mathcal R_{\rm free}$, every $\mathcal I$, and both models. Capture is also guaranteed **at** $\alpha = 2s/(1+s)$.
2. **Theorems 2 and 4.**
   - $\kappa_{\rm PP}(s;\mathcal R,\mathcal I) \le \alpha_{\rm sym}(s)$ whenever $\mathcal R \supseteq \mathcal R^{\rm al}_1$ and $\mathcal I$ contains the Theorem 2 state.
   - $\kappa_{\rm PP}(s;\mathcal R,\mathcal I) \le \hat\alpha(s,m)$ whenever $\mathcal R \supseteq \mathcal R^{\rm al}_m$ and $\mathcal I$ contains the certificate's state.
   - At $\alpha = \hat\alpha$ itself the orbit is captured by tangency. So these are bounds on the supremum, and the guarantee at $\kappa_{\rm PP}$ itself is undetermined.
3. **Bracket for $\mathcal R_{\rm all}$.** Because $\mathcal R^{\rm al}_{16} \subseteq \mathcal R_{\rm all}$, for $s \in \{6/5, 3/2, 2\}$:
$$\frac{2s}{1+s} \le \kappa_{\rm PP}(s;\mathcal R_{\rm all},\mathcal I_{\rm all}) \le \hat\alpha(s,16).$$
   The Stage 3 statement "for unaligned runners no escape is proven" is correct only for classes that exclude alignment, such as $\mathcal R_{a,\Phi}$ with $0 \notin \Phi$.
4. **Theorem 3.** $\kappa_{\rm PP} \le \kappa^\*$, and $\kappa^\*(s;\mathcal R_{\rm all},\mathcal I_{\rm all},\text{bounded}) \ge s$. In the exact-speed model, only $\kappa^\* \ge 2s/(1+s)$ is known.
5. **Theorem 5 (§3.5).** If $\alpha_{\rm sym}(s) < s$, then $\kappa_{\rm PP} < \kappa^\*$ in the bounded-speed model, for any $\mathcal R \supseteq \mathcal R^{\rm al}_1$ with $\mathcal I_{\rm all}$.
6. **Divisibility.** $\kappa_{\rm PP}(s;\mathcal R^{\rm al}_{km},\mathcal I) \le \kappa_{\rm PP}(s;\mathcal R^{\rm al}_{m},\mathcal I)$. This is consistent with the certified $\hat\alpha(s,m)$ decreasing along $m = 1, 2, 4, 8, 16$.
7. **Lemma S (§3.5).** $\alpha_{\rm sym}(s) \ge 2s/(1+s) > 1$, by relations 1 and 2: an escape strictly below the Theorem 1 bound would contradict Theorem 1.

---

## 3. Theorem 1 — improved capture theorem

### 3.1 Statement

> **Theorem 1.** Assume the following:
> - $R_C > R_E$, in any dimension $d \ge 1$;
> - either speed model;
> - any runner strategy, under either speed model or even with arbitrary measurable control of speed at most $R_E$, any decision schedule or none, and any information, including full knowledge of the chaser's future;
> - any initial positions with $D(0) > \varepsilon$, any initial chaser velocity, any phase $\varphi_C$;
> - the chaser plays PP at every $t_k$.
>
> If
> $$\alpha_C = \frac{R_E\tau_C}{\varepsilon} \le \frac{2s}{1+s},$$
> then capture occurs by time
> $$T^\* \le \varphi_C + (K+2)\,\tau_C, \qquad K = \left\lceil \frac{(D_1 - L)^+}{L - \rho} \right\rceil,$$
> where $D_1 = \|\mathbf x_E(\varphi_C) - \mathbf x_C(\varphi_C)\| \le D(0) + (R_C + R_E)\varphi_C$.

### 3.2 Proof

**Lemma A (runner displacement).** For $\sigma \ge 0$,
$$\|\mathbf x_E(t_k + \sigma) - \mathbf e_k\| \le R_E\sigma.$$

*Proof.* The runner's speed never exceeds $R_E$, and its path is absolutely continuous. ∎

This is the **only** property of the runner the proof uses. That single fact is why the theorem is indifferent to the runner's schedule, phase, information and dimension.

**Lemma B (one PP interval).** Fix $k$, and suppose no capture has occurred by $t_k$, so $D_k > \varepsilon$. On $[t_k, t_{k+1}]$ the chaser moves along $\mathbf c_k + R_C\sigma\hat{\mathbf u}_k$.

- **(i) Approach: $D_k \ge L$.** Then $D_{k+1} \le D_k - (L - \rho)$.
- **(ii) Overshoot: $D_k < L$.** Then:
  - **(a)** at $\sigma^\* = D_k/R_C \in (0, \tau_C)$, the separation is at most $D_k/s$;
  - **(b)** $D_{k+1} \le L + \rho - D_k$.

*Proof of (i).* The chaser ends at $\mathbf c_k + L\hat{\mathbf u}_k$, a point on the segment $[\mathbf c_k, \mathbf e_k]$ at distance $D_k - L$ from $\mathbf e_k$. By Lemma A, the runner ends within $\rho$ of $\mathbf e_k$. By the triangle inequality, $D_{k+1} \le (D_k - L) + \rho$.

*Proof of (ii)(a).* At $\sigma^\*$ the chaser is exactly at $\mathbf e_k$. By Lemma A, the runner is within $R_E\sigma^\* = D_k/s$ of $\mathbf e_k$.

*Proof of (ii)(b).* At the end of the interval, the chaser is at $\mathbf e_k + (L - D_k)\hat{\mathbf u}_k$. The runner is within $\rho$ of $\mathbf e_k$. Apply the triangle inequality. ∎

**Corollary C (one-interval capture).** If $\varepsilon < D_k \le s\varepsilon$ and $D_k < L$, the interval $[t_k, t_{k+1}]$ contains a capture.

*Proof.* By Lemma B(ii)(a), the separation at $t_k + \sigma^\*$ is at most $D_k/s \le \varepsilon$. ∎

**Main argument.**

1. **Reduction.** If $\alpha_C \le 1$, Proposition 1 of the specification applies; its proof is cases (i) and (ii)(a) above with $\rho \le \varepsilon$. So assume $1 < \alpha_C \le 2s/(1+s)$. Then:
   - $s\varepsilon < L$, because $s\varepsilon = L/\alpha_C$ and $\alpha_C > 1$;
   - $\rho \le s\varepsilon$, because $\rho/(s\varepsilon) = \alpha_C/s$ and $2s/(1+s) < s$ for $s > 1$;
   - $L + \rho \le 2s\varepsilon$, because this is $\alpha_C(1+s)\varepsilon \le 2s\varepsilon$, which is the hypothesis.

2. **Approach phase.** While $D_k \ge L$ and no capture has occurred, Lemma B(i) gives a decrease of at least $L - \rho = (R_C - R_E)\tau_C > 0$ per step. So within $K$ steps of $t_1 = \varphi_C$, either capture has occurred or some $D_j \le L$ with $j \le K$. Take $j$ minimal.

3. **Case $D_j = L$ exactly.** Lemma B(i) gives $D_{j+1} \le \rho \le s\varepsilon < L$. So, if no capture has happened yet, Corollary C applies at step $j+1$: capture by $t_{j+2}$.

4. **Case $D_j < L$.**
   - If $D_j \le s\varepsilon$, Corollary C gives capture by $t_{j+1}$.
   - Otherwise $D_j > s\varepsilon$, and Lemma B(ii)(b) gives
   $$D_{j+1} \le L + \rho - D_j < L + \rho - s\varepsilon \le s\varepsilon.$$
   Since $s\varepsilon < L$, Corollary C applies at step $j+1$ unless capture already happened: capture by $t_{j+2}$.

In every case capture occurs by $t_{j+2} \le \varphi_C + (K+2)\tau_C$. ∎

### 3.3 Required checks

**Geometric reason for the improvement.** Proposition 1 shows that a single PP pass captures when $\rho \le \varepsilon$. Theorem 1 adds the inequality from Lemma B(ii)(b):
$$D_k + D_{k+1} \le L + \rho \qquad \text{for every overshoot step.}$$
- An overshoot that misses requires $D_k > s\varepsilon$: the runner must start the pass far enough away to sidestep $D_k/s > \varepsilon$ by the moment the chaser crosses $\mathbf e_k$.
- The next pass needs $D_{k+1} > s\varepsilon$ as well.
- The two together need $L + \rho > 2s\varepsilon$.
- In words: the chaser's overshoot $L - D_k$ plus the runner's escape budget $\rho$ is shared between the two consecutive passes, and cannot pay for two near-misses in a row.

**Decrease of a potential.**
- Approach steps decrease $D$ by the fixed amount $L - \rho$.
- Overshoot steps admit no monotone potential: $D_{k+1}$ may exceed $D_k$.
- The proof does not need one. It shows that an overshoot step either captures, or produces a state captured in the next step. This is a two-step argument, not a Lyapunov argument.

**Overshoot.** This is exactly case (ii). Moving past $\mathbf e_k$ is what allows (ii)(b); it is not a defect of PP that needs repair (compare Theorem 3 and §B.2a of the specification).

**Near-tangential motion.**
- No step of the proof depends on the shape of the runner's path. The bounds are pathwise inequalities.
- Capture in Corollary C may be by tangency, when $D_j/s = \varepsilon$ exactly. That still counts, because the capture ball is closed.
- Under the hypothesis of the theorem, the second step is never a tie: $D_{j+1} < s\varepsilon$ holds *strictly*, so the separation at $t_{j+1} + \sigma^\*$ is $< \varepsilon$.

**Equality $\alpha_C = 2s/(1+s)$.** It is covered, and the argument above is unchanged. Equality gives $L + \rho = 2s\varepsilon$, and strictness comes from $D_j > s\varepsilon$.

This contrasts with BP at $\alpha_C = 1$ and with Theorem 3 at $\alpha_C = s$. In those cases the threshold capture *is* an exact tangency against a runner fleeing in a straight line. That is a measure-zero event that floating-point simulation can resolve either way; the test suite avoids those exact points.

**Runner decision frequency and phases.**
- Only Lemma A concerns the runner, and it is schedule-free.
- The chaser's phase $\varphi_C$ enters only through $D_1$ and the time offset.

**Dimension.** Only the triangle inequality and the fact that $\mathbf c_k$, $\mathbf e_k$ and the chaser's path are collinear are used. The proof holds in any normed space whose capture set is the norm ball; for the model, that means $\mathbb R^d$ with the Euclidean norm.

**Which chaser controls.** The proof uses exactly two properties of the chaser on each period:
- **(P1)** if $D_k \le L$, the chaser is at $\mathbf e_k$ at time $t_k + D_k/R_C$;
- **(P2)** at $t_{k+1}$, $\|\mathbf c_{k+1} - \mathbf e_k\| \le L - D_k$ in case (ii), and $= D_k - L$ in case (i).

In this model the chaser's velocity is constant on $[t_k, t_{k+1})$. Then (P1) forces $\mathbf v_C = R_C\hat{\mathbf u}_k$. So **within the model, Theorem 1 is a theorem about PP only.**
- BP violates (P1).
- In a model allowing intra-period control, the same proof covers any chaser that runs at full speed to $\mathbf e_k$ and then moves arbitrarily.

PP is admissible in both speed models, so the theorem holds in both.

**Explicit capture-time bound.** Since $K \le (D_1 - L)^+/(L-\rho) + 1$,
$$T^\* \ \le\ \varphi_C + 3\tau_C + \frac{(D_1 - L)^+}{R_C - R_E}, \qquad D_1 \le D(0) + (R_C + R_E)\varphi_C.$$
Against a runner fleeing along the initial line of sight, any chaser needs $T^\* \ge (D(0) - \varepsilon)/(R_C - R_E)$ (specification §B.2). So the bound is tight up to $O(\tau_C)$ terms.

### 3.4 What auditing (P1)–(P2) produced: a hybrid chaser (Theorem 3)

> **Theorem 3 (bounded-speed model).** Consider the chaser $H$ that, at each $t_k$:
> - plays BP if $D_k > s\varepsilon$;
> - plays PP if $D_k \le s\varepsilon$.
>
> 1. If $\alpha_C \le s$, $H$ captures every runner, with $T^\* \le \varphi_C + (K+2)\tau_C$.
> 2. If $\alpha_C > s$, there is an initial state and a runner that $H$ never captures.

*Proof of part 1.* If $\alpha_C \le 1$, Proposition 1's proof applies directly, because $H$ coincides with PP when $D_k \le L$ and $s\varepsilon \ge L$. So let $1 < \alpha_C \le s$; then $s\varepsilon < L$ and $\rho \le s\varepsilon$.

- **$D_k > L$.** BP has speed $R_C$, so it coincides with PP; Lemma B(i) applies.
- **$s\varepsilon < D_k \le L$.** BP has speed $D_k/\tau_C \le R_C$, so it is admissible. The chaser lands exactly on $\mathbf e_k$ at $t_{k+1}$. By Lemma A, $D_{k+1} \le \rho \le s\varepsilon$. At step $k+1$, $H$ plays PP with $D_{k+1} \le s\varepsilon < L$, and Corollary C captures by $t_{k+2}$.
- **$D_k \le s\varepsilon$.** Here $D_k < L$, so Corollary C captures by $t_{k+1}$.

The count of steps is as in Theorem 1.

*Proof of part 2.* Assume $\alpha_C > s$, so $\rho > s\varepsilon$; also $\rho < L$.
- Start both agents fresh and collinear, with $D(0) \in (s\varepsilon, L]$.
- Let the runner move forever at $R_E\hat{\mathbf u}_0$. All motion stays on one line.
- At $t_0$, $H$ brakes and lands on $\mathbf e_0$ at $t_1$, while the runner is $\rho$ further on. So $D_1 = \rho \in (s\varepsilon, L)$.
- By induction, $D_k = \rho$ for all $k \ge 1$, and $H$ brakes forever.
- On each interval the separation is affine between $D_k$ and $D_{k+1}$, so it never drops below $\min(D(0), \rho) > s\varepsilon \ge \varepsilon$. ∎

The construction needs the specific start $D(0) \in (s\varepsilon, L]$. From a far start, the approach steps can land the separation in $(\varepsilon, s\varepsilon]$, where $H$'s pure-pursuit step captures. An escape construction only requires *some* initial state, so this is enough.

**Remarks.**
- At $\alpha_C = s$, the straight-flee runner gives $D_{k+1} = s\varepsilon$, and PP then touches the ball exactly: capture by tangency.
- $H$ uses $\varepsilon$ and speeds below $R_C$, so it is not admissible in the exact-speed model. In that model the best proven guarantee remains Theorem 1.
- Theorem 3 does not contradict Theorem 2. At $s = 2$ and $\alpha_C = 1.9 > \alpha_{\rm sym}(2)$, the symmetric-pass runner of Theorem 2 escapes PP but is captured by $H$. This is checked in `test_hybrid_captures_up_to_alpha_s`.

### 3.5 Policy separation (Theorem 5) — *Rev 2*

> **A change of chasing strategy alone can turn a game that admits indefinite evasion into one with guaranteed capture.** The speeds, decision clocks and capture radius stay the same.

> **Lemma S.** For every $s > 1$, $\tfrac14 < G(s) \le \big(\tfrac{1+s}{2s}\big)^2$. Equivalently,
> $$\frac{2s}{1+s} \le \alpha_{\rm sym}(s) < 2.$$

*Proof.*
- **Upper bound on $\alpha_{\rm sym}$.**
  - Since $\frac{d}{dy}\frac{y}{s-y} = \frac{s}{(s-y)^2}$, it follows that $g'(y) = 2y - \frac{s(s^2-1)}{4(s-y)^2}$.
  - At $y = s/2 \in (0,s)$: $g(s/2) = \frac{s^2}{4} - \frac{s}{2}\cdot\frac{s^2-1}{2s} = \frac14$ and $g'(s/2) = s - \frac{s^2-1}{s} = \frac1s > 0$.
  - So $g > \frac14$ just to the right of $s/2$. Hence $G(s) > \frac14$, i.e. $\alpha_{\rm sym}(s) < 2$.
- **Lower bound.** Suppose $\alpha_{\rm sym}(s) < 2s/(1+s)$. Pick $\alpha_C$ strictly between the two. Theorem 2 then gives an escape from PP at $\alpha_C \le 2s/(1+s)$, which contradicts Theorem 1. ∎

(The lower bound can be strict. Only the weak inequality is needed here.)

> **Theorem 5 (policy separation; bounded-speed model).** Let $s > 1$ and $\alpha_{\rm sym}(s) < \alpha_C \le s$. Let $\mathcal R$ be any runner class with $\mathcal R^{\rm al}_1 \subseteq \mathcal R \subseteq \mathcal R_{\rm free}$, for example $\mathcal R_{\rm all}$, and take $\mathcal I = \mathcal I_{\rm all}$.
> - **(a) PP does not guarantee capture.** There is an initial state and a runner in $\mathcal R^{\rm al}_1$ that PP never captures.
> - **(b) $H$ guarantees capture.** The hybrid chaser $H$ of Theorem 3 captures every runner in $\mathcal R_{\rm free}$, from every initial state with $D(0) > \varepsilon$, by time $\varphi_C + (K+2)\tau_C$.
>
> Consequently
> $$\kappa_{\rm PP}(s;\mathcal R,\mathcal I_{\rm all}) \;\le\; \alpha_{\rm sym}(s) \;<\; \alpha_C \;\le\; s \;\le\; \kappa^\*(s;\mathcal R,\mathcal I_{\rm all},\text{bounded}).$$
>
> **When the interval is non-empty.** The interval $(\alpha_{\rm sym}(s), s]$ is non-empty for every $s \ge 2$, by Lemma S.
> - Numerically, $\alpha_{\rm sym}(s) < s$ exactly when $s > s_0 \approx 1.7078$. This value was computed, not proven.
> - For $\mathcal R \supseteq \mathcal R^{\rm al}_m$, the certificates widen the interval to $(\hat\alpha(s,m), s]$. For example it is $(1.6540, 2]$ at $s = 2$ with $m = 16$.

*Proof.*

**(a)** Theorem 2 applies, because $\alpha_C > \alpha_{\rm sym}(s)$. Its runner decides only at the chaser's decision times, so it belongs to $\mathcal R^{\rm al}_1$. Its initial state belongs to $\mathcal I_{\rm all}$, and PP never captures it.

**(b)** This is Theorem 3, part 1. The argument is restated here so that this section stands alone. It uses Lemmas A and B and Corollary C of §3.2.

*Setting up.* If $\alpha_C \le 1$, then $s\varepsilon \ge L$. So $H$ plays PP whenever $D_k \le L$, and plays BP at full speed (which equals PP) whenever $D_k > L$. Proposition 1 then applies. So assume $1 < \alpha_C \le s$. Then:
- $s\varepsilon = L/\alpha_C < L$;
- $\rho = \alpha_C\varepsilon \le s\varepsilon$.

*Each step.* Consider a chaser decision $t_k$ with no capture yet, so $D_k > \varepsilon$.
- **$D_k > L$.** BP has speed $\min(R_C, D_k/\tau_C) = R_C$, so it plays PP. Lemma B(i) gives $D_{k+1} \le D_k - (L-\rho)$.
- **$s\varepsilon < D_k \le L$.** BP has speed $D_k/\tau_C \le R_C$, which is admissible in the bounded-speed model.
  - The chaser arrives exactly at $\mathbf e_k$ at $t_{k+1}$.
  - By Lemma A, $D_{k+1} \le \rho \le s\varepsilon$.
- **$\varepsilon < D_k \le s\varepsilon$.** $H$ plays PP, and $D_k < L$. By Lemma B(ii)(a), at $t_k + D_k/R_C$ the chaser is at $\mathbf e_k$ and the runner is within $D_k/s \le \varepsilon$ of it. This is capture.

*Putting the steps together.*
- The first case can repeat at most $K = \lceil (D_1 - L)^+/(L-\rho) \rceil$ times.
- After that, $D \le L$. Either $D \le s\varepsilon$ already, giving capture within one period, or one braking step brings it to $\le s\varepsilon$ and the next period captures.
- Before the first chaser decision, the runner and chaser move for at most $\varphi_C$, and $D_1 \le D(0) + (R_C + R_E)\varphi_C$.

None of this uses the runner's schedule, phase or information. Only Lemma A concerns the runner. ∎

**Corollary 5.1 (the instance $s = 2$, $\alpha_C = 19/10$).** In the bounded-speed model, with $R_C = 2R_E$ and $R_E\tau_C = 1.9\,\varepsilon$:
1. **PP is evaded forever** by the following explicit runner. Take $y = 6/5$. Then
   $$g(6/5) = \tfrac{36}{25} - \tfrac{9}{8} = \tfrac{63}{200} > \tfrac{100}{361} = \alpha_C^{-2},$$
   since $63\cdot 361 = 22743 > 20000$. Also $\cos^2\theta = \frac{3}{4\cdot(6/5)(4/5)} = \frac{25}{32} \in (0,1)$.
   - Start at separation $D = \tfrac65 R_E\tau_C$, with both agents deciding at $t = 0$.
   - At each chaser decision the runner plays, in the frame $(\hat{\mathbf u}_k, \hat{\mathbf n}_k)$, the velocity
   $$\mathbf v_E = R_E\left(\tfrac18,\ \tfrac{3\sqrt7}{8}\right), \qquad \|\mathbf v_E\|^2 = R_E^2\cdot\tfrac{1 + 63}{64} = R_E^2.$$
   - This is the Theorem 2 rule: $R_C\hat{\mathbf u} + (2D\cos\theta/\tau_C)(-\cos\theta,\ \sin\theta) = (2 - \tfrac{15}{8},\ \tfrac{3\sqrt 7}{8})$ in units of $R_E$.
   - Its closest approach in every period is $\sqrt{63/200}\,R_E\tau_C \approx 0.5612\,R_E\tau_C = 1.0664\,\varepsilon$.
   - The exact rational certificate `theory/certificates/orbits/s2-1_m01.json` (valid for $\alpha_C \ge 1.7807$) proves the same thing with rational velocities.
2. **The hybrid chaser $H$ captures every runner** from every initial state, by $\varphi_C + (K+2)\tau_C$, because $\alpha_C = 1.9 \le 2 = s$.
3. **Therefore** $\kappa_{\rm PP}(2;\mathcal R,\mathcal I_{\rm all}) < 1.9 < \kappa^\*(2;\mathcal R,\mathcal I_{\rm all},\text{bounded})$ for every $\mathcal R \supseteq \mathcal R^{\rm al}_1$.

**Why this shows PP is not optimal for guaranteed capture.**
- *Definition.* Call a chaser strategy *guarantee-optimal* for a configuration if it guarantees capture at every $\alpha_C$ at which **some** admissible chaser does; that is, if $A_{\sigma_C} = A^\*$.
- *Application.* By Theorem 5, $1.9 \in A^\* \setminus A_{\rm PP}$ at $s = 2$. So PP is not guarantee-optimal for any configuration with $\mathcal R \supseteq \mathcal R^{\rm al}_1$ and $\mathcal I = \mathcal I_{\rm all}$ in the bounded-speed model.
- *Strength of the conclusion.* This is a statement about uniform guarantees. It does not say PP does worse against every runner or from every start. It says that at these parameters PP admits an indefinitely evading runner, while $H$ admits none.

**The mechanism.**
- When $D_k \le L$, PP flies *through* the observed point $\mathbf e_k$ and ends $L - D_k$ beyond it. The symmetric pass is built so that this overshoot hands back exactly the separation $D$ the runner started with.
- $H$ removes the overshoot in the middle range $s\varepsilon < D \le L$. It brakes onto $\mathbf e_k$, which leaves at most $\rho \le s\varepsilon$ of separation. From there a full-speed pass leaves the runner a sidestep budget of only $D/s \le \varepsilon$, and that is capture.

**What is not claimed.**
- **$H$ is not claimed to be optimal.** Theorem 3 part 2 shows that $H$ itself fails above $\alpha_C = s$. Other chasers may succeed there, and $\kappa^\*$ may exceed $s$. Whether $\kappa^\*$ is even finite is open.
- **No separation is claimed in the exact-speed model.** There $H$ is not admissible, because it brakes.
- **The PP escape is proven only from a specific initial state with aligned clocks.** The theorem quantifies over $\mathcal I_{\rm all}$ and over runner classes containing $\mathcal R^{\rm al}_1$, and over nothing narrower.

*Evidence and reproduction.*
- `tests/test_theory_scenarios.py::test_hybrid_captures_up_to_alpha_s` runs the $(2, 19/10)$ case: the symmetric-pass runner escapes PP for 200 periods and is captured by $H$ within the Theorem 3 bound.
- `test_policy_separation_instance_exact` checks the rational facts of Corollary 5.1 exactly.
- The figure `figures/stage3/policy_separation.{png,pdf}` comes from `experiments/policy_separation.py`, which makes two deterministic engine runs. Its numbers are in `results/stage3/policy_separation.txt`: PP's minimum separation over 40 periods is $1.0670\,\varepsilon$ (the optimal $y$, not $6/5$), and $H$ captures at $t = 1.295\,\tau_C$.

---

## 4. Theorem 2 — the period-1 symmetric-pass escape

### 4.1 Setting and statement

**Setting.**
- **Normalisation.** Write $y = D/(R_E\tau_C)$. The pass profile is
$$g(y) = y^2 - \frac{y\,(s^2-1)}{4(s-y)}, \quad 0 < y < s, \qquad G(s) = \max_{0<y<s} g(y), \qquad \alpha_{\rm sym}(s) = G(s)^{-1/2}.$$
- **Clocks.** $\tau_E = \tau_C/m$ for some integer $m \ge 1$ (the construction only uses $m = 1$ behaviour), with the runner's lattice containing the chaser's. In particular $a = 1$ with $\varphi_E = \varphi_C$ qualifies.

> **Theorem 2.** Let $s > 1$ and $\alpha_C > \alpha_{\rm sym}(s)$. Pick any $y \in (0, s)$ with $g(y) > \alpha_C^{-2}$; one exists by the definition of $G$. Set
> $$D = y\rho, \qquad \cos^2\theta = \frac{s^2-1}{4y(s-y)}, \qquad \theta \in (0, \pi/2).$$
> **Initial state.** $\mathbf x_C(0) = 0$ and $\mathbf x_E(0) = (D, 0, \dots, 0)$. Both agents decide at $t = 0$, so both start fresh and $\varphi_C = \varphi_E = 0$.
>
> **Runner rule.** At each chaser decision $t_k$, let $\hat{\mathbf u}_k = (\mathbf e_k - \mathbf c_k)/D_k$, and let $\hat{\mathbf n}_k$ be $\hat{\mathbf u}_k$ rotated by $+\pi/2$ in the plane of motion. The runner plays
> $$\mathbf v_E = R_C\hat{\mathbf u}_k + \frac{2D\cos\theta}{\tau_C}\big(-\cos\theta\,\hat{\mathbf u}_k + \sin\theta\,\hat{\mathbf n}_k\big),$$
> and holds it for the whole chaser period. If $m > 1$, it re-selects the same velocity at its intermediate decisions.
>
> **Conclusion.** Against PP:
> 1. $\|\mathbf v_E\| = R_E$ at every period;
> 2. $D_k = D$ for every $k$;
> 3. the minimum separation over each period is exactly $D\sin\theta = \rho\sqrt{g(y)} > \varepsilon$;
> 4. the runner is never captured.

### 4.2 Proof

1. **Frame.** At $t_k$, translate and rotate so that $\mathbf c_k = 0$ and $\mathbf e_k = (D_k, 0)$. PP plays $\mathbf v_C = (R_C, 0)$. Write the relative velocity as
$$\mathbf w = \mathbf v_E - \mathbf v_C = |\mathbf w|(-\cos\theta, \sin\theta), \qquad |\mathbf w| = 2D\cos\theta/\tau_C.$$
The relative position is $\mathbf r(\sigma) = (D_k, 0) + \sigma\mathbf w$ for $\sigma \in [0, \tau_C]$.

2. **Speed.** One has
$$\|\mathbf v_E\|^2 = |\mathbf w|^2 - 2R_C|\mathbf w|\cos\theta + R_C^2 = R_C^2 - \frac{4D\cos^2\theta}{\tau_C}\left(R_C - \frac{D}{\tau_C}\right) = R_E^2\left(s^2 - 4\cos^2\theta\, y(s - y)\right).$$
The choice of $\cos^2\theta$ makes this exactly $R_E^2$. Consistency requires $\cos^2\theta \in (0,1)$:
   - $\cos^2\theta > 0$ because $s > 1$ and $0 < y < s$;
   - $\cos^2\theta < 1$ because $g(y) > 0$ is equivalent to $\frac{s^2-1}{4(s-y)} < y$, i.e. $\cos^2\theta < 1$.

3. **Return to $D$, by induction on $k$.** Suppose $D_k = D$. Then
$$\|\mathbf r(\tau_C)\|^2 = D^2 + 2\tau_C D\,\mathbf w_x + \tau_C^2|\mathbf w|^2 = D^2 - 2\tau_C D|\mathbf w|\cos\theta + \tau_C^2|\mathbf w|^2 = D^2,$$
because $\tau_C|\mathbf w| = 2D\cos\theta$. Hence $D_{k+1} = D$.

4. **Minimum over the whole period.** $\|\mathbf r(\sigma)\|^2$ is a convex quadratic in $\sigma$. Its minimiser is $\sigma_\* = D\cos\theta/|\mathbf w| = \tau_C/2$, which lies inside the period, and the minimum value is $D^2\sin^2\theta$. Then
$$D^2\sin^2\theta = y^2\rho^2\left(1 - \frac{s^2-1}{4y(s-y)}\right) = \rho^2 g(y) > \rho^2\alpha_C^{-2} = \varepsilon^2.$$
At the endpoints the separation is $D > D\sin\theta > \varepsilon$. So no capture occurs in $[t_k, t_{k+1}]$.

5. **Exact recurrence of the whole state.** Let $\Phi_k$ be the orientation-preserving isometry that maps the frame at $t_k$ to the standard frame.
   - PP is equivariant under isometries.
   - The runner rule is equivariant under orientation-preserving isometries, because $\hat{\mathbf n}_k$ is built by a fixed rotation.
   - In standard frames, the configuration at $t_k$ is identical for every $k$: separation $D$, both agents deciding, both clock phases $0 \bmod \tau_C$.
   - The committed velocities at $t_k^-$ do not enter the decisions at $t_k$, because both agents re-decide then.
   - So, by induction, the full state at $t_{k+1}$ is the image of the state at $t_k$ under one fixed orientation-preserving isometry $g$.

   The state means positions, the velocities committed at $t^-$, and both clocks.

6. **Relative versus absolute coordinates.**
   - In **relative coordinates** (separation, velocities relative to the line of sight, clock phases), the state recurs **exactly** with period $\tau_C$.
   - In the plane, from the computation in step 3, the line of sight rotates by $\psi = \pi - 2\theta \in (0, \pi)$ per period. So $g$ is a rotation through $\psi \notin 2\pi\mathbb Z$, and therefore a rotation about a fixed centre $\mathbf z$.
   - Both agents' positions at the times $t_k$ lie on two fixed circles about $\mathbf z$, and their paths are bounded.
   - The **absolute** trajectory is exactly periodic if and only if $\psi/2\pi \in \mathbb Q$. Otherwise it is bounded and quasi-periodic, but it never captures.

7. **Indefinite repetition.** Steps 3–5 hold for every $k$ by induction. Each period is capture-free by step 4. ∎

**Information.** The runner uses only $\mathbf c_k$ and $\mathbf e_k$, which it observes at $t_k$. It never uses PP's new velocity at the simultaneous decision.

The rule does not even need to know the chaser plays PP. However, its *success* is established only against PP.

### 4.3 Remaining checks

**Threshold.**
- At $\alpha_C = \alpha_{\rm sym}(s)$, the best pass has minimum exactly $\varepsilon$, which is capture (closed ball), so this family gives no escape.
- For $\alpha_C > \alpha_{\rm sym}$, a whole interval of admissible $y$ gives a positive margin.

**Exact versus bounded speed.**
- As stated, the runner moves at exactly $R_E$, so the orbit is admissible in **both** speed models.
- Slower runners also work. With $\cos^2\theta$ above its minimum, $\|\mathbf v_E\|^2 = R_E^2(s^2 - 4\cos^2\theta\,y(s-y)) < R_E^2$, and the miss $D\sin\theta$ decreases continuously. So whenever $\alpha_C > \alpha_{\rm sym}$, there are orbits with $\|\mathbf v_E\| < R_E$, though only in the bounded-speed model.

**Higher dimensions.**
- All motion lies in the plane spanned by the initial line of sight and $\hat{\mathbf n}_0$. PP keeps the chaser on the line of sight, so it never leaves that plane.
- The orbit therefore embeds unchanged in $\mathbb R^d$ for $d \ge 2$, and the proof is unchanged.
- In $d = 1$ there is no sidestep, and no escape from PP exists: PP catches any one-dimensional runner, since $s > 1$.

**Values.**

| $s$ | 1.05 | 1.2 | 1.5 | 2 | 3 | 10 | $\to\infty$ |
|---|---|---|---|---|---|---|---|
| $2s/(1+s)$ (Thm 1) | 1.0244 | 1.0909 | 1.2000 | 1.3333 | 1.5000 | 1.8182 | 2 |
| $\alpha_{\rm sym}(s)$ (Thm 2) | 1.2251 | 1.4343 | 1.6301 | 1.7806 | 1.8964 | 1.9901 | 2 |

As $s \to \infty$, both columns tend to 2, which determines $\kappa_{\rm PP}(\infty) = 2$ for aligned runners. Indeed $g(s/2) = 1/4$ for every $s$, so $\alpha_{\rm sym} \le 2$, and $2s/(1+s) \to 2$.

---

## 5. Theorem-status table

The "Spec" column gives the label used in `stage0_spec.md`.

### 5.1 Proven

| Result (Spec label) | Statement | Assumptions | Evidence | Limitations | H |
|---|---|---|---|---|---|
| Escape lemma (B.1) | If $R_E \ge R_C$, a runner that flees at each of its decisions with $D > \varepsilon$ is never caught. | Unbounded space; any chaser | Proof: triangle inequality. | Needs the runner free to choose its direction. | H4 |
| Interception lemma; $s \le 1$ outcome (B.1a/b) | Capture by $T$ is possible iff $\exists t \le T$ with $\lVert\mathbf e(t)-\mathbf c_0\rVert \le R_C t + \varepsilon$. For $s \le 1$, the outcome is decided in the runner's first commitment window. | Known constant runner velocity; perfect information | Proof. | Unbounded space. | H4 |
| Prop 1 (B.2) | PP captures every runner if $\alpha_C \le 1$. | Either speed model; any runner; any $d$ | Proof. | Superseded by Thm 1. | H1 |
| **Thm 1 (B.2b, "Prop 1′")** | PP captures every runner if $\alpha_C \le 2s/(1+s)$; explicit time bound. | Either speed model; any runner schedule, phase or information; any $d$ | Proof, §3. Engine checks at and 3% below the bound against 5 runner types, including the best-response planner. | Not known to be sharp. | H1 falsified |
| BP threshold (B.2a) | BP captures every runner iff $\alpha_C \le 1$. | Bounded-speed model | Proof; witness is straight flee. | BP specifically. | H2 |
| BP is not dominated by PP (B.2a, clarification) | There is a runner that BP catches and PP misses. | $R_C=4$, $R_E=2$, $\tau_C=1$, $\tau_E=1/4$, $\varepsilon=0.1$; explicit scripted runner | Hand computation plus regression test. | A single example. | H2 |
| **Thm 3** (new; spec Rev 4 §B.2c) | The hybrid BP/PP chaser captures every runner iff $\alpha_C \le s$. | Bounded-speed model; chaser knows $\varepsilon$ | Proof, §3.4; engine checks just inside and just outside the bound. | Not admissible with exact speed. Only a lower bound on the best chaser. | H2 |
| **Lemma M** (Rev 2) | Guarantees are monotone in $\alpha_C$ when only $\varepsilon$ varies; thresholds are suprema of intervals. | Runner class closed under open-loop replay; fixed speeds, clocks, phases and initial-state class | Proof, §2.4. | Not about families that move $D(0)$ or the horizon with $\alpha_C$, as the sweeps do. | — |
| **Lemma S** (Rev 2) | $2s/(1+s) \le \alpha_{\rm sym}(s) < 2$. | $s > 1$ | Proof, §3.5. | — | H1, H2 |
| **Thm 5** (Rev 2) | Policy separation: for $\alpha_{\rm sym}(s) < \alpha_C \le s$, PP admits an indefinitely evading runner, while $H$ captures every runner. Instance: $s = 2$, $\alpha_C = 1.9$. | Bounded-speed model; runner class contains aligned runners; all initial states | Proof, §3.5; exact instance check; engine check; figure. | $H$ not claimed optimal; nothing claimed in the exact-speed model. | H2 |
| Scale invariance (lemma) | If neither strategy uses $\varepsilon$, scaling space and time by $\lambda$ maps trajectories to trajectories. So the outcome depends on $\alpha_C$ only through comparing $\varepsilon$ with the closed loop's scale-free closest approach. | Policies independent of $\varepsilon$ | Proof: immediate. | Not for $H$ or the planner. | — |

### 5.2 Constructively demonstrated

| Result (Spec label) | Statement | Assumptions | Evidence | Limitations | H |
|---|---|---|---|---|---|
| **Thm 2 (B.3a, "Prop 3")** | Exact periodic escape from PP for $\alpha_C > \alpha_{\rm sym}(s)$. | Runner lattice contains the chaser's; specified initial state | Proof, §4; engine run of 3,000 periods with drift $< 10^{-11}$. | Against PP only. Aligned clocks only. | H1, H2, H5 |
| **Thm 4** (new; Rev 4 §B.3b) | Exact periodic escape from PP for $\alpha_C \ge \alpha_c(s,m)$, for the 15 pairs in §7. | $\tau_E = \tau_C/m$, aligned | **Computer-assisted proof in exact rational arithmetic**; re-checked by independent code. *Rev 2:* standalone standard-library verifier `theory/certificates/verify.py`, with negative tests; all legs have unit speed, so both speed models are covered. | Specific $(s, m)$ only, not a formula in $s$. Specific initial state; aligned clocks. | H1 |

### 5.3 Numerically supported

| Result | Statement | Evidence | Limitations | H |
|---|---|---|---|---|
| Multi-leg optimum | $\alpha^\*_m(s)$ decreases slowly with $m$, e.g. 1.630 → 1.540 for $s=1.5$, $m = 1 \to 16$; period-2 search returns period-1 solutions. | SLSQP with 40 random starts; nesting checks. | Not a global optimality certificate; the limit $m \to \infty$ is not computed. | H1′ |
| No escape near the lower bound | Planner found no escape at any swept $\alpha_C \le 7/5$, with random phases, at $s \in \{1.2, 1.5, 2\}$ and $a \in \{1/4, 1, 2\}$. | 5,184-game sweep, 3 planner configurations. | Planner is incomplete; the $\alpha_C$ grid is coarse. | H1′ |
| Phase dependence | The same states give escape 12/12 with aligned clocks and 0/12 with random phases, at ($s=1.5$, $\alpha_C=1.6$) and ($s=1.2$, $\alpha_C=1.4$). | Planner runs. | Planner-dependent. | H3 |
| Perpendicular orbit | The perpendicular runner against PP converges geometrically (factor ≈ 0.556 per period) to a fixed point $D^\*/(R_E\tau_C) \approx 1.055$, with closest approach $\approx 0.521\,R_E\tau_C$ ($s=1.5$, $a=1/4$). | Long runs. | No proof of the fixed point. | — |
| Less agile runner escapes PP | $a = 2$, i.e. the chaser is faster *and* more agile: planner escapes 12/12 at $s=1.2$, $\alpha_C=5/2$. | Planner runs. | No construction. | Case 1 |

### 5.4 Conjectural

| Claim | Status |
|---|---|
| **H1′:** for aligned runners with $m \to \infty$, $\kappa_{\rm PP}(s)$ equals the limit of the periodic-orbit thresholds. Equivalently, the optimal evasion of PP is period-1. | Supported only by the numerics in 5.3. |
| The guarantee region of PP is an interval in $\alpha_C$ (monotonicity). | Unproven. *Rev 2: proven (Lemma M), moved to 5.1.* |
| Runners not aligned with the chaser's clock can escape PP at some finite $\alpha_C$. | Planner evidence at $\alpha_C \ge 8/5$; no construction. |
| $\kappa^\*(s) < \infty$ for the best chaser (upper half of H2). | Open. Theorem 3 gives $\kappa^\* \ge s$. |

### 5.5 Falsified

| Hypothesis | How |
|---|---|
| **H1 (original):** PP's threshold against agile runners is exactly $\alpha_C = 1$. | Theorem 1. |
| "BP never beats PP" (Stage 2, empirical). | Explicit counterexample. |
| "Stage 2 heuristics find the escape boundary." | The planner and the certified orbits escape at $\alpha_C$ where the heuristics never did. |

---

## 6. Numerical results and their limitations

### 6.1 Sweep setup

| Parameter | Value |
|---|---|
| Normalisation | $\varepsilon = R_E = 1$, so $\alpha_C = \tau_C$ |
| Initial separation | $D_0 = 10$ |
| $s$ | $\{1.2, 1.5, 2.0\}$ |
| $\alpha_C$ | $\{1, 21/20, 11/10, 6/5, 7/5, 8/5, 2, 5/2\}$ |
| $a$ | $\{1/4, 1, 2\}$ |
| Initial states | 12 paired states, with random line of sight and headings, and phases $j/32$ of each period (seed 2027) |
| Horizon | $H = (D_0 + \tau_C)/(s-1) + 43\tau_C$ |
| Runners | flee, perpendicular, predictive, and the planner in 3 configurations: (24 directions, beam 32, horizon 2 chaser periods), (24, 96, 4), (48, 64, 4) |

The sweep has 5,184 games and is reproducible bit for bit. Its CPU cost is about 1,800 s, and that figure is not itself reproducible. Files: `results/stage3/sweep.csv`, `figures/stage3/escape_vs_alpha.*`.

**"Escape" below always means "no capture within $H$".** It never means a proven infinite escape.

**Escapes out of 12, for the planner (any of its 3 configurations):**

| $s$ \ $a$ | 1/4 | 1 | 2 |
|---|---|---|---|
| 1.2 | 0 up to 7/5; 12 at 8/5; 12; 12 | 0 up to 7/5; 7; 11; 12 | 0 up to 8/5; 4; 12 |
| 1.5 | 0 up to 8/5; 12; 12 | 0 up to 8/5; 11; 12 | 0 up to 2; 9 |
| 2.0 | 0 up to 8/5; 12; 12 | 0 up to 8/5; 11; 12 | 0 up to 2; 10 |

Each cell lists the counts at the swept $\alpha_C$ values in increasing order, starting where they first become nonzero.

**Other observations.**
- No game was ever won by the runner at $\alpha_C \le 2s/(1+s)$, by any runner. This is consistent with Theorem 1, which is not a test of it.
- Clearance: among the 548 planner survivals, the median minimum separation is $1.20\varepsilon$ and the smallest is $1 + 8.6\times10^{-4}$ in units of $\varepsilon$. No survival rests on a floating-point near-tangency.
- Of all captures, 193 of 4,473 happen after $H/2$. The finite horizon therefore matters somewhat, and longer horizons could convert some "escapes" into captures.

### 6.2 The best-response planner

**State and model.**
- The runner plans against a *known* PP chaser. PP depends only on positions, so the chaser's future is a deterministic function of the runner's future path, and best response becomes single-agent planning.
- The planner's state is the pair of positions, the chaser's committed velocity, and the exact (rational) times of all future chaser and runner decisions within the horizon.

**Actions.** At each of its decisions, the runner chooses one of:
- $n_{\rm dirs}$ headings, evenly spaced from "directly away from the chaser", times speed fractions (default: full speed only); or
- "hold the current velocity". This is fix 1.

**Horizon.** $\lceil h\,\tau_C/\tau_E\rceil$ runner legs, capped at a maximum depth. Here $h \in \{2, 4\}$ is the horizon in chaser periods.

**Search.** Beam search over leg sequences.
- Each leg is simulated exactly in a vectorised rollout. The chaser re-aims by PP at its true decision times inside the leg, and capture is detected by the closed-form first-contact formula.
- The rollout is tested against the main engine for random plans, with agreement to $10^{-12}$, including captures between decisions.

**Ranking.** Lexicographic: (survived the horizon; later capture; larger minimum separation). Partial plans are ranked after **completing them to the horizon by holding their last velocity**. This is fix 2. Ties go to the earlier candidate, so the search is deterministic.

**Clocks.**
- Chaser and runner decision times are exact rationals, generated from the observed phase and periods.
- At a simultaneous decision, the chaser's new velocity is computed from the PP rule and the current positions, never observed. A test checks that the plan is independent of the chaser's stale velocity when the chaser decides now.

**Information.** The planner reads only the `Observation` object. It is a stateless function of that observation, and tests check determinism and statelessness.

**Complexity.** Per runner decision the cost is $O(\text{depth}\cdot B\cdot A\cdot(1+\text{events per leg}))$ for expansion, plus $O(\text{depth}^2\cdot B\cdot A)$ leg-simulations for the completion rollouts. Here $A = n_{\rm dirs}\cdot|\text{speeds}| + 1$.

**The two defects, found by starting the planner on states where an escape provably exists:**
1. *No "hold velocity" action.* Headings were measured relative to the current line of sight, which rotates. So "keep going straight" was almost never available, and a runner with 4 decisions per chaser period could not copy a 1-decision runner.
2. *Myopic pruning.* Ranking partial plans by their prefix discarded exactly the plans that head toward a close tangent pass, because they look worse than fleeing until the pass happens.

**Ablation.** Started on certified orbit states with aligned clocks, at margins of 2/5/15/30% above the orbit's threshold, with 3 values of $s$ each (`results/stage3/planner_ablation.txt`):

| Orbit | Configuration | No fixes | Hold only | Rollout only | Both |
|---|---|---|---|---|---|
| Thm 2 symmetric pass ($a = 1$) | small | 2/2/3/3 | 2/2/3/3 | 2/2/3/3 | 2/2/3/3 |
| Thm 2 symmetric pass ($a = 1$) | large | 3/3/3/3 | 3/3/3/3 | 3/3/3/3 | 3/3/3/3 |
| 4-leg orbit ($a = 1/4$) | small | 0/0/0/3 | 0/0/0/2 | 0/3/3/3 | 0/3/3/3 |
| 4-leg orbit ($a = 1/4$) | large | 0/0/0/2 | 0/0/0/2 | 3/3/3/3 | 3/3/3/3 |

Entries are escapes out of 3, at margins 2%/5%/15%/30%.

- **Rollout-completed ranking is the decisive fix.**
- The hold action matters at the margin. The regression test (`test_both_planner_fixes_needed_near_threshold`) is a state at a 2.6% margin, small configuration, where *only* both fixes together escape.
- **The corrected planner still fails at 2% margins with the small configuration.** It is not a reliable detector of escape near a threshold.

**Original versus corrected, same sweep** (`sweep_original_planner.csv`, `figures/stage3/planner_comparison.*`):
- 14 states escape only with the corrected planner; none escape only with the original.
- The largest change is at $s = 2$, $\alpha_C = 2$: from 4 to 12 states at $a = 1/4$, and from 8 to 11 at $a = 1$.
- The location of the first swept $\alpha_C$ with any escape is unchanged by the fixes.
- The planner configurations still disagree in places. For example, at $s = 2$, $a = 1$, $\alpha_C = 2$: 6, 11 and 11 of 12.

**Limitations.**
- Discrete headings.
- Finite horizon and greedy beam search: no optimality certificate of any kind.
- The planner is a lower bound on the runner's capability. Its failures say nothing about capture.

---

## 7. Higher-period and multi-leg orbits; exact certification

### 7.1 Optimisation problem

The runner's clock is aligned, with $\tau_E = \tau_C/m$. At every chaser decision the state, modulo isometries, is just $D$. A **period-$P$ orbit** is a sequence of $P$ passes, $D_1 \to D_2 \to \dots \to D_P \to D_1$. Each pass consists of $m$ straight runner legs, written in the frame of that chaser period.

The objective is to maximise the worst closest approach $M$ over the cycle, in units of $\rho$. The orbit then escapes iff $\alpha_C > 1/M$. Because the closed loop does not depend on $\varepsilon$, the scale-invariance lemma applies.

Results (`results/stage3/orbits.json`, `orbit_table.md`; SLSQP from 40 random starts, plus a warm start from the $m/2$ optimum with every leg split in two):

| $s$ | $m$ | $\alpha^\*$ (float) | $D/\rho$ | Closure residual | Clearance at $1.01\alpha^\*$ | 2,000 periods at $1.01\alpha^\*$ | At $0.99\alpha^\*$ |
|---|---|---|---|---|---|---|---|
| 1.2 | 1 | 1.43427 | 0.9342 | 2e-13 | 1.01000 ε | no capture | caught by t = 0.42 |
| 1.2 | 2 | 1.40123 | 0.9421 | 7e-13 | 1.01000 ε | no capture | caught |
| 1.2 | 4 | 1.39752 | 0.9407 | 8e-14 | 1.01000 ε | no capture | caught |
| 1.2 | 8 | 1.39278 | 0.9392 | 7e-14 | 1.01000 ε | no capture | caught |
| 1.2 | 16 | 1.38892 | 0.9399 | 5e-14 | 1.01000 ε | no capture | caught |
| 1.5 | 1 | 1.63008 | 1.0208 | 4e-13 | 1.01000 ε | no capture | caught |
| 1.5 | 2 | 1.56953 | 1.0427 | 6e-12 | 1.01000 ε | no capture | caught |
| 1.5 | 4 | 1.55947 | 1.0400 | 3e-13 | 1.01000 ε | no capture | caught |
| 1.5 | 8 | 1.54739 | 1.0377 | 1e-13 | 1.01000 ε | no capture | caught |
| 1.5 | 16 | 1.53962 | 1.0409 | 6e-14 | 1.01000 ε | no capture | caught |
| 2.0 | 1 | 1.78061 | 1.2140 | 7e-13 | 1.01000 ε | no capture | caught |
| 2.0 | 2 | 1.70087 | 1.2572 | 8e-13 | 1.01000 ε | no capture | caught |
| 2.0 | 4 | 1.68468 | 1.2544 | 1e-12 | 1.01000 ε | no capture | caught |
| 2.0 | 8 | 1.66613 | 1.2531 | 4e-12 | 1.01000 ε | no capture | caught |
| 2.0 | 16 | 1.65396 | 1.2605 | 4e-14 | 1.01000 ε | no capture | caught |

Robustness checks:
- **Period 2.** Every $P = 2$ optimisation returned $D_1 = D_2$ with the same value as $P = 1$. Asymmetric two-pass cycles gave no gain in 40 starts. That is evidence, not proof.
- **Agreement with theory.** At $m = 1$ the optimiser reproduces $\sqrt{G(s)}$ to six digits.
- **Nesting.** $M_{2m} \ge M_m$ holds throughout.
- **Convergence.** The sequence in $m$ is not converged: at $s = 1.5$ it still decreases by about 0.008 per doubling of $m$.

**A small closure residual is not a proof.** The float orbits above are numerical objects. Section 7.2 turns them into exact ones.

### 7.2 Exact certification (Theorem 4)

**Key observation.** Fix the $m$ leg velocities $\mathbf v_1, \dots, \mathbf v_m$ in the period frame, so the chaser runs from $0$ along $+x$ at speed $s$, with $\tau_C = R_E = 1$. The runner's endpoint is then $(D + X, Y)$, with $X, Y$ independent of $D$. The closure condition $\|(D + X - s, Y)\|^2 = D^2$ is therefore **linear** in $D$:
$$D^\* = \frac{(X - s)^2 + Y^2}{2(s - X)} \qquad (X < s).$$

**Certificate.** For given rational data, the following are checked in exact arithmetic:
1. **Rational velocities.** Each optimised heading is replaced by an exact rational unit vector, via the Pythagorean parametrisation $\big((1-t^2)/(1+t^2),\ 2t/(1+t^2)\big)$ with rational $t$. Each speed is replaced by a rational $q \le 1$.
2. $\|\mathbf v_j\|^2 \le 1$.
3. $D^\* > 0$, with closure *exact*.
4. On every leg, the minimum of the convex quadratic $\|\mathbf r_j + \sigma\mathbf w_j\|^2$ over $\sigma \in [0, 1/m]$ exceeds $\alpha_c^{-2}$. The minimiser $\sigma$ is rational, so this minimum is computed exactly.

> **Theorem 4 (computer-assisted).** For each $(s,m)$ in the table below, a runner with $\tau_E = \tau_C/m$, aligned with the chaser, starting at separation $D^\*\rho$ and replaying the certified legs in each period's frame, is never captured by PP, for every $\alpha_C \ge \alpha_c(s,m)$.

*Proof.*
- Items 2–4 give one capture-free period that returns to $D^\*$.
- The isometry argument of §4.2 step 5 then gives exact recurrence.
- For larger $\alpha_C$, i.e. smaller $\varepsilon/\rho$, the clearance only improves, by the scale-invariance lemma. ∎

| $s$ | $m$ | $D^\*/\rho$ | Clearance$/\rho$ | Certified $\alpha_c$ |
|---|---|---|---|---|
| 6/5 | 1 / 2 / 4 / 8 / 16 | 0.9342 / 0.9421 / 0.9407 / 0.9392 / 0.9399 | 0.69722 / 0.71366 / 0.71555 / 0.71799 / 0.71999 | 1.4343 / 1.4013 / 1.3976 / 1.3928 / **1.3890** |
| 3/2 | 1 / 2 / 4 / 8 / 16 | 1.0208 / 1.0427 / 1.0400 / 1.0377 / 1.0409 | 0.61347 / 0.63713 / 0.64124 / 0.64625 / 0.64951 | 1.6301 / 1.5696 / 1.5595 / 1.5474 / **1.5397** |
| 2 | 1 / 2 / 4 / 8 / 16 | 1.2140 / 1.2572 / 1.2544 / 1.2531 / 1.2605 | 0.56160 / 0.58794 / 0.59358 / 0.60019 / 0.60461 | 1.7807 / 1.7009 / 1.6847 / 1.6662 / **1.6540** |

**Reproduction.** The exact data, as fraction strings ($D^\*$, clearance², every leg velocity), are in `results/stage3/certified_orbits.json`.
- `python experiments/stage3.py certify` regenerates them.
- `tests/test_certificates.py` re-checks all 15 certificates from the JSON using code that shares nothing with the generator.
- Each certified orbit was also run in the floating-point engine for 500 periods at $1.001\,\alpha_c$ without capture. That run is a sanity check, not part of the proof.

**Choice of certification method.** Interval arithmetic and validated fixed-point methods were unnecessary, because the closure equation is linear once the legs are fixed. The same idea extends to period-$P$ cycles: $P$ linear closure equations in $(D_1, \dots, D_P)$.

What this does **not** give is the optimum over legs. A certified $\alpha_c$ is an upper bound on the threshold, and it is tight only to the extent that the optimiser found the true optimum.

### 7.3 Independent certificate package — *Rev 2*

The 15 certificates of Theorem 4 now live in `theory/certificates/` as self-contained files.
- **What a file records.** Each file records:
  - the exact $s$ and $m$;
  - the clock schedule ($\tau_E = \tau_C/m$, both phases 0);
  - $D_0$;
  - every leg's rational velocity, start time and duration;
  - PP's velocity;
  - the relative trajectory $\mathbf r_0 + t\mathbf w$ on each leg;
  - the exact minimiser and minimum on the closed leg interval;
  - the closure vector and the claimed $\alpha_c$.
- **Verifier.** `theory/certificates/verify.py` uses only the Python standard library and shares no code with the simulator, the optimiser or the generator. It recomputes everything from the primary data, accepting a certificate only if all of the following hold:
  1. **Speed.** $\|V_j\| \le 1$.
  2. **Schedule.** The leg times match the runner clock.
  3. **Pursuit.** The chaser's velocity is PP's, computed from positions with an exact rational square root.
  4. **Integration.** The legs are re-integrated exactly.
  5. **Closure.** The orbit closes exactly.
  6. **Clearance.** Every leg's closed-interval minimum exceeds $1/\alpha_c^2$ strictly.
  7. **Recurrence.** The runner policy, rotated into each period's frame, is executed for 3 periods in absolute coordinates with exact rational frames.
  8. **Records.** Every recorded derived value matches.
- **Result.** **15/15 verified.**
- **Negative tests.** `tests/test_certificate_package.py` covers:
  - overspeed;
  - a false exact-speed claim;
  - non-closure;
  - entering the ball;
  - an exact touch mid-leg;
  - four kinds of schedule violation;
  - a tampered record.

  Each is rejected for the stated reason. Output is byte-identical across processes and hash seeds.

**Proof from the data.** Checks 1–6 establish one capture-free period that returns to separation $D_0$ with both agents deciding. The isometry-equivariance argument of §4.2, step 5, then gives exact recurrence for every period. That argument is spelled out for the leg-schedule policy in `theory/certificates/README.md`. Check 7 independently executes that policy.

**Threshold convention.**
- For a certified orbit with exact minimum squared clearance $c$, write $\hat\alpha = 1/\sqrt c$. The orbit escapes iff $\alpha_C > \hat\alpha$; at $\alpha_C = \hat\alpha$ it touches the closed ball, which counts as capture.
- The stored $\alpha_c$ is $\hat\alpha$ rounded **up** to four decimals, with $1/\alpha_c^2 < c$ verified strictly. So "escape for every $\alpha_C \ge \alpha_c$" is correct with equality included.
- The sharper "escape for every $\alpha_C > \hat\alpha$" is also proven.

| $s$ | $m$ | $\hat\alpha(s,m)$ (10 digits) | certified $\alpha_c$ |
|---|---|---|---|
| 6/5 | 1 / 2 / 4 / 8 / 16 | 1.4342676433 / 1.4012340270 / 1.3975219111 / 1.3927787386 / **1.3889168761** | 1.4343 / 1.4013 / 1.3976 / 1.3928 / **1.3890** |
| 3/2 | 1 / 2 / 4 / 8 / 16 | 1.6300837216 / 1.5695293557 / 1.5594714977 / 1.5473856808 / **1.5396185998** | 1.6301 / 1.5696 / 1.5595 / 1.5474 / **1.5397** |
| 2 | 1 / 2 / 4 / 8 / 16 | 1.7806140964 / 1.7008681679 / 1.6846806900 / 1.6661329315 / **1.6539612377** | 1.7807 / 1.7009 / 1.6847 / 1.6662 / **1.6540** |

The $m = 1$ rational orbits reproduce $\alpha_{\rm sym}(s)$ to 10 digits.

**Corrections made in Rev 2.**
1. **Theorem 4 holds in both speed models.** §8 said it was "a bounded-speed statement unless every $q = 1$". Every leg of all 15 certificates has $\|V_j\| = 1$ exactly; the verifier checks this, and the files record `speed_model: exact`.
2. **Monotonicity in $\alpha_C$ is now proven** for configurations satisfying (R) (Lemma M, §2.4). It was previously listed as open (§2.3, §5.4).
3. **"No escape is proven for runners whose clock is not aligned"** is true only for classes that exclude alignment. For $\mathcal R_{\rm all}$, which contains the aligned runners, PP's threshold is bracketed (§2.5, item 3).
4. **"$\alpha_{\rm sym}(s) \in (1,2)$" is now proven** (Lemma S). It was previously asserted without proof.

**A worked example small enough to check by hand.** It is in `theory/certificates/examples/`.
- Take $s = 4/3$ and a runner that moves perpendicular to the line of sight at full speed, from $D_0 = 25/24$.
- The closest approach is exactly $5/8$, at mid-period, and the orbit closes exactly.
- So PP is evaded for every $\alpha_C > 8/5$, and at $\alpha_C = 8/5$ capture occurs by tangency.

---

## 8. The remaining capture–escape gap

Let $\mathcal R_m$ be the runners with $\tau_E = \tau_C/m$, whose phase is part of the initial state, so an escape may choose it. Any escape for $\mathcal R_1$ is also one for $\mathcal R_m$, because the runner re-selects the same velocity at its extra decisions.

| $s$ | Proven guarantee: $\kappa_{\rm PP} \ge 2s/(1+s)$ | Constructive escape for $\mathcal R_1$: $\alpha_{\rm sym}$ | Certified escape for $\mathcal R_{16}$ | Open interval for $\mathcal R_{16}$ | Planner, random phases (no escape / escape) | Planner, aligned clocks, $a = 1/4$ |
|---|---|---|---|---|---|---|
| 1.2 | 1.0909 | 1.4343 | 1.3890 | (1.0909, 1.3890) | 7/5 / 8/5 | escapes at 7/5 (12/12) |
| 1.5 | 1.2000 | 1.6301 | 1.5397 | (1.2000, 1.5397) | 8/5 / 2 | escapes at 8/5 (12/12) |
| 2.0 | 1.3333 | 1.7806 | 1.6540 | (1.3333, 1.6540) | 8/5 / 2 | none at 8/5 (consistent: $1.6 < 1.654$) |

**Which assumptions move the boundaries.**
- **Lower bound.** Theorem 1 is pathwise, so it holds for *every* runner class. Moving it up requires using the runner's geometry, not only its speed bound. The inequality (†) $D_k + D_{k+1} \le L + \rho$ credits the runner with a full mid-pass sidestep $D_k/s$ and a full end-of-pass displacement $\rho$, and no single path achieves both. Section 11 proposes how to exploit this.
- **Upper bound.**
  - The bound depends on clock alignment: every construction requires the runner to decide at the chaser's decision instants.
  - For runners with a fixed phase offset, or with $\tau_E/\tau_C \notin 1/\mathbb N$, no escape is proven. The planner at random phases first escapes at $\alpha_C \in \{8/5, 2\}$, and it also escapes at $a = 2$ for $\alpha_C \ge 2$.
  - So $\kappa_{\rm PP}$ genuinely depends on the runner class, and possibly on the phase. It is **not** a function of $s$ alone without specifying these.
- **Speed model.**
  - Theorems 1, 2 and 4 hold in both speed models, with one caveat: the certified legs may have $q < 1$, so Theorem 4 is a bounded-speed statement unless every $q = 1$. *Rev 2: every leg of every certificate has $q = 1$ exactly, so the caveat is void (§7.3).*
  - Theorem 3 needs bounded speed.
- **Chaser class.** All escape constructions are against PP. Theorem 3's chaser captures every Theorem 2 or Theorem 4 runner with $\alpha_C \le s$.

---

## 9. Implications for H1–H5

- **H1** (exact PP threshold $\alpha_C = 1$): **falsified** by Theorem 1. It is replaced by **H1′**: determine $\kappa_{\rm PP}(s; \mathcal R_m)$. Currently $2s/(1+s) \le \kappa \le \alpha_c(s, m)$. Numerics suggest that periodic orbits are optimal, and that the truth lies near the orbit side of the gap; neither is proven.
- **H2** ($1 < \kappa^\*(s) < \infty$ for the best chaser):
  - **The lower half is proven:** $\kappa^\*(s) \ge s$ in the bounded-speed model (Theorem 3), and $\kappa^\*(s) \ge 2s/(1+s)$ in the exact-speed model (Theorem 1).
  - The upper half, finiteness, is open. No escape construction against a general chaser exists.
- **H3** (agility effects under fixed cadence): new evidence that **clock alignment** matters a great deal. Against PP, the same runner and states gave 12/12 escapes aligned and 0/12 unaligned. This is planner evidence, and it supports treating phase as a first-class state variable. Nothing about monotonicity is established.
- **H4** ($s \le 1$): unchanged, and fully characterised (specification §B.1b).
- **H5** (2D versus 3D):
  - Theorems 1 and 3 are dimension-free.
  - Theorems 2 and 4 embed in any $\mathbb R^d$ with $d \ge 2$, so escape thresholds in 3D are at most the 2D ones.
  - Whether 3D lowers them is open.

---

## 10. Literature status and search checklist

> *Rev 2.* This section is superseded by `theory/literature_review.md`, which reads the primary sources and records what was and was not accessible. The Rev 1 text below is kept for history.

Nothing below has been verified beyond the level stated.

| Work | Access | Relation |
|---|---|---|
| S. A. Aleem, C. Nowzari, G. J. Pappas, *Self-triggered pursuit of a single evader with uncertain information*, arXiv:1512.06184 (v2, Jan 2016; preprint stated as submitted to Automatica; partly presented at IEEE CDC 2015). | Abstract and the first part of the HTML text read. Appendix and Sections 4–7 not read. | **Closest prior work found.** It treats a zero-order-hold pure-pursuit pursuer with capture checked continuously, but the pursuer **chooses** each inter-sample time from the current distance, so that the distance decreases monotonically. In our model the interval is a fixed exogenous $\tau_C$, and both overshoot and runner agility are central. No condition of the form $R_E\tau \le \varepsilon$, no overshoot analysis and no periodic evasion were found in the parts read. Proposition 1 and Theorem 1 must still be positioned carefully against it. |
| S. D. Bopardikar, F. Bullo, J. P. Hespanha, discrete-time pursuit–evasion with sensing limitations (IEEE T-RO 2008; ACC 2007 versions). | Abstracts and listings only. | Synchronous, turn-based; capture conditions on the ratio of sensing radius to step size. A different information and timing structure, but the closest discrete-time capture conditions. Must be read. |
| Classical sources: Isaacs (1965); Krasovskii and Subbotin (1988); Friedman (1971); Elliott and Kalton (1972); Sgall (2001); Nahin (2007). | Not checked. | See specification §D. |

**Search checklist** (not yet done):
1. Full text of Aleem–Nowzari–Pappas, including the CDC 2015 version. Does any part fix the sampling period?
2. Full text of Bopardikar–Bullo–Hespanha (T-RO 2008), for any statement analogous to Theorem 1.
3. "Sampled-data pure pursuit" or "zero-order hold pursuit" with *fixed* period: whether capture conditions of the form $R_E T \le c\,\varepsilon$ and the overshoot inequality (†) are known.
4. Periodic or limit-cycle evasion of discrete-time pure pursuit, especially in missile-guidance literature on "sampling-induced miss distance". The overlap is conceptual only; nothing tactical should be imported.
5. Krasovskii–Subbotin "step-by-step" strategies with fixed, player-specific partitions.
6. Forward citations of 1–2.

**No result in this document should be called novel until 1–5 are done.**

---

## 11. Recommended theoretical direction for Stage 4

**Close the gap for aligned runners by solving the one-pass reachability problem exactly.** For runners in $\mathcal R_m$, and in the continuous-control limit, the state at chaser decisions is the single number $D$. Indefinite evasion is then equivalent to non-emptiness of the *viability kernel* of the set-valued map
$$D \mapsto \{\,D' : \exists \text{ runner path over one period, clearance} > \varepsilon,\ \text{ending at separation } D'\,\}.$$
Three reasons this is the right next problem:
- It replaces the lossy inequality (†) with the exact relation, so it can only sharpen Theorem 1.
- It decides whether non-periodic (period $\ge 2$) evasion can beat period-1 orbits.
- It is a one-dimensional problem, plausibly solvable semi-analytically. It amounts to the reachable set of a speed-limited point avoiding a disc that moves faster than it along a line, and that geometry is classical.

The certification machinery of §7.2 extends directly to any candidate it produces.

A secondary problem: the unaligned runner. Does a fixed phase offset $\delta \in (0, \tau_E)$ admit any escape from PP at finite $\alpha_C$?

---

## Appendix A — Reproduction

All commands run from the repository root, with Python 3.12, NumPy, SciPy and Matplotlib.

| What | Command | Output |
|---|---|---|
| Tests (129 at Rev 1; 147 at Rev 2) | `python -m pytest` | — |
| Certificate verification (Rev 2) | `python theory/certificates/verify.py` | stdout; `theory/certificates/SUMMARY.md` with `--summary` |
| Policy-separation figure (Rev 2) | `python experiments/policy_separation.py` | `figures/stage3/policy_separation.{png,pdf}`, `results/stage3/policy_separation.txt` |
| Periodic-orbit optimisation | `python experiments/stage3.py orbits` | `results/stage3/orbits.json` |
| Certificates | `python experiments/stage3.py certify` | `results/stage3/certified_orbits.json` |
| Closure table | `python experiments/stage3.py closure` | `results/stage3/orbit_table.md` |
| Sweep, corrected planner | `python experiments/stage3.py sweep` | `results/stage3/sweep.csv` |
| Sweep, original planner | `python experiments/stage3.py sweep_original` | `results/stage3/sweep_original_planner.csv` |
| Planner ablation | `python experiments/stage3.py ablation` | `results/stage3/planner_ablation.txt` |
| Phase-alignment check | `python experiments/stage3.py phase` | `results/stage3/phase_alignment_check.txt` |
| Figures | `python experiments/stage3.py figures` | `figures/stage3/*.{png,pdf}` |

Configuration: `configs/stage3.json`.

Figures:
- `threshold_map`: proven curves, certified points, numerical brackets.
- `escape_vs_alpha`: sweep results, markers only, since the $\alpha_C$ grid is sparse.
- `planner_comparison`: before and after the two planner fixes.
- `escape_orbits`: Theorem 2 and certified orbits in absolute coordinates, plus the perpendicular fixed point.
- `separation_vs_time`: continuous-time separation in units of $\varepsilon$.
- `policy_separation` (Rev 2): the same runner and start against PP (escape) and the hybrid chaser (capture), at $s = 2$, $\alpha_C = 1.9$.
