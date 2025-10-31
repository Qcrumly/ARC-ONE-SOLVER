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
