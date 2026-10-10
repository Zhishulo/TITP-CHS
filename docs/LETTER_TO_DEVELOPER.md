# 致《This Is the President》开发团队的信（无偿赠与汉化）

> 发送对象：本作 **开发商 = SuperPAC**、**发行商 = THQ Nordic**（Steam appid `730430`，2021-12-06 发售）。
> 本地化预算与「是否上官方中文」由**发行商**拍板 → **主送 THQ Nordic，抄送 SuperPAC**。
> 游戏数据目录写作 `MyMottoMe`（工作室早期名/法人名），信里带一句便于对方内部对号。
> 发信人：**枝树（zhishu）**，邮箱 **963336185@qq.com**。
> 用法：把下面**英文正本**复制进邮件/私信，替换 `[...]` 占位内容；俄文摘要建议同时附上（团队是俄罗斯工作室），
> 中文对照仅供你自己核对，不必发。
> 发送渠道见文末「投递渠道」。

---

## 一、English（正本，直接复制）

**Subject:** Free Simplified Chinese localization for This Is the President — a gift from your Chinese players

Dear THQ Nordic publishing team, and dear SuperPAC team,

My name is `枝树（zhishu）`, a player from China and a long-time fan of *This Is the President*. Thank you for making a game that is genuinely funny and genuinely political — the mole hunt alone was worth the price.

I am writing about something our small group of players has built, and we would like to give it to you — for free, with no strings attached.

**What we made.** A complete Simplified Chinese localization of the game:

- 24,312 unique translated strings (28,144 entries across all files), roughly 1.07 million Chinese characters;
- every dialogue line, event, document, bill, news item and tweet, all menus, settings, tooltips, tutorials, turn summaries and end-of-month budget screens;
- the handful of strings that the English build still leaves in Russian or German (for example the mole-hunt questions and the Chief of Staff job title) are translated as well;
- a small runtime plug-in that supplies CJK glyphs to the game's TextMeshPro font assets, because those assets ship as static atlases without Chinese glyphs. Without it, Chinese text renders as empty boxes. The plug-in only touches fonts — it does not modify game logic, saves, or balance;
- an automated one-click installer (bundled portable Python, no dependencies) with a clean uninstall that restores the original files bit-for-bit.

**What we are offering.** We hand the localization over to you, free of charge:

1. **No payment, no royalties, no conditions.** We are not selling it and never will. We are not asking for credits, though you are welcome to mention the community if you wish.
2. **You may use it however you like** — ship it as an official Simplified Chinese language option, include it in a patch, or simply keep it in your archive. We assign whatever rights we hold in the translation text to MyMottoMe, and we are happy to release it under CC0 / public domain if that is easier for your legal team.
3. **We can deliver it in whatever format suits you.** The data is currently plain JSON keyed by the English source string; we can also produce CSV, a Unity `TextAsset` set, or per-scene tables — whatever your pipeline prefers.
4. **We can hand over the tooling as well** (MIT-licensed injection script and the font plug-in source), or simply hand over the finished data and step back.

**Two smaller things that may be useful to you.** While translating we kept a list of source-text issues in the English build: leftover Russian/German strings that display to English players, several typos, and two placeholders that never get replaced. They are listed in the attached `OFFICIAL_SUBMISSION.md`, section 5. Feel free to use that list even if you decide against the localization.

**Our request.** Please let us know which of these you would prefer:

- **(a)** you adopt the localization (officially or as a patch) — we will prepare anything you need;
- **(b)** you allow us to publish it as a free fan translation for the Chinese community, with the disclaimer that it is unofficial;
- **(c)** you would rather it not exist — say the word and we will take it down immediately, no hard feelings.

Option (b) is what we will do by default if we do not hear back, but we would much rather do this with your blessing. If it matters to you, we are also happy to keep the fan release free, non-commercial, and clearly marked as unofficial.

**Where you can look at it right now.** We have already published the fan build so that Chinese players can use it today while we wait for your answer:

