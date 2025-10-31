## v2.9.9 — 2025-10-31
- Add **public API shim** to stabilize notebook usage:
  - Introduce `SearchSettings` (beam_width, max_depth, max_seconds, GOF-9000 flags).
  - Expose stable `solve_task(task_id, task_json, settings)` even when internal solver names vary.
  - Normalize outputs to list of dicts with `grid` and `_telemetry.ops_tokens`.
  - Print one-time banner: `[ARC-ONE] API shim active — version v2.9.9 | solve_task + SearchSettings normalized.`
- No changes to core solver behavior; patch is compatibility-only.
