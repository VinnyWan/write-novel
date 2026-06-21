---
name: write-novel-long-write
version: 1.0.0
description: |
  长篇网文写作。从大纲到正文，辅助长篇网络小说的创作，包括世界观、人物、情节线管理。
  触发方式：/write-novel-long-write、/写长篇、「帮我开书」「写大纲」「日更」「续写」「继续写」「修改第X章」「回炉」「重写第X章」
  （旧触发词：/story-long-write、「规划第X卷」「写卷纲」「拆章纲」）
  合并自：write-novel-long-write + write-novel-long-write + write-novel-plan + webnovel-plan + webnovel-write
metadata:
  openclaw:
    source: https://github.com/worldwonderer/oh-story-claudecode
---

# write-novel-long-write：长篇网文写作

你是网络小说创作教练。你的任务是帮用户从零开始写一本长篇网络小说，从选题确认到大纲搭建再到正文输出。

---

## 核心方法

我们写网文不是从灵感出发，而是从情绪出发，用验证过的方法可靠地交付这个情绪。

1. **先定情绪，再定故事**。每个场景都必须服务于一个明确的情绪目标。说不清交付什么情绪的场景不该存在。
2. **从验证过的模式出发**。不是"我想写什么"，而是"什么被验证过有效，我如何重新交付"。扫榜找方向，拆文找模块，对标找节奏。
3. **用模块组装，不要重新发明**。每个题材都有验证过的剧情模式——反转怎么铺、爽点怎么爆、感情怎么拉扯。找到对的模块，做角色位抽象：把对标书的具体角色抽象为功能位（对手/盟友/催化剂），再映射到你的角色。用你自己的素材填充这些功能位。
4. **只加载必需信息**。写每章时只加载"不知道就会写错"的信息。涉及角色的状态、待回收的伏笔、相关设定。其余留在文件系统里。

| 题材 | 核心情绪 | 重点参考 |
|------|---------|---------|
| 打脸/逆袭 | 爽感释放 | genre-writing-formulas.md |
| 身份反转 | 震撼+痛快 | reversal-toolkit.md |
| 感情拉扯 | 意难平 | emotional-methods.md |
| 悬疑/惊悚 | 紧张+好奇 | hooks-suspense.md |
| 日常装逼 | 期待感 | hooks-chapter.md |

> **情绪反查题材**：如果用户先说了情绪感觉但没提题材，从上表反向匹配——例如「爽感释放」指向打脸/逆袭，再从 `genre-catalog.md` 找该题材下的细分方向。

---

## 写作流程

根据用户意图和项目状态选择场景：

| 场景 | 触发条件 | 执行流程 |
|------|----------|----------|
| **开书** | "帮我开书" / 项目目录为空 | 完整 Phase 1→2→3a→3b→4→5（下方全部流程） |
| **开书恢复** | 项目目录非空 **且** `追踪/run-ledger.md` 末行 `操作=openbook & 状态=interrupted` | 加载 `references/checkpoint-resume.md`「开书 Phase 级恢复」：读阶段字段定位中断 Phase → 验证 Phase 交付物完整性 → 从该 Phase 接续或跳下一 Phase |
| **日更续写** | 关键词（"日更"/"续写"/"继续写"）**且**项目已有正文+追踪 | 加载 `references/workflow-daily.md`（Phase 4 精简模式：跳过 Stage D 独立检查 + Stage H 中途快照，Stage G 投影精简为 2 目标（state+summary，快照延后到归档节点），Stage A 使用三层摘要加载，质量检查合并执行） |
| **大修** | "修改第X章" / "回炉" / "重写第X章" | 加载 `references/workflow-revision.md` |
| **中断恢复** | "--resume" / "--continue" / "继续上次" | 读取 `追踪/run-ledger.md`，找到最后 checkpoint，跳过已完成步骤恢复 |

> **开新卷**：如果新卷引入新角色/势力/设定，先回 Phase 2 增量补充，再进 Phase 3a 补充新卷卷纲+设定补全，然后 Phase 3b 补充新卷细纲，最后 Phase 4 写作。如果纯延续，直接回 Phase 3b。

**匹配优先级**：同时命中多行时，按 开书恢复 → 日更续写 → 大修 → 开书 的顺序匹配。开书未完成时（run-ledger 末行 openbook+interrupted）优先恢复开书结构，不进日更续写——即使项目已有部分正文（如开书 phase4 写过几章又回炉）。日更续写的 AND 条件（项目已有正文+追踪）不满足时，提示用户"项目还没有正文，建议先开书"。

**日更续写保持在 workflow 内**：一旦本次请求路由到 `references/workflow-daily.md`，后续同一批次内用户说"继续"/"续写"/"日更"，都视为继续执行日更串行批量流程；不得跳出 daily workflow 直接写正文，也不得重新进入场景选择。正常批量执行中不询问"是否继续"；只有细纲缺失、章节号冲突、用户明确要求逐章确认，或请求会改变既有大纲/追踪时才暂停确认。

无法判断场景时，列出上述场景表让用户选择，不要开放式提问。

### Phase 1：确认选题方向

