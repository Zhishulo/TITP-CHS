"""Apply zh translations to dictionary JSONs and rebuild resources.assets.

Usage: inject.py <base_dir> <game_assets_dir>
- reads dump/textassets/*.json (originals), applies zh/*.json maps
- writes build/textassets/*.json (translated)
- rebuilds resources.assets (fonts swapped + translated TextAssets) into build/
"""
import json
import re
import sys
from pathlib import Path

import UnityPy

base = Path(sys.argv[1])
assets_dir = Path(sys.argv[2])  # dir holding original resources.assets

dump = base / 'dump' / 'textassets'
build_ta = base / 'build' / 'textassets'
build_ta.mkdir(parents=True, exist_ok=True)

# merge all zh maps into one lookup: en_text -> zh_text
zh = {}
for f in sorted((base / 'zh').glob('*.json')):
    zh.update(json.loads(f.read_text(encoding='utf-8')))
print('zh map size:', len(zh))

LANG_SLOTS = (1, 2, 3, 4)


def translate_obj(obj):
    """Translate localizationStrings-style dict. Returns (new_obj, hit_count)."""
    hits = 0
    for item in obj.get('localizationStrings', []):
        for pair in item.get('translationPairs', []):
            if pair.get('language') in LANG_SLOTS:
                t = pair.get('text', '')
                if t in zh:
                    pair['text'] = zh[t]
                    hits += 1
    return obj, hits


def translate_event(obj):
    hits = 0
    for line in obj.get('eventLines', []):
        for pair in (line.get('localizationSerializable') or []):
            if pair.get('language') in LANG_SLOTS:
                t = pair.get('text', '')
                if t and t in zh:
                    pair['text'] = zh[t]
                    hits += 1
    return hits


total_hits = 0
translated_files = 0
for f in sorted(dump.glob('*.json')):
    raw = f.read_text(encoding='utf-8')
    if 'localizationStrings' in raw:
        obj = json.loads(raw)
        obj, h = translate_obj(obj)
    elif 'eventLines' in raw:
        obj = json.loads(raw)
        h = translate_event(obj)
    else:
        continue
    if h:
        out = build_ta / f.name
        out.write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        translated_files += 1
        total_hits += h
print(f'translated {total_hits} strings across {translated_files} files')

# rebuild resources.assets: swap fonts + replace TextAssets + TMP dynamic conversion
sys.path.insert(0, str(Path(__file__).parent))
from tmp_patch import patch_env

# font source mode: argv[3] = 'os' (OS font by name) or path to a font file
font_mode = sys.argv[3] if len(sys.argv) > 3 else 'os'
OS_FONT_NAMES = ['Microsoft YaHei', 'SimHei']
if font_mode == 'os':
    fonts_reg = b''
    fonts_bold = b''
else:
    fonts_reg = Path(font_mode).read_bytes()
    fonts_bold = Path(font_mode).read_bytes()
BOLD_MARKERS = ('Bold', 'Black', 'SemiBold', 'Heavy')

# script class lookup for TMP detection
ggm = UnityPy.load(str(assets_dir / 'globalgamemanagers.assets'))
ggm_scripts = {}
for obj in ggm.objects:
    if obj.type.name == 'MonoScript':
        try:
            d = obj.read()
            ggm_scripts[obj.path_id] = f'{d.m_Namespace}.{d.m_ClassName}'
        except Exception:
            pass

env = UnityPy.load(str(assets_dir / 'resources.assets'))
swapped = 0
replaced = 0
for obj in env.objects:
    t = obj.type.name
    if t == 'Font':
        if font_mode == 'none':  # text-only injection: keep vanilla Font assets untouched
            continue
        tt = obj.read_typetree()
        name = tt.get('m_Name', '')
        if name == 'debug_cour':
            continue
        tt['m_FontData'] = fonts_bold if any(m in name for m in BOLD_MARKERS) else fonts_reg
        tt['m_FontNames'] = OS_FONT_NAMES
        tt['m_FontRenderingMode'] = 2
        obj.save_typetree(tt)
        swapped += 1
    elif t == 'TextAsset':
        d = obj.read()
        name = d.m_Name
        src = build_ta / f'{name}.json'
        if src.exists():
            data = src.read_bytes()
            if isinstance(d.m_Script, str):
                data = data.decode('utf-8')
            d.m_Script = data
            d.save()
            replaced += 1
