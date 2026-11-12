# How to Win a Game of Tag — Stage 0 Research Specification

Status legend used throughout:
**[Proved]** full argument written here, still needs your independent check ·
**[Sketch]** argument outlined, gaps named · **[Conjecture]** · **[Heuristic]** · **[Decision]** needs your call.

## Revision log

**Rev 0 (2026-11-11).** The original Stage 0 spec. Its text is kept below unchanged.

**Rev 1 (2026-11-11).** Decisions after review. Each affected section carries a marked **Rev 1** note, and the original reasoning is left in place.

1. **Speed model.** The primary model is now $\|\mathbf v_i\| \le R_i$. At each decision time the agent chooses a full velocity vector, direction and magnitude, and holds it until its next decision. Exact speed $\|\mathbf v_i\| = R_i$ is kept as a variant (`speed_mode="exact"`).
2. **Case 4 is retained.** We document that it is degenerate in unbounded space. Added: an interception lemma (§B.1a), a full outcome characterization for $s \le 1$ (§B.1b), and reachable sets. The bounded arena is deferred and not implemented.
3. **Agility is a fixed periodic cadence for now.** The distinction between a fixed schedule and a maximum available frequency is now explicit (§A.4 note, H3).
4. **Qualifications on the hypotheses.**
   - H1: surviving one interval does not imply indefinite evasion.
   - §A.6: uniform guarantees are separated from state-conditioned results.
   - H5: the 2D/3D equivalence stays a conjecture.
5. **Citations remain unverified** (§D).

**Rev 2 (2026-11-12).** New result from Stage 2: braking pursuit (§B.2a). It satisfies Proposition 1, and $\alpha_C \le 1$ is sharp for it. Nothing earlier was changed. The reason for the addition is that the Stage 2 experiment surfaced the behaviour, and the proof is short and complete.

**Rev 3 (2026-11-12).** Stage 3 theory, from analysing pure pursuit (PP) against a best-responding runner.
- §B.2b extends PP's capture guarantee to $\alpha_C \le 2s/(1+s)$. This **falsifies H1 as stated**.
- §B.3a constructs an exact periodic escape orbit for $\alpha_C > \alpha_{\text{sym}}(s)$.
- Together they bracket PP's threshold. H1's original text is kept, with a Rev 3 note.

**Rev 4 (2026-11-12).** Stage 3 consolidation. Full proofs and the theorem-status table are in `theory/stage3_mathematical_review.md`, which numbers the results as follows: Prop 1′ = Thm 1, Prop 3 = Thm 2. New here:
- §B.2c: a hybrid braking/pursuit chaser captures every runner iff $\alpha_C \le s$. This is a proof, and it settles the lower half of H2.
- §B.3b: exact-rational certification of multi-leg escape orbits (Thm 4).
- The H2 status is updated.
- Nothing earlier was changed.

**Rev 5 (2026-11-12).** Stage 3.5 verification. Nothing in the model changed. The new material lives in `theory/`:
- **Theorem 4 certificates.** They are now standalone files in `theory/certificates/`, checked by an independent standard-library verifier. All 15 pass, and all hold in **both** speed models, since every leg has unit speed. This voids the "bounded-speed unless q = 1" caveat.
- **Monotonicity in $\alpha_C$.** It is proven whenever only $\varepsilon$ varies (review §2.4, Lemma M). So the threshold definitions no longer need the "for every $\alpha' \le \alpha$" clause. Review §2.5 makes the runner-class and initial-state quantifiers explicit, and **no threshold is a function of $s$ alone**.
- **Policy separation (review §3.5, Theorem 5; bounded-speed model).** For $\alpha_{\rm sym}(s) < \alpha_C \le s$, which includes $s = 2$, $\alpha_C = 1.9$, PP admits an indefinitely evading runner while the §B.2c chaser captures every runner. So PP is not guarantee-optimal (H2).
- **Index and literature.** The theorem index is `theory/theorem_register.md`. The literature comparison is `theory/literature_review.md`, and it claims no novelty.

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

> **Rev 1 — primary speed model.** Replace $\dot{\mathbf x}_i = R_i\mathbf u_i$, $|\mathbf u_i| = 1$ with
> $$\dot{\mathbf x}_i = \mathbf v_i(t),\qquad \|\mathbf v_i\| \le R_i,\qquad \mathbf v_i \text{ constant between consecutive decisions of agent } i.$$
> There is no intra-interval control: no acceleration, no braking mid-interval, no turning mid-interval. An agent may stop ($\mathbf v_i = 0$), but only at a decision time. The state stores velocities $\mathbf v_i$ instead of headings $\mathbf u_i$. Everything in A.3 above stays true with $R_E\mathbf u_E - R_C\mathbf u_C$ replaced by $\mathbf w = \mathbf v_E - \mathbf v_C$, which may now be $0$.
> The exact-speed variant $\|\mathbf v_i\| = R_i$ is retained for robustness checks.

### A.4 Information and strategies

