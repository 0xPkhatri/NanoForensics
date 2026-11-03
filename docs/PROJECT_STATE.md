# Project state

Previously passed phase checkpoints: 4d464af, e86808e, e6c9226, bd467ee. Their LAMMPS trajectory evidence is INVALIDATED by the new measured z/vz constraint check. Two-body pair validation and NumPy-only physics checks remain valid.

[~] Reverify Phase 1 with solver sflj-1.1: enforce2d must be defined after Langevin.
[ ] Regenerate frozen benchmark under corrected 2D solver; retain earlier DB/report as invalid audit history.
[ ] Re-run Phase 2, Phase 3, Phase 4, Phase 5 gates in order.

The initial Phase 5 run passed 9 tests but did not check z/vz. It cannot serve as final acceptance. No scientific thresholds have been loosened. No protocol or preparation changes are authorized as tuning.