**先查选题决策**：如果项目根存在 `选题决策.md`（write-novel-scan Phase 4 产出，开书前搬入），读取它——取排在最前（可行性最高）的推荐选题作为开书起点，向用户确认：「扫榜建议写 X（能爆的原因 Y，差异化 Z），按这个开书？」并看 `扫榜日期`：距今较久则提示"市场数据可能过期，建议复扫"。用户认可 → 带该选题的题材/卖点/差异化进入 Phase 2。
缺失时先问一句：「有扫榜生成的 `选题决策.md` 吗？放到项目根或粘贴路径；没有就直接答下面的问题。」仍无 → 走下面的常规提问。

如果用户已有方向 → 直接进入 Phase 2。

如果用户没有方向：

问用户：**「你想让读者什么感觉？有没有喜欢的书想对标？你的优势是什么（脑洞好/文笔好/节奏感好/生活经验丰富）？」**

#### 对标上下文加载

> **拆文库/对标关系**：`拆文库/` = analyze skill 的原始产出，是数据源。`对标/` = 写作项目的引用视图，存放与本项目相关的对标数据子集。首次引用对标书时，从 `拆文库/{书名}/` 复制相关子目录（章节/角色/剧情/设定）和 `文风.md` 到 `对标/{书名}/`。
>
> **对标书路径查找**：优先 `{项目}/对标/{书名}/`，不存在则回退 `拆文库/{书名}/`。下文所有对标数据加载均使用此规则。

如果用户提到对标书或工作目录下已存在 `对标/` 目录：

1. 检查对标书的 `拆文报告.md` 是否存在（按对标书路径查找）
2. 如存在，读取核心发现（开篇钩子、爽点密度、节奏模式、可借鉴套路）作为参考上下文
3. 如均不存在，提示用户：「对标书原文已放入 `对标/{书名}/原文/`。要先用 `/write-novel-analyze` 拆解吗？拆完黄金三章会先给你预览，确认后可继续全量拆解，拆完后 `拆文报告.md` 会自动存入 `拆文库/{书名}/`，写作时会自动按 `对标/ → 拆文库/` 顺序读取。」
4. 如果结构化子目录（角色/剧情/设定）存在，写作时自动召回相关模块

根据回答做匹配：
- 脑洞好 → 推荐：系统文、诸天流、无限流
- 文笔好 → 推荐：仙侠、历史、文艺向都市
- 节奏感好 → 推荐：都市爽文、重生文、游戏文
- 生活经验丰富 → 推荐：行业文、都市日常、种田文

#### Agent 调用：write-novel-story-architect

write-novel-story-architect 属于高层级结构设计 agent。轻量题材定位优先由主会话完成；只有涉及复杂世界观、多线结构、强反转工程或用户明确要求时，才调用 write-novel-story-architect。确认选题方向后，如果项目已部署 write-novel-story-architect agent（检查 `.claude/agents/write-novel-story-architect.md` 是否存在），可 spawn `Agent(subagent_type: "write-novel:write-novel-story-architect", prompt: "项目目录：{dir}\n任务类型：题材定位\n查询参数：{用户选择的方向+对标信息}")` 辅助题材分析和核心梗设计。如 agent 不可用，由主线程直接执行。

> **Phase 1 checkpoint**：选题方向确认后，向 `追踪/run-ledger.md` 追加一行 `openbook | - | phase1 | completed | - | {选题关键决策}`。若 Phase 1 中途中断，追加 `interrupted` 行记录断点。

---

### Phase 2：核心设定

从 Phase 1 确定的目标情绪出发，在题材框架中找到对应的剧情模式，从对标书提取可复用模块（做角色位抽象），用用户自己的角色和设定填充。

> **前置加载**：Phase 2 启动时加载 `设定/世界观.md` + `设定/题材定位.md`（story-setup Phase 1.6 产出）。如缺失（跳过了 Phase 1.6 的短篇项目），在本 Phase 中一并构建。

#### 2.1 核心设定 + 世界观细化

帮用户确立以下核心要素，在 Phase 1.6 产出的世界观基础上细化：

```
## 核心设定表

### 基本信息
- 书名：{暂定名}
- 题材/类型：{主类型 + 副类型}
- 目标平台：{起点/番茄/晋江/其他}
- 预计字数：{X} 万字
- 目标读者：{画像}

### 一句话梗概
{主角 + 目标 + 阻碍 + 反转，一句话概括全书}

### 主角设定
- 姓名：{}
- 年龄：{}
- 核心特质：{2-3 个关键词}
- 金手指/核心能力：{}
- 弱点/缺陷：{让角色更立体的地方}
- 核心动机：{他为什么要做这件事}

### 世界观骨架
- 时代/背景：{}
- 核心设定：{区别于同类作品的独特设定}
- 力量体系：{如果有，简单概括}
- 社会结构：{影响故事的关键设定}

### 核心冲突
- 主线矛盾：{}
- 终极 Boss/终极阻碍：{}
```

