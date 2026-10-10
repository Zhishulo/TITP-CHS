# 术语表与翻译口径（v1.0 定稿）

> 本文件面向参与/维护汉化的人。完整对照表见工程内 `glossary_draft.txt`（2400+ 条）与 `data\zh\*.json`（75 文件 / 28144 条）。
> 全部 72 组事件已译完，跨文件同串异译已用 `tools\unify_collisions.py` 全局归并（归并策略：出现文件数最多者胜，其次取更长者，再次取字典序最小者），术语已用 `tools\fix_terms.py` 定点统一。

## 1. 硬性规则

| 规则 | 说明 |
|------|------|
| 占位符 | `<b>`、`</b>`、`<i>`、`<color=…>`、`{0}`、`{VAR|NAME|UNIT}` 原样保留，个数与顺序一致 |
| 转义 | 字面 `\n` 原样保留（游戏用它换行） |
| 社交 | `@handle` 原样，其后用全角「：」；话题标签保留 `#` 前缀、内文译中文 |
| 表情/动作 | `*emote*` 星号保留，内容译中文（`*wink*`→`*眨眼*`，全库 96 处汉化 vs 6 处保留） |
| 金额 | 统一 `$1,000,000` 形式，不写「100 万美元」；「数百万美元」这类模糊量不折算 |
| 标点 | `--`/`–` → `——`；`...` → `……`；引号用中文 “ ”；作品/报刊/节目名加《》 |
| 脏话 | 不净化，按原力度直译 |
| 唯一性 | 同一英文串必须同一译文（跨文件也一样），已全局归并，当前冲突键 = 0 |
| 调试 token | `TEST_MONOLOGUE`、`ABCDABCD`、`QUOTE TEXT`、`TWEET TEXT`、`DID_A OR DID_B` 等原样保留 |

## 2. 固定译法（核心）

**人物**

| 原文 | 译文 | 备注 |
|------|------|------|
| Antonio Estaba | 安东尼奥·埃斯塔巴 | 主角 |
| Archie Wister | 阿奇·威斯特 | |
| Ellie | 艾莉 | 第一夫人 |
| Alta (Lando) | 阿尔塔（·兰多） | **勿与 Ellie 混译** |
| Paul Leroy | 保罗·勒罗伊 | 记者 |
| Joe Lynn | 乔·琳恩 | 记者（早期批次有「林恩」，已统一为「琳恩」） |
| Warren Monger | 沃伦·蒙格 | 国家情报总监 |
| Faist / Feist | 费斯特 | 源文两种拼写同一人 |
| Brezich | 布雷齐奇 | 国名 |
| Fouquois | 福夸 | 大法官（源文有 Angelo/Angela 拼写差异） |
| Vasquez | 瓦斯奎兹 | 大法官 |
| de Baca / Dujevska / Rostoch | 德·巴卡 / 杜耶夫斯卡 / 罗斯托奇 | |
| Peaches（角色昵称） | 桃桃 | 作为爱称/角色名统一作「桃桃」；字面「桃子」（真正在说水果）保留原样 |

**机构 / 概念**

| 原文 | 译文 |
|------|------|
| Secret Service | 特勤局 |
| CIA | 中情局 |
| FBI | 联调局 |
| Congress / congressman | 国会 / 议员 |
| House of Representatives / Senate | 众议院 / 参议院 |
| Supreme Court / justice | 最高法院 / 大法官 |
| Amendment 28 | 第28修正案 |
| deep state | 深层政府 |
| the establishment | 建制派 |
| Big Pharma | 大型药企 |
| the Pit | 坑 |
| Gitmo | 关塔那摩 |

**媒体 / 作品**（统一加《》）

《只谈DC》(Just DC)、《向死而生》(Left for Dead)、《不偏不倚》(Right in the Center)、《高曼》(Goldman)、《沙砾》(Sands)、《变革之风》(Wind of Change)、《火热美国》(Hot America)、《美国揭秘》(America Unveiled)、《闺蜜》(Girlfriends)。

**称谓**：Mr. President→总统先生；President-elect→当选总统先生；Sir→先生；Boss→老板；Chief→老大；Cowboy→牛仔；Buddy→哥们 / Dude→老兄（同一句里的 Buddy/Dude 变体只在各自词条内统一）；Honey/Darling→亲爱的。

## 3. 已收口的口径（阶段 3 决议）

| 议题 | 决议 |
|------|------|
| President-elect | **当选总统**（「候任总统」「总统当选人」已全部回改） |
| Big Pharma | **大型药企** |
| Goldman | **《高曼》**（《高盛》《戈德曼》已回改） |
| Just DC | **《只谈DC》**；同句涉及 Right in the Center 时作《不偏不倚》 |
| Sands | **《沙砾》**（《金沙》《桑兹》已回改） |
| CIA | **中情局**（「中央情报局」已回改） |
| Amendment 28 | **第28修正案**（「第 28 修正案」「第二十八修正案」已回改） |
| Brezich / Tuman / Sandy Lake | 布雷齐奇 / 图曼-1 / 桑迪莱克 |
| ZellCoin | 保留拉丁并统一大小写 |
| 事件标题 | 不加《》；仅作品/报刊/节目名加《》 |
| PLACEHOLDER | 译为「占位符」（对齐德/日版本） |
| Anne IV | 统一为「安娜四世」（多数派；g031 的「安妮四世」已回改） |
| 事件面板俄文残留 | 官方英文版本遗留的俄文/德文串由插件 `ui_extra.tsv` 覆盖为中文 |

## 4. 已知不可译项

- **引擎 token**：`999_TEST_DIALOGUE.tsv` 中 `DID_A OR DID_B`、`ITEMS_TOTAL: >0` 一类为调试 token，按原样保留。
- **URL 式标签**：`MILFs` / `BDSM` / `BLACKED` 等成人站标签保留拉丁。
- **品牌 / 专名**：`XM177`、`M4`、`M16`、`VPN`、`U盘`、`LGBT`、`Res Publica`、`TITPOTUS`（游戏内乐队名）、`CarpeDiem`、`Snapchat`、`Champ-Chomp` 等保留。
- **图形元素**：图标、地图标记、无文字的艺术资源不翻译。
