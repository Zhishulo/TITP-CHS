#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""把「普查里仍在显示英文、但确属游戏真实内容」的串补进 work\ui_extra.tsv。
词典里已有的直接取词典译文；词典没有的用手工译文（NEW）。
跳过已存在的键与明显的设计占位串（Some Title / New Text / Undefined_* 等）。
用法: python tools\augment_ui_extra.py [--apply]
"""
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
UI = BASE / "work" / "ui_extra.tsv"

KEYS = [
    "Ineffective Manager", "Courting the Elites", "Lobbying Successful", "Prize Fund",
    "per month", "Reconcile", "Finish", "Cancel", "Apply", "Back", "Audio", "Visuals",
    "Game", "Sign", "Vice President", "President", "Persuasion", "Money", "Rest", "Other",
    "Go Back", "Colonize Mars", "Draft of First Executive Order: Cure Cancer",
    "Vote", "Accept", "Decline", "Laws", "Impeach", "Veto",
]

NEW = {
    "Why was it Ngoyen's foundation that was robbed?\\nКак думаешь, почему грабанули именно фонд Нгуен?":
        "为什么被抢的偏偏是阮氏基金会？",
    "She was spending the foundation's money on her personal needs":
        "她把基金会的钱用在了自己的私事上",
    "They thought the were doing a good deed": "他们以为自己在做好事",
    "What drove the crimonal?": "是什么驱使了这个罪犯？（原文 crimonal 系 criminal 笔误）",
    "What does the wierd work shcedule mean?": "那奇怪的工作时间表意味着什么？（原文 wierd/shcedule 系笔误）",
    "What is the flaw in Amendment 28?": "第28修正案的漏洞是什么？",
    "Why can't you remain in office for another term?": "你为什么不能连任？",
    "How do you lose an election to Wister?": "你怎么会输给威斯特？",
    "You won't get impeached no matter what you do.": "无论你做什么，都不会被弹劾。",
    "Whenever mist hangs over the waters of Lake Orwell on Harlech Island, sailors catch sight of a phantom castle just out of reach. As they draw near, it fades into the fog like a mirage, leaving only questions for all who have borne witness to this <style=b>\u201cCastle Strangerock.\u201d":
        "每当雾气笼罩哈莱克岛奥威尔湖的水面，水手们就会看见一座近在咫尺却无法抵达的幻影城堡。他们靠近时，城堡便如海市蜃楼般消失在雾中，只给所有亲眼目睹过它的人留下无尽疑问——<style=b>“异乡岩城堡”。",
}


def main() -> int:
    apply = "--apply" in sys.argv
    zh = {}
    for p in sorted((BASE / "zh").glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(k, str) and isinstance(v, str):
                    zh.setdefault(k, v)

    text = UI.read_text(encoding="utf-8")
    existing = set()
    for line in text.splitlines():
        if line.strip() and not line.startswith("#"):
            existing.add(line.split("\t")[0])

    added, skipped = [], []
    for k in KEYS:
        if k in existing:
            skipped.append((k, "already in ui_extra"))
            continue
        v = zh.get(k)
        if not v:
            skipped.append((k, "not in corpus"))
            continue
        added.append((k, v))
    for k, v in NEW.items():
        if k in existing:
            skipped.append((k.split("\\n")[0][:40], "already in ui_extra"))
        else:
            added.append((k, v))

    print(f"will add {len(added)} entries; skipped {len(skipped)}")
    for k, v in added:
        print(f"  + {k[:60]!r} -> {v[:40]!r}")
    for k, why in skipped:
        print(f"  - {k[:60]!r} ({why})")

    if apply and added:
        lines = text.splitlines()
        if not lines or not lines[-1].strip():
            lines = [ln for ln in lines]
        lines.append("")
        lines.append("# --- 由 tools/augment_ui_extra.py 追加：普查发现仍在显示英文的真实内容 ---")
        for k, v in added:
            lines.append(f"{k}\t{v}")
        UI.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\napplied -> {UI}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
