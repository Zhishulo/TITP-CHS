#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《This Is the President》简体中文补丁 —— 译文注入脚本

把 data/zh/*.json 里的 en→zh 映射写进游戏的
  This Is the President_Data/resources.assets
  This Is the President_Data/sharedassets0.assets
并把这 16 个 legacy Font 资产的内嵌数据换成 Noto Sans SC 子集，
供 BepInEx 插件 TITPFontFix 在运行时生成 CJK 动态字体图集。

用法:
    python patch.py                     # 自动定位 Steam 游戏目录
    python patch.py --game "<dir>"      # 手动指定
    python patch.py --restore           # 从备份还原（等于 uninstall）
    python patch.py --list-games        # 只打印找到的候选目录
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

BASE = Path(__file__).resolve().parent
ZH_DIR = BASE / "data" / "zh"
FONT_FILE = BASE / "data" / "fonts" / "sub-Regular.ttf"
BACKUP_DIR = BASE / "assets_backup"
INFO_FILE = BASE / "install_info.json"

LANGS = (1, 2, 3, 4)          # English / Russian / German / Japanese 槽位全部改写
FONT_NAMES = ["Noto Sans SC", "Microsoft YaHei", "SimHei"]
ASSET_FILES = ("resources.assets", "sharedassets0.assets")

GAME_EXE = "This Is the President.exe"
DATA_DIR = "This Is the President_Data"


# ---------------------------------------------------------------- 定位游戏
def steam_roots() -> list[Path]:
    roots: list[Path] = []
    try:
        import winreg  # type: ignore

        for hive, key in (
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Valve\Steam"),
        ):
            try:
                with winreg.OpenKey(hive, key) as k:
                    for value in ("InstallPath", "SteamPath"):
                        try:
                            p = winreg.QueryValueEx(k, value)[0]
                            if p:
                                roots.append(Path(p))
                        except OSError:
                            pass
            except OSError:
                pass
    except Exception:
        pass

    roots += [Path(r"C:\Program Files (x86)\Steam"), Path(r"C:\Program Files\Steam")]
    seen, out = set(), []
    for r in roots:
        if r.exists() and str(r).lower() not in seen:
            seen.add(str(r).lower())
            out.append(r)
    return out


def candidate_games() -> list[Path]:
    """所有找到的 Steam 库中，包含本游戏 Data 目录的路径。"""
    cands: list[Path] = []
    roots = steam_roots()
    libs: list[Path] = list(roots)

    # libraryfolders.vdf: 追加其它磁盘上的库
    for root in roots:
        vdf = root / "steamapps" / "libraryfolders.vdf"
        if not vdf.exists():
            continue
        try:
            for line in vdf.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if '"path"' in line:
                    p = line.split('"path"')[1].strip().strip('"').replace("\\\\", "\\")
                    if p:
                        libs.append(Path(p))
        except OSError:
            pass

    seen = set()
    for lib in libs:
        game = lib / "steamapps" / "common" / "This Is the President"
        if (game / DATA_DIR / "resources.assets").exists():
            key = str(game).lower()
            if key not in seen:
                seen.add(key)
                cands.append(game)
    return cands


def resolve_game(arg: str | None) -> Path:
    if arg:
        p = Path(arg)
        if (p / DATA_DIR / "resources.assets").exists():
            return p
        if (p / "resources.assets").exists():
            return p.parent          # 用户直接拖了 Data 目录
        sys.exit(f"[×] 这个目录里找不到 {DATA_DIR}\\resources.assets: {p}")
    cands = candidate_games()
    if not cands:
        sys.exit("[×] 没找到游戏目录，请用 --game \"<游戏根目录>\" 指定。")
    return cands[0]


# ---------------------------------------------------------------- 译文映射
def load_zh() -> dict[str, str]:
    zh: dict[str, str] = {}
    files = sorted(ZH_DIR.glob("*.json"))
    if not files:
        sys.exit(f"[×] 译文目录为空: {ZH_DIR}")
    for f in files:
        zh.update(json.loads(f.read_text(encoding="utf-8")))
    return zh


def translate_payload(text: str, zh: dict[str, str]) -> tuple[str, int]:
    """把 TextAsset 里的本地化 JSON 文本翻译成中文；返回 (新文本, 命中数)。"""
    if "localizationStrings" not in text and "eventLines" not in text:
        return text, 0
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return text, 0

    hits = 0
    if "localizationStrings" in data:
        for item in data.get("localizationStrings", []) or []:
            for pair in item.get("translationPairs", []) or []:
                if pair.get("language") in LANGS:
                    t = pair.get("text", "")
                    if t in zh:
                        pair["text"] = zh[t]
                        hits += 1
    elif "eventLines" in data:
        for line in data.get("eventLines", []) or []:
            for pair in (line.get("localizationSerializable") or []):
                if pair.get("language") in LANGS:
                    t = pair.get("text", "")
                    if t and t in zh:
                        pair["text"] = zh[t]
                        hits += 1
    if not hits:
        return text, 0
    return json.dumps(data, ensure_ascii=False, separators=(",", ":")), hits


# ---------------------------------------------------------------- 注入
def patch_assets(env, zh: dict[str, str], ttf: bytes) -> tuple[int, int, int]:
    fonts = texts = hits = 0
    for obj in env.objects:
        kind = obj.type.name
        if kind == "Font":
            tree = obj.read_typetree()
            if tree.get("m_Name") == "debug_cour":
                continue
            tree["m_FontData"] = ttf
            tree["m_FontNames"] = FONT_NAMES
            tree["m_FontRenderingMode"] = 2
            obj.save_typetree(tree)
            fonts += 1
        elif kind == "TextAsset":
            data = obj.read()
            script = data.m_Script
            if not isinstance(script, str):
                continue
            new_text, h = translate_payload(script, zh)
            if h:
                data.m_Script = new_text
                data.save()
                texts += 1
                hits += h
    return fonts, texts, hits


def claim_backup(game: Path, marker: Path) -> None:
    """确保 assets_backup 是本机为当前游戏目录建立的；否则丢弃外来备份。"""
    if not BACKUP_DIR.exists():
        return
    if marker.exists():
        try:
            info = json.loads(marker.read_text(encoding="utf-8"))
        except Exception:
            info = {}
        if str(info.get("game", "")) == str(game):
            return
        print(f"[!] assets_backup 属于另一个游戏目录（{info.get('game')}），已重新备份。")
    elif any(BACKUP_DIR.iterdir()):
        print("[!] assets_backup 里存在来源不明的备份（可能是解压压缩包时带进来的），已丢弃。")
    shutil.rmtree(BACKUP_DIR, ignore_errors=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def do_patch(game: Path) -> int:
    try:
        import UnityPy
    except ImportError:
        sys.exit("[×] 缺少 UnityPy，请先运行:  python -m pip install -r requirements.txt")

    data_dir = game / DATA_DIR
    zh = load_zh()
    ttf = FONT_FILE.read_bytes()
    print(f"[i] 游戏目录 : {game}")
    print(f"[i] 译文条目 : {len(zh)}")
    print(f"[i] 字体      : {FONT_FILE.name} ({len(ttf)} B)")

    # 备份目录：只认「本机为这个游戏目录建过的备份」，避免误用他人/压缩包里带来的备份
    BACKUP_DIR.mkdir(exist_ok=True)
    marker = BACKUP_DIR / "backup_info.json"
    claim_backup(game, marker)
    work = BASE / "_work"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()

    total = {"fonts": 0, "texts": 0, "hits": 0}
    for name in ASSET_FILES:
        src = data_dir / name
        if not src.exists():
            print(f"[!] 跳过（不存在）: {name}")
            continue
        # 备份原文件（只备份一次，避免把已汉化版本当原件）
        bak = BACKUP_DIR / name
        if not bak.exists():
            shutil.copy2(src, bak)
            print(f"[i] 已备份原文件 -> assets_backup\\{name}")
        else:
            print(f"[i] 备份已存在，沿用 assets_backup\\{name}")

        env = UnityPy.load(str(src))
        fonts, texts, hits = patch_assets(env, zh, ttf)
        env.save("none", str(work))
        out = work / name
        shutil.copy2(out, src)
        print(f"[√] {name}: 字体 {fonts} 个 / TextAsset {texts} 个 / 命中 {hits} 处")
        total["fonts"] += fonts
        total["texts"] += texts
        total["hits"] += hits

    shutil.rmtree(work, ignore_errors=True)
    (BACKUP_DIR / "backup_info.json").write_text(
        json.dumps(
            {
                "game": str(game),
                "backed_up_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "files": {n: sha256_of(BACKUP_DIR / n) for n in ASSET_FILES if (BACKUP_DIR / n).exists()},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    INFO_FILE.write_text(
        json.dumps(
            {"game": str(game), "patched_at": time.strftime("%Y-%m-%d %H:%M:%S"), **total},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    if total["hits"] == 0:
        print("[!] 一处都没命中：可能已经打过补丁，或游戏版本不匹配。")
        return 1
    print(f"[√] 注入完成：字体 {total['fonts']} 个，TextAsset {total['texts']} 个，命中 {total['hits']} 处")
    return 0


def do_restore(game: Path) -> int:
    data_dir = game / DATA_DIR
    if not BACKUP_DIR.exists():
        sys.exit("[×] 没有备份（assets_backup），无法还原。可用 Steam「验证游戏文件完整性」恢复。")
    marker = BACKUP_DIR / "backup_info.json"
    if marker.exists():
        try:
            info = json.loads(marker.read_text(encoding="utf-8"))
        except Exception:
            info = {}
        if str(info.get("game", "")) != str(game):
            print(f"[!] 警告：备份来自 {info.get('game')}，与当前游戏目录不一致，还原可能不适用。")
    else:
        print("[!] 警告：备份来源不明（没有 backup_info.json），仅在确认它就是这个游戏的原版文件时才继续。")
    for name in ASSET_FILES:
        bak = BACKUP_DIR / name
        if bak.exists():
            shutil.copy2(bak, data_dir / name)
            print(f"[√] 已还原 {name}")
    print("[√] assets 已还原；如需彻底卸载，再手动删除游戏目录下的 winhttp.dll / doorstop_config.ini / BepInEx")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="This Is the President 简体中文补丁")
    ap.add_argument("--game", help="游戏根目录")
    ap.add_argument("--restore", action="store_true", help="从备份还原原版 assets")
    ap.add_argument("--list-games", action="store_true", help="只列出找到的游戏目录")
    args = ap.parse_args()

    if args.list_games:
        for c in candidate_games():
            print(c)
        return 0

    game = resolve_game(args.game)
    return do_restore(game) if args.restore else do_patch(game)


if __name__ == "__main__":
    raise SystemExit(main())
