# Matthew Schmidt — personal site

Single static file: `index.html` (all CSS + JS inline). No build step, no framework, no
dependencies. Deployed on Railway from GitHub `matthewschmidt1-lgtm/matthew-schmidt`;
every push to `main` redeploys https://matthew-schmidt-production.up.railway.app.
`package.json` exists only so Railway has a `serve` process to run.

## Workflow for every change

1. Edit `index.html`.
2. Preview locally: `python3 -m http.server 8935` from this folder (there is no node/npx),
   then open `http://localhost:8935` in the Browser pane. Kill it when done
   (`pkill -f "http.server 8935"`).
3. Verify in the Browser pane before committing: console errors, the specific change, and
   mobile (`resize_window` preset `mobile`, reset to `desktop` after). Check
   `document.documentElement.scrollWidth === clientWidth` for horizontal overflow.
4. Commit with a message that explains *why*, then `git push`. Matthew checks the live
   Railway site himself rather than screenshots, so push after each verified change.

Book cover images under `images/books/` are not in the local checkout — the six
`ERR_CONNECTION_REFUSED` console errors for them are pre-existing and expected locally.

## Page structure (top to bottom)

hero `#home` → about `#about` (story, Continued Learning `#learning` with certificate modal and a My Reflections modal (`#reflectModalOverlay`), Operating Philosophy, The Blind Spot loop cards, which open `#loopModalOverlay`: three stages Activity → Learning → Insight, content in `loopStages`) →
Three Lenses `#lenses` (Venn diagram; circles and overlaps open `#vennModalOverlay`, seven stages Business → System → People → Leadership → Capability → Scale → The Multiplier, content in `vennStages`) → The Path to Agency `#seeing` (the books network, The Multiplier on the left → lenses → shared ideas → six books on the right, hover/tap traces a path, book nodes open the shared lens modal, force nodes (seven: Awareness, Trust, Conditions, Value, Incentives, Leverage, Excellence) open `#ideaModalOverlay` (Healthy / Warning signs / The pattern / The move / Ask, data in `ideaData`); The Multiplier node (and the phone bubble) opens `#multModalOverlay`, the one card styled differently, and gets a slow halo once the network has drawn in → The Friction `#friction` (one question, three short lines, one visual `.fgap`: a line from Intention to Results broken in the middle, pulses leave Intention and fade at the rust gap; HTML + CSS keyframes, no JS, pulses stop under reduced motion; no cards, no modal, no scroll choreography) →
`.shift` "Things I've Built:" heading → project previews (`.room` sections: Friction
`#ideas`, Decision OS, Algorithm Atlas, Stillward, Water, Night Night, separated by `.built-divider`) → Things I
Believe `#beliefs` → Reading `#reading`; then the Knowledge → Agency strip). Phones: landscape fits the whole SVG; portrait hides it and shows `.net-drill`: The Multiplier, three lens bubbles, and for the chosen lens a tree of its forces and the books behind them that JS builds from the main SVG's edges and labels (the SVG is the no-JS fallback) → close `#contact`.

- The nav scroll-spy is generic: each `.topnav-links a` has a `data-id` matching a section
  id. **`id="ideas"` must stay on whichever project section comes first** so the Ideas
  link and its active state land at the top of the projects.
- Section spacing uses order-independent adjacent-sibling selectors
  (`.shift + .room`, `.built-divider + .room`) so project sections can be reordered
  without touching CSS. The five `.built-divider` signal lines shift their blip
  left → right down the list (H120 / H295 / H470 / H645 / H820).
- Each project preview scopes its own product palette as custom properties on the
  section (`.friction-room{--fr-*}`, `.decision-room{--do-*}`, `.atlas-room{--at-*}`, `.aspen-room{--as-*}`, `.water-room{--wa-*}`),
  pulled from that project's source. Don't leak them into `:root`.

## Design scales (pass 1, 2026-10-18)

All sizes, spacing and motion read from named tokens on `:root`; don't add raw values.
- Type: `--fs-micro` 10.5, `--fs-label` 12, `--fs-label-l` 13, `--fs-small` 15, `--fs-body-s` 16.5,
  `--fs-body` 18, `--fs-body-l` 20, `--fs-lede` 24, `--fs-lede-l` 28, and fluid `--fs-lede-fluid`,
  `--fs-h3`, `--fs-h2-s`, `--fs-h2`, `--fs-h1`, `--fs-display`.
- Spacing: `--s1` 4 … `--s12` 128 (4, 8, 12, 16, 24, 32, 40, 48, 56, 64, 96, 128). Nudges under
  6px and negative margins stay raw.
