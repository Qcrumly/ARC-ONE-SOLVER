## v2.9.12 — 2025-10-31
- **Identity policy (shape-aware):** Block identity ops (`tile(1,1)`, `scale(1)`, `resize(H,W==in)`) when input/target shapes differ;
  allow only on true identity layouts and suppress redundant depth-0 no-ops.
- **Scale-rails enforcement:** Apply hard scale-sign gating (compression→extraction+alignment; expansion→tiling/resize+alignment)
  directly within successor generation.
- **Telemetry:** Added `rails_scale_sign`, `depth`, and `identity_policy` breadcrumbs to beam entries for mining.

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
