# How to Win a Game of Tag — Stage 5: the optimal-chaser problem

*2026-11-13. This document is a first pass at H2's open upper half: is $\kappa^\*(s)$ finite, and
can any chaser beat the hybrid chaser $H$ of Theorem 3 ($\kappa^\*(s) \ge s$, bounded-speed model)?*

**Status up front.** No improvement on $\kappa^\*(s) \ge s$ is found here, and $\kappa^\*$'s finiteness
is still open. What this pass does establish: the one natural "smarter chaser" candidate already in
the codebase (`Intercept`, built in Stage 2) is not a viable route to beating $s$, and the one class of
runner that would be easy to rule out (straight flight) cannot witness any finite upper bound on
$\kappa^\*$ at all, for any $s$. That clears away a false lead and narrows what a real upper-bound
construction would have to look like.

## 1. The problem

Recall (stage0_spec.md §B.2c/§3.5, Thm 3): $\kappa^\*(s;\mathcal R,\mathcal I_{\rm all},\text{bounded})$ is
the supremum of $\alpha_C$ for which **some** admissible chaser strategy guarantees capture of
**every** runner in $\mathcal R$. Known so far, for $\mathcal R \supseteq \mathcal R^{\rm al}_1$:

$$\kappa_{\rm PP}(s) \;\le\; s \;\le\; \kappa^\*(s), \qquad \text{the upper half open.}$$

The lower bound is $H$ (brake onto the observed point while $D > s\varepsilon$, else PP). $H$ is known to
fail above $\alpha_C = s$ against one specific runner: straight flight in a fixed direction, which pins
the separation at $\rho = \alpha_C\varepsilon$ forever because $H$ never reads the runner's *velocity*,
only its position. That suggests two questions:

1. Is the straight-flight failure a fundamental obstruction (so $\kappa^\* = s$), or an artifact of $H$
   ignoring information it could have used?
2. If some other chaser does read velocity (or more), can it push the threshold past $s$?

## 2. Straight flight cannot witness any finite upper bound on $\kappa^\*$

**Proposition 11.** Let $s > 1$. For *every* $\alpha_C$, there is a chaser strategy that captures every
runner moving at a fixed velocity $\mathbf v_E$ ($\|\mathbf v_E\| \le R_E$) from a fixed initial point,
in finite time independent of how the chaser's own decision period is scheduled.

*Proof.* This is the Interception Lemma (stage0_spec.md §B.1a) plus one remark already recorded there.
Let $\mathbf e(t) = \mathbf e_0 + \mathbf v_E t$, $\mathbf c_0$ the chaser's position at $t=0$, and
$f(t) = \|\mathbf e(t)-\mathbf c_0\| - R_C t - \varepsilon$. Then $f(0) = \|\mathbf e_0-\mathbf c_0\|-\varepsilon > 0$, and

$$f(t) \;\le\; \|\mathbf e_0-\mathbf c_0\| + \|\mathbf v_E\| t - R_C t - \varepsilon \;=\; \|\mathbf e_0-\mathbf c_0\|-\varepsilon - (R_C-\|\mathbf v_E\|)t \;\xrightarrow{t\to\infty}\; -\infty,$$

since $R_C = sR_E \ge s\|\mathbf v_E\| > \|\mathbf v_E\|$ when $s>1$. So $f$ has a root $t^\*$, and by (★)'s $(\Leftarrow)$ direction a single
constant-velocity chaser leg (re-selected every period, as the Lemma's "precommitted chaser" remark
allows) achieves capture by $t^\*$ — a time that depends only on $s$ and the initial geometry, **not on
$\alpha_C$**. $\blacksquare$

**Corollary.** No straight-flight (open-loop constant-velocity) runner can be used to prove
$\kappa^\*(s) < \infty$, for any $s > 1$. Any valid upper-bound construction needs a runner that reacts
to the chaser's actual moves — which is exactly what defeated $H$'s specific rule but is absent from the
straight-flight witness itself.

