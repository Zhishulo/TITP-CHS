#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Normalize explicit money amounts to the dominant '$N' style.

Only *explicit* amounts are touched (digit or Chinese-numeral based, optionally
followed by 万/亿).  Vague quantity words such as 数百万美元 / 数十亿美元 are
left untouched because they have no exact numeric equivalent.

Usage:
  python tools/normalize_money.py            # dry run + report
  python tools/normalize_money.py --apply    # rewrite zh/*.json (backup first)
"""
import argparse
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZH = os.path.join(ROOT, "zh")
BACKUP = os.path.join(ROOT, "work", "zh_backup_before_money")
REPORT = os.path.join(ROOT, "work", "money_normalize_report.txt")

DIGITS = {"零": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5,
          "六": 6, "七": 7, "八": 8, "九": 9}
UNITS = {"十": 10, "百": 100, "千": 1000}
SCALES = {"万": 10 ** 4, "亿": 10 ** 8}

CN_NUM = r"[零一二三四五六七八九十百千万亿两]+"


def cn_to_int(text):
    """Parse a Chinese numeral (up to 亿 scale). Returns None on failure."""
    if not text:
        return None
    total = 0
    section = 0
    number = 0
    for ch in text:
        if ch in DIGITS:
            number = DIGITS[ch]
        elif ch in UNITS:
            section += (number if number else 1) * UNITS[ch]
            number = 0
        elif ch in SCALES:
            section += number
            total += (section if section else 1) * SCALES[ch]
            section = 0
            number = 0
        else:
            return None
    return total + section + number


def fmt(amount):
    """Render an integer amount as $1,234,567 (no decimals kept)."""
    if amount is None:
        return None
    amount = int(round(amount))
    return "${:,}".format(amount)


def convert(value):
    """Return (new_value, list_of_changes)."""
    changes = []
    out = value

    # 0) ranges first: "9.5亿至11亿美元" / "5,000万至1亿美元" must not be split
    def repl_range(m):
        n1, s1, n2, s2 = m.group("n1"), m.group("s1"), m.group("n2"), m.group("s2")
        try:
            v1 = float(n1.replace(",", ""))
            v2 = float(n2.replace(",", ""))
        except ValueError:
            return m.group(0)
        if not s1 and s2:
            s1 = s2  # elided scale: "5,000万至1亿" -> both use 万
        scale = {"": 1, "万": 10 ** 4, "亿": 10 ** 8}
        a1 = v1 * scale.get(s1, 1)
        a2 = v2 * scale.get(s2, 1)
        rendered = "%s至%s" % (fmt(a1), fmt(a2))
        changes.append((m.group(0), rendered))
        return rendered

    pat_range = re.compile(
        r"(?P<n1>\d[\d,]*(?:\.\d+)?)(?P<s1>[万亿]?)至(?P<n2>\d[\d,]*(?:\.\d+)?)"
        r"(?P<s2>[万亿]?)(?:美元|美金)")
    out = pat_range.sub(repl_range, out)

    # 1) digits with optional decimal + 万/亿 + 美元/美金
    def repl_digit(m):
        num = m.group("num").replace(",", "")
        scale = m.group("scale")
        try:
            amount = float(num)
        except ValueError:
            return m.group(0)
        if scale == "万":
            amount *= 10 ** 4
        elif scale == "亿":
            amount *= 10 ** 8
        rendered = fmt(amount)
        changes.append((m.group(0), rendered))
        return rendered

    pat_digit = re.compile(
        r"(?P<num>\d[\d,]*(?:\.\d+)?)\s*(?P<scale>[万亿]?)\s*(?:美元|美金)")
    out = pat_digit.sub(repl_digit, out)

    # 2) Chinese numerals + 美元/美金 (explicit only; 数/几 prefixes excluded)
    def repl_cn(m):
        prefix = m.group("prefix")
        num = m.group("num")
        if prefix:
            return m.group(0)
        if not num or set(num) <= {"万", "亿"}:
            return m.group(0)  # bare 万/亿 belongs to a preceding digit amount
        scale = m.group("scale")
        base = cn_to_int(num)
        if base is None:
            return m.group(0)
        if scale == "万":
            base *= 10 ** 4
        elif scale == "亿":
            base *= 10 ** 8
        rendered = fmt(base)
        changes.append((m.group(0), rendered))
        return rendered

    pat_cn = re.compile(
        r"(?P<prefix>[数几])?(?P<num>" + CN_NUM + r")(?P<scale>[万亿]?)(?:美元|美金)")
    out = pat_cn.sub(repl_cn, out)

    return out, changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    files = sorted(f for f in os.listdir(ZH) if f.endswith(".json"))
    per_file = {}
    log = []
    for name in files:
        path = os.path.join(ZH, name)
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        changed = False
        for k, v in list(data.items()):
            new, ch = convert(v)
            if ch and new != v:
                data[k] = new
                changed = True
                log.append((name, k, v, new, ch))
        if changed:
            per_file[name] = data
            if args.apply:
                if not os.path.isdir(BACKUP):
                    os.makedirs(BACKUP)
                shutil.copy2(path, os.path.join(BACKUP, name))
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=0)
                    fh.write("\n")

    with open(REPORT, "w", encoding="utf-8") as fh:
        fh.write("money normalization report (style: $1,234,567)\n")
        fh.write("files touched: %d, entries changed: %d\n\n" % (len(per_file), len(log)))
        for name, k, v, new, ch in log:
            fh.write("== %s\n" % name)
            fh.write("KEY  %s\n" % k.replace("\n", "\\n"))
            for old, rep in ch:
                fh.write("  %s -> %s\n" % (old, rep))
            fh.write("OLD  %s\nNEW  %s\n\n" % (v.replace("\n", "\\n"), new.replace("\n", "\\n")))

    print("files touched: %d, entries changed: %d" % (len(per_file), len(log)))
    print("report:", REPORT)
    if not args.apply:
        print("dry run only; rerun with --apply")
    else:
        print("applied; backup in", BACKUP)
    return 0


if __name__ == "__main__":
    sys.exit(main())
