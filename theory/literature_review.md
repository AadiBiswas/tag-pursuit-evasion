# Literature review: sampled pursuit, discrete-time pursuit and periodic evasion

*Stage 3.5, 2026-11-12. This review is focused, not exhaustive. The search log and access limits are recorded below.*

> **Stage 4A update.** Two sources are updated here:
> - **Bopardikar–Bullo–Hespanha.** The exact theorem statements have been recovered from page images, and the DOI is verified. Their Prop. III.4 is a circling evasion of a greedy discrete-time pursuer: the closest prior construction to our periodic orbits.
> - **Alonso–Goldstein–Reingold.** The metadata is verified, but the full text could not be read.
>
> Details are in `theory/stage4_viability_analysis.md` §8, and that section supersedes the corresponding entries below. Theorem 2 stays *Potentially distinct*, now with the BBH precedent cited.

**Status labels**, for each contribution of ours:
- **Previously established** — follows from a source we read.
- **Potentially distinct** — differs from every source we read, but the search is incomplete.
- **Unresolved** — too little evidence either way.

**Nothing here is labelled novel.** Bibliographic entries are in [`references.bib`](../references.bib). The BibTeX key appears in brackets on first mention.

## 1. Sources examined

### 1.1 Aleem, Nowzari, Pappas — self-triggered pursuit [AleemNowzariPappas2015]

*Self-triggered Pursuit of a Single Evader with Uncertain Information*, arXiv:1512.06184.
- v1 dated 19 Dec 2015, v2 dated 19 Jan 2016.
- Comments field: preprint for submission to Automatica.
- Partly presented at IEEE CDC 2015, which is their reference [1].
- No journal version located.

**Access.** The full v2 text was read: the arXiv HTML rendering, covering the abstract through Appendix B and the references. The PDF text was also extracted locally. Section and equation numbers below follow v2. Page numbers were not recorded.

| Aspect | Model |
|---|---|
| Motion | Planar single integrators. The pursuer runs at fixed speed $v_p$, normalised to 1. The evader has speed $\le \nu < 1$ and moves in continuous time (§2–3, Eq. 4). |
| Pursuer control | Zero-order-hold pure pursuit (Eq. 2): heading toward the evader position sampled at $t_k$, held until $t_{k+1}$. |
| Update times | **Self-triggered**, chosen by the pursuer: $t_{k+1} = t_k + \phi(D_k, \nu)$ (Eqs. 3, 6). The inter-sample time is state-dependent and shrinks with the distance. The evader has no schedule. |
| Observation | Exact evader position at sample times (§3). §4 adds a bounded estimate error $\gamma_k = \beta \hat D_k$. §5 adds memory of earlier estimates. |
| Capture | Distance $\le \varepsilon$. Remark 3.3 states that capture is declared at any time, not only at updates. Open or closed ball is not specified. |
| Evader | Worst case over its reachable set in the analysis. A heuristic four-direction evader in the simulations (§6). |

**Main results.**
- **Proposition 3.1.** With the trigger of Eq. 6, $D_{k+1} \le h(\nu) D_k$ with $h(\nu) < 1$. Appendix B bounds the separation as $D_k - (1-\nu)\phi$.
- **Theorem 3.2.** Capture occurs in finitely many samples, $n_{\max} = \lceil \log(\varepsilon/D_0)/\log h(\nu) \rceil$ (Eq. 8), and $T_{\rm cap} < D_0/(1-\nu)$.
- **Remark 3.3.** Gives $T_{\rm cap} \le (D_0 - \varepsilon)/(1-\nu)$, and the classical continuous-time bound $(D_0-\varepsilon)/(v_p - v_e)$, which they cite to Isaacs.
- **Theorem 4.1.** Inter-sample times are bounded below by $\varepsilon\,q(\nu)$, so there is no Zeno behaviour under bounded estimation error (Eqs. 12–13).
- **§5.** Memory can only lengthen the inter-sample times (Eqs. 18–19).
- **Methods.** Worst-case reachable-set geometry; geometric series.

