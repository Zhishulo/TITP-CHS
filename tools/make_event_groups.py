"""Group work/events/*.tsv into translation units of ~MAXLINES translatable rows.

Source-per-row rule (matches what the game can display):
  use lang1 (col 1) if it is not ':[PLACEHOLDER]', else lang2 (col 2), else lang3 (col 3).
Rows whose source text is already covered by an existing zh map are skipped.

Writes work/event_groups.json = [
  {"group": "g001", "lines": N, "files": ["01.tsv", ...]}, ...]
and prints a summary.
"""
import json
import sys
from pathlib import Path

base = Path(sys.argv[1] if len(sys.argv) > 1 else r'C:\Users\96333\TITP-CHS')
maxlines = int(sys.argv[2]) if len(sys.argv) > 2 else 450

known = set()
for f in sorted((base / 'zh').glob('*.json')):
    try:
        known.update(k.strip() for k in json.loads(f.read_text(encoding='utf-8')))
    except Exception as exc:  # noqa: BLE001
        print('skip', f.name, exc)

PH = ':[PLACEHOLDER]'


def rows(path):
    """yield source text per row"""
    out = []
    for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        parts = line.split('\t')
        if len(parts) < 3:
            continue
        src = ''
        for col in (1, 2, 3):
            if col < len(parts) and parts[col].strip() and parts[col].strip() != PH:
                src = parts[col].strip()
                break
        if src:
            out.append(src)
    return out


items = []
for f in sorted((base / 'work' / 'events').glob('*.tsv')):
    srcs = rows(f)
    todo = [s for s in srcs if s not in known]
    if todo:
        items.append((f.name, len(todo)))

items.sort(key=lambda t: (-t[1], t[0]))

groups = []
cur = {'group': '', 'lines': 0, 'files': []}
for name, n in items:
    if cur['files'] and cur['lines'] + n > maxlines:
        groups.append(cur)
        cur = {'group': '', 'lines': 0, 'files': []}
    cur['files'].append(name)
    cur['lines'] += n
if cur['files']:
    groups.append(cur)
for i, g in enumerate(groups, 1):
    g['group'] = 'g%03d' % i

out = base / 'work' / 'event_groups.json'
out.write_text(json.dumps(groups, ensure_ascii=False, indent=1), encoding='utf-8')
print('files_with_todo:', len(items), 'groups:', len(groups), 'total_lines:', sum(g['lines'] for g in groups))
print('wrote', out)
for g in groups[:8]:
    print(' ', g['group'], g['lines'], g['files'][:4], '...' if len(g['files']) > 4 else '')
print('  ...')
for g in groups[-3:]:
    print(' ', g['group'], g['lines'], g['files'][:4])
