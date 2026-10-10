## 《This Is the President》完整简体中文汉化 v1.0.3

**全文本汉化**，覆盖游戏从主菜单到结局的全部文字。

### v1.0.3 修订（2026-10-11，原版「雇佣」失效修复）

修好第二处**原版自身的逻辑错误**：「申请」窗口点「雇佣」→ 确认框选「是」→ 结果页点「关闭」之后，
候选人**不会加入团队**（薪水和事件结果却已经生效，所以看起来像「点了没反应」）。

原因是原版在生成结果页（immediate result）时，只把玩家选的 `SelectedOption` 复制给了新的
`MicroMonologueElement`，**没有复制 `accepted`**；结果页的 `MicroMonologueElement.Initialize()`
于是改用 `EventProcessor.GetCurrentLine()` 重新推断，而此时当前行恰好是 **REJECT** 行 ⇒ 结果页报告
`accepted=false` ⇒ 点「关闭」时 `CloseClicked()` 以 `result=false` 回调
`ApplicationsWindow.OnHire` 的 `if (result) Hire(slot)` ⇒ 雇佣被静默跳过。

- 影响：**原版游戏同样会出现，与汉化无关**；现象是弹窗、台词、薪水变化都正常，就是队伍里不会多出这个人
- 修复：插件升到 **v8.3.0**，用两个 Harmony prefix 把玩家真正点击的那个元素的 `accepted` 记下来，
  在结果页 `CloseClicked()` 之前还原回去（只补这个丢失的字段，**不改事件数据、存档与平衡**）
- 验证：实机跑通「雇佣 → 是 → 关闭」，日志出现 `Hire slot=key=DIPLOMAT_1 …` 与
  `CharacterManager.HireCharacter key=DIPLOMAT_1`，地图底部团队栏由 5 人变 6 人（新增「天 吴」），
  申请窗口官方栏同步清空

### v1.0.2 修订（2026-10-11，原版崩溃兜底）

修好一处**原版自身的崩溃**导致的卡死：在「申请」窗口点「雇佣」后弹出的确认框（「是」/「否」）
按钮亮着却点不动、事件卡在那里走不下去。

原因是原版在求值事件条件 `REQUEST_AGING` 时，先解引用 `GameHandler.CurrentEventProcessor`
（此刻恰好为 null）才判空，于是抛 `NullReferenceException`，微独白弹窗的初始化中途中断——
按钮的点击回调根本没来得及挂上（所以看起来是「亮着但没反应」）。

- 影响：**原版游戏同样会出现，与汉化无关**；`Player.log` 里的异常栈为
  `ConditionHelper.<>c.<.cctor>b__89_51` → `EventProcessor.GetFirstMicromonologueLine()`
  → `MicroMonologueElement.Initialize`
- 修复：插件 `TITPFontFix` 升到 **v8.0.0**，给 `ConditionPostfixListElement.GetChar()` 挂 Harmony finalizer——
  条件求值抛异常时按「条件不成立」处理（`__result='f'`）并记一条告警，让事件继续。
  **不改任何游戏数据、存档与平衡**
- 验证：实机跑通「雇佣 → 确认框 → 是/否可点 → 事件继续」；日志里 7 条兜底告警，无其它异常

### v1.0.1 修订（2026-10-11，重要）

修复一处**会让游戏卡死**的缺陷：推特回复行译文里的冒号被写成了全角「：」，
而游戏是用半角冒号切分该行（`TwitterReply.Initialized` 里的 `Split(':')`）；
切不开时发送推文会在中途抛异常，表现为**第一条推文选满后点 Send 毫无反应**
（按钮是亮的，点了不动；游戏不崩、不报错，但事件永远走不下去）。

- 影响：2026-10-10 发布的 v1.0 包与本页早前的 v1.0.1 包（玩到第一条推文必卡；用其中任一版本都请换成本页 ZIP）
- 修复：157 条回复行改回半角冒号（38 个文件）→ 重新注入 → 重新打包
- **已装旧版请重新下载本页 ZIP 覆盖安装**（`install.bat`），存档不受影响；也可用 `uninstall.bat` 还原后重装
- 验证：实机跑通第一条推文（Send → 三条回复 → 事件继续），并对全工程做了同类分隔符解析普查