**Not in the paper.** None of the following appears anywhere in it:
- a fixed exogenous sampling period;
- an evader with its own decision clock;
- overshoot (the pursuer passing the sampled point);
- a condition relating $\nu\cdot$(period) to $\varepsilon$, other than the lower bound in Theorem 4.1;
- any evasion or periodic-orbit result.

### 1.2 Bopardikar, Bullo, Hespanha — discrete-time games with limited sensing [BopardikarBulloHespanha2008]

*On Discrete-time Pursuit-evasion Games with Sensing Limitations*, IEEE Transactions on Robotics 24(6):1429–1439, 2008.
- Metadata comes from the authors' publication list and BibTeX file.
- The DOI was not verified: dblp refused automated access, and IEEE Xplore was not opened.
- Earlier versions appeared at ACC 2007, which is their [18] and [19].

**Access.**
- The author-hosted final manuscript (`distrpe-shaunak.pdf`) was read via local text extraction.
- Mathematical symbols are lost in that extraction, so the exact inequalities of the theorems are **not** reliably recovered.
- The proofs are in a technical report, CCDC-08-0313, which is their [23] and was not obtained.

| Aspect | Model |
|---|---|
| Motion | Discrete time, planar. **Alternating moves**, evader first (§II, Fig. 1). Every player has the same stepping radius $r_{\rm step}$: "identical motion capabilities". |
| Environment | Single pursuer: bounded convex $Q$. Multiple pursuers ($N \ge 5$): unbounded plane. |
| Observation | Sensing radius $r_{\rm sens}$. Measurements are taken before and after the evader's move. The evader is a "reactive rabbit" that moves only after first detection. |
| Capture | **Point capture** (same position) **at discrete times**. |
| Results (§III) | Lemma III.2 bounds the time of the SWEEP phase. Theorem III.3 (GREEDY: move toward the last sensed evader position at maximum step) is a sufficient condition on $r_{\rm sens}/r_{\rm step}$ for the pursuer to keep sensing the evader, after which Sgall's LION strategy captures; the condition is stated to be tight against GREEDY. Multiple pursuers: a randomized SWEEP over a "trapping chain" formation (Definition III.6) gives a capture probability independent of the evader's location; capture then follows by the PLANES strategy. |
| Methods | Reduction to known unlimited-sensing strategies, namely Sgall's LION and Kopparty–Ravishankar's PLANES. |

### 1.3 Yufereva — discrete-time simple pursuit in compact spaces [Yufereva2016]

*Lion and Man Game in Compact Spaces*, arXiv:1609.01897. The year is inferred from the identifier. No venue was found.

**Access.** The arXiv HTML rendering was read through §5.3. §5.4 onward was seen only as an automated summary, so it is partial.

| Aspect | Model |
|---|---|
| Motion | Continuous time, equal speeds (1), on a **compact** geodesic space with the betweenness property. |
| Pursuer | **Discrete-time simple pursuit.** At times $i\varepsilon$ the lion takes a geodesic toward the man's *current* position and follows it for time $\varepsilon$, **stopping if it reaches that point**. The re-planning period equals the capture radius. |
| Capture | $\varepsilon$-capture: distance $< \varepsilon$ at some time, checked continuously. |
| Results | Proposition 1: every $\varepsilon$-simple-pursuit curve reaches distance $< \varepsilon$. Theorem 4.1: the lion wins in such spaces. Corollary 1: the same for compact spaces with a convex metric. Examples include CAT(0) spaces. |
| Methods | Compactness, and limit points of the sampled trajectory. |

### 1.4 Shchelchkov — nonlinear games with discrete control [Shchelchkov2023]

*Relative optimality in nonlinear differential games with discrete control*, Sbornik: Mathematics 214(9):1337–1350, 2023, DOI 10.4213/sm9851e.

**Access.** English text on Math-Net.Ru was read through the start of the proof of Theorem 4. The conclusion and the references were seen only in summary.