- **Observation:** at each of its decision times, an agent observes the full current state $S(t^-)$, including the opponent's committed heading *and its clock phase*, plus the full history.
- **Strategy:** a nonanticipative map from observed history to $S^{d-1}$, evaluated only at the agent's own decision times.
- **Simultaneous decisions** ($t \in \mathcal{T}_C \cap \mathcal{T}_E$): both agents choose from the same information $S(t^-)$, and neither sees the other's new heading. This can recur for commensurate clocks (e.g. $a = 2$ with aligned phases), so it is not a measure-zero corner case for the sweep you proposed.
- **Consequence worth stating up front:** when agent $i$ decides and agent $j$ is mid-commitment, agent $i$ knows $j$'s exact path until $j$'s next decision. *Agility is therefore an information advantage:* the more agile agent is more often the "last mover." I think this is the right lens for the whole paper.

> **Rev 1 — what "agility" means in Stage 1.** Two readings must not be conflated.
> - **(Fixed cadence; the current model.)** Agent $i$ decides *exactly* at $\varphi_i + k\tau_i$. Here $A_i = 1/\tau_i$ is a schedule, not a capability. Raising $A_i$ from $1/\tau$ to $1/\tau'$ enlarges the agent's set of feasible control signals **only if** the new lattice contains the old one ($\tau = m\tau'$ with matching phase). Two non-nested schedules, such as $\tau = 1$ and $\tau' = 0.7$, give *incomparable* action sets. Neither agent can imitate the other.
> - **(Maximum frequency; the physically meaningful reading.)** Agent $i$ may decide at any times it likes, subject to a minimum gap $\tau_i$ between decisions. A larger $A_i$ then gives a superset of feasible schedules. So *any* guaranteed outcome is weakly monotone in $A_i$, trivially.
>
> Under fixed cadence, an apparent "more agility hurts" effect is therefore a statement about schedule geometry or resonance, **not** evidence that agility is harmful. Results must be labeled with the reading they use. Flexible scheduling is deferred and not implemented in Stage 1.

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

> **Rev 1 — qualification.** The sentence above is too broad. It is correct only for **uniform** questions: "does the chaser guarantee capture from *every* initial state?" In those, $D_0$, headings and phases are quantified over rather than fixed, and $H = \infty$. Proposition 1 is such a uniform statement.
>
> For **state-conditioned** results, the full normalized state cannot be discarded. These are questions like "is capture guaranteed from *this* state?", "what is the capture time?", or "does the runner escape from here?" The state that must be kept is: $D_0/\varepsilon$; the initial velocities relative to the LOS, which are now direction *and* magnitude $\|\mathbf v_i(0)\|/R_i \in [0,1]$; the phases $\varphi_i/\tau_i$; whether each agent starts fresh ($\varphi_i = 0$) or precommitted; and $h$ if the horizon is finite.
>
> Example: Proposition 1's time bound depends on $D_0$ and $\varphi_C$. B.1b's Case 4 outcome depends on all of the initial state.
>
> Revised state dimension: 2D needs 2 angles and 2 speed fractions for the initial velocities, plus 2 phases and $D_0/\varepsilon$. 3D needs 3 angles, with the rest the same. Whether a smaller sufficient set exists for a *specific* state-conditioned question has to be shown question by question.

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

> **Rev 1 — re-checked under $\|\mathbf v\|\le R$. [Proved]** The proof uses only two facts: the runner can choose $\mathbf v_E = R_E\hat{\mathbf u}$, which is admissible in both speed models; and every chaser path satisfies $|\mathbf x_C(t_0+\sigma) - \mathbf x_C(t_0)| \le R_C\sigma$, which holds for any piecewise-constant velocity with $\|\mathbf v_C\|\le R_C$. So the lemma holds unchanged, in any dimension.
>
> One edge case is worth recording. If $D = \varepsilon$ exactly at the runner's decision, capture has already occurred, because the definition uses $\le$. The lemma needs $D > \varepsilon$ strictly.

### B.1a Interception lemma (finite initial commitment) **[Proved]** — *Rev 1, new*

**Setting.**
- The runner moves with a known constant velocity $\mathbf v_E$, with $\|\mathbf v_E\| \le R_E$, on $[0, T]$, starting from $\mathbf e_0$. Its path is $\mathbf e(t) = \mathbf e_0 + \mathbf v_E t$.
- The chaser starts at $\mathbf c_0$ and is free to choose a velocity at $t = 0$.
- $\|\mathbf e_0 - \mathbf c_0\| > \varepsilon$.

**Claim.** In the primary model, there is a chaser control with capture by time $T$ **iff**
$$\exists\, t\in[0,T]:\quad \|\mathbf e_0 + \mathbf v_E t - \mathbf c_0\| \ \le\ R_C t + \varepsilon. \tag{★}$$
If (★) holds, a *single constant velocity* chosen at $t=0$ achieves capture.

*Proof.*
- (⇒) Suppose some admissible chaser path captures at $t \le T$. Any path with speed $\le R_C$ satisfies $\|\mathbf x_C(t) - \mathbf c_0\| \le R_C t$. So
  $$\|\mathbf e(t) - \mathbf c_0\| \le \|\mathbf e(t) - \mathbf x_C(t)\| + \|\mathbf x_C(t) - \mathbf c_0\| \le \varepsilon + R_C t.$$
  This direction holds for **every** chaser class with speed bounded by $R_C$: any decision schedule, even continuous control. Chaser agility therefore cannot enlarge the set of interceptable lines.
- (⇐) Let $t^\*$ satisfy (★), and $\mathbf p = \mathbf e(t^\*) - \mathbf c_0$. Then $t^\* > 0$, since $\|\mathbf p\| > \varepsilon$ at $t = 0$.
  - If $\|\mathbf p\| \le R_C t^\*$, take $\mathbf v_C = \mathbf p / t^\*$. This is admissible, and $\mathbf x_C(t^\*) = \mathbf e(t^\*)$.
  - Otherwise $R_C t^\* < \|\mathbf p\| \le R_C t^\* + \varepsilon$. Take $\mathbf v_C = R_C\mathbf p/\|\mathbf p\|$. Then $\|\mathbf e(t^\*) - \mathbf x_C(t^\*)\| = \|\mathbf p\| - R_C t^\* \le \varepsilon$.
  - If the chaser's clock forces re-decisions before $t^\*$, it re-selects the same velocity. ∎

**Exact-speed variant.** (★) is still necessary and sufficient, but the construction changes. Let $f(t) = \|\mathbf e(t) - \mathbf c_0\| - R_C t - \varepsilon$. It is continuous, $f(0) > 0$, and $f(t^\*) \le 0$, so there is an earliest root $t' \le t^\*$. The full-speed choice $\mathbf v_C = R_C(\mathbf e(t') - \mathbf c_0)/\|\cdot\|$ gives separation exactly $\varepsilon$ at $t'$.

