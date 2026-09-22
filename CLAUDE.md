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

hero `#home` → about `#about` (story, Operating Philosophy, The Blind Spot loop cards) →
Three Lenses `#lenses` (Venn diagram) → The Friction `#friction` (three cards + modal) →
`.shift` "Things I've Built:" heading → project previews (`.room` sections: Friction
`#ideas`, Stillward, Clarity, Night Night, separated by `.built-divider`) → Things I
Believe `#beliefs` → How I Work `#capabilities` → Reading `#reading` → close `#contact`.

- The nav scroll-spy is generic: each `.topnav-links a` has a `data-id` matching a section
  id. **`id="ideas"` must stay on whichever project section comes first** so the Ideas
  link and its active state land at the top of the projects.
- Section spacing uses order-independent adjacent-sibling selectors
  (`.shift + .room`, `.built-divider + .room`) so project sections can be reordered
  without touching CSS. The three `.built-divider` signal lines shift their blip
  left → center → right down the list.
- Each project preview scopes its own product palette as custom properties on the
  section (`.friction-room{--fr-*}`, `.clarity-room{--cl-*}`, `.aspen-room{--as-*}`),
  pulled from that project's source. Don't leak them into `:root`.

## Conventions that are easy to break

- **Visible by default, JS only hides.** Reveal-on-scroll content is visible in CSS; JS
  adds `.pre-reveal`/`.pre-anim` only when an IntersectionObserver + a safety-net
  `setTimeout` can guarantee revealing it, and only when `prefers-reduced-motion` is off.
  A real "stuck invisible" bug came from breaking this.
- **Strip `.pre-anim` after an entrance settles** — its higher-specificity rules otherwise
  out-rank hover states (documented in the lens-map code).
- **Animate SVG group transforms with SMIL (`<animateTransform>`), not CSS `transform`.**
  CSS transforms on nested `<g>` pivot around each element's own bounding box, not the
  local origin the shapes are drawn from; this collapsed the Clarity clover into a blob.
  Plain `<animate>` on `cx`/`cy`/opacity is fine. `transform-box: view-box` did not fix it.
- **Reduced motion:** CSS animations are neutralised by the global
  `@media (prefers-reduced-motion)` block (add new animated selectors there with
  `animation:none !important`). SMIL ignores that media query, so the JS guard near the
  top of the script removes `<animateTransform>`/`<animate>` under `.clarity-clover` and
  `.aspen-scene` when `reduced` is true — extend that selector for any new SMIL.
- The shared modal chrome (`.book-modal-overlay`) is reused by three overlays (books,
  lenses, friction cards). Click handlers select by class (e.g. `.friction-cta`) — don't
  reuse those class names on unrelated elements; a "Try Friction" link once triggered the
  wrong modal that way.
- Interactive non-button SVG elements need `tabindex="0" role="button"` + `aria-label`;
  prefer real `<button>`/`<a>` where possible. Project mock cards that link out are `<a>`;
  non-live ones (Clarity, "Coming Soon") are plain `<div>`/`<span>`.

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
