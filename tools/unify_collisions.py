#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unify same-English-different-Chinese entries across all zh/*.json.

Policy (recorded in the report):
  canonical value = the variant used by the most files;
  tie-break 1     = longer value wins (usually the more complete rendering);
  tie-break 2     = lexicographically smaller value.

Usage:
  python tools/unify_collisions.py            # dry run, writes report only
  python tools/unify_collisions.py --apply    # rewrites zh/*.json (backup first)
"""
import argparse
import collections
import json
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZH = os.path.join(ROOT, "zh")
BACKUP = os.path.join(ROOT, "work", "zh_backup_before_unify")
REPORT = os.path.join(ROOT, "work", "collision_unify_report.txt")

SKIP_KEYS = set()  # keys deliberately allowed to differ (none currently)


def load_all():
    data = {}
    for name in sorted(os.listdir(ZH)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(ZH, name)
        with open(path, encoding="utf-8") as fh:
            data[name] = json.load(fh)
    return data


def pick_canonical(key, variants):
    """variants: list of (value, [files])"""
    ranked = sorted(variants, key=lambda vf: (-len(vf[1]), -len(vf[0]), vf[0]))
    return ranked[0][0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    data = load_all()
    index = collections.defaultdict(lambda: collections.defaultdict(list))
    for name, d in data.items():
        for k, v in d.items():
            index[k][v].append(name)

    collisions = {k: v for k, v in index.items() if len(v) > 1 and k not in SKIP_KEYS}
    print("files %d  entries %d  colliding keys %d" % (
        len(data), sum(len(d) for d in data.values()), len(collisions)))

    changes = collections.defaultdict(list)  # filename -> [(key, old, new)]
    canon = {}
    for k, variants in collisions.items():
        variants = [(v, files) for v, files in variants.items()]
        best = pick_canonical(k, variants)
        canon[k] = best
        for v, files in variants:
            if v == best:
                continue
            for f in files:
                changes[f].append((k, v, best))

    total_changes = sum(len(v) for v in changes.values())
    print("canonical picks %d  total entry rewrites %d  files touched %d" % (
        len(canon), total_changes, len(changes)))

    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("collision unification report\n")
        fh.write("policy: most-files wins; tie -> longer; tie -> lexicographic\n")
        fh.write("colliding keys: %d, entry rewrites: %d, files touched: %d\n\n" % (
            len(canon), total_changes, len(changes)))
        for k in sorted(canon):
            variants = [v for v, _ in index[k].items()]
            fh.write("[%s]\n" % k.replace("\n", "\\n"))
            for v in sorted(variants):
                mark = "  <= KEPT" if v == canon[k] else ""
                fh.write("    %s%s\n" % (v.replace("\n", "\\n"), mark))
            fh.write("\n")
    print("report:", REPORT)

    if not args.apply:
        print("dry run only; rerun with --apply to rewrite zh/*.json")
        return 0

    if not os.path.isdir(BACKUP):
        os.makedirs(BACKUP)
    for name, items in changes.items():
        src = os.path.join(ZH, name)
        shutil.copy2(src, os.path.join(BACKUP, name))
        d = data[name]
        for k, old, new in items:
            d[k] = new
        with open(src, "w", encoding="utf-8", newline="") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=0)
            fh.write("\n")
    print("applied; originals backed up to", BACKUP)
    return 0


if __name__ == "__main__":
    sys.exit(main())