The earliest root $t'$ is also the **earliest possible capture time** in both models, by the (⇒) bound. So the straight full-speed leg toward $\mathbf e(t')$ is time-optimal.

**Closed form.** Both sides of (★) are nonnegative, so square them. With $\mathbf p_0 = \mathbf e_0 - \mathbf c_0$, (★) at $t$ is equivalent to
$$(\|\mathbf v_E\|^2 - R_C^2)\,t^2 + 2(\mathbf p_0\!\cdot\!\mathbf v_E - \varepsilon R_C)\,t + \|\mathbf p_0\|^2 - \varepsilon^2 \ \le\ 0.$$
This is a quadratic inequality on $[0,T]$. Its smallest feasible root is $t'$.

**Precommitted chaser.** Suppose the chaser is committed to $\mathbf v_C(0)$ until $\varphi_C < T$. Let $\mathbf c_1 = \mathbf c_0 + \mathbf v_C(0)\varphi_C$. Capture by $T$ is possible iff either the committed segment already captures, i.e. $\min_{t\in[0,\varphi_C]}\|\mathbf r(t)\| \le \varepsilon$, which is the exact interval check, or
$$\exists\,t\in[\varphi_C, T]:\ \|\mathbf e(t) - \mathbf c_1\| \le R_C(t-\varphi_C) + \varepsilon.$$
The proof is the same. If $\varphi_C \ge T$, only the segment check applies.

**Assumptions used:**
- perfect information, i.e. the chaser knows $\mathbf e_0$ and $\mathbf v_E$;
- a Euclidean norm;
- unbounded, obstacle-free space;
- the runner's velocity is exactly constant on $[0,T]$;
- a closed capture ball ($\le\varepsilon$);
- $\|\mathbf e_0 - \mathbf c_0\| > \varepsilon$.

No assumption on dimension is needed.

**Reachable sets (primary model).**
- *Chaser:* $\{\mathbf c_0 + \mathbf v_C(0)t\}$ for $t \le \varphi_C$. After that, the closed ball $\bar B(\mathbf c_1, R_C(t - \varphi_C))$.
  - *Proof sketch:* "⊆" is the speed bound. "⊇" holds because each point of the ball is reached at time $t$ by one constant velocity of norm $\le R_C$. That velocity is admissible under bounded speed; under exact speed only the sphere is reached at time $t$, though the interior is reached earlier.
- *Runner:* the point $\mathbf e(t)$ for $t \le \varphi_E$. After that, $\bar B(\mathbf e(\varphi_E), R_E(t - \varphi_E))$.
- Capture by $t$ is possible iff the $\varepsilon$-neighbourhoods of the two reachable sets at some time $\le t$ intersect *along a common time*. (★) is exactly this, for a point runner path against a ball.

### B.1b Outcome for $s \le 1$ under optimal play **[Proved, from B.1 + B.1a]** — *Rev 1, new*

Let $R_E \ge R_C$, and suppose the runner is precommitted to $\mathbf v_E(0)$ until $\varphi_E$. Then the chaser can force capture **iff** the precommitted-chaser version of (★) holds with $T = \varphi_E$.

- If it holds, B.1a gives a capture.
- If it fails, there is no capture on $[0,\varphi_E]$ against any chaser. Taking $t = \varphi_E$ in the failed condition gives $\|\mathbf r(\varphi_E)\| > \varepsilon$. At $\varphi_E$ the runner flees, and B.1 applies.
- A simultaneous chaser decision at $\varphi_E$ changes nothing.
- A fresh-start runner ($\varphi_E = 0$) with $D_0 > \varepsilon$ always escapes.

This is the complete answer to Case 4 in the baseline model. RQ2 becomes the geometry of (★) over the initial-state distribution.

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

