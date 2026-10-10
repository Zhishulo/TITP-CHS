#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把插件普查文件里「当前仍在显示的英文串」与 zh/*.json 语料比对：
   ① 语料里有 → 说明该串本该被替换却没替换（键不匹配 / 在 ui_extra 缺失）→ 真 BUG
   ② 语料里没有 → 尚未翻译的内容（可能是运行时拼接的动态文本）
用法: python tools\census_coverage.py <ui_strings.txt> [--full]
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
CJK = re.compile(r"[\u4e00-\u9fff]")
LATIN = re.compile(r"[A-Za-z]{3,}")


def load_zh() -> dict[str, str]:
    zh: dict[str, str] = {}
    for p in sorted((BASE / "zh").glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(k, str) and isinstance(v, str):
                    zh.setdefault(k, v)
    return zh


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    census = Path(sys.argv[1])
    full = "--full" in sys.argv
    zh = load_zh()
    ui_extra = {}
    up = BASE / "work" / "ui_extra.tsv"
    if up.exists():
        for line in up.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                ui_extra[parts[0]] = parts[1]

    rows = []
    for line in census.read_text(encoding="utf-8", errors="replace").splitlines():
        if "\t" not in line:
            continue
        node, text = line.split("\t", 1)
        text = text.replace("\\r", "\r").replace("\n", "\\n").replace("\\t", "\t")
        plain = text.strip()
        if not plain or CJK.search(plain):
            continue
        if not LATIN.search(plain):
            continue
        rows.append((node, plain))

    bug, untranslated = [], []
    seen = set()
    for node, text in rows:
        if text in seen:
            continue
        seen.add(text)
        if text in zh or text in ui_extra:
            bug.append((node, text))
        else:
            untranslated.append((node, text))

    print(f"census english strings : {len(seen)}")
    print(f"[BUG] in corpus but still english : {len(bug)}")
    for node, text in (bug if full else bug[:25]):
        print(f"   - {text[:70]!r} @ {node}")
    print(f"[TODO] not in corpus              : {len(untranslated)}")
    for node, text in (untranslated if full else untranslated[:40]):
        print(f"   - {text[:90]!r} @ {node}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
