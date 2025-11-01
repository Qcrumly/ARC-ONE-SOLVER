## v2.9.18 — 2025-11-01
- **Depth-0 identity ban extended to phase-tiles:** `phase_tile`, `phase_tile_row`, and `phase_tile_col` with `(1,1,*)` are blocked as opening moves, matching the existing `tile`/`tile_masked` policy.
- **Robust single-int sanitizer:** callable and method operators normalize forms like `remove_isolated((1))` or `'1'` to plain `1` so object tools stay reachable.
- Keeps prior guards: no size-ops at depth 0; directional resize/scale in early steps; strengthened object-first prior.

## v2.9.17 — 2025-11-01
- **Depth-0 masked identity ban:** `tile_masked(1,1,0)` blocked at step 0, same as `tile(1,1)`.
- **Robust int-arg parsing:** normalize single-int ops like `remove_isolated((1))` → `1` so object tools stay available.
- **Object-first opening bias:** at depth 0, when |φ[obj]| > 0.30, up-rank `keep_n_largest`/`remove_isolated` (+0.80) and `fill_holes`/`keep_rings`/`largest` (+0.60).
- Keeps previous guards: no size-ops at depth 0; directional checks for resize/scale in early steps.

## v2.9.16 — 2025-11-01
- **Hard block `resize`/`scale`/`tile` at depth 0.** Enforces structure-first openings across all code paths.
- **Wrap function-style ops too.** Registry wrappers now handle both `.apply` methods and bare callables, so step-0 bans and directional checks always apply.
- **Early gating hardened.** `resize`/`scale`/`tile` are removed from the allowed set when `depth < 1`, preventing bad candidates from being proposed.
- Directional guards for size changes are still active from depth ≥ 1 (block expanding when shrink is needed, and vice-versa).

## v2.9.15 — 2025-11-01
- **No-guess rule at step 0:** when direction cannot be inferred, `resize/scale` are forbidden as the first move. Prevents harmful blind opens on hard evals.
- **Better direction inference:** guards now read `program.ctx['in_shape'/'out_shape']` when available; falls back to common attributes.
- **Enumerator shields:** when available, `resize.args_enum(...)` is filtered to prefer candidates consistent with the required direction (and avoid obvious mismatches).

## v2.9.14 — 2025-11-01
- **Operator-level early-step direction guards**: `resize/scale` refuse the wrong direction for the first K steps, inferred from input→target area (shrink when target is smaller; grow when target is larger). Stops early wrong-way expansions on compression tasks.
- **Identity policy at step 0**: block `tile(1,1)`, `scale(1)`, and `resize(H,W==current)` as the **first** step unless the task is truly identity. Avoids no-op starts that stall progress.
- Telemetry note: `early_dir_guard_steps=K` recorded once at import.

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