- release page (ZIP, 28 MB, with SHA-256): https://github.com/Zhishulo/TITP-CHS/releases/tag/v1.0.0
- direct download: https://github.com/Zhishulo/TITP-CHS/releases/download/v1.0.0/TITP-CHS-v1.0.zip
- source, translation data and tooling (MIT / CC0): https://github.com/Zhishulo/TITP-CHS

If you would prefer it not to be public while you consider option (a), tell us and we will make the repository private or take it down the same day.

Thank you for reading, and for the game. If any of this is useful, `963336185@qq.com` reaches me directly; I am also `枝树 / zhishu`.

With respect,
`枝树（Zhishu）`
`[日期]`

**Attached / available on request**

- `TITP-CHS-v1.0.zip` — the complete package (translation data, font under SIL OFL 1.1, plug-in, installer)
- or simply download it: https://github.com/Zhishulo/TITP-CHS/releases/download/v1.0.0/TITP-CHS-v1.0.zip
- `OFFICIAL_SUBMISSION.md` — scope of coverage, technical approach, and the list of source-text issues
- `TERMINOLOGY.md` — the glossary and translation conventions we used

---

## 二、Русский（摘要，建议附在英文正文之后）

**Тема:** Бесплатная локализация This Is the President на китайский язык — подарок от китайских игроков

Здравствуйте, команда MyMottoMe!

Мы — небольшая группа китайских игроков, и мы сделали полную локализацию *This Is the President* на упрощённый китайский язык: 24 312 уникальных строк (примерно 1,07 млн иероглифов), включая все диалоги, события, документы, законопроекты, меню и обучение, а также небольшой плагин, который добавляет китайские глифы в шрифты TextMeshPro (сами шрифты в игре статические, без китайских символов).

Мы хотим **подарить** эту локализацию вам — бесплатно и без каких-либо условий: без оплаты, без роялти, без требования указания авторства. Вы можете использовать её как официальный китайский язык, включить в патч или просто сохранить у себя. Мы готовы передать данные в любом формате и, если нужно, отпустить их под CC0.

Если вы предпочитаете, чтобы мы опубликовали её сами как неофициальный фанатский перевод — мы будем рады вашему разрешению. Если вы против — мы немедленно всё удалим.

Спасибо за игру! С уважением, `[имя]`, `[почта]`.

---

## 三、中文对照（自己核对用，不必发）

主题：为《This Is the President》无偿提供简体中文本地化

尊敬的 MyMottoMe 团队：

我是中国玩家 `[姓名]`，很喜欢《This Is the President》。我们做了一套完整的简体中文化，想**无偿送给你们**，不附带任何条件。

- 共 24312 条唯一译文（28144 条目）、约 107 万汉字，覆盖全部对话、事件、文档、法案、新闻、推文、菜单、设置、教程、回合结算与月度预算界面；
- 英文版里残留的俄文/德文串（例如猎鼹行动的问答、幕僚长职务名）也一并译成中文；
- 附带一个小插件为游戏的 TextMeshPro 字体补上汉字字形（原字体是静态图集、不含汉字，否则显示为方框）。插件只动字体，不改游戏逻辑、存档与平衡；
- 一键安装器（自带便携 Python，零依赖），卸载可逐字节还原原文件。

我们的提议：
1. **不要报酬、不要版税、不要条件**，也不会拿去卖；署名可有可无。
2. 你们可以**随意使用**：作为官方简体中文、做成补丁、或只是存档。译文相关权利让渡给 MyMottoMe；如法务更方便，也可按 CC0 / 公有领域发布。
3. 数据现在是「英文原文 → 中文」的 JSON，也可以出 CSV、Unity TextAsset 或按场景拆表，随你们管线。
4. 工具链（MIT 许可的注入脚本、插件源码）也可以一并交出，或只交成品数据、我们退出。

另外：翻译过程中我们整理了一份**英文版原文问题清单**（残留俄德文、拼写错误、两个永不替换的占位符），见附件 `OFFICIAL_SUBMISSION.md` 第 5 节，即便你们不采用汉化也可以直接拿去修。

