#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Targeted terminology fixes across zh/*.json (curated, guarded).

Each rule: (name, key_must_contain or None, compiled regex, replacement)
Rules are applied to Chinese values only, and only for entries whose English
key optionally contains a marker string.

Usage:
  python tools/fix_terms.py            # dry run + report
  python tools/fix_terms.py --apply
"""
import argparse
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZH = os.path.join(ROOT, "zh")
BACKUP = os.path.join(ROOT, "work", "zh_backup_before_terms")
REPORT = os.path.join(ROOT, "work", "term_fix_report.txt")

RULES = [
    # publication names
    ("Just DC brackets", None, re.compile(r"(?<!《)只谈DC(?!》)"), "《只谈DC》"),
    ("Right in the Center vs Just DC", "Right in the Center",
     re.compile(r"《只谈DC》"), "《不偏不倚》"),
    ("Goldman majority", None, re.compile(r"《高盛》"), "《高曼》"),
    ("Goldman minority", None, re.compile(r"《戈德曼》"), "《高曼》"),
    ("Goldman bare", None, re.compile(r"(?<!《)高盛(?!》)"), "高曼"),
    ("Sands majority", None, re.compile(r"《金沙》"), "《沙砾》"),
    ("Sands minority", None, re.compile(r"《桑兹》"), "《沙砾》"),
    ("Sands bare", None, re.compile(r"(?<!《)桑兹(?!》)"), "沙砾"),
    ("Left for Dead standalone", None, re.compile(r"^向死而生$"), "《向死而生》"),
    # places
    ("Sandy Lake", None, re.compile(r"桑迪湖"), "桑迪莱克"),
    ("Tuman pipeline", None, re.compile(r"雾-1"), "图曼-1"),
    # people
    ("Brezich", None, re.compile(r"布雷齐(?!奇)"), "布雷齐奇"),
    # institutions and politics
    ("President-elect", None, re.compile(r"候任总统"), "当选总统"),
    ("CIA short form", None, re.compile(r"中央情报局"), "中情局"),
    ("Big Pharma", None, re.compile(r"(?<!型)大药企"), "大型药企"),
    # numeric punctuation
    ("Amendment 28 spacing", None, re.compile(r"第\s+28\s*修正案|第\s*28\s+修正案"), "第28修正案"),
    ("Amendment 28 chinese numeral", None, re.compile(r"第二十八修正案"), "第28修正案"),
    ("President-elect long form", None, re.compile(r"总统当选人"), "当选总统"),
    # late additions (post-g071/g072)
    ("Vasquez", None, re.compile(r"瓦斯克斯"), "瓦斯奎兹"),
    ("ZellCoin casing", None, re.compile(r"\b[Zz]ellcoin\b"), "ZellCoin"),
    ("Sir vs Mister", "Mister", re.compile(r"^先生$"), "长官"),
    ("Gitmo", None, re.compile(r"吉特莫"), "关塔那摩"),
    ("Lynn", None, re.compile(r"林恩"), "琳恩"),
    ("Anne IV", None, re.compile(r"安妮四世"), "安娜四世"),
    ("Queen Anne", None, re.compile(r"安妮女王"), "安娜女王"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(ZH) if f.endswith(".json"))
    per_rule = {name: 0 for name, _, _, _ in RULES}
    log = []
    touched = {}
    for name in files:
        path = os.path.join(ZH, name)
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        changed = False
        for k, v in list(data.items()):
            new = v
            for rname, marker, pat, repl in RULES:
                if marker is not None and marker not in k:
                    continue
                new2, n = pat.subn(repl, new)
                if n:
                    per_rule[rname] += n
                    log.append((name, rname, k, v, new2))
                    new = new2
            if new != v:
                data[k] = new
                changed = True
        if changed:
            touched[name] = data
            if args.apply:
                if not os.path.isdir(BACKUP):
                    os.makedirs(BACKUP)
                shutil.copy2(path, os.path.join(BACKUP, name))
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=0)
                    fh.write("\n")

    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("term fix report\n\n")
        for rname, n in sorted(per_rule.items(), key=lambda x: -x[1]):
            fh.write("%-34s %d\n" % (rname, n))
        fh.write("\nentries changed: %d, files touched: %d\n\n" % (len(log), len(touched)))
        for name, rname, k, v, new in log:
            fh.write("== [%s] %s\nKEY %s\nOLD %s\nNEW %s\n\n" % (
                rname, name, k.replace("\n", "\\n")[:200],
                v.replace("\n", "\\n")[:400], new.replace("\n", "\\n")[:400]))

    total = sum(per_rule.values())
    print("substitutions: %d, entries changed: %d, files touched: %d" % (
        total, len(log), len(touched)))
    for rname, n in sorted(per_rule.items(), key=lambda x: -x[1]):
        if n:
            print("  %-34s %d" % (rname, n))
    print("report:", REPORT)
    print("applied" if args.apply else "dry run only; rerun with --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
