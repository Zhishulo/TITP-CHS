"""Merge translated batch files (N|zh) into zh maps keyed by EN string.

Usage: merge_batches.py [base_dir]
Reads batches/<stem>_<start>.src and matching .zh, validates counts and markup,
writes zh/<stem>.json  (en_string -> zh_string)
"""
import json
import re
import sys
from pathlib import Path

base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd() / 'TITP-CHS'
batches = base / 'batches'
zhdir = base / 'zh'
zhdir.mkdir(exist_ok=True)

TAG = re.compile(r'</?\s*[a-zA-Z][^>]*>?|<[a-zA-Z]+=?|\{[0-9]\}|&#\d+;')


def read_pairs(stem, start):
    src = (batches / f'{stem}_{start}.src').read_text(encoding='utf-8').splitlines()
    zhf = batches / f'{stem}_{start}.zh'
    zh = zhf.read_text(encoding='utf-8').splitlines() if zhf.exists() else None

    def parse(lines):
        m = {}
        last = None
        for line in lines:
            head = line.split('|', 1)
            if len(head) == 2 and head[0].strip().isdigit():
                n = int(head[0].strip())
                m[n] = head[1]
                last = n
            elif last is not None:
                m[last] += '\n' + line
        return m

    return parse(src), (parse(zh) if zh else {})


def tags_of(s):
    return sorted(re.sub(r'\s+', '', t).lower() for t in TAG.findall(s))


problems = []
maps = {}
for srcf in sorted(batches.glob('*.src')):
    stem_start = srcf.stem
    stem, _, start = stem_start.rpartition('_')
    src_map, zh_map = read_pairs(stem, int(start))
    missing = [n for n in src_map if n not in zh_map]
    extra = [n for n in zh_map if n not in src_map]
    for n in missing:
        problems.append(f'{stem_start}: MISSING zh for #{n}: {src_map[n][:60]}')
    for n in extra:
        problems.append(f'{stem_start}: EXTRA zh #{n}')
    for n, z in zh_map.items():
        if n in src_map:
            ts, tz = tags_of(src_map[n]), tags_of(z)
            if ts != tz:
                problems.append(f'{stem_start}: TAG MISMATCH #{n}\n  src: {src_map[n][:80]}\n  zh : {z[:80]}')
    # merge even with problems (missing stay untranslated)
    m = maps.setdefault(stem, {})
    for n, z in zh_map.items():
        if n in src_map and z.strip():
            m[src_map[n]] = z

for stem, m in maps.items():
    (zhdir / f'{stem}.json').write_text(json.dumps(m, ensure_ascii=False, indent=0), encoding='utf-8')
    print(f'{stem}: {len(m)} translated strings')

print('problems:', len(problems))
for p in problems[:40]:
    print(' ', p)
