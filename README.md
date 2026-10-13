![AI Supply Chain Monitor](docs/header.png)

**Live:** https://mehrabiani.com/projects/aisc/

What's in a chip, really? The engineering that goes behind building and designing a chip that'll eventually go into a computer used to train AI is pretty interesting because it's one of the few consumer-facing technologies that can be traced down to atomic level. But the business behind it is just as interesting because there are companies that make or source the components, package chips into systems, supply the tools and materials, provide electricity, and employ the people who keep all of these facilities running. 

I wanted to learn more about AI infrastructure industry and my first instinct was to follow the money and map it out in visual way. This led to a dashboard that tracks around 62 publicly-traded companies across five layers of supply chain: demand, systems, silicon, tools, and power. 

It auto-updates every Monday (hopefully) and was build with Claude Fable 5.1 and Opus 5.5. I wanted to turn it into a hacker-like terminal because it looks so cool to me. It was supposed to be a personal project but some friends encouraged me to post it on here. I hope it's useful or at least interesting. I'm also curious to see what people think about tools like this and if you've ever built something similar.

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