> **Rev 1 — independent re-verification under $\|\mathbf v\| \le R$. [Proved]**
>
> *Definition.* PP means that at each chaser decision $t_k$ the chaser chooses $\mathbf v_C = R_C\hat{\mathbf u}_k$ with $\hat{\mathbf u}_k = (\mathbf e - \mathbf c)/D_k$, i.e. **full speed**. This is admissible in both speed models.
>
> *What the proof uses about the runner:* $\|\mathbf x_E(t_k+\sigma) - \mathbf x_E(t_k)\| \le R_E\sigma$. This holds for any runner in either model, and also for a runner with continuous control or clairvoyance.
>
> Line by line, for each case:
> - **(i) $D_k \ge R_C\tau_C$.** At the end of the interval the chaser is at $\mathbf c + R_C\tau_C\hat{\mathbf u}_k$, on the segment $[\mathbf c, \mathbf e]$. Its distance to $\mathbf e$ is $D_k - R_C\tau_C \ge 0$. The triangle inequality gives $D_{k+1} \le D_k - R_C\tau_C + R_E\tau_C$.
>   - *Boundary $D_k = R_C\tau_C$:* then $D_{k+1} \le R_E\tau_C \le \varepsilon$, so capture is detected at or before $t_{k+1}$. That is consistent with the bound.
> - **(ii) $\varepsilon < D_k < R_C\tau_C$.** Set $\sigma^\* = D_k/R_C \in (0, \tau_C)$. Then $\mathbf x_C(t_k + \sigma^\*) = \mathbf e$, and $\|\mathbf r(t_k+\sigma^\*)\| \le R_E\sigma^\* = D_k R_E/R_C < R_E\tau_C \le \varepsilon$.
>   - The final inequality is where the hypothesis enters. It is strict in the middle step, so capture happens strictly inside the interval.
> - **Termination.** Each case-(i) step lowers $D$ by $\delta = (R_C - R_E)\tau_C > 0$. So after at most $K = \lceil (D_1 - R_C\tau_C)^+/\delta\rceil$ such steps we have $D_K \le R_C\tau_C$, and the next interval captures. This gives the same bound as before.
>
> *Gaps checked:*
> - Capture occurring *before* $\varphi_C$ makes the statement vacuous.
> - $D_1$ is finite: $D_1 \le D_0 + (R_C + R_E)\varphi_C$.
> - Simultaneous decisions are irrelevant, because the runner bound is pathwise.
> - $R_C > R_E$ is used only for $\delta > 0$. The runner's agility $\tau_E$ never enters.
>
> *Not claimed:*
> - that $R_E\tau_C \le \varepsilon$ is necessary for PP (that is H1);
> - that PP is time-optimal against every runner;
> - anything for PP variants that use less than full speed. For example, "brake to arrive exactly at $\mathbf e$ at $t_{k+1}$" does not obviously satisfy either case and is not covered.
>
> Numerical consistency checks are in `tests/test_theory_scenarios.py`. They cover 5 speed/period combinations × 4 runner periods × 15 initial states × 5 runner behaviours, including the overshoot regime $R_C\tau_C > \varepsilon$. They are finitely many cases, not a proof.

**Capture-time bound [Proved, same argument].** Let $D_1 = |\mathbf r(\varphi_C)| \le D_0 + (R_C + R_E)\varphi_C$, and
$$K = \left\lceil \frac{(D_1 - R_C\tau_C)^+}{(R_C - R_E)\tau_C} \right\rceil.$$
Then
$$
T^\star \ \le\ \varphi_C + (K+1)\tau_C \ =\ \frac{D_0}{R_C - R_E} + O\!\left(\tau_C\cdot\frac{R_C+R_E}{R_C-R_E}\right).
$$

**Matching lower bound [Proved].** If the runner's initial heading is along the LOS, or $\varphi_E = 0$, it can flee in a fixed direction. Projecting onto that direction gives, for every chaser,
$$T^\star \ge \frac{D_0 - \varepsilon}{R_C - R_E}.$$
So when $\alpha_C \le 1$, PP is time-optimal up to $O(\tau_C)$ against the straight-flee runner. It is **not** claimed to be time-optimal against every runner.

### B.2a Braking pursuit: same guarantee, and the threshold is sharp **[Proved]** — *Rev 2, new*

**Braking pursuit (BP).** At each decision $t_k$ the chaser plays
$$\mathbf v_C = \min(R_C,\ D_k/\tau_C)\,\hat{\mathbf u}_k.$$
This lands it exactly on the runner's observed position $\mathbf e_k$ at $t_{k+1}$ whenever $D_k \le R_C\tau_C$. It is admissible only in the bounded-speed model.

**(a) BP satisfies Proposition 1, with the same time bound.**
- If $D_k \ge R_C\tau_C$, BP coincides with PP, and §B.2 case (i) applies.
- If $D_k < R_C\tau_C$, then $\mathbf x_C(t_{k+1}) = \mathbf e_k$, so $\|\mathbf r(t_{k+1})\| \le R_E\tau_C \le \varepsilon$.

Note that this reaches the $\varepsilon$-ball only **at the endpoint**, and with equality when $\alpha_C = 1$ and the runner flees straight. Compare PP, which captures strictly inside the interval (§B.2 (ii)). So at $\alpha_C = 1$, BP's capture is a tie that floating point can break either way. The Stage 2 sweep hit this 32 times. ∎

