# 《This Is the President》汉化包 —— 发布指南（v1.0.3）

> 这份文档是给你（发布者）看的操作手册：**上传什么、帖子怎么写、用户怎么引导、被问到怎么答**。
> 帖子模板可以直接复制粘贴。

---

## 一、你要上传的东西：只有一个文件

| 项目 | 值 |
| --- | --- |
| 文件 | `TITP-CHS-v1.0.3.zip`（在 `C:\Users\96333\TITP-CHS\dist\`） |
| 大小 | 29,320,555 字节（29.32 MB） |
| 条目数 | 802 |
| SHA-256 | `076A705A2F5BDC9F5404E90325CC9883E4B44D6528D0A89F71AFC7D92FD97E2C` |

**只上传这一个 ZIP，不要上传整个文件夹**（文件夹里没有多余东西，但网盘用户容易点错进目录）。
在网盘同一目录再放一个 `sha256.txt`，内容一行：

```
076A705A2F5BDC9F5404E90325CC9883E4B44D6528D0A89F71AFC7D92FD97E2C  TITP-CHS-v1.0.3.zip
```

包内已经包含用户需要的一切，**用户不需要安装 Python、不需要单独下载 BepInEx、不需要下载字体**：
便携 Python 运行时、BepInEx 5.4.22 x64 原版、字体、插件 DLL、75 个译文数据文件、安装/卸载脚本、README、术语表、上交官方材料。

### 推荐的上传渠道（按优先级）

1. **网盘**：蓝奏云（<100 MB 免费、免注册下载体验最好）→ 主推；备用 百度网盘 / 夸克 / 123 云盘（同样传 ZIP，不要传文件夹）。
2. **Steam 社区 → 指南（Guide）**：发一篇图文指南，正文里放网盘链接。这是最容易被玩家搜到的地方（游戏 appid `730430`）。
3. **国内社区**：B 站（发一条演示视频，简介放链接）、贴吧（This Is the President 吧 / 单机游戏吧）、NGA、其乐（keylol）、QQ 群。
4. **GitHub Release（已完成）**：仓库 https://github.com/Zhishulo/TITP-CHS 已建好并上传了 ZIP 资产，发帖、给官方的信都可以直接引用；校验值天然可信。
5. **不要**传到需要注册/限速严重的网盘作为唯一渠道，也**不要**收费或设置付费门槛。

### 已上传（2026-10-07）

| 渠道 | 链接 | 提取码 |
| --- | --- | --- |
| 百度网盘（无需提取码，**需换成 v1.0.3**） | https://pan.baidu.com/s/5FNp0TWim0T-a0X7-_8oktg | 无，直接打开 |
| **GitHub Release 页面** | https://github.com/Zhishulo/TITP-CHS/releases/tag/v1.0.3 | 无 |
| **GitHub 直链**（可给外网/官方） | https://github.com/Zhishulo/TITP-CHS/releases/download/v1.0.3/TITP-CHS-v1.0.3.zip | 无 |

**发布前必须核对**：网盘上那份必须是最终版 —— 大小 `29,320,555` 字节，
SHA-256 `076A705A2F5BDC9F5404E90325CC9883E4B44D6528D0A89F71AFC7D92FD97E2C`。
若你是在本指南更新前下载的 ZIP（大小/哈希对不上），**请重新上传**，否则用户拿到的可能是旧译文。


---

## 二、发布帖模板（直接复制改）

### 标题（三选一）

- `《This Is the President》完整简体中文汉化 v1.0｜全自动安装｜无需 Python｜正版可用`
- `【汉化】This Is the President 总统模拟器 完整中文补丁 v1.0（2.8 万条 / 107 万字）`
- `This Is the President 简体中文补丁 v1.0 —— 菜单/对话/文档/法案全中文`

### 正文

```
【汉化信息】
游戏：This Is the President（Steam appid 730430）
版本：v1.0（完整版）
完成度：全文本汉化 —— 24312 条唯一译文 / 28144 条条目 / 约 107 万汉字
覆盖：主菜单、设置、难度、存档、开场旁白、全部事件对话、文档阅读、
      月度账单/预算、法案、HUD、教程、回合结算，以及官方英文版里残留的俄文/德文串

【效果预览】（放 3-4 张截图：主菜单 / 难度选择 / 对话 / 文档面板）

【下载】
GitHub（推荐，免登录、可断点续传）：
  页面：https://github.com/Zhishulo/TITP-CHS/releases/tag/v1.0.3
  直链：https://github.com/Zhishulo/TITP-CHS/releases/download/v1.0.3/TITP-CHS-v1.0.3.zip
百度网盘（无需提取码）：https://pan.baidu.com/s/5FNp0TWim0T-a0X7-_8oktg
校验：29,320,555 字节，SHA-256 076A705A2F5BDC9F5404E90325CC9883E4B44D6528D0A89F71AFC7D92FD97E2C


【安装：三步】
1. 解压 ZIP 到任意目录（路径不要有中文以外的怪符号，普通目录即可）
2. 双击 install.bat
   - 如果没自动找到游戏，把游戏根目录（含 This Is the President.exe）拖进窗口回车
   - 想装到别的 Steam 库：install.bat --list-games 会列出所有库
