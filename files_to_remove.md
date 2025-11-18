# Files Safe to Remove from Repository

Based on analysis of image references across all .rst files in the documentation, the following image files are **only** referenced in `gallery.rst` and can be safely removed after the gallery update:

## Files that can be removed:

1. `docs/source/mods/figures/lop_siouxfalls.png`
   - Only referenced in gallery.rst (2x - light and dark)
   - Not used anywhere else

2. `docs/source/mods/figures/max-flow-min-cut.png`
   - Only referenced in gallery.rst (2x - light and dark)
   - Not used anywhere else

3. `docs/source/mods/figures/metromap_uberlin.png`
   - Only referenced in gallery.rst (2x - light and dark)
   - Not used anywhere else

4. `docs/source/mods/figures/qubo.png`
   - Only referenced in gallery.rst (2x - light and dark)
   - Not used anywhere else

## Files that should NOT be removed:

These files are referenced in other documentation files and must be kept:

1. `docs/source/mods/figures/bipartite-matching-example.png`
   - Referenced in: gallery.rst (removed) AND mods/bipartite-matching.rst
   - **KEEP** - still used in bipartite-matching.rst

2. `docs/source/mods/figures/bipartite-matching-flow.png`
   - Referenced in: gallery.rst (removed) AND mods/bipartite-matching.rst
   - **KEEP** - still used in bipartite-matching.rst

3. `docs/source/mods/figures/min-cost-flow-result.png`
   - Referenced in: gallery.rst (removed) AND mods/min-cost-flow.rst
   - **KEEP** - still used in min-cost-flow.rst

4. `docs/source/mods/figures/mwis.png`
   - Referenced in: gallery.rst (removed) AND mods/mwis.rst
   - **KEEP** - still used in mwis.rst

5. `docs/source/mods/figures/opf.png`
   - Referenced in: gallery.rst (removed) AND mods/opf/opf.rst
   - **KEEP** - still used in opf.rst

6. `docs/source/mods/figures/mvp.png`
   - Referenced in: gallery.rst (removed) AND mods/portfolio.rst
   - **KEEP** - still used in portfolio.rst

7. `docs/source/mods/figures/sharpe-ratio.png`
   - Referenced in: gallery.rst (removed) AND mods/sharpe-ratio.rst
   - **KEEP** - still used in sharpe-ratio.rst

8. `docs/source/mods/icons/lad-regression.png` (old single icon)
   - Only referenced in gallery.rst (removed)
   - **CAN REMOVE** - replaced by lad-regression-light.png and lad-regression-dark.png

## Summary

**Files safe to remove (5 total):**
```
docs/source/mods/figures/lop_siouxfalls.png
docs/source/mods/figures/max-flow-min-cut.png
docs/source/mods/figures/metromap_uberlin.png
docs/source/mods/figures/qubo.png
docs/source/mods/icons/lad-regression.png
```

All other images that were previously in gallery.rst are still referenced in their respective mod documentation pages and should be retained.