**(b) Sharpness.** Let $R_E\tau_C > \varepsilon$, i.e. $\alpha_C > 1$, with any $s$ and any runner agility. Start both agents fresh and collinear, with $D_0 > \varepsilon$, and let the runner move with constant velocity $R_E\hat{\mathbf u}_0$ along the initial line of sight. Then BP never captures. Separation stays $\ge \min(D_0, R_E\tau_C)$ forever.

*Proof.* All motion is on the line of sight, and separation is affine on each chaser interval.
- If $D_k \ge R_C\tau_C$, then $D_{k+1} = D_k - (R_C - R_E)\tau_C \ge R_E\tau_C$.
- If $D_k < R_C\tau_C$, the chaser lands on $\mathbf e_k$ while the runner has moved $R_E\tau_C$ further on. So $D_{k+1} = R_E\tau_C$.

In both cases the minimum over $[t_k, t_{k+1}]$ is $\min(D_k, D_{k+1})$. Induction gives the claim. ∎

**Consequences.**
- Under uniform guarantees (§A.6 Rev 1), BP guarantees capture **iff** $\alpha_C \le 1$, for every $s > 1$. This is the exact analogue of H1 for BP, and unlike H1 it is proven. The decisive runner is the trivial one: it flees straight.
- PP catches that same runner for every $\alpha_C$, because a collinear chaser that is faster cannot pass the runner without touching it.
- So "fixing" PP's overshoot destroys the mechanism that closes the final gap.

> **Rev 2 clarification (2026-11-12): what §B.2a does *not* show.** The result is about **uniform guarantees by BP**. It does not say that PP dominates BP. Dominance would mean that PP captures every runner strategy that BP captures, and that is **false**.
>
> *Counterexample*, checked by hand and as a regression test (`test_braking_beats_pure_pursuit_on_a_specific_runner`):
> - $R_C = 4$, $R_E = 2$, $\tau_C = 1$, $\tau_E = 1/4$, $\varepsilon = 0.1$.
> - $\mathbf c_0 = 0$, $\mathbf e_0 = (1, 0)$. Both agents start fresh at $t = 0$.
> - The runner plays $(0,2)$ on $[0, 1/4)$, then $(-1/2, -1)$ on $[1/4, 1)$.
> - PP plays $(4,0)$. Its closest approach is $\sqrt{0.2} \approx 0.4472$, at $t = 0.2$: no capture in $[0,1]$.
> - BP plays $(1,0)$ and meets the runner. The two coincide at $t = 0.75$, so the first contact is at $t = 0.75 - 0.1/\sqrt{3.25} \approx 0.6945$.
>
> The Stage 2 statement "BP never captured where PP failed" is an **empirical** observation, valid for those three runners on those 40 paired states. It is not a theorem.
- The numerical counterpart: the sweep pinned BP-vs-flee separation at $R_E\tau_C$ to relative precision $2\times10^{-11}$ in 1,396 runs.

### B.2b PP captures beyond $\alpha_C = 1$: guarantee up to $2s/(1+s)$ **[Proved]** — *Rev 3, new*

**Proposition 1′.** Let $R_C > R_E$ and
$$\alpha_C = \frac{R_E\tau_C}{\varepsilon} \ \le\ \frac{2s}{1+s}, \qquad s = R_C/R_E.$$
Then PP captures every runner. This holds for any runner agility or information (clairvoyance included), any dimension, both speed models, and any initial state and phases. Capture happens by $\varphi_C + (K+2)\tau_C$, with $K$ as in §B.2.

*Proof.* Write $L = R_C\tau_C$ and $\rho = R_E\tau_C$. If $\alpha_C \le 1$, Proposition 1 applies, so assume $\alpha_C > 1$. Then $s\varepsilon < L$, because $s\varepsilon < L \iff \varepsilon < \rho$. As in §B.2:
- **Case (i), $D_k \ge L$:** $D_{k+1} \le D_k - (L - \rho)$, a fixed positive decrease.
- **Case (ii), $D_k < L$ (overshoot):**
  - At $\sigma^\* = D_k/R_C$ the chaser sits on $\mathbf e_k$. The runner is within $D_k/s$ of it, so the interval captures if $D_k \le s\varepsilon$.
  - Otherwise, at the end of the interval the chaser is $L - D_k$ past $\mathbf e_k$ along $\hat{\mathbf u}_k$, and the runner is within $\rho$ of $\mathbf e_k$. So
  $$D_{k+1} \le L + \rho - D_k. \tag{†}$$

Suppose an overshoot step $k$ does not capture, so $D_k > s\varepsilon$. Then by (†), $D_{k+1} < L + \rho - s\varepsilon \le s\varepsilon$, where the last inequality is exactly the hypothesis $L + \rho \le 2s\varepsilon$. Since $s\varepsilon < L$, step $k+1$ is again an overshoot with $D_{k+1} \le s\varepsilon$, and it captures.

Case (i) steps end after at most $K$ steps. If $D_K = L$ exactly, case (i) gives $D_{K+1} \le \rho$. With $\rho \le s\varepsilon$ (because $\alpha_C \le 2s/(1+s) < s$) and $\rho < L$, the next interval captures. ∎

