# How to Win a Game of Tag — Stage 0 Research Specification

Status legend used throughout:
**[Proved]** full argument written here, still needs your independent check ·
**[Sketch]** argument outlined, gaps named · **[Conjecture]** · **[Heuristic]** · **[Decision]** needs your call.

---

## A. Formal game definition

### A.1 Primitives

| Symbol | Meaning |
|---|---|
| $d \in \{2,3\}$ | spatial dimension |
| $R_C, R_E > 0$ | speeds (chaser, runner) |
| $A_i > 0$, $\tau_i = 1/A_i$ | agility = decision rate; $\tau_i$ = commitment period |
| $\varepsilon > 0$ | capture radius |
| $H \in (0,\infty]$ | horizon |

### A.2 State

$$
S(t) = \big(\mathbf{x}_C,\ \mathbf{x}_E,\ \mathbf{u}_C,\ \mathbf{u}_E,\ \varphi_C,\ \varphi_E\big)
$$

- $\mathbf{x}_i \in \mathbb{R}^d$ positions; $\mathbf{u}_i \in S^{d-1}$ current committed headings.
- $\varphi_i \in [0, \tau_i)$ = time until agent $i$'s next decision.

Decision times are the lattice $\mathcal{T}_i = \{\varphi_i(0) + k\tau_i : k \ge 0\}$. If $\varphi_i(0) > 0$, agent $i$ is committed to $\mathbf{u}_i(0)$ on $[0, \varphi_i(0))$.

### A.3 Dynamics

$$
\dot{\mathbf{x}}_i = R_i \mathbf{u}_i(t), \qquad \mathbf{u}_i \text{ constant on } [t_k^i, t_{k+1}^i).
$$

Both agents' trajectories are piecewise linear. Between consecutive events (the merged set $\mathcal{T}_C \cup \mathcal{T}_E$), the relative position $\mathbf{r} = \mathbf{x}_E - \mathbf{x}_C$ is affine:

$$
\mathbf{r}(t_0+\sigma) = \mathbf{r}_0 + \sigma \mathbf{w}, \qquad \mathbf{w} = R_E\mathbf{u}_E - R_C\mathbf{u}_C.
$$

So the minimum separation on an inter-event interval has a closed form: minimize a quadratic in $\sigma$ over $[0, \Delta]$. **The capture check is exact, with no time-stepping error.** This is the main reason the event-driven engine can be mathematically clean.

### A.4 Information and strategies

- **Observation:** at each of its decision times, an agent observes the full current state $S(t^-)$, including the opponent's committed heading *and its clock phase*, plus the full history.
- **Strategy:** a nonanticipative map from observed history to $S^{d-1}$, evaluated only at the agent's own decision times.
- **Simultaneous decisions** ($t \in \mathcal{T}_C \cap \mathcal{T}_E$): both agents choose from the same information $S(t^-)$, and neither sees the other's new heading. This can recur for commensurate clocks (e.g. $a = 2$ with aligned phases), so it is not a measure-zero corner case for the sweep you proposed.
- **Consequence worth stating up front:** when agent $i$ decides and agent $j$ is mid-commitment, agent $i$ knows $j$'s exact path until $j$'s next decision. *Agility is therefore an information advantage:* the more agile agent is more often the "last mover." I think this is the right lens for the whole paper.

### A.5 Outcomes

- Capture time: $T^\star = \inf\{t \in [0,H] : |\mathbf{r}(t)| \le \varepsilon\}$.
- Assume $|\mathbf{r}(0)| > \varepsilon$. Otherwise the game is trivial.

The five statements you listed get distinct names:

| Name | Definition |
|---|---|
| *Reachable* | ∃ chaser path, ∃ runner path with capture (cooperative) |
| *Capture vs. σ_E* | ∃ chaser strategy capturing against a **fixed** runner strategy |
| *Guaranteed capture* | ∃ chaser strategy capturing against **every** admissible runner strategy |
| *Guaranteed escape* | ∃ runner strategy avoiding capture against every chaser strategy |
| *H-capture* | any of the above with $T^\star \le H$ |
| *Empirical frequency* | fraction of initial states drawn from a stated distribution μ, for **named** strategies |