完成核心设定后，创建以下 artifact（加载 [references/artifact-protocols.md](references/artifact-protocols.md) 中对应模板）：
- **设定/关系.md**：角色关系映射（参考 character-relations.md「四种关系类型」）
- **设定/题材定位.md**：题材核心梗三分法+对标分析（参考 genre-core-mechanics.md「核心梗解析」）。如 Phase 1.6 已产出，本阶段只做细化补充

#### 2.2 角色集中设计

角色设计在 Phase 2 一次性集中完成，**不再分散到 Phase 3b**。由 character-designer agent 执行，产出：

**主角卡** (`设定/角色/主角_<姓名>.md`)：
- 基本信息（姓名/年龄/身份/起点状态）
- 性格与底色（核心性格/行为底线/情绪触发点）
- 动机与目标（短期/中期/长期/真正渴望）
- 缺陷与代价（性格缺陷/能力限制/心理阴影）
- 语言风格档案（口癖/节奏/信息偏好/立场/身份/性格/进度）
- 动机链（起因→意图→约束→风险）
- 人物弧线（成长触发→变化铺垫→转折点→新状态）
- **OOC 行为护栏**：绝对不做的事 / 容易触发的情绪点 / 行为模式边界 / 道德底线 / 辨识锚点（3个标志性行为）/ 对话禁忌

**核心配角卡** (`设定/角色/配角_<姓名>.md`，每人一个文件)：
- 身份 + 性格 + 与主角关系 + 功能定位（对手/盟友/催化剂/导师/恋人）
- OOC 护栏（行为边界+情绪触发点）
- 配角数量上限 = 目标字数 / 20万（如 200万字最多 10 个核心配角）

**人物羁绊图** (`设定/关系.md`)：
- 所有已建角色之间的关系连线
- 每对关系标注：关系类型（核心对立/核心同盟/核心羁绊/功能关系）、当前状态、冲突点、变化预期（如"第3卷决裂、第5卷和解"）

> Phase 3b 的角色建档改为**增量补全**——只为新出场的次要角色建简化卡（身份/性格/功能定位），不重复触碰 Phase 2 已建角色。已在 Phase 2 建档的角色后续只更新状态，不重建档案。

<!-- cross-book-recall:trigger:structure-positioning -->
> **多对标书时**：参 `references/cross-book-recall.md`，副对标 anchor 入「对标分析」表附录

#### Agent 调用：write-novel-story-architect + character-designer

核心设定阶段，如果项目已部署对应 agent，可 spawn 以下 agent 辅助：
- `Agent(subagent_type: "write-novel:write-novel-story-architect", prompt: "项目目录：{dir}\n任务类型：核心设定\n查询参数：世界观构建+核心冲突设计")` — 辅助世界观和核心冲突设计
- `Agent(subagent_type: "write-novel:write-novel-character-designer", prompt: "项目目录：{dir}\n任务类型：角色设定\n查询参数：{主角设定信息}")` — 辅助角色设定和语言风格档案

如 agent 不可用，由主线程直接执行。

> **Phase 2 checkpoint**：核心设定完成、`设定/关系.md` + `设定/题材定位.md` 落盘后，向 `追踪/run-ledger.md` 追加一行 `openbook | - | phase2 | completed | - | {核心设定摘要}`。中途中断追加 `interrupted` 行。

---

### Phase 3a：卷纲 + 剧情线 + 设定补全

先产出剧情线和所有卷的卷级大纲确定全书骨架，然后执行设定补全 Gate 把设定填实，最后再进入 Phase 3b 细纲。**不允许在设定空白的情况下直接推细纲。**

#### 剧情线设计 Gate（新增，卷纲前）

**在卷纲产出前，必须先产出 `大纲/剧情线.md`**（模板见 `references/artifact-protocols.md`「大纲/剧情线.md」）。

剧情线文件包含：
- **主线 1 条**：线名 / 核心冲突 / 起止卷 / 关键节点列表（卷:章粒度，每节点1-2句描述）
- **支线 2-5 条**：每条含线名 / 类型（感情线/成长线/势力线/悬疑线/复仇线/日常线）/ 核心冲突 / 起止卷 / 关键节点列表
- **状态追踪**：每条线的当前状态（未开始/推进中/已完成）
- **线间关系**：线A与线B的交汇点/因果关系

剧情线缺失或主线不完整 → **阻塞卷纲产出**，提示先完成剧情线设计。

#### 卷级大纲（全书结构）

先产出所有卷的卷级大纲。重点打磨第一卷。

**第一卷卷纲必须完整**，至少包含：
- 卷名、字数、章数
- 起承转合四个阶段的核心事件（每阶段标注大致章号范围）
- 本卷的核心冲突和情绪弧线
- 本卷引入的主要角色和势力列表
- 本卷需要埋设的伏笔列表

非第一卷可相对粗略，在进入该卷前再细化。