### v1.0.1 修复内容

在 v1.0 基础上修正了 5 处译文缺陷（均可在游戏内直接看到）：

| # | 位置 | 问题 | 修复 |
|---|------|------|------|
| 1 | 人物百科 · 詹姆斯·布坎南 | 简介里的换行被写成了字面 `\n`，游戏里会显示成「\n」两字 | 改为真实换行 |
| 2 | 人物百科 · 沃伦·G·哈定 | 同上 | 同上 |
| 3 | 文档 · 颂歌《宇宙合众国》 | 三段歌词仍是英文，未翻译 | 整段译成中文（与游戏内已有译法统一） |
| 4 | 文档 · 歌曲《伟大国度的生活》 | 歌词未译、`Chorus:` 提示未译 | 歌词译中文、`Chorus:` → `副歌：` |
| 5 | 文档 · 歌曲《美国彩虹》 | 歌词未译 | 歌词译中文 |

同时修正了 v1.0 安装包内 `data\zh\dict_main.json` 未刷新的问题（术语统一轮次的改动没有同步进包），并让构建脚本自动应用这批数据修订，避免回归。

### 内容

- **24,312 条唯一译文 / 28,144 条目 / 约 107 万汉字**
- 全部事件对话（72 个事件组、1404 个事件文件）、文档、法案、新闻、推文、内阁与幕僚对话
- 全部界面：主菜单、设置、难度、存档、教程、HUD、回合结算、月度账单/预算面板
- 官方英文版里**残留的俄文/德文串**（猎鼹行动问答、幕僚长职务名、人物介绍台词等）一并译成中文
- 158 条硬编码 UI 覆盖表（程序集/预制体里写死的英文，词典无法覆盖的部分）

### 技术方案（两层）

1. **注入层**：把译文写进游戏自己的 `TextAsset` 语言槽（4 个语言槽全部替换），并换上中文字体 —— 游戏 95% 的文本走这条路。
2. **运行时层**：附带的 BepInEx 插件 `TITPFontFix` 为游戏的 TextMeshPro 字体资产在运行时烘出 CJK 动态图集（原始资产是静态图集、不含汉字，不装插件会显示方框），并覆盖硬编码 UI。**只动字体 + 两处原版 bug 兜底，不改游戏数据、存档与平衡。**

### 安装

1. 下载本 Release 的 `TITP-CHS-v1.0.3.zip` 并解压到任意目录
2. 双击 `install.bat`（未自动找到游戏时把游戏根目录拖进窗口回车；多 Steam 库用 `install.bat --list-games`）
3. 从 Steam 正常启动游戏

**无需安装 Python**（包内自带便携运行时），**无需单独下载 BepInEx**（包内是官方原版 5.4.22 x64）。
安装前会自动备份原始 `resources.assets` / `sharedassets0.assets`，`uninstall.bat` 可逐字节还原。

### 校验

```
文件：TITP-CHS-v1.0.3.zip
大小：29,320,555 字节
SHA-256：076A705A2F5BDC9F5404E90325CC9883E4B44D6528D0A89F71AFC7D92FD97E2C
```

Windows 上可用 `certutil -hashfile TITP-CHS-v1.0.3.zip SHA256` 自行核对。

### 反馈

遇到问题请附 `BepInEx\LogOutput.log` 与截图。

### 免责声明

非官方汉化，与 SuperPAC / THQ Nordic 无隶属关系。**完全免费，禁止售卖**。
包内不含任何游戏原始资源；字体为 Noto Sans SC 子集（SIL OFL 1.1）；BepInEx 为 LGPL-2.1 原版。
请支持正版。若权利方要求，将立即下架。

译文数据与工具链**无偿提供给游戏权利方**（SuperPAC / THQ Nordic），详见 `docs/OFFICIAL_SUBMISSION.md`。