请求你们在三种方案中选一个：
- (a) 你们采纳（官方或补丁形式）——我们按需准备任何格式；
- (b) 允许我们作为免费非官方汉化发布给中文社区；
- (c) 不希望它存在——一句话我们立刻下架，绝不纠缠。

如果收不到回复，我们默认走 (b)：免费、非商业、明确标注非官方。但我们更希望得到你们的祝福。

---

## 四、投递策略：先发行商，抄送开发商

| 角色 | 是谁 | 在「上不上官方中文」上的权力 | 建议 |
| --- | --- | --- | --- |
| **发行商** | **THQ Nordic**（Embracer 集团） | **决定权**：本地化预算、商店页语言项、补丁发布都归发行商 | **主送**：官网联系表单 / 官方 Discord / X `@THQNordic` |
| **开发商** | **SuperPAC**（游戏数据目录里写作 `MyMottoMe`） | 技术实现方，决策权小；2021 年的游戏，团队多半在做别的项目 | **抄送**：既是礼貌，也方便发行商内部找到对接人 |
| **玩家支持** | Quantic Lab（Steam 商店页公示 `support@quanticlab.com`） | 无决定权，但这是官方公示的唯一邮箱 | 另发一封**简版**（3–5 句 + GitHub Release 链接），请求转交本地化团队 |

**结论：主送发行商 THQ Nordic，抄送开发商 SuperPAC，另外给 `support@quanticlab.com` 发一封请求转交的简版。**

为什么是这个顺序：
- 汉化要变成「官方中文」，卡点是**预算与法务**，这两件事只有发行商能拍板；开发商点头也上不了架。
- 但纯技术上评估这份汉化（插件是否安全、能否进管线）需要开发商，所以必须抄送。
- 玩家支持邮箱是工单系统，直接发长信会被当投诉归档；发简版请求转交反而有效。

**不建议打电话**：这三家都没有对公众开放的本地化决策电话线，电话只会被转到客服；书面邮件/表单才能留下证据链（万一将来需要证明「我们主动征求过许可」）。

### 具体渠道（按成功率）

1. **THQ Nordic 官网联系表单 / 官方 Discord / X `@THQNordic`** —— 主渠道，正文用上面的英文正本。
2. **SuperPAC**：Steam 商店页的开发商链接、官网、X；找不到公开邮箱就通过发行商转达（信里已写明 cc: SuperPAC）。
3. **`support@quanticlab.com`** —— 简版转交请求，附 GitHub Release 链接（https://github.com/Zhishulo/TITP-CHS/releases/tag/v1.0.0）。
4. 若两周无回复：在 Steam 社区讨论区发一个礼貌的公开帖（@ 开发者），标题写明「gift, free, no strings」，这通常比邮件更快被看到。

小提示：
- 一封信只发一次，别群发轰炸；两周无回复再换渠道，并在新渠道里注明「已通过 X 渠道致信，未获回复」。
- **别把 28 MB 的 ZIP 塞邮件**：给 GitHub 链接（https://github.com/Zhishulo/TITP-CHS/releases/download/v1.0.0/TITP-CHS-v1.0.zip）+ 只附 `OFFICIAL_SUBMISSION.md`；对方回信索要时再按其要求方式交付。GitHub 对外网可直连，比百度网盘可靠得多。
- 明确写「不要报酬、不要署名、可让渡权利」，能省掉对方内部法务一半顾虑。
- 若对方要求下架：**立刻照做**并在发布帖注明 —— 对社区声誉反而更好，也保住将来合作的可能。

## 五、发送前核对清单

- [ ] 替换全部 `[...]` 占位（姓名、邮箱、Steam/Discord）
- [ ] 决定是否附 ZIP（>25 MB 建议只给网盘链接）
- [ ] 附 `OFFICIAL_SUBMISSION.md` 与 `TERMINOLOGY.md`
- [ ] 用 DeepL/母语者快速过一遍俄文摘要
- [ ] 记下发送日期与渠道，方便 1–2 周后跟进
