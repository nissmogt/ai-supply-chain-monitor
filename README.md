![AI Supply Chain Monitor](docs/header.png)

**Live:** https://mehrabiani.com/projects/aisc/

This project was inspired by a Youtube video https://www.youtube.com/watch?v=p8UurM1wvvM

As fascinating as the science behind chip-making is, a business has to make each and every part. Another company packages it, and others sell the power, etc. This was the idea behind the AI Supply Chain Monitor. It auto-updates every Monday (hopefully) and was built with Claude, Fable 5.1 and Opus 5. I had the idea to turn it into a hacker-like terminal because it just looks so cool to me. It was supposed to be a personal project I can send to friends. Anyway, this is my first time posting on here, encouraged by those friends. Hope this is useful.

## Files

- `index.html` — the page, exactly as deployed.
  Plain HTML with no build step; it reads the JSON in `data/aisc/` straight from this repo over raw.githubusercontent.com.
- `scripts/aisc_update.py` — installs a week's snapshot and brief and rebuilds the manifest. It refuses malformed dates, unknown tickers, and any week where fewer than half the companies carry a market cap.
- `data/aisc/` — the weekly JSON, with the data contract in `data/aisc/README.md`.
  The live site reads these files directly, so a merge here is live within about five minutes.

## Publishing

A week is published by a pull request into `main` that adds one snapshot and one brief under `data/aisc/`.
The `aisc-guard` check rejects a pull request that touches anything outside `data/aisc/`, edits or deletes an earlier week, or fails `scripts/aisc_update.py`.
The check is required on `main`, so a week goes live only after it passes.