3. 从 Steam 正常启动游戏，界面就是中文了

全程不需要装 Python（包内自带便携运行时），不需要手动装 BepInEx（包内是原版 5.4.22 x64）。

【卸载】
双击 uninstall.bat 即可完全还原（会先备份原始文件再改，卸载时自动还原）。
装之前会自动把原版 resources.assets / sharedassets0.assets 备份到包的 assets_backup\ 目录，
随时可以手动还原。

【常见问题】
Q1 杀毒软件/Windows Defender 报警怎么办？
   → 报警的是 BepInEx 的 winhttp.dll（Unity 游戏通用的插件加载器，官方原版）。
     把游戏目录加入白名单即可。补丁本身不联网、不改存档、不修改游戏逻辑。
Q2 装了会不会影响成就/云存档？
   → 不影响。存档格式没动，成就照常解锁；卸载后原来的英文存档还能继续用。
Q3 游戏更新后会怎样？
   → 更新会覆盖 assets 文件，汉化会失效。重新跑一次 install.bat 即可（先 uninstall 再 install 更保险）。
Q4 字体是从哪来的？可以转载吗？
   → 思源黑体子集（Source Han Sans / Noto Sans SC），SIL OFL 1.1 开源许可，允许再分发，
     包内附 OFL.txt 原文。
Q5 为什么还有个别英文/俄文？
   → 少数文字是画在图片里的（没法翻译），另有极少数官方残留串。
     看到漏网的可以把截图发出来，下个版本补。
Q6 支持 Mac / Linux / Steam Deck 吗？
   → 不支持。补丁是 Windows 专用（BepInEx Win 版 + 原生 DLL）；Steam Deck 理论上可用 Proton 试，但未验证。
Q7 报错/黑屏/插件没生效？
   → 把 BepInEx\LogOutput.log 和截图发到帖子里，一看就知道原因。

【报错请提供】
- 游戏根目录下的 BepInEx\LogOutput.log
- 出问题的界面截图

【校验】
TITP-CHS-v1.0.3.zip
大小：29,320,555 字节
SHA-256：076A705A2F5BDC9F5404E90325CC9883E4B44D6528D0A89F71AFC7D92FD97E2C

【免责声明】
本补丁为个人兴趣制作的非官方汉化，完全免费，禁止任何形式的售卖或付费下载。
仅供学习交流使用，请支持正版。若官方采纳或要求下架，将立即配合处理。
译文数据与插件源码可无偿提供给游戏官方（见包内 docs\OFFICIAL_SUBMISSION.md）。
字体遵循 SIL OFL 1.1。
```

---

## 三、怎么引导用户（发帖后的互动话术）

1. **第一句话永远给动作**：「解压 → 双击 install.bat → Steam 启动」三步，不要先讲原理。
2. **主动交代"不用装 Python"**：这是和大多数 Unity 汉化最大的差别，用户最容易在这里放弃。
3. **主动交代杀软误报**：把 Q1 放在 FAQ 第一条，能省掉一半的提问。
4. **引导用户看 README**：包内 `README.md` 写得更细（目录结构、参数、手动指定游戏路径）。
5. **收反馈的格式**：明确要 `BepInEx\LogOutput.log` + 截图。日志里插件会写清哪一步失败。
6. **更新帖**：每次更新只改「更新日志 + 校验值」两处，标题加 v1.0.3，旧链接保留。
7. **不要承诺时间表**：写「有空就更」比「下周更新」安全。

---

## 四、发布前自检清单

- [x] ZIP 内**不含**任何游戏原始资源（无 `assets_backup\`、无 `install_info.json` 泄漏本机路径）
- [x] 校验值已记录（上文 + README + PROGRESS）
- [x] 包内 `README.md` / `install.bat` / `uninstall.bat` / `patch.py` / `runtime\` 齐全
- [x] 安装→重复安装→还原 已端到端实测（`--restore` 后哈希精确回到原版 `860CA5A1E11BC56E`）
- [x] 字体 OFL 协议随包分发
- [ ] 你本人实机跑一遍（菜单 → 新游戏 → 对话 → 文档 → 签署法案 → 结束回合）
- [ ] 截图 3-4 张（建议：主菜单 / 难度 / 对话 / 文档面板）

---

## 五、给官方的那封信

本作 **开发商 = SuperPAC**、**发行商 = THQ Nordic**（Steam appid 730430）。「上不上官方中文」由**发行商**拍板
→ **主送 THQ Nordic，抄送 SuperPAC**；另给商店页公示的玩家支持邮箱 support@quanticlab.com 发一封请求转交的简版。
不建议打电话（三家都没有对公众开放的决策线，电话只会被转客服）。
**交付方式**：给国外团队**不要用百度网盘**（需中国手机号注册、海外访问慢）。
优先 GitHub Release 或 WeTransfer / OneDrive / Google Drive 链接；邮件里只附 `OFFICIAL_SUBMISSION.md`，
对方回信索要完整包时再按其要求交付。

见包内 `docs\LETTER_TO_DEVELOPER.md`（英文正本 + 俄文摘要 + 中文对照，可直接复制发送）。
配套材料：`docs\OFFICIAL_SUBMISSION.md`（技术方案与覆盖范围）、`docs\TERMINOLOGY.md`（术语表）。
