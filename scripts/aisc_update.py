#!/usr/bin/env python3
"""Install a weekly AI Supply Chain Monitor snapshot and brief, then rebuild the manifest.

    scripts/aisc_update.py --snapshot new-snapshot.json --brief new-brief.json

Either argument may be omitted. The manifest is always rebuilt from whatever is
on disk, so a bad run can be repaired by deleting the offending file and
re-running with no arguments. The page at /projects/aisc/ reads only
data/aisc/manifest.json plus the files it names.
"""
import argparse, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "aisc")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LAYERS = {"hyperscaler", "datacenter-cloud", "servers", "networking-optics", "compute",
          "memory", "foundry", "packaging", "substrates", "equipment", "materials",
          "eda-ip", "energy", "power-cooling", "policy"}


def die(msg):
    sys.exit("aisc_update: " + msg)


def load(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        die("cannot read %s: %s" % (path, e))


def check_snapshot(doc, tickers):
    for field in ("as_of", "run_date", "values"):
        if field not in doc:
            die("snapshot is missing %r" % field)
    if not DATE.match(str(doc["as_of"])):
        die("snapshot as_of must be YYYY-MM-DD, got %r" % doc["as_of"])
    vals = doc["values"]
    if not isinstance(vals, dict) or not vals:
        die("snapshot values must be a non-empty object")
    unknown = sorted(set(vals) - tickers)
    if unknown:
        die("snapshot has tickers not in universe.json: %s" % ", ".join(unknown))
    priced = [t for t, v in vals.items() if isinstance(v, dict) and v.get("mcap_usd_b")]
    if len(priced) < len(tickers) // 2:
        die("only %d of %d companies have a market cap — refusing a half-empty snapshot"
            % (len(priced), len(tickers)))
    missing = sorted(tickers - set(vals))
    return doc["as_of"], len(priced), missing


def check_brief(doc):
    for field in ("date", "items"):
        if field not in doc:
            die("brief is missing %r" % field)
    if not DATE.match(str(doc["date"])):
        die("brief date must be YYYY-MM-DD, got %r" % doc["date"])
    if not isinstance(doc["items"], list) or not doc["items"]:
        die("brief needs at least one item")
    for i, it in enumerate(doc["items"]):
        for field in ("headline", "summary", "layer"):
            if not it.get(field):
                die("brief item %d is missing %r" % (i, field))
        if it["layer"] not in LAYERS:
            die("brief item %d has unknown layer %r" % (i, it["layer"]))
    return doc["date"]


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, separators=(",", ":"), ensure_ascii=False)


def dates_in(subdir):
    d = os.path.join(DATA, subdir)
    if not os.path.isdir(d):
        return []
    return sorted((f[:-5] for f in os.listdir(d) if f.endswith(".json") and DATE.match(f[:-5])),
                  reverse=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot")
    ap.add_argument("--brief")
    args = ap.parse_args()

    universe = load(os.path.join(DATA, "universe.json"))
    tickers = {c["ticker"] for c in universe.get("companies", [])}
    if not tickers:
        die("universe.json lists no companies")

    if args.snapshot:
        doc = load(args.snapshot)
        as_of, priced, missing = check_snapshot(doc, tickers)
        write(os.path.join(DATA, "snapshots", as_of + ".json"), doc)
        print("snapshot %s installed — %d/%d companies priced" % (as_of, priced, len(tickers)))
        if missing:
            print("  no value this week for: %s" % ", ".join(missing))

    if args.brief:
        doc = load(args.brief)
        date = check_brief(doc)
        write(os.path.join(DATA, "briefs", date + ".json"), doc)
        print("brief %s installed — %d items" % (date, len(doc["items"])))

    snaps, briefs, history = dates_in("snapshots"), [], []
    for d in reversed(snaps):
        doc = load(os.path.join(DATA, "snapshots", d + ".json"))
        total = sum((v or {}).get("mcap_usd_b") or 0 for v in doc["values"].values())
        history.append({"as_of": d, "total_usd_b": round(total, 2)})
    for d in dates_in("briefs"):
        doc = load(os.path.join(DATA, "briefs", d + ".json"))
        briefs.append({"date": d, "week_label": doc.get("week_label", ""), "title": doc.get("title", "")})

    if not snaps:
        die("no snapshots on disk — nothing to publish")

    write(os.path.join(DATA, "manifest.json"), {
        "schema": 1,
        "updated": snaps[0],
        "snapshots": snaps,
        "briefs": briefs,
        "history": history,
    })
    print("manifest rebuilt — %d snapshots, %d briefs, latest %s at $%.2fT"
          % (len(snaps), len(briefs), snaps[0], history[-1]["total_usd_b"] / 1000))


if __name__ == "__main__":
    main()