With simultaneous moves, "guaranteed capture" and "guaranteed escape" need not be complementary for pure strategies; there can be a gap. For guarantees I'll use the conservative convention: the opponent is allowed to know your simultaneous choice. Every result below holds under that convention anyway.

### A.6 Normalization **[Proved: dimensional analysis]**

The model has 7 parameters ($R_C, R_E, A_C, A_E, \varepsilon, D_0, H$) and 2 units (length and time). Buckingham π leaves **5 independent groups**, so your set $(s, a, \lambda, b, h)$ is complete and minimal. On top of those groups:

- **State variables:**
  - Phases $\varphi_C/\tau_C$ and $\varphi_E/\tau_E \in [0,1)$.
  - Headings modulo the symmetry group: in 2D, 2 angles relative to line of sight (LOS); in 3D, 3 angles (two polar angles from LOS plus a relative azimuth).
- **Total dimension:** 9 in 2D and 10 in 3D.

**Recommended alternative scaling for the theory.** Measure length in units of $\varepsilon$ and time in units of $\varepsilon/R_E$. Then define

$$
\alpha_C = \frac{R_E \tau_C}{\varepsilon} = \frac{1}{\lambda a b},\qquad
\alpha_E = \frac{R_E \tau_E}{\varepsilon} = \frac{1}{\lambda b}.
$$

$\alpha_C$ is "how many capture radii the runner can drift during one chaser blink." The theory below says guaranteed-capture questions for $s>1$ depend only on $(s, \alpha_C, \alpha_E)$, because $D_0$ and $H$ drop out. That is a smaller sufficient parameterization under the infinite-horizon/guarantee assumption, which is what you asked for. Keep $(s,a,\lambda,b,h)$ for finite-horizon experiments.

---

## B. Mathematical sanity checks

### B.1 Escape lemma: $s \le 1$ is decided in the runner's first commitment window **[Proved]**

*Claim.* Let $R_E \ge R_C$. Suppose that at some runner decision time $t_0$ we have $D := |\mathbf{r}(t_0)| > \varepsilon$. Then the runner strategy "point directly away from the chaser's current position at every decision" avoids capture forever, against **every** chaser strategy, with any agility and any information.

*Proof.* Let $\hat{\mathbf{u}} = \mathbf{r}(t_0)/D$. For $\sigma \in [0, \tau_E]$:

$$
|\mathbf{r}(t_0+\sigma)| \ \ge\ |\mathbf{x}_E(t_0) + R_E\sigma\hat{\mathbf{u}} - \mathbf{x}_C(t_0)| - |\mathbf{x}_C(t_0+\sigma) - \mathbf{x}_C(t_0)| \ \ge\ D + (R_E - R_C)\sigma \ \ge\ D.
$$

So separation at the next runner decision is $\ge D > \varepsilon$, and induction finishes it. The bound holds pathwise, so the chaser's clock, agility and knowledge are irrelevant. ∎

*Consequences:*
- **Cases 2 and 4, and $s = 1$, are degenerate under the baseline model.**
  - The runner can be captured only on $[0, \varphi_E(0)]$, while it is still committed to its initial heading.
  - With that heading known (perfect information), the chaser faces a *one-shot interception of a straight-line target*. After its own first decision at $\varphi_C$, one straight leg is optimal and further chaser agility is useless.
  - So in Case 4, $A_C$ matters **only through the chaser's initial phase** $\varphi_C \in [0,\tau_C)$, and $A_E$ only through the window length $\varphi_E \in [0,\tau_E)$.
  - If $\varphi_E(0) = 0$, the runner is never caught.
