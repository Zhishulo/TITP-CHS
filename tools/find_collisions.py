import json, os, glob, collections

ZH = r"C:\Users\96333\TITP-CHS\zh"
WORK = r"C:\Users\96333\TITP-CHS\work"

files = sorted(glob.glob(os.path.join(ZH, "*.json")))
per_key = collections.defaultdict(dict)   # key -> value -> [files]
counts = {}
for f in files:
    name = os.path.basename(f)
    try:
        data = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        print("ERR", name, e)
        continue
    counts[name] = len(data)
    for k, v in data.items():
        if not isinstance(k, str) or not isinstance(v, str):
            continue
        per_key[k][v] = per_key[k].get(v, []) + [name]

collisions = {k: v for k, v in per_key.items() if len(v) > 1}
print("files:", len(files), "total keys:", len(per_key), "colliding keys:", len(collisions))

rows = []
for k, vals in collisions.items():
    opts = sorted(vals.items(), key=lambda kv: -len(kv[1]))
    rows.append({
        "src": k,
        "n_variants": len(opts),
        "variants": [{"zh": z, "files": fs} for z, fs in opts],
    })
rows.sort(key=lambda r: (-r["n_variants"], r["src"]))
json.dump(rows, open(os.path.join(WORK, "collisions.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

with open(os.path.join(WORK, "collisions.txt"), "w", encoding="utf-8") as fh:
    for i, r in enumerate(rows, 1):
        fh.write("[%d] %s\n" % (i, r["src"]))
        for v in r["variants"]:
            fh.write("      %s   <- %s\n" % (v["zh"], ",".join(v["files"])))
print("written:", os.path.join(WORK, "collisions.json"), os.path.join(WORK, "collisions.txt"))
top = [r for r in rows if r["n_variants"] >= 3]
print("keys with >=3 variants:", len(top))
for r in top[:15]:
    print("  ", r["src"][:60], "->", [v["zh"] for v in r["variants"]][:4])