| Aspect | Model |
|---|---|
| Dynamics | $\dot x = f(x,u) + g(x,v)$, and a second-order analogue. The pursuer's control takes values in a finite set. The evader's control is any measurable function. |
| Pursuer updates | Piecewise-constant strategies on a partition **chosen by the pursuer**. A fixed step suffices, chosen small: Theorem 2's proof takes $\Delta = T/q$ with $q$ large. |
| Capture | $\varepsilon$-capture in the sense of reaching **arbitrarily small** neighbourhoods of 0 (Definitions 2, 5). There is no fixed radius. |
| Results | Theorem 2: tracking of an auxiliary simple-motion trajectory to any accuracy. Theorem 4: capture for the second-order system. Theorems 1 and 3 are cited from the author's earlier work. |

**Related but not read.** A *Differential Equations* (2022) paper by the same author on constant-step strategies was located, but the download was refused (HTTP 403).

### 1.5 Pan, Zhu — timing-aware games with self-triggered control [PanZhu2025]

*Timing-Aware Two-Player Stochastic Games with Self-Triggered Control*, arXiv:2512.18109, v1 dated 19 Dec 2025.

**Access.** Read through §4. Only a summary of §5 and the conclusion was seen.
- **Model.** Both players choose their own dwell times and hold open-loop controls in between. The clocks are asynchronous and are part of the strategies. The model is a controlled PDMP with discounted cost plus a per-trigger cost.
- **Results.** Theorem 1 is a verification theorem for Nash equilibria. Theorem 2 is a contraction result for the Stackelberg follower.
- **Scope.** There is **no capture radius** and no capture or evasion theorem. The pursuit example is cost-based.

### 1.6 Located but not read

| Work | Why it matters | Status |
|---|---|---|
| Alexander, Bishop, Ghrist, *Pursuit and evasion in non-convex domains of arbitrary dimension* (RSS 2006 proceedings, cited as BBH [7]). Also the preprint `convexcapture.pdf`. | A greedy discrete pursuit strategy in general dimension. | The preprint download was refused (HTTP 403). |
| Alonso, Goldstein, Reingold, *Lion and man: upper and lower bounds*, ORSA J. Computing 4(4), 1992 (cited as BBH [6] and ANP [2]). | BBH describe it as a pursuer moving toward the man's current or previous position, reducing the distance to a finite non-zero amount. This is the closest classical relative of our overshoot question. | Not obtained. **Highest-priority unread source.** |
| Sgall, *A solution of David Gale's lion and man problem*, TCS 259, 2001. | Discrete-time capture with equal speeds. | Not obtained. |
| Bopardikar, Bullo, Hespanha, CDC 2008, range-only measurements. | Discrete-time capture when the evader's step is $< 0.5$. | Seen in search results only. |
| Krasovskii–Subbotin positional games; step-by-step strategies. | Fixed partitions of time, applied to both players. | Only secondary search hits. |
| Missile-guidance work on sampling-induced miss distance. | Discrete-time pure pursuit against weaving targets. | Search hits were simulation studies or about proportional navigation. No theorem found. |

## 2. Comparison with our results

Each entry is compared only with what was actually read.

