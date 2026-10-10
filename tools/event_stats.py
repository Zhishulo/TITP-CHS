"""Event translation workload stats: how many unique EN strings remain untranslated."""
import json
import sys
from pathlib import Path

base = Path(sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\96333\TITP-CHS')
known = set()
for f in sorted((base / 'zh').glob('*.json')):
    known.update(k.strip() for k in json.loads(f.read_text(encoding='utf-8')))

evdir = base / 'work' / 'events'
files = sorted(evdir.glob('*.tsv'))
total = 0
uniq = set()
empty = 0
covered = 0
per_file = []
for f in files:
    n = 0
    for line in f.read_text(encoding='utf-8', errors='ignore').splitlines():
        parts = line.split('\t')
        if len(parts) < 2:
            continue
        en = parts[1].strip()
        if not en or en == ':[PLACEHOLDER]':
            empty += 1
            continue
        n += 1
        total += 1
        if en in known:
            covered += 1
        else:
            uniq.add(en)
    per_file.append((f.name, n))

per_file.sort(key=lambda t: -t[1])
print(f'event files={len(files)} lines_total={total} empty={empty} already_covered={covered} unique_untranslated={len(uniq)}')
print('biggest files:', per_file[:10])
print('smallest files:', per_file[-5:])
buckets = {}
for name, n in per_file:
    b = (n // 20) * 20
    buckets[b] = buckets.get(b, 0) + 1
print('distribution by line-count bucket (size:files):', dict(sorted(buckets.items())))
