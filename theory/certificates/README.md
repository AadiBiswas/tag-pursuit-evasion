# Escape certificates for Theorem 4

Exact rational certificates that an aligned runner evades full-speed pure pursuit (PP) forever, plus a standalone verifier.

```
python theory/certificates/verify.py                       # all orbits/*.json
python theory/certificates/verify.py examples/*.json       # the hand-checkable example
python theory/certificates/verify.py --summary SUMMARY.md  # regenerate the table
python theory/certificates/build.py                        # regenerate orbits/ from results/stage3/certified_orbits.json
```

- `verify.py` uses only the Python standard library (`fractions`, `json`, `math`, `decimal`). It imports nothing from `tagsim`, `experiments/` or `build.py`.
- No floating-point number enters any accept/reject decision. Floats appear only in printed messages and in the summary's decimal columns.
- The data were produced by an optimiser, then rounded to rationals. The optimiser's residuals play no part in the proof. Only the rational data below and the recurrence argument do.

## Units and frame

- **Units:** $R_E = \tau_C = 1$. So $\rho = R_E\tau_C = 1$, $s = R_C$, and the capture radius is $\varepsilon = 1/\alpha_C$.
- **Frame:** each chaser period $[k, k+1]$ has its own frame. The chaser is at the origin and the runner at $(D_0, 0)$. The $x$-axis is the line of sight $\hat u_k$, and $\hat n_k$ is $\hat u_k$ rotated by $+90°$.

## Certificate fields (`orbits/*.json`)

| field | meaning |
|---|---|
| `s` | speed ratio $R_C/R_E$, exact rational |
| `m` | runner decisions per chaser period, so $\tau_E = \tau_C/m$ |
| `clocks` | $\tau_C = 1$, $\tau_E = 1/m$, phases $\varphi_C = \varphi_E = 0$ (aligned) |
| `speed_model` | `exact` if every leg has $\|V_j\| = 1$, otherwise `bounded` |
| `D0` | separation at every chaser decision ($D^\*$) |
| `alpha_c` | rational threshold claimed: escape for every $\alpha_C \ge$ `alpha_c` |
| `legs[j]` | `t_start` $= j/m$; `duration` $= 1/m$; `runner_velocity` $V_j$ (frame coordinates); `chaser_velocity` $(s, 0)$; relative trajectory $r(t) = $ `r0` $+\, t\,$`w` for $t \in [0, 1/m]$; `t_min` (exact minimiser on the closed interval); `min_sq_sep` |
| `closure` | `r_end` $= r(\tau_C)$ in the period-$k$ frame, and its squared norm |
| `min_sq_clearance` | minimum over all legs of `min_sq_sep` |

All rationals are stored as strings like `"1389/1000"`.

## What the verifier checks

The verifier recomputes everything from the primary data (`s`, `m`, `clocks`, `D0`, the $V_j$, `alpha_c`). It accepts a certificate only if all of the following hold.

1. **Speed.** $\|V_j\|^2 \le 1$ for every leg. If the certificate claims the exact-speed model, $\|V_j\|^2 = 1$.
2. **Schedule.** There are $m$ legs, each starting at $j/m$ and lasting exactly $1/m$, with $\tau_E = 1/m$ and both phases 0. So every chaser decision time is also a runner decision time.
3. **Pursuit.** The chaser's velocity is $s\,(e-c)/\|e-c\|$, computed from the positions at the period start with an exact rational square root.
4. **Integration.** The leg start points $r_j$ are re-integrated exactly.
5. **Closure.** $\|r(\tau_C)\|^2 = D_0^2$ exactly.
6. **Clearance.** On each leg, the minimum of the convex quadratic $\|r_j + t w_j\|^2$ over the **closed** interval $[0, 1/m]$ is taken at the clamped vertex. That is a rational point, so the minimum is exact. Each minimum must be strictly greater than $1/\alpha_c^2$, which covers both endpoints and the interior between decisions.
7. **Recurrence.** The runner policy below is run against PP in absolute coordinates, exactly, for 3 periods.
   - At each chaser decision the separation must be exactly $D_0$.
   - Every leg must keep clear of the capture radius.
   - The rotation between successive frames is rational: $\hat u_{k+1} = r_{\rm end}/D_0$. So this simulation involves no rounding.
8. **Records.** Every derived number written in the file equals the recomputed one.

## Runner policy, and why one verified period gives forever