*Remarks.*
- The only new ingredient beyond Proposition 1 is (†): the separation after an overshoot is at most $L + \rho$ minus the separation before it. The runner cannot make two near-misses in a row.
- $2s/(1+s) \in (1, 2)$. It tends to 1 as $s\to1^+$ and to 2 as $s\to\infty$.
- The argument is pathwise, like Proposition 1. That is why agility, information and dimension drop out.
- (†) is wasteful, though. It credits the runner with both the full sidestep $D_k/s$ at mid-interval and the full displacement $\rho$ at the end, and no single path achieves both.

**Checked in code.** `test_extended_threshold` runs on the boundary and 3% inside it, with $s \in \{1.2, 1.5, 3\}$. The runners are flee, perpendicular, predictive, random, and the Stage 3 best-response planner, with random phases and $a \in \{1/4, 1, 2\}$. Every run is captured within the bound. These are finitely many cases.

### B.3a An exact periodic escape from PP **[Proved]** — *Rev 3, new*

**Setting.** Units $R_E = 1$, $R_C = s > 1$. The runner decides at every chaser decision; this holds for $a = 1$ with aligned phase, or for any runner whose lattice contains the chaser's. Define, for $0 < y < s$,
$$g(y) = y^2 - \frac{y(s^2-1)}{4(s-y)}, \qquad G(s) = \max_{0<y<s} g(y), \qquad \alpha_{\text{sym}}(s) = G(s)^{-1/2}.$$

**Proposition 3.** If $\alpha_C > \alpha_{\text{sym}}(s)$, there is an initial state from which the runner evades PP forever. Specifically: collinear positions, separation $D = y^\*\tau_C$ with $y^\* = \arg\max g$, and both agents deciding at $t = 0$. The separation at every chaser decision equals $D$, and the closest approach in every period is $\tau_C\sqrt{G(s)} > \varepsilon$. The runner moves at exactly full speed, so the orbit is also admissible in the exact-speed model.

*Proof.*
1. **Frame.** At a chaser decision, place the chaser at the origin with velocity $s\hat{\mathbf x}$ and the runner at $(D, 0)$. The runner holds one velocity $\mathbf v$ for the period. The relative velocity is $\mathbf w = \mathbf v - s\hat{\mathbf x}$; write $\mathbf w = |\mathbf w|(-\cos\theta, \sin\theta)$.
2. **Return condition.** The relative position $(D,0) + \sigma\mathbf w$ is at distance $D$ again at $\sigma = 2D\cos\theta/|\mathbf w|$. Setting this equal to $\tau_C$ gives $|\mathbf w| = 2D\cos\theta/\tau_C = 2y\cos\theta$, where $y = D/\tau_C$.
3. **Closest approach.** It occurs at $\sigma = \tau_C/2$, inside the interval, at distance $D\sin\theta$.
4. **Speed limit.** $|\mathbf v|^2 = |\mathbf w|^2 - 2s|\mathbf w|\cos\theta + s^2 \le 1$ becomes $4\cos^2\theta\, y(s-y) \ge s^2 - 1$. This forces $y < s$, i.e. $D < R_C\tau_C$, the overshoot regime.
5. **Maximize the miss.** Taking the smallest admissible $\cos^2\theta$ gives $(D\sin\theta)^2 = \tau_C^2\, g(y)$. So a pass that misses by more than $\varepsilon$ exists iff $\tau_C^2 G(s) > \varepsilon^2$, i.e. $\alpha_C > \alpha_{\text{sym}}(s)$.
6. **Repeat.** At the next chaser decision the separation is again $D$, and PP re-aims along the new line of sight. The same construction, rotated, applies, because PP and the runner's rule are both rotation-equivariant. ∎

**Values** (`best_pass` in `best_response.py`; checked against a 200k-point grid):

| $s$ | 1.05 | 1.2 | 1.5 | 2 | 3 | 10 | $\to\infty$ |
|---|---|---|---|---|---|---|---|
| $2s/(1+s)$ (§B.2b, capture) | 1.024 | 1.091 | 1.200 | 1.333 | 1.500 | 1.818 | 2 |
| $\alpha_{\text{sym}}(s)$ (escape) | 1.225 | 1.434 | 1.630 | 1.781 | 1.896 | 1.990 | 2 |

**Consequences.**
- For runners that can decide at every chaser decision,
$$\frac{2s}{1+s} \ \le\ \kappa_{\text{PP}}(s) \ \le\ \alpha_{\text{sym}}(s).$$
  Here $\kappa_{\text{PP}}$ is the supremum of $\alpha_C$ at which PP's uniform guarantee holds. Both bounds tend to 2 as $s \to \infty$, which pins the limit. **The gap for finite $s$ is open.**
- **Agility is not what defeats PP.** The orbit needs only $a = 1$, so a runner exactly as agile as the chaser escapes. What matters is $\alpha_C$, the chaser's blink length relative to the tag radius.
- Whether a *less* agile runner ($a > 1$) can escape for some $\alpha_C$ is open.
- **Checked in code.** `test_symmetric_pass_evades_forever` runs 3,000 periods at three $(s, \alpha_C)$ pairs with $\ge 4\%$ miss margin. The separation at every decision equals $D$ to $10^{-11}$, and the minimum separation equals the predicted miss to $10^{-9}$.