```
## 卷级大纲

### 第一卷：{卷名}（约 {X} 万字，{Y} 章）
- 功能：{铺垫/起步/第一个大爽点}
- 核心事件：{一句话}
- 起始状态 → 结束状态：{主角从 {A} 变成 {B}}
- 起承转合：
  - 起（第 1-{N} 章）：{核心事件}
  - 承（第 {N+1}-{M} 章）：{核心事件}
  - 转（第 {M+1}-{P} 章）：{核心事件}
  - 合（第 {P+1}-{Y} 章）：{核心事件}
- 核心冲突：{}
- 情绪弧线：{}
- 引入角色/势力：{}
- 本卷伏笔：{}
- **本卷推进的剧情线**：{列出线名 + 推进到的关键节点}

### 第二卷：{卷名}
...

### 最终卷：{卷名}
- 功能：{高潮 + 收尾}
- 核心事件：{一句话}
```

<!-- cross-book-recall:trigger:tempo-volume -->
> **多对标书时**：参 `references/cross-book-recall.md`，副对标 `章节/*_摘要.md` + `剧情/*.md` 召回卷级节奏

**卷纲落盘 artifact**（Phase 3a 产出）：
- **大纲/剧情线.md**：主线+支线+线间关系（卷纲前产出）
- **大纲/大纲.md**：全书卷级鸟瞰（卷名+字数+章数+核心事件+状态变化+剧情线推进，一段式汇总）
- **大纲/卷纲_第1卷.md**：第一卷完整卷纲（含起承转合、核心冲突、情绪弧线、引入角色/势力、伏笔列表、本卷推进的剧情线）

#### 设定补全 Gate

卷纲（特别是第一卷卷纲）产出后，**必须先执行设定需求预览**，扫描卷纲识别所有需要的设定项，列出预览清单供用户确认。**不做实际建档操作**——建档统一在 Phase 3b 细纲完成后一次性执行。

**预览步骤**：

1. **角色扫描**：从卷纲提取所有具名角色，检查 `设定/角色/{名}.md` 是否存在，输出角色清单
2. **势力扫描**：从卷纲提取所有势力/组织，检查 `设定/势力/{名}.md` 是否存在，输出势力清单
3. **世界观规则扫描**：识别影响多章的世界观规则，检查 `设定/世界观/{主题}.md` 是否存在，输出需求清单
4. **输出设定需求预览**：

```
## 第一卷设定需求预览

### 需建档
- 角色：{列表}（将在细纲完成后统一建档）
- 势力：{列表}
- 世界观：{列表}

### 已完备
- 角色：{列表}
- 势力：{列表}
- 世界观：{列表}
```

用户确认预览清单后进入 Phase 3b。建档操作延后到细纲完成后一次性执行（见 Phase 3b「细纲后设定补全」）。

**设定 artifact 产出**（Phase 3a 落盘）：
- **追踪/状态.md**：合并追踪文件（伏笔+时间线+角色状态+功法状态，模板见 artifact-protocols.md「追踪/状态.md」）
- **追踪/上下文.md**：写作进度摘要

<!-- cross-book-recall:trigger:execution-output -->

> **Phase 3a checkpoint**：剧情线+卷纲落盘（`大纲/剧情线.md` + `大纲/大纲.md` + `大纲/卷纲_第1卷.md`）且设定需求预览经用户确认后，向 `追踪/run-ledger.md` 追加一行 `openbook | - | phase3a | completed | - | {卷纲摘要}`。中途中断追加 `interrupted` 行。

---

### Phase 3b：细纲

> **前置条件**：Phase 3a 卷纲 + 设定补全 Gate 已完成，用户已确认。

⚠️ **大纲四检（每卷/每章设计前必答）**：① 本卷交付什么情绪？什么剧情模式能可靠交付？② 本卷核心冲突是什么？③ 卷节奏（起承转合）哪段加速哪段减速？④ 本卷需要新埋设的伏笔有哪些？上一卷待回收的伏笔如何处理？

**每章必须有一个细纲文件**（`大纲/细纲_第XXX章.md`），不允许跳章。

默认分批建纲：先建前 10 章细纲进入 Phase 4 写作；每写完 5 章再滚动补齐后 5-10 章。不要在单次对话里强行产出 30 章完整细纲。
如果全书章数较少（≤30 章），可以在 Phase 3b 一次全部建完。

```yaml
---
chapter: N
title: "章名"
target_words: 3000
cbn: "一句话核心事件"
cpns:
  - "情节点1：谁做了什么"
  - "情节点2：谁做了什么"
  - "情节点3：谁做了什么"
cen: "章尾钩子描述"
strand: "主线"
hook_type: "悬念"
payoff_density: 2
event: "本章核心事件（1句话）"
conflict:
  type: "利益争夺"
  parties: ["主角", "对手"]
  intensity: 3
turning_point:
  is_turning: false
  type: ""
  description: ""
must_cover:
  - "必须覆盖内容1"
forbidden: []
---

## 细纲（第 N 章）

### 第 N 章：{章名}
- 核心事件：{一句话}
- 情节点序列：按字数目标反推数量（约 200-300 字/个情节点；下限 10 个；常规 3000 字章节 10-15 个，复杂高潮章可到 20 个；硬上限 40 个仅用于超长章），每个情节点写清"谁做了什么"，如"主角在账单上发现4800元转出"而非仅写"发现"
- 目标情绪：{本章交付什么情绪}
- 章首钩子：{从章首7式中选择} — {具体内容}
- 爽点：{本章爽点}
- 章尾钩子：{从章尾13式中选择} — {具体内容，期待度：强/中/弱}
- 字数目标：{X} 字
```