**This chaser already exists in the codebase.** `Intercept` (`src/tagsim/strategies.py`, built in Stage
2) is precisely the construction above: it computes $t^\*$ from the runner's last committed velocity via
`contact_time` (the quadratic form of (★)) and aims full speed at the predicted contact point, falling
back to PP if no contact is predicted. Stage 2's sweep already recorded `intercept vs flee: 1.00
(480/480)` captured at every tested $\alpha_C > 1$ (`results/stage2/note.md`); `test_intercept_beats_flee_at_large_alpha`
below extends this to $\alpha_C$ up to 500, confirming capture time scales with $\alpha_C$ as the proof
predicts, not with the threshold the position-only chaser $H$ has.

So $H$'s failure above $\alpha_C = s$ is **not evidence that $\kappa^\*(s) = s$.** It is a statement about
$H$ specifically: $H$ throws away velocity information that a predictive chaser could use to beat this
particular runner at any $\alpha_C$.

## 3. But `Intercept` does not dominate $H$ either

This narrows the search, but it does not yield a better chaser. `Intercept`'s model of the opponent —
"holds its last committed velocity" — is exactly wrong against a runner that changes heading every
period, which is what the hard runners in this problem already do (Theorem 2's symmetric-pass orbit).
Checking `Intercept` against that orbit (`test_intercept_loses_to_symmetric_pass_below_s` below):

| $s$ | $\alpha_C$ | $H$ captures symmetric-pass? | `Intercept` captures symmetric-pass? |
|---|---|---|---|
| 2 | 1.801 ($< s$) | **yes** | **no** |
| 2 | 1.99 ($< s$) | **yes** | **no** |
| 1.5 | 1.51 ($> s$, $< \alpha_{\rm sym}$) | no | no |

At $s=2$, $\alpha_C \in \{1.801, 1.99\}$ — strictly inside $H$'s proven guarantee region
($\alpha_C \le s$) — `Intercept` still loses to the symmetric-pass orbit. So `Intercept` is not a
refinement of $H$; it trades one failure mode (ignoring velocity) for another (extrapolating a velocity
that the runner deliberately keeps changing). This matches the Stage 2 note's empirical observation that
intercept's advantage "is largest against runners whose velocity stays predictable" and vanishes against
an agile one. It rules out "the natural upgrade of $H$" as a route to $\kappa^\* > s$.

## 4. What this leaves open

- **Straight flight is void as a witness (§2), and the natural predictive upgrade of $H$ does not beat
  $H$ either (§3).** Neither direction moves the known bracket $\kappa^\*(s) \ge s$.
- **The real obstacle is the same one Stage 3/4 already found for PP: a runner that changes heading in
  sync with the chaser's own decisions.** Settling $\kappa^\*(s)=s$ (vs. $\kappa^\*(s)>s$) requires
  showing some chaser beats — or no chaser can beat — a periodic/orbit-style runner specifically, which
  is a genuinely two-sided optimization: the chaser's rule and the runner's orbit would have to be solved
  *together* (an Isaacs-type value problem), not read off a one-sided best response the way Stage 3's
  $g(y)$ analysis handles PP. None of the certificate machinery built in Stages 3–4C (which all fix one
  side's rule and optimize the other) applies directly to this.
- Whether $\kappa^\*(s)$ is even finite is therefore still open. $s$ is the best proven value either way.

## 5. Recommendation

Stop here rather than hand-build a two-sided differential-game solver on a hunch. The two findings above
are real (a proof and a clean, reproducible engine refutation) but they are negative results about two
candidate routes, not progress toward a value. A genuine next step would need to pose the two-sided
problem properly (what does the chaser observe about the runner's *schedule*, not just its last
velocity?) before any computation is worth running. Given the paper's own stopping pattern elsewhere,
that is better spent as a clearly-scoped question for the next pass than as more exploratory code here.

## Appendix: reproduction

- `tests/test_optimal_chaser.py::test_intercept_beats_flee_at_large_alpha` — Proposition 11 / §2, for
  $\alpha_C \in \{5, 50, 500\}$ at three values of $s$.
- `tests/test_optimal_chaser.py::test_intercept_loses_to_symmetric_pass_below_s` — §3's table.
- `results/stage2/note.md` — the original intercept-vs-flee sweep this builds on.
