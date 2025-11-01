## v2.9.13 — 2025-11-01
- **Operator-level directional guards** (early steps): `resize/scale` now refuse the wrong direction for the first K steps, inferred from input→target area (shrink when target is smaller; grow when target is larger). Prevents early wrong-way expansions on compression tasks.
- **Identity ejection (runtime)**: `tile(1,1)`, `scale(1)`, and `resize(H,W==current)` rejected in policy overlays unless the task is truly identity; avoids no-op starts that stall progress.
- **Object-centric nudge (runtime)**: gentle preference for topology/object ops (`keep_n_largest`, `remove_isolated`, `fill_holes`, etc.) when the signal is object-heavy.
- No DSL changes; guards are conservative and limited to early steps to protect search diversity.

## v2.9.12 — 2025-10-31
- **Identity policy (shape-aware):** Block identity ops (`tile(1,1)`, `scale(1)`, `resize(H,W==in)`) when input/target shapes differ; allow only on true identity layouts. Also block as the first step even when shapes match (prevents useless no-op at depth 0).  
- **Scale-rails enforcement:** Apply compression/expansion rails (extraction+alignment vs tiling/resize+alignment) directly where successors are produced, not just in helpers.  
- **Telemetry breadcrumbs:** record `rails_scale_sign`, `rail_depth`, and `identity_policy` to aid mining.

## v2.9.11 — 2025-10-31
- **A→B→A micro-debate (ρ-gated):** Selectively runs a single repair pass and reconciles {A,B,A′} only when ρ ≥ 0.55.
- **Diversity guard:** Enforces minimum dissimilarity between attempt_1 and attempt_2 using token-Jaccard and grid dissimilarity; nudges attempt_2 policy when too similar.
- **Seconds-aware schedule:** Expands max_seconds only when progress is healthy; caps at ~2× base.
- **Determinism & banner:** Fixed seeds and OMP threads with one-line run banner.
- **Submission helper:** `make_sample_submission(preds_by_tid)` for Kaggle schema.
- **Telemetry:** Added `rho`, `debate`, `diversity_nudge`, `seconds_after_schedule`, and existing rails/object flags to `_telemetry`.
- No DSL changes; behavior focuses on flipping “almosts” safely.

## v2.9.10 — 2025-10-31
- **Telemetry**: Added `_telemetry_note` helper and ensured every returned result includes `_telemetry.ops_tokens`.
  - Synthesizes tokens from program steps if not explicitly recorded.
- **Search heuristic**: Object-centric soft preference:
  - When |φ[obj]| > 0.30 (or early shape-match), softly up-rank `keep_n_largest`, `remove_isolated`, `fill_holes`, `keep_rings`, `largest`, `center_largest`, `mask`.
  - Keep object tools available under early rails by widening `_gate_allowed_ops` non-destructively.
- No DSL changes; behavior is a gentle tie-breaker to flip “almosts”.

## v2.9.9 — 2025-10-31
- Add **public API shim** to stabilize notebook usage:
  - Introduce `SearchSettings` (beam_width, max_depth, max_seconds, GOF-9000 flags).
  - Expose stable `solve_task(task_id, task_json, settings)` even when internal solver names vary.
  - Normalize outputs to list of dicts with `grid` and `_telemetry.ops_tokens`.
  - Print one-time banner: `[ARC-ONE] API shim active — version v2.9.9 | solve_task + SearchSettings normalized.`
- No changes to core solver behavior; patch is compatibility-only.