- This answers RQ2 almost completely, and the answer is unexciting. **[Decision]** See §B.5.

### B.2 Your candidate proposition, verified and strengthened **[Proved]**

**Proposition 1.** Assume $R_C > R_E$ and
$$
R_E\,\tau_C \le \varepsilon \qquad(\text{i.e. } \alpha_C \le 1).
$$
Then **pure pursuit (PP)** captures in finite time, for any dimension $d \ge 1$, any initial headings and phases, and any runner. This includes a runner with continuous control and full knowledge of the chaser's future commitments. PP means aiming at the runner's current position at each chaser decision.

Your hypothesis $R_C\tau_C \le \varepsilon$ implies this one because $R_E < R_C$, so the stated proposition is true. The weaker hypothesis is the right one, and it is $\lambda a b \ge 1$ in your variables.

*Proof.*
1. Let $t_k = \varphi_C + k\tau_C$ and $D_k = |\mathbf{r}(t_k)|$, and suppose no capture has occurred by $t_k$, so $D_k > \varepsilon$. Let $c, e$ be the positions at $t_k$, and $\hat{\mathbf u} = (e-c)/D_k$.
2. Over the interval, the runner's displacement satisfies $|\mathbf{x}_E(t_k+\sigma) - e| \le R_E\sigma$ for every admissible runner. This is the only fact used about the runner.
3. **Case (i): $D_k \ge R_C\tau_C$.** At the end of the interval the chaser sits at $c + R_C\tau_C\hat{\mathbf{u}}$, which is at distance $D_k - R_C\tau_C$ from $e$. By the triangle inequality,
   $$D_{k+1} \le D_k - (R_C - R_E)\tau_C.$$
4. **Case (ii): $\varepsilon < D_k < R_C\tau_C$ (overshoot).** At $\sigma^\* = D_k/R_C < \tau_C$ the chaser is exactly at $e$, so
   $$|\mathbf r(t_k+\sigma^\*)| \le R_E D_k / R_C < R_E\tau_C \le \varepsilon.$$
   That is capture within the interval.
5. Case (i) cuts $D$ by a fixed positive amount each step, so case (ii), or capture, is reached after finitely many steps. ∎

The original triangle-inequality idea works. What it was missing is the overshoot case. Under your hypothesis $R_C\tau_C \le \varepsilon$, case (ii) never happens, which is why the proof seemed to need it.

**Capture-time bound [Proved, same argument].** Let $D_1 = |\mathbf r(\varphi_C)| \le D_0 + (R_C + R_E)\varphi_C$, and
$$K = \left\lceil \frac{(D_1 - R_C\tau_C)^+}{(R_C - R_E)\tau_C} \right\rceil.$$
Then
$$
T^\star \ \le\ \varphi_C + (K+1)\tau_C \ =\ \frac{D_0}{R_C - R_E} + O\!\left(\tau_C\cdot\frac{R_C+R_E}{R_C-R_E}\right).
$$

**Matching lower bound [Proved].** If the runner's initial heading is along the LOS, or $\varphi_E = 0$, it can flee in a fixed direction. Projecting onto that direction gives, for every chaser,
$$T^\star \ge \frac{D_0 - \varepsilon}{R_C - R_E}.$$
So when $\alpha_C \le 1$, PP is time-optimal up to $O(\tau_C)$ against the straight-flee runner. It is **not** claimed to be time-optimal against every runner.

### B.3 Where PP's argument breaks: the matador geometry **[Proved, single interval]**

Suppose the chaser commits to PP at distance $D$, and the runner sees that commitment immediately. Over $v \in S^{d-1}$, the relative velocity $\mathbf w = R_E v - R_C\hat{\mathbf u}$ ranges over a sphere of radius $R_E$ centered at $-R_C\hat{\mathbf u}$.

