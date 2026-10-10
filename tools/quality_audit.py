#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""全库译文质量审计：逐条扫描 zh\*.json，按规则找出「可能没翻 / 翻漏 / 结构走样」的条目。
用法: python tools\quality_audit.py [--samples N]
输出: 控制台摘要 + work\quality_audit.txt（全量清单）
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ZH = BASE / "zh"
OUT = BASE / "work" / "quality_audit.txt"

CJK = re.compile(r"[\u3400-\u9fff\u3000-\u303f\uff00-\uffef]")
LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z'\-]{1,}")
PLACEHOLDER = re.compile(r"\{[^}]*\}")
TAG = re.compile(r"<[^>]*>")
HANDLE = re.compile(r"@[A-Za-z0-9_]+")
HASHTAG = re.compile(r"#[A-Za-z0-9_]+")

# 允许原样保留的拉丁内容（品牌 / 调试 token / 平台 / 专有缩写）
ALLOW = {
    "TEST_MONOLOGUE", "ABCDABCD", "TEST1", "TEST2", "TEST3", "TEST4",
    "QUOTE", "TEXT", "TWEET", "PLACEHOLDER", "END", "OF", "MONTH",
    "ZellCoin", "zellcoin", "CarpeDiem", "Lil", "Doc", "Snapchat", "TikTok",
    "Twitter", "YouTube", "Google", "Netflix", "Facebook", "Instagram",
    "TITPOTUS", "POTUS", "USA", "US", "AI", "BDSM", "MILFs", "BLACKED",
    "FreeTritch", "Tritch", "Mars", "Area", "UFO", "PMC", "CIA", "FBI",
    "VAR", "CHARACTER1_FIRSTNAME", "CHARACTER2_FIRSTNAME", "ELECTIONS_PRIZE_TOTAL",
    "AMENDMENT_PRIZE_TOTAL", "MONEY", "NAME", "NUMBER", "player", "PLAYER",
}

NUMERIC = re.compile(r"^[\s$€£¥0-9,.%+\-/x×:()]*$")


def cjk_len(s):
    return len(CJK.findall(s))


def norm_words(s):
    return [w for w in LATIN_WORD.findall(s) if w not in ALLOW]


def main():
    samples = 20
    if "--samples" in sys.argv:
        samples = int(sys.argv[sys.argv.index("--samples") + 1])

    # key -> [(value, file)]
    table = defaultdict(list)
    for p in sorted(ZH.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"!! {p.name}: {e}")
            continue
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(k, str) and isinstance(v, str):
                    table[k].append((v, p.name))

    findings = defaultdict(list)
    for k, vs in table.items():
        v, fn = vs[0]
        if len({x for x, _ in vs}) > 1:
            findings["INCONSISTENT"].append((fn, k, v))
            continue
        if NUMERIC.match(k):
            continue

        # A 完全没翻（值与原文逐字相同）
        if v == k and norm_words(k):
            findings["IDENTICAL"].append((fn, k, v))
        # B 译文无汉字但原文有英文实词
        elif cjk_len(k) == 0 and cjk_len(v) == 0 and len(norm_words(k)) >= 2:
            findings["NO_CJK"].append((fn, k, v))

        # C 长原文译得过短
        if len(k) > 60 and cjk_len(v) < max(6, len(k) // 12):
            findings["TOO_SHORT"].append((fn, k, v))

        # D 占位符集合不一致
        if sorted(PLACEHOLDER.findall(k)) != sorted(PLACEHOLDER.findall(v)):
            findings["PLACEHOLDER"].append((fn, k, v))
        # E 富文本标签不一致
        if sorted(TAG.findall(k)) != sorted(TAG.findall(v)):
            findings["TAG"].append((fn, k, v))
        # F @handle 不一致
        if sorted(HANDLE.findall(k)) != sorted(HANDLE.findall(v)):
            findings["HANDLE"].append((fn, k, v))
        # G #话题 数量不一致
        if len(HASHTAG.findall(k)) != len(HASHTAG.findall(v)):
            findings["HASHTAG"].append((fn, k, v))
        # H 字面 \n 数量不一致
        if k.count("\\n") != v.count("\\n"):
            findings["ESCAPED_NL"].append((fn, k, v))
        # I 译文里残留 ≥3 个连续英文实词
        stray = [w for w in re.findall(r"[A-Za-z][A-Za-z'\- ]{12,}", v)]
        if stray and cjk_len(v) > 0:
            tail = [w for w in re.findall(r"(?:[A-Za-z][A-Za-z'\-]+[ ]){2,}[A-Za-z][A-Za-z'\-]+", v)]
            if tail:
                findings["STRAY_ENGLISH"].append((fn, k, v))

    order = ["INCONSISTENT", "IDENTICAL", "NO_CJK", "TOO_SHORT", "PLACEHOLDER",
             "TAG", "HANDLE", "HASHTAG", "ESCAPED_NL", "STRAY_ENGLISH"]

    lines = []
    print(f"审计条目数: {len(table)}（唯一键，来自 {len(list(ZH.glob('*.json')))} 个文件）\n")
    for kind in order:
        items = findings[kind]
        print(f"== {kind}: {len(items)} ==")
        for fn, k, v in items[:samples]:
            print(f"   [{fn}] {k[:70]!r} -> {v[:70]!r}")
        if len(items) > samples:
            print(f"   ... 另有 {len(items) - samples} 条，见报告文件")
        lines.append(f"\n== {kind}: {len(items)} ==")
        for fn, k, v in items:
            lines.append(f"[{fn}] {k}\n    -> {v}")
        print()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"全量报告: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