| Our result (register ID) | Closest source | What the source gives | Difference | Status |
|---|---|---|---|---|
| Lemma B(i): $D_{k+1} \le D_k - (L - \rho)$ when $D_k \ge L$ | ANP, App. B | The same bound with their interval $\phi$: separation $\le D_k - (1-\nu)\phi$. | None in substance. | **Previously established** (and elementary). |
| Prop 1: PP captures if $R_E\tau_C \le \varepsilon$ | Yufereva, Thm 4.1; ANP, Thm 3.2 | Yufereva: discrete simple pursuit with re-planning period equal to the capture radius, **equal speeds**, **compact** space, with the lion stopping at the man's point. ANP: ZOH pure pursuit captures with **pursuer-chosen**, shrinking intervals. | Ours uses a fixed exogenous period, an unbounded space, a faster chaser that does not stop (overshoot), and any runner clock. Neither source implies it: ANP's monotone decrease fails once $D < L$ with a fixed period; Yufereva needs compactness. | **Potentially distinct.** Its elementary nature makes folklore likely. |
| Thm 1: PP captures if $\alpha_C \le 2s/(1+s)$ (overshoot pairing $D_k + D_{k+1} \le L+\rho$) | none found | No source we read analyses the passes after an overshoot. | — | **Potentially distinct.** Alonso–Goldstein–Reingold and the sampled-guidance literature are unread. |
| Thm 2 / Thm 4: indefinite periodic evasion of fixed-period PP; exact rational certificates | none found | Every source we read proves capture. Yufereva's setting rules out evasion, by compactness and stop-at-target. BBH's GREEDY fails only through loss of sensing. | — | **Potentially distinct.** No source we read gives periodic evasion of sampled pure pursuit. |
| Thm 3: brake onto the observed point while $D > s\varepsilon$, then PP; captures iff $\alpha_C \le s$ | Yufereva (stop at target); BBH GREEDY (step toward the last sensed point) | Landing on the last observed point is an existing ingredient. | The threshold $\alpha_C \le s$, its sharpness, and the switch at $s\varepsilon$ were not found. | **Potentially distinct** as a theorem. The ingredient is **previously established**. |
| Thm 5: policy separation (PP evaded, $H$ guarantees) at $s = 2$, $\alpha_C = 1.9$ | none found | — | Depends on Theorems 2 and 3. | **Potentially distinct.** |
| Lemma M: monotonicity in $\varepsilon$ | standard | — | A routine inclusion argument. | **Not claimed** as a contribution. |
| Linear-closure certificates (exact rationals) | general computer-assisted-proof practice | — | Exact rational verification is standard. Only the observation that closure is linear in $D$ is specific to us. | **Unresolved.** Not claimed. |
| Engine: closed-form continuous contact detection, exact rational clocks | standard computational geometry | — | — | Not a mathematical contribution. |

**Asynchronous or unequal update rates with capture guarantees.** Among the sources read, only Pan–Zhu model two clocks, and they have no capture criterion. ANP and Yufereva give the evader continuous control; BBH alternate turns of equal size. So we found no source that analyses capture or evasion with **two fixed, unequal decision periods** and continuous capture checking. Given the gaps in §3, this remains **Unresolved**, not a novelty claim.

## 3. Search log and limitations

**Queries run** (web search, 2026-11-12):
1. sampled-data pure pursuit, fixed sampling period, capture radius, overshoot;
2. discrete-time pursuit–evasion with a faster pursuer, capture radius, pure pursuit, periodic evasion;
3. pursuit–evasion with different or asynchronous control update frequencies, zero-order hold;
4. discrete-time lion and man, greedy strategy (Alonso–Goldstein–Reingold);
5. pure pursuit in discrete-time guidance: sampling, miss distance, weaving;
6. Krasovskii–Subbotin step-by-step / piecewise-constant strategies;
7. Shchelchkov constant-step partition;
8. Petrosyan discrete-time simple pursuit.

**Limitations.**
- **Not done:**
  - forward citations of ANP and BBH, because dblp blocked automated access and Google Scholar was not used;
  - the IEEE Xplore records;
  - the Russian-language literature on discrete pursuit beyond the Shchelchkov items;
  - books (Isaacs; Krasovskii–Subbotin; Petrosyan, *Differential Games of Pursuit*).
- **Read only partially** (§1): BBH, because symbols were lost in extraction; Yufereva; Shchelchkov; Pan–Zhu.
- **Classical claims cited second-hand only:** the continuous-time pure-pursuit capture time $(D_0-\varepsilon)/(R_C-R_E)$, which ANP attribute to Isaacs, was not checked against Isaacs.

**Before any novelty claim:**
1. Alonso–Goldstein–Reingold (1992), and Alexander–Bishop–Ghrist.
2. The BBH technical report CCDC-08-0313, and Bopardikar's 2010 dissertation.
3. Petrosyan's discrete-time pursuit results, and the Krasovskii–Subbotin step-by-step literature.
4. Forward-citation search on ANP and BBH.
5. Sampled pure-pursuit guidance: a textbook-level check of whether capture conditions of the form $R_E T \le c\,\varepsilon$ are standard.