- The largest angle between $\mathbf w$ and the line of sight is $\arcsin(1/s)$. That is the tangent sidestep.
- The resulting minimum separation is exactly $D/s$, reached at $\sigma = D/R_C$.
- So a reactive runner survives a PP pass iff $D > s\varepsilon$, and the pass ends inside the interval iff $D < R_C\tau_C$.
- **That escape window $(s\varepsilon,\ R_C\tau_C)$ is nonempty iff $\alpha_C > 1$**, which is exactly the complement of Proposition 1's hypothesis.

This is the precise reason I suspect Proposition 1 is sharp for PP (H1 below). It is only a one-interval statement, so it is **not** yet an escape theorem.

### B.4 Summary table under the baseline model

| Regime | Status |
|---|---|
| $s \le 1$ (Cases 2, 4, and equal speed) | Decided in $[0,\varphi_E]$. Pure one-shot interception geometry. [Proved] |
| $s > 1$, $\alpha_C \le 1$ (Cases 1/3 with "quick enough" chaser) | Guaranteed capture by PP, any runner agility. Time $\approx D_0/(R_C-R_E)$. [Proved] |
| $s > 1$, $\alpha_C > 1$ | **Open.** This is the real research region. Runner agility $\alpha_E$ should matter here. |
| $\tau_C, \tau_E \to 0$ | Recovers classical simple-motion pursuit in unbounded space: capture iff $s>1$. Consistent with the above. [Proved, as a limit of the bounds] |

### B.5 Ambiguities needing your decision

1. **[Decision] Case 4 degeneracy.** Under perfect information in unbounded space, Case 4 reduces to interception within the runner's first commitment window. Options:
   - (a) Accept this and study it as an interception-window geometry problem: cheap, exact, but thin.
   - (b) Add a **bounded arena**, where a faster runner can't flee forever. This connects to lion-and-man.
   - (c) **Observation delay / sampled observation.** Agents see the opponent's state as of their own last decision, not continuously.
   - (d) Restrict the runner to a named strategy class, which loses "optimal" claims.
   - (e) Wait for the turning-rate model.

   My recommendation: (a) now, since it's quick and gives one clean proposition, and (b) as the substantive Case-4 extension. Don't change the model silently; this needs your call.
2. **[Decision] Exact speed $|\mathbf u| = 1$ vs. $|\mathbf u| \le 1$.** This is not innocuous.
   - A chaser that can slow down can avoid the overshoot in §B.3, so the relaxation probably changes the $\alpha_C>1$ answer.
   - The relaxation is also what makes the 2D→3D projection lemma (H5) work.
   - Proposition 1 holds under both.

   Recommendation: keep $|\mathbf u| = 1$ as primary, as you specified, and treat $\le 1$ as a labeled variant.
3. **Opponent clock observable?** I assumed yes (perfect information). If not, commitments become partially hidden. That is a meaningfully different game.
4. **Simultaneous moves.** I use the conservative pure-strategy convention (§A.5). Exact small-game solvers may need mixed strategies at simultaneous nodes; I'll flag it wherever it matters.

---

## C. Research hypotheses

**H1 — Proposition 1 is sharp for pure pursuit. [Conjecture]**
- *Claim:* for every $s>1$ and $\alpha_C > 1$, there exist $\bar\alpha_E > 0$ and an initial state from which a runner with $\alpha_E < \bar\alpha_E$ avoids PP forever.
- *Why interesting:* together with Proposition 1, it would give an exact threshold $\alpha_C = 1$ for PP against agile runners. That is "if you can't leave the tag radius during one of the chaser's blinks, you lose; otherwise you can play matador."
- *Falsified by:* a proof that PP captures for some $\alpha_C>1$ against all sufficiently agile runners, or by numerics showing that no runner policy, including best-response search, escapes near $\alpha_C = 1^+$. A heuristic runner failing to escape does **not** falsify it.
- *Also expected:* for sluggish runners (large $\alpha_E$), PP's capture region extends past $\alpha_C = 1$. That is the agility-vs-speed tradeoff in its clearest form.