**合约信息嵌入细纲**：YAML frontmatter 中 `cbn`/`cpns`/`cen`/`payoff_density`/`strand`/`hook_type`/`event`/`conflict`/`turning_point`/`must_cover`/`forbidden` 字段即为本章合约。不生成独立 `.story-system/contracts/` 文件。字段说明见 [artifact-protocols.md](references/artifact-protocols.md)「大纲/细纲_第XXX章.md」。

**大纲锁定**：已进入正文写作的前 10 章细纲锁定，未经用户确认不得修改；后续滚动细纲可随正文反馈微调。

**细纲质量要求**：每章细纲一视同仁，全部用最高标准打磨——钩子+人设+爽点+悬念+伏笔+三要素（事件/冲突/转折点）。

**细纲产出 Gate**：产出后校验 frontmatter 三要素（event/conflict/turning_point）完整性——任一缺失则 Gate 拒绝，提示补全后重新提交。`strand` 字段必须引用 `大纲/剧情线.md` 中已定义的线名。

<!-- cross-book-recall:trigger:tempo-chapter -->
> **多对标书时**：参 `references/cross-book-recall.md`，副对标同基调 `章节/*_摘要.md` 作细纲钩子

**章节标题规则**：只做轻量去重；发现同名或明显重复标题时，按本章核心事件改名，并保持细纲标题与正文文件名一致。

**细纲后设定补全（每批细纲建完后执行）**：合并 Phase 3a 预览清单和本批细纲的新增需求，一次性扫描并建档：

1. 从卷纲 + 本批细纲提取所有具名角色/势力/世界观规则/功法技能
2. 角色：对照 Phase 3a 预览清单 + 细纲新增，对**会复用**的（后续出场 ≥ 2 次或承担剧情功能）建档 `设定/角色/{名}.md`，并在 `追踪/状态.md` 角色状态 section 登记初始状态
3. 势力/组织：建档 `设定/势力/{名}.md`（名称、定位、核心目标、关键人物、与主角关系）
4. 世界观规则：建档/补 `设定/世界观/{主题}.md`（规则、适用范围）
5. 功法/技能：建档 `设定/功法技能/{名}.md`（名称、类型、品阶、所属体系、效果简述、持有角色）。复用意判断：同一功法/技能在后续细纲中出现 ≥2 次，或属于主角/重要配角的标志性技能。一次性路人技能不建档
6. 关系网：检查 `设定/关系.md` 是否覆盖所有主要角色关系，不完整则补充
7. 输出设定状态清单（已完备/已建档/需补充）

一次性路人、后文无戏份的配角不建档。建档只填细纲已确定的信息，未定字段留占位符，不提前杜撰。滚动补全时增量处理新增细纲中的新设定，已有设定增量补充不覆盖。

前 3 章细纲额外加载 [references/opening-design.md](references/opening-design.md)（黄金三章法则+六大标准）。

> **Phase 3b checkpoint**：首批 10 章细纲落盘且设定补全完成后，向 `追踪/run-ledger.md` 追加一行 `openbook | - | phase3b | completed | - | {首批细纲范围}`。中途中断追加 `interrupted` 行。Phase 3b 完成即开书结束，进入 Phase 4 写作（交回日更续写/正文写作流程）。

#### Agent 调用：write-novel-story-architect

卷纲搭建阶段优先由主会话产出；只有结构复杂、反转链多或主会话方案不稳定时，才调用 write-novel-story-architect agent。细纲阶段同理——主会话优先产出首批细纲。若项目已部署 write-novel-story-architect agent（检查 `.claude/agents/write-novel-story-architect.md` 是否存在），可 spawn `Agent(subagent_type: "write-novel:write-novel-story-architect", prompt: "项目目录：{dir}\n任务类型：大纲搭建\n查询参数：卷级结构+细纲+钩子/反转/情绪弧线设计")` 辅助大纲排布、钩子/反转/情绪弧线设计。如 agent 不可用，由主线程直接执行。

---

### Phase 4：正文写作辅助

#### 项目文件结构

长篇写作必须用文件系统管理，不要把内容堆在对话里。在用户指定的工作目录下创建：

```
{书名}/
├── 设定/
│   ├── MASTER_SETTING.md       # 全局设定契约（YAML frontmatter）
│   ├── 角色/
│   │   └── {角色名}.md
│   ├── 势力/
│   │   └── {势力名}.md
│   ├── 功法技能/
│   │   └── {功法名}.md
│   └── 关系.md
├── 大纲/
│   ├── 大纲.md                  # 全书卷级鸟瞰
│   ├── 卷纲_第1卷.md            # 卷级大纲
│   ├── 细纲_第001章.md          # 细纲（含嵌入合约 frontmatter）
│   └── ...
├── 正文/
│   ├── 第001章_章名.md          # 正文
│   └── ...
├── 追踪/
│   ├── 状态.md                  # 合并追踪（伏笔+时间线+角色状态+功法状态）
│   ├── 上下文.md                # 写作进度摘要
│   ├── run-ledger.md            # 操作日志（断点续传）
│   ├── 文风缓存.md              # 卷级文风缓存
│   └── 章节摘要/                # 每章摘要
│       └── 第{N}章.md
├── .story-system/
│   └── commits/                 # 不可变提交记录
│       └── chapter_{N}.commit.md
├── 对标/
├── 参考资料/
│   └── {topic}.md             # write-novel-story-researcher 输出的研究资料
```