### B.2c A hybrid chaser captures up to $\alpha_C = s$ **[Proved]** — *Rev 4, new*

**Chaser $H$.** At each decision, $H$ plays BP if $D_k > s\varepsilon$ and PP otherwise.

**Statement.** In the bounded-speed model, $H$ captures every runner iff $\alpha_C \le s$.

**Proof idea.**
- BP lands exactly on the observed point, so the next separation is at most $\rho = R_E\tau_C$.
- If $\rho \le s\varepsilon$, the next PP pass captures, by §B.2 case (ii).
- If $\alpha_C > s$, a collinear straight-line runner pins the separation at $\rho > s\varepsilon$, and $H$ brakes forever.
- At $\alpha_C = s$, capture is by exact tangency against that runner.

The full proof is in the review, §3.4. This gives $\kappa^\*(s) \ge s$ for the best chaser. Theorem 3 needs speeds below $R_C$, so it does not apply in the exact-speed model.

The result came out of asking which properties of PP the proof of §B.2b uses. Within this model, with constant velocity per period, that proof applies to PP only.

### B.3b Certified multi-leg escape orbits **[Computer-assisted proof, exact rational arithmetic]** — *Rev 4, new*

**Key fact.** Once the runner's legs within a period are fixed, the closure condition "separation returns to $D$" is **linear** in $D$. So rational leg velocities give an exact rational closing separation $D^\*$, and exact rational clearances.

**Result.** For $s \in \{6/5, 3/2, 2\}$ and $m \in \{1, 2, 4, 8, 16\}$, a runner with $\tau_E = \tau_C/m$, aligned with the chaser, escapes PP for all $\alpha_C \ge \alpha_c(s,m)$. The best values are:

| $s$ | $\alpha_c(s, 16)$ |
|---|---|
| 6/5 | 1.3890 |
| 3/2 | 1.5397 |
| 2 | 1.6540 |

These improve on $\alpha_{\text{sym}}(s)$.

**Data and checks.** The certificate data are in `results/stage3/certified_orbits.json`, and `tests/test_certificates.py` re-checks them independently. Details are in the review, §7.

### B.3 Where PP's argument breaks: the matador geometry **[Proved, single interval]**

Suppose the chaser commits to PP at distance $D$, and the runner sees that commitment immediately. Over $v \in S^{d-1}$, the relative velocity $\mathbf w = R_E v - R_C\hat{\mathbf u}$ ranges over a sphere of radius $R_E$ centered at $-R_C\hat{\mathbf u}$.

- The largest angle between $\mathbf w$ and the line of sight is $\arcsin(1/s)$. That is the tangent sidestep.
- The resulting minimum separation is exactly $D/s$, reached at $\sigma = D/R_C$.
- So a reactive runner survives a PP pass iff $D > s\varepsilon$, and the pass ends inside the interval iff $D < R_C\tau_C$.
- **That escape window $(s\varepsilon,\ R_C\tau_C)$ is nonempty iff $\alpha_C > 1$**, which is exactly the complement of Proposition 1's hypothesis.

This is the precise reason I suspect Proposition 1 is sharp for PP (H1 below). It is only a one-interval statement, so it is **not** yet an escape theorem.

> **Rev 1.**
> - Under the primary model the runner's tangent velocity is still admissible, because its norm is exactly $R_E$. The single-interval computation is therefore unchanged. It is checked numerically in `test_tangent_sidestep_min_distance`.
> - Surviving one chaser commitment **does not** imply indefinite evasion. After the pass, the next state, meaning separation, phases and the chaser's new aim, may be worse for the runner. Indefinite evasion needs an invariant set of states that the runner can maintain forever.
> - The bounded-speed model also gives the *chaser* new options, such as braking to avoid overshooting. So the $\alpha_C > 1$ region may behave differently from the exact-speed model.

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

> **Rev 1 — resolutions.**
> 1. Case 4 is retained in the paper. We document the unrestricted-space escape (B.1) and the finite-commitment interception (B.1a/b). The bounded arena is a future option and is not implemented.
> 2. The primary speed model is $\|\mathbf v\| \le R$, with exact speed kept as a variant.
> 3. The opponent's clock is observable. Perfect information is unchanged.
> 4. Simultaneous moves: both agents observe the state at $t^-$, and neither sees the other's new choice. The engine enforces this by freezing all observations before any policy is queried.

---

## C. Research hypotheses

**H1 — Proposition 1 is sharp for pure pursuit. [Conjecture]**
- *Claim:* for every $s>1$ and $\alpha_C > 1$, there exist $\bar\alpha_E > 0$ and an initial state from which a runner with $\alpha_E < \bar\alpha_E$ avoids PP forever.
- *Why interesting:* together with Proposition 1, it would give an exact threshold $\alpha_C = 1$ for PP against agile runners. That is "if you can't leave the tag radius during one of the chaser's blinks, you lose; otherwise you can play matador."
- *Falsified by:* a proof that PP captures for some $\alpha_C>1$ against all sufficiently agile runners, or by numerics showing that no runner policy, including best-response search, escapes near $\alpha_C = 1^+$. A heuristic runner failing to escape does **not** falsify it.
- *Also expected:* for sluggish runners (large $\alpha_E$), PP's capture region extends past $\alpha_C = 1$. That is the agility-vs-speed tradeoff in its clearest form.