**H2 — Smarter chasers beat the PP threshold, but not without bound. [Conjecture]**
- *Claim:* let $\kappa^\*(s)$ be the supremum of $\alpha_C$ for which *some* chaser strategy guarantees capture against a fully agile runner ($\alpha_E \to 0$). Then $1 < \kappa^\*(s) < \infty$.
- *Heuristic:* a chaser can time its approach so that its next decision lands with $D \le s\varepsilon$, where the sidestep fails. The runner can perturb the post-interval distance by about $\pm R_E\tau_C$, and once that exceeds the window width $(s-1)\varepsilon$, timing should fail.
- *Why interesting:* $\kappa^\*(s)$ is literally "how much sluggishness can a given speed advantage buy back" (RQ1 and RQ4).
- *Falsified by:* a proof that $\kappa^\* = 1$ (PP is optimal), or that $\kappa^\* = \infty$ for some $s$.

**H3 — Agility is monotone under refinement but not in general. [Partly provable + Conjecture]**
- *Provable [Sketch]:* if the runner's decision lattice contains another runner's lattice ($\tau_E' = \tau_E/k$ with aligned phase), the more frequent runner can mimic the less frequent one. So the guaranteed-escape region is monotone along such chains.
- *Conjecture:* for non-nested clocks (e.g. $a = 1$ vs. $a = 1.3$), the guaranteed-capture region and worst-case capture time are **non-monotone** in $a$, because of resonance between decision lattices.
- *Why interesting:* it would show that "agility" as decision frequency is not a scalar advantage. Phase structure matters. That directly addresses your requirement not to assume monotonicity.
- *Falsified by:* a monotonicity proof, or a fine $a$-sweep with best-response opponents showing no non-monotonicity beyond CI width.

**H4 — Case 4 capture probability depends on agility only through phases, and saturates. [Follows from B.1 + Conjecture on form]**
- Under B.1, for $s<1$ with initial headings and phases drawn uniformly, $P_{\text{cap}}(s,a,\lambda,b)$ is an integral of a one-shot interception indicator over $(\varphi_C, \varphi_E, \text{headings})$.
- *Conjecture:* $P_{\text{cap}}$ is increasing in $a$ and converges as $a\to\infty$ to the $\varphi_C = 0$ value, with a gap of $O(1/(\lambda a))$.
- *Why interesting:* it gives a clean, checkable answer to RQ2 in the baseline model, and validates the engine against a semi-analytic quantity.
- *Falsified by:* the computed integral.

**H5 — Dimension doesn't move the guarantee thresholds. [Partial Sketch + Conjecture]**
- *Sketch (needs the $|\mathbf u|\le1$ relaxation):* a planar escape strategy lifts to 3D. The runner stays in a plane containing the LOS and its initial heading, and plays against the projection of the chaser. That projection is an admissible planar chaser with speed $\le R_C$, and 3D distance is at least the projected distance. So $\text{Escape}_{2D} \Rightarrow \text{Escape}_{3D}$.
- *Conjecture:* $\kappa^\*_{3D}(s) = \kappa^\*_{2D}(s)$ and the H1 threshold is dimension-free, while finite-horizon capture *frequencies* under uniform heading measures differ.
- *Why interesting:* this is RQ5, and it separates "3D is genuinely harder" from "3D just has a different heading distribution."
- *Falsified by:* a 3D-only escape maneuver (a non-planar sidestep that beats a chaser who captures in 2D).

---

## D. Novelty and literature assessment

**Nothing below has been verified yet.** These are works I recall and believe to be relevant. Every entry must be checked against the primary source before it enters the BibTeX file. Stage L, below, does this.

### D.1 Closest frameworks, and how we likely differ

| Framework | Recalled anchor(s), to verify | Likely relation to our model |
|---|---|---|
| Positional differential games with **step-by-step / piecewise-constant controls on a time partition** | Krasovskii & Subbotin, *Game-Theoretical Control Problems* (Springer, 1988) | **Probably the closest formal ancestor.** Their partitions are a proof device that is refined to zero. Ours are *fixed, player-specific, asynchronous* and are the object of study. We must check whether fixed unequal partitions are already analyzed. |
| Value of differential games via discretization; nonanticipative strategies | Friedman, *Differential Games* (1971); Elliott & Kalton, Mem. AMS (1972) | Upper/lower value via time discretization with one player moving first. This is related to our last-mover structure. |
| Classical simple-motion pursuit, isotropic rocket, homicidal chauffeur | Isaacs, *Differential Games* (1965); Merz, PhD thesis on the homicidal chauffeur (Stanford, 1971) | Continuous control, plus the curvature constraint for our secondary model. Our $\tau\to0$ limit should recover simple motion. |
| Lion and man (bounded arena, equal speed) | Littlewood's *Miscellany* (Besicovitch's solution); Sgall, TCS 2001 (discrete-time lion and man); Alonso, Goldstein & Reingold (1992, lion-and-man bounds) | Relevant if we adopt arena option (b). Discrete-time versions are close cousins, but they are synchronous and turn-based. |
| Discrete-time pursuit-evasion with sensing limits | Bopardikar, Bullo & Hespanha, IEEE T-RO (~2008) | Discrete time, but synchronous. Check for capture-radius-vs-step-length conditions resembling Proposition 1. **High risk of overlap with Proposition 1.** |
| Pursuit in $\mathbb{R}^n$ / multi-dimensional | Kopparty & Ravishankar, IPL (~2005); Pshenichnyi (simple pursuit, 1970s) | RQ5 baselines. |
| Reachability / HJI | Mitchell, Bayen & Tomlin, IEEE TAC (2005) | Numerical capture regions in continuous time. Possibly a validation tool for the $\tau\to0$ limit only. |
| Information patterns / leader–follower | Başar & Olsder, *Dynamic Noncooperative Game Theory* (SIAM, 2nd ed. 1999) | The formal language for our "agility = information advantage" framing. |
| Surveys | Chung, Hollinger & Isler, *Autonomous Robots* (2011); Nahin, *Chases and Escapes* (2007) | Map the field and fix the narrative framing. |