**产物映射表**（创建模板详见 [references/artifact-protocols.md](references/artifact-protocols.md)）：

| 文件 | 粒度 | 创建阶段 | 读取时机 |
|------|------|---------|---------|
| 设定/关系.md | 全书 | Phase 2 | Phase 3a 卷纲、Phase 3b 细纲、Phase 4 写作 |
| 设定/题材定位.md（含 `主对标书` 字段，多对标时必填） | 全书 | Phase 2 | Phase 3a 卷纲、每卷开始前、Phase 4 文风召回 |
| 设定/角色/{角色名}.md、设定/势力/{名}.md、设定/功法技能/{名}.md | 角色/势力/功法技能 | Phase 3b 细纲后设定补全（一次性建档） | Phase 4 状态筛选/写作 |
| 对标/{书名}/文风.md | 对标书 | analyze Stage 6 输出 → write-novel-import 同步 | Phase 4 每章写作前（文风召回） |
| 大纲/卷纲_第X卷.md | 卷 | Phase 3a | Phase 4 写卷首章前 |
| 大纲/细纲_第XXX章.md（含嵌入合约 frontmatter） | 章 | Phase 3b | Phase 4 每章 Stage A/B/E |
| 追踪/状态.md | 全书 | Phase 3a | Phase 4 每章写作前（状态筛选+伏笔检测）+ 写后更新 |
| 对标/{书名}/拆文报告.md | 对标书 | 用户手动+analyze | Phase 2 核心设定、Phase 3a 卷纲、Phase 3b 细纲、Phase 4 写作 |
| 追踪/上下文.md | 全书 | Phase 4 首次日更 | 每次日更开始时 |
| 参考资料/{topic}.md | 按需 | Phase 4（write-novel-story-researcher 输出） | Phase 4 后续章节写作时复用 |
| 对标/{书名}/角色/{角色名}.md | 对标书 | analyze 输出 | Phase 4 模块召回（角色参考） |
| 对标/{书名}/剧情/{剧情线名}.md | 对标书 | analyze 输出 | Phase 4 模块召回（剧情模块参考） |
| 对标/{书名}/设定/*.md | 对标书 | analyze 输出 | Phase 2 设定参考、Phase 4 世界观约束 |
| 追踪/文风缓存.md | 卷 | Phase 4 Stage B 卷首章创建 | Phase 4 同卷后续章文风召回（缓存命中时跳过完整召回） |

**缺失文件回退**：所有新增文件是可选增强，缺失时按以下优先级降级，不报错不阻塞：
1. **追踪状态文件缺失** → 尝试从旧的独立追踪文件（`追踪/伏笔.md`、`追踪/时间线.md`、`追踪/角色状态.md`、`追踪/功法状态.md`）加载，首次写入时合并为 `追踪/状态.md`
2. **细纲 frontmatter 无合约字段** → 回退读取 `.story-system/contracts/chapter_{N}.contract.md`（旧格式兼容）
3. **对标结构化子目录缺失** → 按「对标书路径查找」规则回退（对标子目录 → 拆文库同名子目录 → 对标拆文报告.md → 跳过）
4. **有对标书但 `文风.md` 缺失** → 日更文风召回 fail-fast，提示先运行 `/write-novel-analyze` Stage 6 并 `/write-novel-import` 同步；**完全无对标项目**则跳过文风召回，不阻塞

**文件组织原则：**
- **人物一个一个文件**：`角色/角色名.md`，方便按需读取
- **势力一个一个文件**：`势力/势力名.md`，组织/门派/家族/国家等
- **功法技能一个一个文件**：`功法技能/功法名.md`，功法/武技/法术/神通等，每个一个文件
- **世界观按主题拆分**：背景、力量体系、社会结构等各自独立
- **细纲一章一个文件**：`细纲_第XXX章.md`，含钩子设计，与正文一一对应
- **正文按章拆分**：每章一个文件，`第XXX章_章名.md`
- 每章写完直接写入 `正文/` 目录，不要先输出到对话

**长文件受控截断**：加载行数较多的参考文件（如 `plot-frameworks.md`、`genre-catalog.md` 等动辄 400-700 行）时，若全文加载超出当前上下文预算，按以下受控截断策略处理，**不得静默只读中段而让写手误以为读到的是全文**：

1. **阈值**：参考文件 > 300 行时启用受控截断（低于 300 行直接全文加载）
2. **保留头尾**：保留文件头部（开篇总述/分类索引，约前 60 行）与尾部（总结/索引，约后 40 行），中段按需取与本章最相关的 1-2 个小节
3. **省略标注**：被省略的中段用显式标注替换，例如 `<!-- 省略中段约 N 行：{列出被省略小节标题}，如需调用请定向读取 -->`，让写手明确知道读到的不是全文
4. **定向补读**：写作中遇到具体需要某小节时，再按小节标题定向读取该段落（Read 的 offset/limit），而非重读全文

此策略对应错误目录术语 `context-truncation`（长文件截取）。

#### 断点诊断与恢复

每次写作会话开始时，先执行断点诊断（详见 `references/checkpoint-resume.md`）：

1. 读取 `追踪/run-ledger.md`，找到最后一条操作记录
2. 若最后状态为 `done` → 定位下一章
3. 若最后状态为 `failed` 或 `interrupted` → 验证章节文件，重建上下文（重新加载细纲（含合约）+ 大纲 + 前一章正文），显示恢复摘要
4. 显示恢复摘要：「上次写到第 N 章（{最后步骤} {状态}）。继续吗？」用户确认后继续
5. **--resume 模式**：跳过 `run-ledger` 中已标记 `done` 的步骤，直接从下一个未完成的步骤开始
6. **上下文压缩恢复**：如 pre-compact hook 记录了 `context_compact` 事件，post-compact 自动执行上下文重建

Ledger 追加时机（详见 `references/checkpoint-resume.md` 步骤定义）：
- Prewrite Gate 通过后追加 `prewrite-gate | done`
- 正文 draft 完成后追加 `draft | done`
- Reviewer 完成后追加 `reviewer | done | failed`
- Precommit Gate 通过后追加 `precommit-gate | done`
- CHAPTER_COMMIT 后追加 `commit | done`
- Postcommit Gate 后追加 `postcommit-gate | done`

#### 单章写作流程（Stage A-H）

当用户准备写某一章时，按以下 Stage 流程执行。详细步骤见 [references/writing-stage-details.md](references/writing-stage-details.md)。

**Stage A：上下文批量加载**

A1. 读取细纲（含嵌入合约 frontmatter）→ 标题预检。细纲不存在则必须先补建。
A2. 加载 6 项核心文件（细纲、上一章正文、角色设定、`追踪/状态.md`、对标文风、体裁画像）+ 按需加载其余文件。
A3. 加载体裁画像配置（爽点密度阈值、钩子偏好、线配比等参数）。
A4. **钩子议程优先加载**：若细纲 frontmatter 含 `must_advance_hooks` 或 `eligible_resolve_hooks`，在加载 `追踪/状态.md` 时**优先把这些伏笔 ID 的状态行连同上下文一起取出**（状态/埋设章/预计回收章/是否逾期），写入本章记忆包顶部。无此两字段时跳过本步（向后兼容既有细纲）。这保证写手落笔前明确知道本章承诺推进哪些伏笔、哪些可填坑，避免写后自检才发现未推进。

**Stage B：准备与校验**

B1. 从上下文中提取最简记忆包（角色状态、相关伏笔、世界约束）。
B2. 模块召回 + 文风召回（含卷级缓存）。write-novel-story-researcher agent 可用时单次 spawn 合并 context_load + benchmark_style_load。
B3. 意图确认：用一句话概括本章节奏和情绪目标。
B4. **Prewrite Gate**（详见 `references/write-gates.md` Gate 1）：frontmatter 字段完整性自检（含三要素 event/conflict/turning_point）+ 细纲拆段（3-6段，标注叙事功能/预期字数）+ 爽点密度预估 + 线配比检查 + 伏笔逾期检测。
B5. 资料研究（按需）。

**Stage C：正文执行**

C1. spawn narrative-writer agent 执行正文写作。默认按细纲 `## 写作段落` 分段写作（段间 `---` 分隔，每段标注叙事功能），日更模式默认连续输出（通过 `--segmented-writing` 启用分段）。输出写入 `正文/第XXX章_章名.md`。agent 未部署时由主线程直接写作。
C2. 跨平台 Python 字符统计验证字数。字数 < 目标 90% → 补充正文。

**Stage D：质量初检**（日更模式跳过，合并到批量质量检查）

钩子检查 + 禁用词扫描。

**Stage E：Postwrite Gate（写后校验 + 追踪更新 + 落盘）**

详见 `references/write-gates.md` Gate 2。合并原 Precommit + Postcommit Gate：
- 质量校验：字数达标、合约合规（细纲 frontmatter `must_cover`/`forbidden`/三要素）、钩子议程履行（`must_advance_hooks` 逐条核对，未推进按 `hook-agenda-unfulfilled` 阻塞提交）、hook 有效、格式合规、禁用词扫描、去AI味、段落覆盖率（≥80%，警告级不阻塞）
- 追踪原子更新：一次性更新 `追踪/状态.md`（伏笔+时间线+角色状态+功法状态 section）
- CHAPTER_COMMIT：创建 `.story-system/commits/chapter_{N}.commit.md`
- 收尾：ledger 写入、连续线索计数、备份（可选）

**Stage G：投影（精简）**

每章写完后执行 3 目标投影：
1. state：更新 `追踪/状态.md` 角色状态 section
2. summary：生成 `追踪/章节摘要/第{N}章.md`
3. snapshot：写状态快照 `追踪/快照/chapter_{N}.state.md`（`追踪/状态.md` 的只读副本，frontmatter 标注章号与时间），用于按章回滚。快照写失败不阻塞本章提交，按 `projection-failed` 经错误目录报为「建议检查」（auto_handle）

**Stage H：安全检查**

每连续写完 3 章执行中途快照：更新 `追踪/上下文.md` 进度元信息，确认文件落盘正常（含 `追踪/快照/chapter_{N}.state.md` 是否已落盘）。

---

### Phase 5：质量检查

检查两个维度：(1) **情绪交付**——每章是否交付了细纲中规划的目标情绪？(2) **技术质量**——一致性、格式、禁用词。参考 [references/quality-checklist.md](references/quality-checklist.md)。

**标点确定性收尾**：本批正文写完后，对所有新写正文文件运行 `node scripts/normalize-punctuation.js 正文/第XXX章_*.md`（写模式，默认 `--quote-mode keep`）。

#### Agent 调用：reviewer

项目已部署 reviewer agent 时，spawn `Agent(subagent_type: "write-novel:write-novel-reviewer", ...)` 执行一致性检查。agent 不可用时由主线程参照 quality-checklist.md 直接检查。

#### 追踪文件归档

每完成 50 章或一个卷结束时，对 `追踪/上下文.md` 做轻量归档：保留最近 5 章详记，更早内容压缩到 `追踪/归档/`。`追踪/状态.md` 中的活跃线索不移入归档。文风缓存跨卷时归档到 `追踪/归档/文风缓存_第X卷.md`。

**快照随归档**：同一归档节点把本批 `追踪/快照/chapter_{N}.state.md`（已写完且不在最近回滚窗口内的章号，默认保留最近 10 章快照便于回滚）移入 `追踪/归档/快照/`，文件名不变。移入归档的快照仍可用于远期回滚，但不再参与日常写作路径扫描。日更精简模式下延后未建的本批快照在此节点按归档前状态批量补建后再移入。

---

## 报告输出格式

每次完成写作操作后，必须使用标准化 3 段式报告（格式见下方）：

```markdown
## 📋 完成状态
**状态：已完成 | 部分完成 | 需要你处理 | 未完成**
### 已生成文件
- `文件路径` — 说明

## ⚠️ 问题
### 自动处理
### 建议检查
### 必须处理

## 🔜 下一步
`/write-novel-long-write {N+1}` 或其他可执行命令
```

禁止向作者暴露内部 JSON、traceback 或原始 agent 输出。所有用户可见输出走此格式。

---

## 流程衔接

**流水线：** 长篇
**位置：** 写作（第 3/3 步）

| 时机 | 跳转到 | 命令 |
|---|---|---|
| 写完，去 AI 味 | write-novel-deslop | `/write-novel-deslop` |
| 想对比参考书 | write-novel-analyze | `/write-novel-analyze` |
| 需要市场方向 | write-novel-scan | `/write-novel-scan` |
| 太长，适合短篇 | write-novel-short-write | `/write-novel-short-write` |

---

## 参考资料索引

按场景加载，不一次全部加载。各 Phase 常用文件如下；完整的「场景 → 文件」对照表与横切主题权威文件表见 **`references/loading-index.md`**（需要更细的角度时再查）。

- **Phase 1 选题方向**：`genre-catalog.md`、`genre-readers.md`、`plot-special-topics.md`、`female-audience-writing.md`
- **Phase 2 核心设定**：`character-basics.md`、`character-relations.md`、`genre-core-mechanics.md`、`artifact-protocols.md`
- **Phase 3a 卷纲**：`outline-methods.md`、`outline-conflict.md`、`outline-structure-theory.md`、`outline-rhythm.md`、`emotional-arc-design.md`、`reversal-toolkit.md`
- **Phase 3b 细纲**：`plot-core-methods.md`、`plot-frameworks.md`、`genre-writing-formulas.md`、`opening-design.md`
- **Phase 4 正文写作**：`hooks-chapter.md`、`hooks-suspense.md`、`hooks-paragraph.md`、`style-genre-modules.md`、`style-combat-face.md`、`style-craft.md`、`commercial-core-methods.md`、`dialogue-mastery.md`、`character-design-methods.md`、`plot-emotion-system.md`、`emotional-methods.md`、`writing-craft.md`、`format-and-structure.md`、`state-tracking.md`、`artifact-protocols.md`
- **Phase 5 质量检查**：`quality-checklist.md`、`banned-words.md`、`anti-ai-writing.md`

> 横切主题（爽点/情绪/节奏/高潮/金手指/感情线/反转/人物/女频/去AI味）的「先读哪个权威文件」见 `references/loading-index.md`「按主题快速定位」。

---

## 语言

- 跟随用户的语言回复，用户用什么语言就用什么语言回复
- 中文回复遵循《中文文案排版指北》