> **Rev 1.** The exact PP threshold remains **conjectural**.
> - The supporting evidence (B.3) is a one-interval survival computation. One-interval survival does not imply indefinite evasion (see the B.3 Rev 1 note).
> - A proof of H1 needs a runner strategy together with an invariant region of states that PP cannot leave.
> - H1 is now stated for the primary bounded-speed model, where PP still means full speed. The runner's tangent sidestep is admissible in that model.

> **Rev 3 — H1 is false as stated.**
> - §B.2b proves PP captures every runner for $1 < \alpha_C \le 2s/(1+s)$, however agile. So the PP threshold is *not* $\alpha_C = 1$.
> - The single-interval survival in §B.3 is exactly the kind of evidence the Rev 1 note warned about. The runner survives one pass but cannot survive the next one.
> - **Replacement question (H1′):** where in $[2s/(1+s),\ \alpha_{\text{sym}}(s)]$ is $\kappa_{\text{PP}}(s)$? Does it depend on the runner's agility class?
> - Stage 3 numerics address H1′ in `results/stage3/note.md`.

**H2 — Smarter chasers beat the PP threshold, but not without bound. [Conjecture]**
- *Claim:* let $\kappa^\*(s)$ be the supremum of $\alpha_C$ for which *some* chaser strategy guarantees capture against a fully agile runner ($\alpha_E \to 0$). Then $1 < \kappa^\*(s) < \infty$.
- *Heuristic:* a chaser can time its approach so that its next decision lands with $D \le s\varepsilon$, where the sidestep fails. The runner can perturb the post-interval distance by about $\pm R_E\tau_C$, and once that exceeds the window width $(s-1)\varepsilon$, timing should fail.
- *Why interesting:* $\kappa^\*(s)$ is literally "how much sluggishness can a given speed advantage buy back" (RQ1 and RQ4).
- *Falsified by:* a proof that $\kappa^\* = 1$ (PP is optimal), or that $\kappa^\* = \infty$ for some $s$.

> **Rev 4 — status.**
> - Lower half **proven**. In the bounded-speed model $\kappa^\*(s) \ge s$ (§B.2c). In the exact-speed model $\kappa^\*(s) \ge 2s/(1+s)$, from PP itself (§B.2b).
> - The heuristic in H2 was the wrong mechanism. The gain over $\alpha_C = 1$ comes from PP's own two-pass structure, and from braking onto the observed point, not from timing the approach.
> - Finiteness of $\kappa^\*$ is **open**.

**H3 — Agility is monotone under refinement but not in general. [Partly provable + Conjecture]**
- *Provable [Sketch]:* if the runner's decision lattice contains another runner's lattice ($\tau_E' = \tau_E/k$ with aligned phase), the more frequent runner can mimic the less frequent one. So the guaranteed-escape region is monotone along such chains.
- *Conjecture:* for non-nested clocks (e.g. $a = 1$ vs. $a = 1.3$), the guaranteed-capture region and worst-case capture time are **non-monotone** in $a$, because of resonance between decision lattices.
- *Why interesting:* it would show that "agility" as decision frequency is not a scalar advantage. Phase structure matters. That directly addresses your requirement not to assume monotonicity.
- *Falsified by:* a monotonicity proof, or a fine $a$-sweep with best-response opponents showing no non-monotonicity beyond CI width.

> **Rev 1 — what H3 is actually about.** Under the fixed-cadence model, a higher nominal frequency on a non-nested lattice is a *different* action set, not a larger one (see the §A.4 Rev 1 note). Non-monotonicity in $a$ would therefore show that **schedule alignment** matters. It would *not* show that more agility hurts.
>
> Under the maximum-frequency reading, monotonicity is immediate. So H3 is a statement about the fixed-cadence model only, and the paper must say so wherever it is reported. Any interpretation of a non-monotone result has to name the reading it uses.

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

> **Rev 1.**
> - The projection sketch now fits the **primary** model directly. The orthogonal projection of a chaser velocity with $\|\mathbf v_C\| \le R_C$ is admissible in the planar game, on the same clock.
> - It is still a **sketch**. What remains is to formalize strategies, i.e. nonanticipative maps on observation histories, and to check that the runner's planar strategy is well-defined on projected observations, including projected precommitted velocities.
> - It would give only $\text{Escape}_{2D}(\text{projected state}) \Rightarrow \text{Escape}_{3D}(\text{state})$.
> - Any **equivalence** of 2D and 3D guarantees remains a conjecture. In particular, the converse direction has no argument at all.
> - Exact-speed variant: the projected chaser is *not* admissible there, so the sketch does not apply.

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

> **Rev 1:** no citation has been verified yet. The status above is unchanged.

## E. Implementation roadmap

> **Rev 1 — Stage 1 as built.**
> - The package lives at `src/tagsim/`, not in the suggested `dynamics/`/`strategies/`/`game/` folders. Three small modules were enough at this size.
> - Stage 1 ships scripted policies only. PP and flee exist only as test-local helpers.
> - Implementation decisions are listed in `NOTES.md`.

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
