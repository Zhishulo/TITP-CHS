r"""Lead 终检：把每个事件组（g001..g072）的 TSV 源文重新抽一遍，
与 zh\events_gNNN.json 的键集合逐字符比对，报告每组的 missing / extra。

取源文规则（TRANSLATION_GUIDE.md 任务 B）：
  lang1 不是 :[PLACEHOLDER] 且非空 -> 用 lang1；否则 lang2；否则 lang3。
  跳过 :[PLACEHOLDER] 与空串；同文件重复源文自动去重（JSON 键唯一）。

用法：
    python tools\verify_all_groups.py            # 汇总
    python tools\verify_all_groups.py -v         # 打印每组明细与问题条目
"""
import argparse
import csv
import io
import json
import os
import sys

ROOT = r"C:\Users\96333\TITP-CHS"
EVENTS = os.path.join(ROOT, "work", "events")
GROUPS = os.path.join(ROOT, "work", "event_groups.json")
ZH = os.path.join(ROOT, "zh")
PLACEHOLDER = ":[PLACEHOLDER]"

csv.field_size_limit(10 * 1024 * 1024)


def read_rows(path):
    with io.open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.reader(fh, delimiter="\t", quoting=csv.QUOTE_NONE)
        rows = list(reader)
    return rows[1:] if rows else []


def pick_source(fields):
    # 列顺序：id, lang1, lang2, lang3, lang4, zh
    for idx in (1, 2, 3):
        if idx < len(fields):
            v = fields[idx]
            if v and v.strip() and v.strip() != PLACEHOLDER:
                return v, ("lang%d" % idx)
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--group", default=None, help="只检查某一组，例如 g067")
    args = ap.parse_args()

    groups = json.load(open(GROUPS, encoding="utf-8"))
    total_keys = 0
    total_missing = 0
    total_extra = 0
    bad_groups = []
    missing_files = []

    for g in groups:
        name = g["group"]
        if args.group and name != args.group:
            continue
        path = os.path.join(ZH, "events_%s.json" % name)
        if not os.path.exists(path):
            bad_groups.append((name, "NO_OUTPUT", 0, 0))
            if args.verbose:
                print("%s: 缺少产物 %s" % (name, path))
            continue

        src = []
        seen = set()
        cyr = 0
        for f in g["files"]:
            fp = os.path.join(EVENTS, f if f.endswith(".tsv") else f + ".tsv")
            if not os.path.exists(fp):
                missing_files.append((name, f))
                continue
            for fields in read_rows(fp):
                v, which = pick_source(fields)
                if v is None:
                    continue
                if any("\u0400" <= ch <= "\u04ff" for ch in v):
                    cyr += 1
                if v not in seen:
                    seen.add(v)
                    src.append(v)

        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)

        srcset = set(src)
        keyset = set(data.keys())
        missing = sorted(srcset - keyset)     # 源文有、译文缺
        extra = sorted(keyset - srcset)       # 译文有、源文无（错键）
        empty = [k for k, v in data.items() if not isinstance(v, str) or not v.strip()]

        total_keys += len(keyset)
        total_missing += len(missing)
        total_extra += len(extra)

        status = "OK" if not missing and not extra and not empty else "FAIL"
        if status == "FAIL":
            bad_groups.append((name, "KEYSET", len(missing), len(extra)))

        if args.verbose or status == "FAIL":
            print("%s: src=%d json=%d missing=%d extra=%d empty=%d cyr_src=%d %s"
                  % (name, len(srcset), len(keyset), len(missing), len(extra), len(empty), cyr, status))
            for k in missing[:5]:
                print("    MISSING %r" % (k[:110],))
            for k in extra[:5]:
                print("    EXTRA   %r" % (k[:110],))

    print()
    print("groups checked : %d" % len(groups))
    print("total json keys: %d" % total_keys)
    print("missing keys   : %d" % total_missing)
    print("extra keys     : %d" % total_extra)
    if missing_files:
        print("missing tsv    : %d" % len(missing_files))
        for name, f in missing_files[:10]:
            print("   %s <- %s" % (name, f))
    if bad_groups:
        print("BAD GROUPS:")
        for row in bad_groups:
            print("   ", row)
        sys.exit(1)
    print("ALL GROUPS OK")


if __name__ == "__main__":
    main()
