# AI Supply Chain Monitor — data

Static JSON behind https://mehrabiani.com/projects/aisc/.
The page is plain HTML and fetches these files directly from this repo over raw.githubusercontent.com, so there is no build step and no deploy.
A week is live about five minutes after its pull request merges into `main`.

## Files

| File | What it holds |
|---|---|
| `universe.json` | The companies tracked: ticker, name, short name, layer, exchange, one-line role. Changes rarely. |
| `snapshots/<date>.json` | One week of market values, keyed by ticker. `date` is the market close the figures reflect. |
| `briefs/<date>.json` | One week of written items, with sources. |
| `manifest.json` | Generated. Lists available dates and precomputes per-week totals for the trend chart. |

Never hand-edit `manifest.json` — `scripts/aisc_update.py` rebuilds it from
whatever snapshots and briefs are on disk.

## Shapes

```jsonc
// snapshots/<date>.json
{
  "as_of": "2026-10-07",       // the market close these figures reflect
  "run_date": "2026-10-07",    // when the refresh ran
  "label": "Oct 7, 2026 close",
  "fx_note": "...", "source_note": "...",
  "values": {
    "NVDA": { "price": 237.47, "currency": "USD", "mcap_usd_b": 5730,
              "fwd_pe": 19.63, "as_of": "2026-10-07", "source": "https://…",
              "note": "optional caveat" }
  }
}

// briefs/<date>.json
{
  "date": "2026-10-07", "week_label": "Oct 1–7, 2026",
  "title": "…", "intro": "…", "movers_note": "…",
  "items": [{ "date": "2026-09-30", "headline": "…", "summary": "…",
              "layer": "memory", "companies": ["MU"],
              "source_url": "https://…", "source_name": "Micron press release" }]
}
```

`layer` must be one of: `hyperscaler`, `datacenter-cloud`, `servers`,
`networking-optics`, `compute`, `memory`, `foundry`, `packaging`, `substrates`,
`equipment`, `materials`, `eda-ip`, `energy`, `power-cooling`, `policy`.

A company row keeps its own `as_of`. When it is more than three days older than
the snapshot's, the page flags that row as a stale quote rather than hiding it.
A missing value is `null`, never a carried-forward number.

## Publishing a week

```sh
git checkout -b aisc-<date> main
scripts/aisc_update.py --snapshot new-snapshot.json --brief new-brief.json
git add data/aisc && git commit -m "aisc: week of <date>" && git push origin aisc-<date>
```

Open a pull request into `main`.
The `aisc-guard` check must pass before it can merge: only `data/aisc/` may change, earlier snapshots and briefs stay untouched, and the script must exit 0.

The script refuses a snapshot whose tickers are not in `universe.json`, whose
dates are malformed, or where fewer than half the companies have a market cap,
so a failed data run cannot publish a half-empty week. Run it with no arguments
to rebuild the manifest alone (useful after deleting a bad week).

## Adding or removing a company

Edit `universe.json` only. The page derives every tier and layer total from it,
and `aisc_update.py` validates future snapshots against it. A ticker added here
shows an empty row until the next refresh prices it.
