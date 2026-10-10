[简体中文](README.md) | **English** | [Русский](README.ru.md)

# This Is the President — Simplified Chinese Localization

> This README is the English edition of the project documentation. The localization itself is **Chinese**
> (it replaces the game's text with Simplified Chinese), so this file is for English-speaking players,
> modders and the rights holders (SuperPAC / THQ Nordic) who want to know what the project does and how
> to install or uninstall it.

**Download the installer → [Releases page](https://github.com/Zhishulo/TITP-CHS/releases/latest)** (TITP-CHS-v1.0.1.zip, 29.3 MB, portable runtime included, **no Python installation needed**)

This repository holds the source of the localization: the asset injector `patch.py`, the BepInEx plug-in
source `plugin/TITPFontFix.cs`, the translation tool chain `tools/*.py`, and the complete translation data
in `data/`. The document below is the same one shipped inside the ZIP.

| | |
| --- | --- |
| Coverage | Every dialogue line, event, document, bill and menu — 24,312 unique entries (~1.07 million Chinese characters) |
| License | Own code MIT; font SIL OFL 1.1; BepInEx LGPL-2.1 — see [THIRD_PARTY.md](THIRD_PARTY.md) |
| Promise | Completely free, never sold, contains no original game assets, one-click restore |
| For the rights holders | Text and tool chain offered free of charge to SuperPAC / THQ Nordic — see [docs/OFFICIAL_SUBMISSION.md](docs/OFFICIAL_SUBMISSION.md) |

---

# This Is the President — Simplified Chinese patch

For the Steam release of **This Is the President** (Unity 2019.4.5f1 / Mono / Steam AppID **730430**).
**Fully localized**: all 72 event groups, the main dictionary, documents, newspapers, tweets, tutorials and UI
(28,144 entries / ~1.07 million characters).

The patch consists of two parts:

| Part | What it does | Does it modify game files? |
|------|--------------|----------------------------|
| **Translation injection** (Python script, one-off) | Writes the Chinese text into every language slot of `resources.assets` / `sharedassets0.assets` (measured on this build: **34,081 strings across 1,407 TextAssets**) and swaps the embedded data of 15 legacy `Font` objects for a Noto Sans SC subset | Yes (the original files are backed up on first run) |
| **BepInEx plug-in `TITPFontFix` v7** | ① At runtime it attaches a dynamic CJK atlas to the static TMP font assets used by 932 `TMP_Text` components (the game's own fonts contain no Chinese glyphs — without the plug-in you get □□□); ② it overrides hard-coded UI strings from prefabs/assemblies using `ui_extra.tsv` (158 entries), including Russian and German leftovers in the official English build | No (BepInEx only) |

> Half of it is not enough: **injection only = boxes everywhere; plug-in only = everything still English.**

---

## 1. Requirements

- Windows 10/11 x64
- A legit Steam copy of the game
- **Python is not required**: the ZIP ships a portable runtime (`runtime\python\`, Python 3.13 + UnityPy, ~57 MB).
  If you delete `runtime\`, you can also use your own Python 3.9+ (64-bit, *Add python.exe to PATH* checked).
- At least 500 MB of free disk space (for the backup of the original assets)

## 2. Installation (recommended: one-click script)

1. Extract the whole `TITP-CHS` folder anywhere (e.g. `D:\TITP-CHS`).
   > Prefer a path **without non-ASCII characters or spaces** — a few systems handle those badly on the command line.
2. Double-click **`install.bat`**.
   - The script uses the bundled portable Python; it falls back to a system Python only if that is missing.
   - It locates the game automatically; if it cannot, drag the game folder into the window.
   - Before injecting, it backs up the original `resources.assets` / `sharedassets0.assets` into `assets_backup\`.
3. When you see `安装完成` ("installation complete"), launch the game from Steam as usual.

The first launch takes a few seconds longer than vanilla (the plug-in bakes the CJK font atlas); afterwards it is normal.

## 3. Installation (manual)

```bat
:: 1) inject the translation (auto-detects the game folder)
runtime\python\python.exe patch.py

:: or point at the game folder explicitly
runtime\python\python.exe patch.py --game "C:\Program Files (x86)\Steam\steamapps\common\This Is the President"

:: 2) install BepInEx and the plug-in
::    copy winhttp.dll, doorstop_config.ini and the whole BepInEx\ folder from bepinex\ into the game root
::    copy plugins\TITPFontFix.dll into <game>\BepInEx\plugins\
::    copy data\fonts\sub-Regular.ttf and data\ui_extra.tsv into <game>\BepInEx\plugins\TITP-CHS\
```

After launching, `<game>\BepInEx\LogOutput.log` should appear and contain
`TITP font fix v7: ... uiMap=158` and `baked 'TITP-CJK' from legacy Font 'LiberationSans'`, which means the plug-in is active.

## 4. Directory layout

```
TITP-CHS\
├─ install.bat                  one-click install
├─ uninstall.bat                restore original assets / remove the plug-in
├─ patch.py                     translation injector (Python + UnityPy, self-contained)
├─ requirements.txt
├─ runtime\python\              portable Python 3.13 + UnityPy (no install needed, deletable)
├─ data\
│  ├─ zh\*.json                 translation data (en→zh, 75 files, 28,144 entries)
│  ├─ ui_extra.tsv              hard-coded UI override table (158 entries)
│  └─ fonts\sub-Regular.ttf     Noto Sans SC subset (SIL OFL 1.1)
│     fonts\OFL.txt             font license (must be redistributed with the pack)
├─ bepinex\                     BepInEx 5.4.22 x64 (LGPL-2.1, taken from the official release)
├─ plugins\TITPFontFix.dll      font/UI plug-in (own work, MIT)
└─ docs\
   ├─ OFFICIAL_SUBMISSION.md    material for the developer
   ├─ TERMINOLOGY.md            glossary and translation conventions
   └─ LETTER_TO_DEVELOPER.md    letter to the development team (Chinese / English / Russian)
```

## 5. Uninstall / restore

```bat
uninstall.bat
```

It will:
1. copy the original files from `assets_backup\` back over `resources.assets` / `sharedassets0.assets`;
2. delete `<game>\BepInEx\plugins\TITPFontFix.dll` and the `TITP-CHS\` data folder;
3. keep `BepInEx\` itself (if you do not want it, delete `winhttp.dll`, `doorstop_config.ini` and `BepInEx\` manually).

Steam's "Verify integrity of game files" also restores the assets, but it does **not** remove BepInEx.

## 6. FAQ

**Q: Everything is □□□ boxes.**
The plug-in did not load. Check: ① is `winhttp.dll` in the game root; ② does `BepInEx\plugins\TITPFontFix.dll` exist;
③ does `BepInEx\LogOutput.log` contain errors.

**Q: Everything is still English.**
The injection failed. Re-run `patch.py` and make sure the final `translated N strings` line has N > 0 (about 34,000).

**Q: The localization stopped working after a game update.**
A Steam update overwrites the assets — just re-run `patch.py` (it will not overwrite the existing backup).

**Q: Can I get banned / do achievements still work?**
BepInEx is a common Unity mod framework, this game has no anti-cheat, and achievements unlock normally.
Multiplayer content is unaffected.

**Q: Some screens are still English.**
Rare leftovers are possible. The plug-in scans UI text every 30 frames and overrides it from `ui_extra.tsv`.
If you find one, append the string as `English<TAB>Chinese` to `<game>\BepInEx\plugins\TITP-CHS\ui_extra.tsv`
(lines starting with `#` are comments; a value of `<clear>` blanks the text).

## 7. Known issues

- A few purely graphical elements (icons, map markers) cannot be translated.
- Lines 2 and 3 of the character intro panels are blanked or re-translated by the plug-in (the `<clear>` entries
  in `ui_extra.tsv`) — this is intended.
- Russian/German strings left over in the official English build (the "mole hunt" panel, the chief-of-staff job
  title, etc.) are translated into Chinese along with everything else.
- Some UI labels wrap onto a second line; that is normal.

## 8. Version and checksums

- Localization version: **v1.0.1 (full fix release)**
- Translation data: `data\zh\*.json`, 75 files / **28,144 entries** / ~**1,069,474 Chinese characters**
- Measured build output: `zh map size 24312`, `translated 34081 strings across 1407 files`, `fonts swapped 15 / textassets replaced 1481`
- Injected assets SHA-256 (first 16 hex digits): `resources.assets 86769CB485AD4E3A`, `sharedassets0.assets AAF29309AF8302A4`
- Plug-in `TITPFontFix.dll` (v7, 17,408 bytes) SHA-256:
  `73DDBC6A47B33F17C7CAA0D937762117B4DB0C0C7EED6678E48ECAEF36794E75`
- Font: `fonts\sub-Regular.ttf` (Noto Sans SC subset, 1,405,748 bytes, SIL OFL 1.1)
- BepInEx: 5.4.22.0 (<https://github.com/BepInEx/BepInEx/releases/tag/v5.4.22>)
- Installer: `TITP-CHS-v1.0.1.zip` — its size and SHA-256 are published with the release itself
  (<https://github.com/Zhishulo/TITP-CHS/releases/tag/v1.0.1>, also written to `sha256.txt` next to the archive).
  On Windows you can verify a download with `certutil -hashfile TITP-CHS-v1.0.1.zip SHA256`; GitHub validates the
  uploaded release asset against the same digest.

## 9. Credits and licensing

- This project distributes **translation data, a font subset and a plug-in only** — no original game assets.
- Font: Noto Sans SC (Google, SIL OFL 1.1) — see `data\fonts\OFL.txt`.
- BepInEx: LGPL-2.1. Plug-in `TITPFontFix`: MIT.
- *This Is the President* is © MyMottoMe. This is a free fan localization; please buy the game.
  If the developers would like to adopt this translation officially, the complete text data can be handed over
  free of charge (see `docs\OFFICIAL_SUBMISSION.md`).
