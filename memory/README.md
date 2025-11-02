Memory v0.1 (ARC-ONE)
=====================

Files read at runtime (optional, read-only):
- memory_bank/motifs.json   # [{"ops":[...], "hit":int, "family":"...", "div_hint":[h,w]|null}, ...]
- memory_bank/priors.json   # {"phi_to_ops": {...}, "ops_global": {...}}
- memory_bank/layouts.json  # [{"task_id":"...", "layout": {...}}, ...]
- memory_bank/shapes.json   # [{"h":int, "w":int, "area":int, "color":int, "bitmap16":[[...],...]}, ...]

Runtime toggles:
--no_use_memory
--no_memory_motifs
--no_memory_priors
--memory_dir /path/to/memory_bank
--memory_max_seeded 3
--memory_prior_alpha 1.0

Kaggle compliance: These files are loaded read-only. No writes on test.
