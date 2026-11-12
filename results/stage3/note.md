# Stage 3 results note (2026-11-12)

The full write-up, with proofs, status table and reproduction commands, is in `theory/stage3_mathematical_review.md`. This note indexes the raw outputs and records what changed between runs.

## Files

| File | Contents |
|---|---|
| `orbits.json` | Float-optimized periodic orbits: $s \in \{1.2, 1.5, 2\}$, $P \in \{1, 2\}$, $m \in \{1, 2, 4, 8, 16\}$. |
| `orbit_table.md` | Closure residuals, clearances, and engine runs at $1.01\times$ and $0.99\times$ each orbit's threshold. |
| `certified_orbits.json` | Exact-rational certificates (Theorem 4). Re-checked by `tests/test_certificates.py`. |
| `sweep.csv` | Corrected planner plus heuristics. 5,184 games. |
| `sweep_original_planner.csv` | The same states with the pre-fix planner. 2,592 games. |
| `planner_comparison.txt` | Per-cell escape counts, original vs corrected planner. |
| `planner_ablation.txt` | Planner fixes switched on and off, started on known escape orbits. |
| `phase_alignment_check.txt` | Sweep states rerun with the runner's clock aligned to the chaser's. |
| `orbit_verification.txt` | 2,000-period engine runs of the $m = 1$ and $m = 16$ orbits. |
| `planner_vs_known_orbit.txt` | The first evidence of the planner defects, from before the fix. Kept for the record. |

## What changed during Stage 3

- **Planner.** The first sweep used a planner with two defects; spec Rev 3 originally reported escape counts from that version.
  - The current `sweep.csv` comes from the corrected planner.
  - The original-planner sweep was regenerated reproducibly as `sweep_original_planner.csv`, using the `hold_action` and `complete_partial_plans` switches.
  - Effect: 14 more states escape with the corrected planner, and none escape only with the original. The largest change is at $s = 2$, $\alpha_C = 2$. The first swept $\alpha_C$ with an escape is unchanged.
- **Clock alignment.**
  - With random phases, the planner never escapes at $s = 1.5$, $\alpha_C = 1.6$ or at $s = 1.2$, $\alpha_C = 1.4$.
  - With the runner's clock aligned to the chaser's, it escapes in 12/12 states at both points, where certified orbits exist.
  - At $s = 2$, $\alpha_C = 1.6$ it escapes in neither case. That is consistent with the certified bound $\alpha_c(2, 16) = 1.654 > 1.6$.

A failure of the planner to find an escape is never evidence that capture is guaranteed.