### D.2 Required searches

Run these on Google Scholar, arXiv, and zbMATH/MathSciNet if available:

1. `"pursuit-evasion" "sampled-data" OR "zero-order hold" capture`
2. `"pursuit" "asynchronous" decision OR update OR sampling game`
3. `"piecewise constant" controls "differential game" pursuit "different" sampling OR partition`
4. `"discrete-time" "lion and man" capture radius step length`
5. `pursuit evasion "decision rate" OR "update rate" OR "reaction time" speed tradeoff`
6. `"pure pursuit" discrete-time OR sampled capture condition "capture radius"`
7. `pursuit evasion "intermittent" OR "event-triggered" control`
8. `"three-dimensional" simple pursuit evasion capture` and `pursuit evasion R^n dimension`
9. `"agility" pursuit evasion game` (likely noisy, but needed to check terminology collisions)
10. Forward-citation search from Krasovskii–Subbotin step-by-step strategies and from Bopardikar et al.

### D.3 Defensible-contribution hypothesis (to test against D.2, not to claim yet)

The candidate niche is that **unequal, asynchronous, fixed decision periods are the primitive object**, with agility read as a last-mover information advantage. Within that niche:

- the exact threshold $\alpha_C = R_E\tau_C/\varepsilon$ and its sharpness for PP;
- the degeneracy of Case 4;
- the 2D/3D projection relation.

If D.2 turns up Proposition 1 in a sampled-data paper, which is plausible, we cite it and move the contribution to H1–H3.

---

## E. Implementation roadmap

Each stage is one small, tested commit. Stages run one at a time.