print(f'fonts swapped: {swapped}, textassets replaced: {replaced}')

# --- TMP handling: argv[4]='tmp' offline static rewrite (broken) | 'notmp' keep vanilla (BepInEx plugin handles TMP) ---
tmp_mode = sys.argv[4] if len(sys.argv) > 4 else 'notmp'
if tmp_mode == 'tmp':
    import bake_sdf
    import freetype

    freq = {}
    texts = []
    for f in sorted((base / 'zh').glob('*.json')):
        for v in json.loads(f.read_text(encoding='utf-8')).values():
            texts.append(v)
    for f in sorted((base / 'batches').glob('*.zh')):
        texts.append(f.read_text(encoding='utf-8', errors='ignore'))
    for t in texts:
        for ch in t:
            freq[ch] = freq.get(ch, 0) + 1
    charset = set(freq.keys())
    charset.update(chr(c) for c in range(0x20, 0x7F))
    charset.update('，。！？；：、""' + "''" + '（）【】《》…—·～％°')
    charset.discard('\n'); charset.discard('\t'); charset.discard('\r')
    print('TMP charset:', len(charset))

    bake_face = freetype.Face(font_mode if font_mode != 'os' else str(base / 'fonts' / 'sub-Regular.ttf'))
    bake_face.set_char_size(bake_sdf.FACE * 64, bake_sdf.FACE * 64, 72, 72)
    pixels, placed, complete = bake_sdf.build_atlas(bake_face, charset, freq)
    n_ok = sum(1 for v in placed.values() if v)
    print(f'baked {n_ok}/{len(placed)} glyphs, complete={complete}')

    n_tmp = 0
    tex_pids = set()
    for obj in env.objects:
        if obj.type.name != 'MonoBehaviour':
            continue
        info = bake_sdf.rewrite_tmp_asset(obj, ggm_scripts, bake_face, placed, 0)
        if info:
            n_tmp += 1
            for afid, apid in info['atlas_pptrs']:
                if afid == 0:
                    tex_pids.add(apid)
    for tp in tex_pids:
        bake_sdf.write_alpha8(env, tp, pixels)
    print(f'resources TMP static rewrite: {n_tmp} assets, {len(tex_pids)} atlases, {bake_sdf.fix_materials(env)} materials fixed')
else:
    print('TMP assets left vanilla (BepInEx plugin will handle)')

env.save('none', str(base / 'build'))
out = base / 'build' / 'resources.assets'
print('saved:', out, out.stat().st_size)

# rebuild sharedassets0.assets: font 1288 -> CJK + optional TMP rewrite
env2 = UnityPy.load(str(assets_dir / 'sharedassets0.assets'))
for obj in env2.objects:
    if obj.type.name == 'Font':
        if font_mode == 'none':
            continue
        tt = obj.read_typetree()
        tt['m_FontData'] = fonts_reg
        tt['m_FontNames'] = OS_FONT_NAMES
        tt['m_FontRenderingMode'] = 2
        obj.save_typetree(tt)
if tmp_mode == 'tmp':
    n_tmp = 0
    tex_pids = set()
    for obj in env2.objects:
        if obj.type.name != 'MonoBehaviour':
            continue
        info = bake_sdf.rewrite_tmp_asset(obj, ggm_scripts, bake_face, placed, 0)
        if info:
            n_tmp += 1
            for afid, apid in info['atlas_pptrs']:
                if afid == 0:
                    tex_pids.add(apid)
    for tp in tex_pids:
        bake_sdf.write_alpha8(env2, tp, pixels)
    print(f'shared TMP static rewrite: {n_tmp} assets, {len(tex_pids)} atlases, {bake_sdf.fix_materials(env2)} materials fixed')
env2.save('none', str(base / 'build'))
out2 = base / 'build' / 'sharedassets0.assets'
print('saved:', out2, out2.stat().st_size)
