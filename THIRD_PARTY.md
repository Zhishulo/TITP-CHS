# 第三方组件与许可 / Third-party components

本仓库与发布包（`TITP-CHS-v1.0.zip`）包含以下第三方组件，均按其原始许可分发：

| 组件 | 版本 | 许可 | 用途 | 来源 |
| --- | --- | --- | --- | --- |
| **BepInEx** | 5.4.22 x64 | LGPL-2.1 | Unity 游戏的插件加载器（发布包内 `bepinex\`，`winhttp.dll` + `doorstop_config.ini`） | https://github.com/BepInEx/BepInEx |
| **Noto Sans SC 子集**（`data/fonts/sub-Regular.ttf`） | 子集化自 Noto Sans SC Thin v2.004 | SIL Open Font License 1.1 | 注入游戏的中文字形来源；许可证全文见 `data/fonts/OFL.txt` | https://fonts.google.com/noto/specimen/Noto+Sans+SC |
| **Python embeddable runtime** | 3.13.7 | PSF License | 发布包内 `runtime\python\`（仅发布包，不含在本仓库） | https://www.python.org/ |
| **UnityPy** | 1.25.4 | MIT | `patch.py` 读写 Unity 资源（仅发布包 `runtime\` 内，仓库不含） | https://github.com/K0lb3/UnityPy |

本仓库自有代码（`patch.py`、`plugin/TITPFontFix.cs`、`tools/*.py`）为 **MIT**，见 `LICENSE`。
译文数据（`data/zh/*.json`、`data/ui_extra.tsv`）无偿提供给游戏权利方，见 `LICENSE` 末尾与 `docs/OFFICIAL_SUBMISSION.md`。

## 免责声明

- 本项目是**非官方**的个人汉化，与 SuperPAC、THQ Nordic 无隶属关系，未获其背书。
- **完全免费**，禁止任何形式的售卖、付费下载或捆绑收费。
- 发布包内**不含**任何游戏原始资源（不含 `resources.assets` / `sharedassets0.assets` 等）。
  安装脚本在用户本地读取自己的游戏文件并注入译文，安装前会自动备份原始文件，卸载可逐字节还原。
- 请支持正版。
- 若游戏权利方要求下架，将立即配合处理。
