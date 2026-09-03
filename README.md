# Matthew Schmidt

Personal site — a single-page, cinematic static build ("Signal & Stillness").
Analytics career and the apps I build (Stillward first), presented as one
discipline of attention practiced at two speeds.

## Deploying on Railway

1. Push this repo to GitHub.
2. In Railway: **New Project → Deploy from GitHub repo** → select this repo.
3. Railway auto-detects Node and runs `npm start`, which serves `index.html`
   via `serve`.
4. Go to **Settings → Networking → Generate Domain** to get a public URL.
5. Every push to the main branch auto-redeploys.

## Notes

- Fully static, client-side, no build step — matches how Stillward itself
  ships. `package.json` only exists so Railway has a process to run.
- Section-by-section design rationale lives in the "Signal & Stillness"
  creative concept and site architecture documents (design references, not
  part of this repo).