- Motion: `--t-fast` .2s, `--t-base` .4s, `--t-slow` .8s, `--t-reveal` 1.2s, `--t-hover` 1.6s;
  `--ease`, `--ease-out`, `--ease-inout`. Ambient loop durations and stagger delays are raw on purpose.
- Product card palettes (`--fr-*`, `--do-*`, `--at-*`, `--as-*`, `--wa-*`) and the high-contrast
  overrides are the only places hard-coded colors belong.

## Conventions that are easy to break

- **Apostrophes in JS strings.** Copy in `loopStages`, `vennStages` and similar arrays lives in
  single-quoted strings; a bare `'s` broke the whole script once (live, for a few hours). Escape it
  (`\'`) or use double quotes, and run the syntax check before pushing:
  `jsc` at `/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc` on the
  extracted `<script>` reports the line. The network entrance block was also lost once by deleting
  between two comment markers; check `whenArrived(seeNet` still exists after removing JS.

- **Visible by default, JS only hides.** Reveal-on-scroll content is visible in CSS; JS
  adds `.pre-reveal`/`.pre-anim` only when an IntersectionObserver + a safety-net
  `setTimeout` can guarantee revealing it, and only when `prefers-reduced-motion` is off.
  A real "stuck invisible" bug came from breaking this.
  For entrances that should be *seen* (the Venn diagram, the Path to Agency network), use the
  `whenArrived(el, ratio, cb)` helper (IntersectionObserver + scroll-position fallback) and
  no timed fallback: a 20s timer used to play them before the visitor scrolled down.
- **Strip `.pre-anim` after an entrance settles** — its higher-specificity rules otherwise
  out-rank hover states (documented in the lens-map code).
- **Animate SVG group transforms with SMIL (`<animateTransform>`), not CSS `transform`.**
  CSS transforms on nested `<g>` pivot around each element's own bounding box, not the
  local origin the shapes are drawn from; this collapsed the (since removed) Clarity clover into a blob.
  Plain `<animate>` on `cx`/`cy`/opacity is fine. `transform-box: view-box` did not fix it.
- **Reduced motion:** CSS animations are neutralised by the global
  `@media (prefers-reduced-motion)` block (add new animated selectors there with
  `animation:none !important`). SMIL ignores that media query, so the JS guard near the
  top of the script removes `<animateTransform>`/`<animate>` under
  `.aspen-scene`/`.decision-scene`/`.water-scene`/`.see-svg` when `reduced` is true — extend that selector for any new SMIL.
- **High contrast is the palette:** `<html data-contrast="high">` selects the brighter text, stronger
  lines and brighter accent on the slate ground. There is no toggle any more (removed 2026-10-22);
  the `:root[data-contrast="high"]` block is simply the site's colors. Translucent surfaces use
  `--nav-bg` / `--backdrop`.
- **Staged panels:** `stagePanel(overlayId, stages)` in the script drives any modal with the
  `.loop-progress` / `.loop-stage` / `.loop-nav` structure: content swaps in place with a fade,
  progress steps are clickable, Back/Next and arrow keys move between stages, and a stage with
  `end:'#selector'` closes and scrolls there. Used by The Blind Spot and The Three Lenses.
- The shared modal chrome (`.book-modal-overlay`) is reused by the certificate, book, force, Blind Spot and Three Lenses overlays (
  lenses, friction cards). Click handlers select by class — don't reuse those class names on unrelated elements; a
  "Try Friction" link once triggered the wrong modal that way.
- Interactive non-button SVG elements need `tabindex="0" role="button"` + `aria-label`;
  prefer real `<button>`/`<a>` where possible. Project mock cards that link out are `<a>`;
  a non-live one would be a plain `<div>`/`<span>` with a "Coming Soon" label (Clarity was, before it was removed).

## Browser-pane testing gotchas

- Screenshots sometimes come back blank/stale; `tabs_select` the tab first and retry, or
  verify with `getComputedStyle`/`getBoundingClientRect` instead. When the pane is
  hidden (`document.hidden === true`) all animations are suspended — polling then shows
  frozen values that are not a bug.
- `find`/`scroll_to` refs go stale after edits; re-run `find`. Navigating to the same
  `#hash` URL does **not** reload the page — use `location.reload()` for a fresh state.
- `svg.setCurrentTime(t)` seeks but keeps playing; pair it with `svg.pauseAnimations()`.
  Both only touch the SMIL clock — CSS `@keyframes` run on a separate clock, so a seeked
  frame can show phases overlapping that never overlap in real playback. Verify SMIL via
  `el.cx.animVal.value` / `getAnimations()`, and CSS timing by real-time polling.
- The pane's "desktop" size is ~815px wide; check true desktop layouts with
  `resize_window` at 1280.