**Policy.** At chaser decision $t_k$, the runner observes $\hat u_k = (e-c)/\|e-c\|$ and sets $\hat n_k = R_{90°}\hat u_k$. On leg $j$ of that period it plays $V_{j,x}\,\hat u_k + V_{j,y}\,\hat n_k$. This needs only:
- positions at $t_k$, which the runner observes because it decides at $t_k$;
- the elapsed time since $t_k$, which it knows from its own clock.

**Claim.** If checks 1–6 pass, PP never captures this runner. The initial state is: separation $D_0$, both agents deciding at $t = 0$, and $\tau_E = \tau_C/m$.

*Proof.*
1. Suppose that at $t_k$ the separation is $D_0$ and both agents decide.
2. PP is equivariant under orientation-preserving isometries: it plays $s\hat u_k$ whatever the history. The runner's policy is defined in the frame $(\hat u_k, \hat n_k)$.
3. So in that frame, the motion on $[t_k, t_{k+1}]$ is exactly the certified local motion, which is the same for every $k$.
4. By checks 5 and 6, the separation at $t_{k+1}$ is $D_0$. By check 2, both agents decide at $t_{k+1}$. And no point of $[t_k, t_{k+1}]$ is within $\varepsilon$.
5. Velocities committed before $t_{k+1}$ do not matter, since both agents re-decide then. So the full state at $t_{k+1}$ (positions, and the clocks mod their periods) is the image of the state at $t_k$ under a rotation plus a translation.
6. Induction on $k$ completes the proof. ∎

Check 7 is not needed for the proof. It is an independent execution of the policy, which would catch a frame or orientation mistake in the argument above.

## Threshold convention: why ≥ is correct here

- Capture means $\|x_E - x_C\| \le \varepsilon$, a closed ball. For a fixed orbit with exact minimum squared clearance $c$, the orbit is capture-free iff $\varepsilon^2 < c$, i.e. iff $\alpha_C > \hat\alpha := 1/\sqrt c$.
- At $\alpha_C = \hat\alpha$ the orbit touches the ball, and that is a capture. The test `test_rejects_exact_touch_between_decisions` checks exactly this case.
- Each certificate's `alpha_c` is a rational with $1/\alpha_c^2 < c$ **strictly** (check 6). So $\alpha_c > \hat\alpha$, and the statement "escape for every $\alpha_C \ge \alpha_c$" holds with equality admitted.
- The sharper statement "escape for every $\alpha_C > \hat\alpha$" is also proven. Here $\hat\alpha$ is irrational in general, and [SUMMARY.md](SUMMARY.md) gives it to 10 digits. The decimals in the Stage 3 tables are these $\alpha_c$ values: $\hat\alpha$ rounded **up** to 4 places.

## Scope of each certificate

What each certificate proves, and nothing more:
- The exact speed ratio `s`. Nothing is claimed for nearby $s$.
- Runner period $\tau_C/m$ with phases aligned to the chaser's clock, from the stated initial state.
  - The same orbit also works for any runner period $\tau_C/(km)$, because the runner repeats each velocity $k$ times.
  - Nothing is claimed for unaligned clocks or for other initial states.
- All $\alpha_C \ge \alpha_c$, any $R_E, \tau_C > 0$ (by scaling), and any dimension $d \ge 2$, since the orbit is planar.
- Both speed models: all 15 certificates have $\|V_j\| = 1$ exactly.

Each certificate is therefore an **upper bound** on $\kappa_{\rm PP}(s; \mathcal R_m^{\rm al})$ (see the review, §2.3). It is not the threshold itself.

## Hand-checkable example

`examples/s4-3_m01_hand.json` takes $s = 4/3$, $m = 1$, $D_0 = 25/24$, and a runner that moves perpendicular to the line of sight at full speed, $V = (0, 1)$.
- The relative velocity is $w = (-4/3, 1)$, with $|w| = 5/3$.
- The minimiser is $t^\* = (25/24)(4/3)/(25/9) = 1/2$.
- The minimum squared separation is $(25/24)^2\,(9/25) = 25/64$, i.e. a separation of $5/8$.
- The end point is $r(1) = (25/24 - 4/3,\ 1) = (-7/24,\ 1)$, with $\|r(1)\|^2 = 625/576 = (25/24)^2$.

So PP never captures this runner for $\alpha_C > 8/5$, and it captures by tangency at $\alpha_C = 8/5$. This is the symmetric pass of Theorem 2 at $y = 25/24$, where $g(y) = 25/64$; it is not the optimal $y$, since $\alpha_{\rm sym}(4/3) = 1.5397$.