| Stage | Deliverable | Tests that must pass |
|---|---|---|
| **1. Kinematics core** | Repo skeleton (`~/code/tag-pursuit-evasion`, Python 3.12, NumPy, pytest). Segment min-distance function; event-driven engine with two decision lattices, the simultaneous-move protocol, an event log and trajectories; seeded determinism. | Closed-form cases: head-on, straight flee (separation exactly $D+(R_E-R_C)t$), perpendicular, tangent sidestep (min $= D/s$ at $D/R_C$). Capture between checkpoints detected. Phase handling. Rotation invariance. Bitwise reproducibility. |
| **2. Baseline strategies + Proposition 1 check** | PP, linear-prediction chaser; direct escape, lateral dodge, tangent-sidestep runner. | Every run with $\alpha_C \le 1$ captures within the B.2 bound (a hard test: any violation is a bug or a proof error). B.1 escape for $s\le1$ holds in every run. |
| **L. Literature verification** | `literature/` notes, verified BibTeX, closest-model comparison table. | Every citation traced to a primary source or dropped. |
| **3. Runner best response vs. PP** | One-interval exact best response from §B.3; multi-interval search (sampled directions + local optimization). | Converges as direction resolution increases; reproduces the analytic single-interval optimum. → H1 |
| **4. Case 4 interception** | Closed-form straight-line intercept; $P_{\text{cap}}$ integral, both by quadrature and by Monte Carlo. | Quadrature and Monte Carlo agree within CI; simulation agrees with the formula. → H4 |
| **5. Exact small game** | Discretized headings, relative-state grid, minimax value iteration for guarantee regions (careful with simultaneous nodes). | Matches Proposition 1 and B.1 exactly; convergence under grid refinement. |
| **6. Adversarial chaser** | Receding-horizon chaser (timing-aware); alternating best responses. | Exploitability measured against Stage 3 runners. → H2, H3 |
| **7. 3D** | Same engine with $d=3$ (should be parametric from Stage 1); planar-embedding tests. | 3D runs restricted to a plane reproduce 2D runs exactly. → H5 |
| **8. Sweeps + figures** | Your speed × agility × $\lambda$ grid, now informed by B.1 (the $s\le1$ columns are interception-window plots), with Wilson CIs. | Reproducible from configs. |
| **9. Manuscript** | Only after the above. | — |

---

## F. First experiment

**Goal:** validate the engine against a theorem and probe H1 at its sharpest point.

- **Setup.** 2D; $s \in \{1.2, 1.4\}$; chaser = PP.
  - $\alpha_C \in \{0.5, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.25, 1.5, 2.0\}$.
  - Runner = tangent-sidestep: at each decision, if the chaser's committed segment would bring it within $s\varepsilon$, play the §B.3 tangent direction; otherwise flee directly.
  - $a \in \{0.25, 0.0625\}$ (runner 4× and 16× more agile).
  - $D_0 = 10\varepsilon$.
  - $N = 1000$ initial states per cell, with headings and phases uniform, using the **same sample across cells**.
  - Horizon = 5× the B.2 time bound.
- **Readouts.**
  - Capture fraction with Wilson 95% CIs.
  - Capture time vs. the B.2 bound.
  - For non-captures, separation over time: bounded-but-never-captured versus growing distinguishes "escape" from "slow capture."
- **Predictions.**
  - $\alpha_C \le 1$: **100% capture, all within the bound.** This is a theorem, so any miss is an engine bug or a proof error.
  - $\alpha_C > 1$: H1 predicts nonzero escape, increasing as $a$ decreases. If none appears, that's evidence the heuristic runner is weak, **not** that H1 is false. Stage 3 then becomes the test.
- **Cost:** about 40k short simulations. Seconds to minutes.

**The specific decisions I need from you before Stage 1:** (1) the Case 4 option in §B.5, (2) exact vs. bounded speed, (3) whether to set up `~/code/tag-pursuit-evasion` as a private GitHub repo now.
