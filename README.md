<!-- gh-header -->
**简体中文** | [English](README.en.md) | [Русский](README.ru.md)

# 《This Is the President》简体中文汉化

**下载安装包 → [Releases 页面](https://github.com/Zhishulo/TITP-CHS/releases/latest)**（TITP-CHS-v1.0.1.zip，29.3 MB，包内自带运行时，**无需安装 Python**）

本仓库是汉化的源码仓库：资源注入器 patch.py、BepInEx 插件源码 plugin/TITPFontFix.cs、
翻译工具链 tools/*.py、以及全部译文数据 data/。下面这份文档与安装包内附带的说明书是同一份。

| | |
| --- | --- |
| 覆盖 | 全部对话 / 事件 / 文档 / 法案 / 界面，24,312 条唯一译文（约 107 万汉字） |
| 许可 | 自有代码 MIT；字体 SIL OFL 1.1；BepInEx LGPL-2.1 —— 见 [THIRD_PARTY.md](THIRD_PARTY.md) |
| 承诺 | 完全免费、禁止售卖、不含任何游戏原始资源、可一键还原 |
| 致官方 | 译文与工具链无偿提供给 SuperPAC / THQ Nordic —— 见 [docs/OFFICIAL_SUBMISSION.md](docs/OFFICIAL_SUBMISSION.md) |

---

# 《This Is the President》简体中文汉化补丁

适用于 Steam 版 **This Is the President**（Unity 2019.4.5f1 / Mono / Steam AppID **730430**）。
**完整汉化**：全部 72 组事件、主词典、文档、报纸、推特、教程与界面均已翻译（28144 条 / 约 107 万字）。

本补丁由两部分组成：

| 部分 | 作用 | 是否改动游戏文件 |
|------|------|------------------|
| **译文数据注入**（Python 脚本，一次性） | 把中文译文写进 `resources.assets` / `sharedassets0.assets` 的全部语言槽位（本轮构建实测：**34081 条字符串 / 1407 个 TextAsset**），并把 15 个 legacy `Font` 的内嵌数据换成 Noto Sans SC 子集 | 是（首次运行会备份原文件） |
| **BepInEx 插件 `TITPFontFix` v7** | ① 运行时把 932 个 `TMP_Text` 用到的静态 TMP 字体资产接上动态 CJK 图集（游戏自带字体没有汉字字形，不装插件会显示 □□□）；② 用 `ui_extra.tsv`（158 条）覆盖硬编码在预制体/程序集里的界面文字——包括官方英文版遗留的俄文、德文串 | 否（只挂 BepInEx） |

> 只装其中一半是不行的：**只有译文 = 满屏豆腐；只有插件 = 全是英文**。

---

## 1. 前置要求

- Windows 10/11 x64
- 已安装游戏的 Steam 正版副本
- **不需要安装 Python**：压缩包内已自带便携版运行时（`runtime\python\`，Python 3.13 + UnityPy，约 57 MB）。
  若你删掉了 `runtime\`，也可自备 Python 3.9+（64 位，勾选 *Add python.exe to PATH*）。
- 磁盘至少 500 MB 空闲（备份原版 assets 用）

## 2. 安装（推荐：一键脚本）

1. 把整个 `TITP-CHS` 文件夹解压到任意位置（例如 `D:\TITP-CHS`）。
   > 路径最好**不要含中文或空格**，个别系统的命令行处理会有兼容问题。
2. 双击 **`install.bat`**。
   - 脚本自动使用包内便携 Python；没有时才回退到系统 Python。
   - 脚本会自动找 Steam 里的游戏目录；找不到时会要求你把游戏目录拖进来。
   - 注入前会自动把原版 `resources.assets` / `sharedassets0.assets` 备份到 `assets_backup\`。
3. 看到 `安装完成` 后，从 Steam 正常启动游戏即可。

首次启动会比原版慢几秒（插件要生成 CJK 字体图集），之后恢复正常。

## 3. 安装（手动）

```bat
:: 1) 注入译文（自动定位游戏目录）
runtime\python\python.exe patch.py

:: 或手动指定游戏目录
runtime\python\python.exe patch.py --game "C:\Program Files (x86)\Steam\steamapps\common\This Is the President"

:: 2) 安装 BepInEx 与插件
::    把 bepinex\ 下的 winhttp.dll、doorstop_config.ini、BepInEx\ 整个复制到游戏根目录
::    把 plugins\TITPFontFix.dll 复制到 <游戏>\BepInEx\plugins\
::    把 data\fonts\sub-Regular.ttf 和 data\ui_extra.tsv 复制到 <游戏>\BepInEx\plugins\TITP-CHS\
```

启动后游戏根目录应出现 `BepInEx\LogOutput.log`，里面有
`TITP font fix v7: ... uiMap=158` 与 `baked 'TITP-CJK' from legacy Font 'LiberationSans'` 即表示插件已生效。

## 4. 目录结构

```
TITP-CHS\
├─ install.bat                  一键安装
├─ uninstall.bat                还原原版 assets / 卸载插件
├─ patch.py                     译文注入脚本（Python + UnityPy，自包含）
├─ requirements.txt
├─ runtime\python\              便携 Python 3.13 + UnityPy（免安装，可删）
├─ data\
│  ├─ zh\*.json                 译文数据（en→zh，75 个文件，28144 条）
│  ├─ ui_extra.tsv              硬编码界面覆盖表（158 条）
│  └─ fonts\sub-Regular.ttf     Noto Sans SC 子集（SIL OFL 1.1）
│     fonts\OFL.txt             字体许可证（必须随包分发）
├─ bepinex\                     BepInEx 5.4.22 x64（LGPL-2.1，取自官方发布包）
├─ plugins\TITPFontFix.dll      汉化字体/界面插件（自研，MIT）
└─ docs\
   ├─ OFFICIAL_SUBMISSION.md    给开发者的说明材料
   ├─ TERMINOLOGY.md            术语表与翻译口径
   └─ LETTER_TO_DEVELOPER.md    致开发团队的信（无偿赠与汉化，中英俄三版）
```

## 5. 卸载 / 还原

```bat
uninstall.bat
```

它会：
1. 用 `assets_backup\` 里的原文件覆盖回 `resources.assets` / `sharedassets0.assets`；
2. 删除 `<游戏>\BepInEx\plugins\TITPFontFix.dll` 与 `TITP-CHS\` 数据目录；
3. 保留 `BepInEx\` 本体（如不需要，手动删掉 `winhttp.dll`、`doorstop_config.ini`、`BepInEx\` 即可）。

Steam 的“验证游戏文件完整性”同样能还原 assets，但**不会**删除 BepInEx。

## 6. 常见问题

**Q: 全是 □□□ 方块？**
插件没加载。检查：① `winhttp.dll` 是否在游戏根目录；② `BepInEx\plugins\TITPFontFix.dll` 是否存在；③ 看 `BepInEx\LogOutput.log` 是否有报错。

**Q: 全是英文？**
译文注入没成功。重跑 `patch.py`，确认结尾打印的 `translated N strings` 中 N > 0（正常值约 34000）。

**Q: 游戏更新后汉化失效？**
Steam 更新会覆盖 assets，重跑一次 `patch.py` 即可（脚本不会覆盖已有备份）。

**Q: 会不会封号 / 影响成就？**
BepInEx 属于常见的 Unity 游戏 mod 框架，本游戏没有反作弊；成就照常解锁。联机内容不受影响。

**Q: 有些界面还是英文？**
极小概率残留。插件每 30 帧扫描一次界面文字并用 `ui_extra.tsv` 覆盖；若发现漏网，把该字符串按 `英文<TAB>中文` 追加到
`BepInEx\plugins\TITP-CHS\ui_extra.tsv` 即可（`#` 开头为注释，值写 `<clear>` 表示清空该文本）。

## 7. 已知问题

- 极少数纯图形化元素（图标、位置标记）无法翻译。
- 人物介绍面板的第 2/3 行残句由插件清空或补译（`ui_extra.tsv` 中的 `<clear>` 条目），属预期行为。
- 官方英文版自身遗留的俄文/德文串（如“鼹鼠调查”面板、幕僚长职务名）已被本补丁一并译成中文。
- 个别界面文字过长时可能换行到第二行，属正常现象。

## 8. 版本与校验

- 汉化版本：**v1.0.1（全量修复版）**
- 译文数据：`data\zh\*.json`，75 个文件 / **28144 条** / 约 **1069474 个汉字**
- 构建实测：`zh map size 24312`、`translated 34081 strings across 1407 files`、`fonts swapped 15 / textassets replaced 1481`
- 注入后 assets SHA-256（前 16 位）：`resources.assets 86769CB485AD4E3A`、`sharedassets0.assets AAF29309AF8302A4`
- 插件 `TITPFontFix.dll`（v7，17408 字节）SHA-256：
  `73DDBC6A47B33F17C7CAA0D937762117B4DB0C0C7EED6678E48ECAEF36794E75`
- 字体：`fonts\sub-Regular.ttf`（Noto Sans SC 子集，1405748 字节，SIL OFL 1.1）
- BepInEx：5.4.22.0（<https://github.com/BepInEx/BepInEx/releases/tag/v5.4.22>）
- 安装包 `TITP-CHS-v1.0.1.zip`（29,312,769 字节）SHA-256：
  `8C49D399D240848DACD2D7E323821C92DFC419AE0BCE2653C145B9BC151AD85C`
  下载后可用 `certutil -hashfile TITP-CHS-v1.0.1.zip SHA256` 核对（GitHub Release 上传的资产已由 GitHub 校验为同一哈希）。

## 9. 鸣谢与许可

- 本项目仅分发**译文数据、字体与插件**，不包含任何游戏原始资源。
- 字体：Noto Sans SC（Google，SIL OFL 1.1）—— 见 `data\fonts\OFL.txt`。
- BepInEx：LGPL-2.1。插件 `TITPFontFix`：MIT。
- 《This Is the President》版权归 MyMottoMe 所有；本项目为无偿粉丝汉化，请支持正版。
  若开发者愿意官方采纳本译文，我们可无偿提供全部译文数据（见 `docs\OFFICIAL_SUBMISSION.md`）。
