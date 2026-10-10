# 《This Is the President》简体中文本地化 —— 说明材料

致：MyMottoMe（游戏开发商）/ 发行方

## 1. 项目概况

| 项 | 内容 |
|----|------|
| 目标 | 为 Steam 版 *This Is the President*（Unity 2019.4.5f1，Mono，AppID 730430）提供高质量简体中文本地化 |
| 性质 | 非商业、无偿粉丝汉化，不收取任何费用；如官方愿意采纳，可无偿转让全部译文 |
| 当前版本 | **v1.0（全量）**：72 组事件 + 主词典 + 文档/报纸/推特/教程/界面，共 **28144 条**（约 107 万汉字） |
| 交付形态 | 玩家侧安装包（译文数据 + BepInEx 插件 + OFL 字体 + 便携 Python + 一键安装脚本） |
| 是否包含游戏资源 | **否**。安装包不含任何游戏原始资源，注入脚本在玩家本地机器上运行，仅改写玩家自己安装的游戏文件 |

## 2. 技术方案

游戏的本地化文本存放在 `resources.assets` / `sharedassets0.assets` 内的 JSON 资源中，每行有 4 个语言槽位
（1=English，2=Russian，3=German，4=Japanese），简体中文缺失。方案分两层：

1. **译文注入**（离线、一次性）
   `patch.py`（Python + UnityPy，包内自带便携运行时）读取玩家本地 assets，把 en→zh 映射写入**全部 4 个语言槽位**，
   因此无论玩家把游戏语言设成哪种，都会显示中文。最近一次构建实测：`translated 34081 strings across 1407 files`，
   命中 1481 个 TextAsset；同时把 15 个 legacy `Font` 资产的内嵌字体数据替换为
   Noto Sans SC 子集（SIL OFL 1.1，随包附带许可证）。
2. **运行时字体与界面桥**（`TITPFontFix.dll`，BepInEx 插件，MIT）
   - 游戏 UI 的 900 多个文本组件使用 25 个 **Static** `TMP_FontAsset`，其中没有汉字字形，直接显示中文会变成方块。
     插件在启动时通过 TMP 官方 API `TMP_FontAsset.CreateFontAsset` 生成一张 4096×4096 的动态 CJK 图集
     （约 2700 字，覆盖全部译文用字），并注册为所有 TMP 字体资产的 fallback；对新出现的文本组件做一次网格刷新。
   - 另有少量字符串硬编码在 UI 预制体/程序集里。插件用一张 124 条的覆盖表（`ui_extra.tsv`）在运行时把它们换成中文，
     其中包括**官方英文版本自身遗留的俄文/德文串**（例如“鼹鼠调查”面板的标题、幕僚长职务名、人物介绍里的德语台词）。
   - 该过程**不修改游戏逻辑、不注入代码逻辑、不联网**。

## 3. 本地化覆盖范围

- 已覆盖：主菜单、设置、存档/读档、难度选择、教程、**全部 72 组事件**的对话与旁白、选择分支、文档、报纸/推特/邮件、
  成就名与描述、HUD 文本、回合结算面板、暂停菜单、人物介绍、字幕与角色名。
- 未覆盖（已知局限）：纯图形元素（图标、地图标记）与调试用测试文本（保留了英文 token）。
- 翻译原则：保留原文语气与讽刺、脏话不净化、金额与社交账号原样保留、作品/报刊名使用中文书名号；
  同一英文串全局唯一译文（已用脚本做跨文件归并，冲突键 0）。

## 4. 若官方愿意采纳

如官方有意将中文纳入正式版本，我们可以提供：

1. **纯文本对照表**（JSON，`原文 → 译文`，28144 条），可直接导入官方本地化管线；
2. **术语表**（人名、机构、媒体名的统一译法，见 `TERMINOLOGY.md`）；
3. **字体授权说明**：所用字体为 Noto Sans SC（SIL OFL 1.1），允许随商业软件嵌入与分发，**无需授权费**；
   官方若已有自备中文字体，只需替换字体资产即可，插件层可完全弃用；
4. **本地化工程脚本**（Python）：从 assets 抽取/回写译文，便于后续版本增量更新。

## 5. 已知原版文本问题（供参考，汉化未擅自修正）

- 同一角色存在拼写变体：`Antonio Estaba` / `Antonio Estabe`；`Faist` / `Feist`；`Angelo` / `Angela Fouquois`。
- **英文版本中残留的俄文/德文串**：`Охота на крота Mole Hunt`、`Поправка Amendment 28.`、
  `Как крот слил содержание указа в прессу?  How did the mole `（末尾带空格）、
  `Why was it Ngoyen's foundation that was robbed? Как думаешь, почему грабанули именно фонд Нгуен?`、
  `Кто был источником? Who was the first source?`、`Юрист`（`Speaker Name Panel/Position`）、
  `Finanzminister`（`Chief Of Staff` 职务名，疑为德语误串）、
  `Sie haben nur keine Ahnung, wer ich wirklich bin, Herr Präsident.`（Joe 的人物介绍台词）。
  这些在英文语言设置下同样会显示，本汉化已一并译成中文。
- 若干界面串存在笔误：`Badget at the end of month`（应为 Budget）、`Lobby the exeeecutive order`、
  `Reach 60% of approal rating`、`Carefree Environment  Environment`、`Dispel rumors` 与其结局描述语义相反、
  `As my the first official act`。
- 事件文件 `069_AMENDMENT_28_INTRODUCTION.tsv` 与 `070_AMENDMENT_28_INTRODUCTION.tsv` 内容完全重复。
- 多处英俄文内容不一致（俄文槽位有额外句子，例如事件 038 中 id 46 的俄文多出一整句）。

## 6. 联系方式

（请在此填写作者联系方式 / 发布页地址）
