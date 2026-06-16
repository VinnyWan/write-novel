# write-novel 使用文档

> AI 辅助长篇小说创作工具，纯 Markdown 驱动，所有操作通过 `/` 命令（skill）完成。

## 目录

- [快速开始](#快速开始)
- [完整流水线](#完整流水线)
- [Skill 详解](#skill-详解)
- [常见场景](#常见场景)
- [文件体系](#文件体系)
- [Agent 体系](#agent-体系)
- [FAQ](#faq)

## 快速开始

第一次使用，按以下顺序执行：

```
/write-novel:story-setup          # 1. 部署基础设施（必须，仅一次）
/write-novel:story                # 2. 路由入口，说出你的意图即可
```

之后只需用 `/write-novel:story` 或用自然语言描述意图，路由会自动分发到对应 skill。也可以直接调用具体 skill：

| 想做什么 | 命令 |
|----------|------|
| 扫榜看市场 | `/write-novel:story-long-scan` |
| 拆解对标书 | `/write-novel:story-long-analyze` |
| 开书写长篇 | `/write-novel:story-long-write` |
| 写短篇 | `/write-novel:story-short-write` |
| 审查已写章节 | `/write-novel:story-review` |
| 去 AI 味 | `/write-novel:story-deslop` |
| 导入已有小说 | `/write-novel:story-import` |
| 查角色/伏笔/进度 | `/write-novel:story-query` |

## 完整流水线

### 长篇流水线（3 步）

```
扫榜 → 拆文 → 写作
```

| 步骤 | 命令 | 产出 | 耗时 |
|------|------|------|------|
| 1. 扫榜 | `/write-novel:story-long-scan` | 扫榜报告 + `选题决策.md` | 10-30 分钟 |
| 2. 拆文 | `/write-novel:story-long-analyze` | `拆文库/{书名}/`（含拆文报告、角色、剧情、设定、文风） | 30 分钟 - 3 小时 |
| 3. 写作 | `/write-novel:story-long-write` | 卷纲 → 章细纲 → 正文（渐进式推进） | 持续进行 |

写作阶段内循环：

```
Phase 1: 选题方向 → Phase 2: 核心设定 → Phase 3: 大纲搭建 → Phase 4: 正文写作 → Phase 5: 质量检查
```

正文写作采用**渐进式**：先建 10 章细纲 → 写 5 章 → 滚动补齐。细纲缓冲降至 ≤ 3 章时自动续建。

### 短篇流水线（3 步）

```
扫榜 → 拆文 → 写作
```

| 步骤 | 命令 | 产出 |
|------|------|------|
| 1. 扫榜 | `/write-novel:story-short-scan` | 扫榜报告 + 选题匹配 |
| 2. 拆文 | `/write-novel:story-short-analyze` | `拆文库/{书名}/`（拆文报告 + 情节节点 + 写作手法） |
| 3. 写作 | `/write-novel:story-short-write` | 核心框架 → 小节大纲 → 正文（单文件 ~8000+ 字） |

### 共享收尾

长篇和短篇写作完成后，共用以下收尾工具：

| 步骤 | 命令 | 说明 |
|------|------|------|
| 审查 | `/write-novel:story-review` | 多视角对抗式审查（full/lean/solo） |
| 去 AI 味 | `/write-novel:story-deslop` | 六关检测 + 3-pass 润色 |
| 封面 | `/write-novel:story-cover` | 生成网文封面图 |

## Skill 详解

### 基础设施

#### `story-setup` — 环境部署

```
/write-novel:story-setup
```

**做什么：** 将 hooks、rules、agents、CLAUDE.md 等基础设施部署到项目目录。**新项目必须先执行此命令。**

**部署内容：**
- `.claude/hooks/` — 6 个自动化 hook 脚本（会话启动、Compact 前后、缺口检测、提交校验）
- `.claude/agents/` — 7 个 agent 定义文件
- `.claude/rules/` — 4 条 path-scoped 规则
- `.claude/settings.local.json` — hooks 注册
- `CLAUDE.md` — 项目指令（合并策略，不覆盖已有内容）

**重新部署：** 已部署的项目再次运行会提示确认，按 `agents_version` 判断是否需要更新。

---

### 市场研究

#### `story-long-scan` — 长篇扫榜

```
/write-novel:story-long-scan
```

**做什么：** 分析起点、番茄、晋江、七猫等平台的排行榜数据，识别市场趋势和热门题材，输出选题决策。

**流程：**
1. 选择平台和题材方向
2. 采集榜单数据（优先脚本采集，也可用户提供）
3. 分析题材分布、新题材信号、经典题材动态
4. 输出扫榜报告 + `选题决策.md`（2-3 个推荐选题）

**关键原则：** 单本排名不是结论，跨样本重复模式才是信号。可行性上限受样本量约束（<15 条强制降级）。

#### `story-short-scan` — 短篇扫榜

```
/write-novel:story-short-scan
```

**做什么：** 分析知乎盐言、点众、黑岩等平台短篇数据，捕捉风口题材和情绪方向。

**与长篇扫榜的区别：** 短篇市场是情绪市场，信号有效期短，必须标注样本日期和复扫节点。输出的是情绪方向而非世界观设定方向。

---

### 拆文分析

#### `story-long-analyze` — 长篇拆文

```
/write-novel:story-long-analyze
```

**做什么：** 深度拆解爆款长篇小说的黄金三章、人设架构、爽点设计、节奏控制。6 阶段管道。

**管道阶段：**

| 阶段 | 内容 | 关键产出 |
|------|------|----------|
| Stage 0 | 概要提取 + 章节边界表 | `概要.md` + 章节索引 |
| Stage 1 | 黄金三章深度拆解 | 3 个深度拆解文件 → **自动停靠**，产出 `快速预览.md` |
| Stage 2 | 逐章摘要（并行 Agent） | `章节/第N章_摘要.md` |
| Stage 3 | 聚合分析（剧情 + 角色合并） | `剧情/*.md` + `故事线.md` |
| Stage 4 | 设定 + 角色关系 | `设定/` + `角色/` |
| Stage 5 | 汇总报告 | `拆文报告.md` |
| Stage 6 | 文风分析 | `文风.md`（句长/标点/对话潜台词 + few-shot 片段） |

**停靠机制：** Stage 0+1 完成后自动停靠，询问是否继续全量拆解。用户说"完整拆解 / 一次跑完"则跳过询问。

**耗时参考：** <50 章 30-60 分钟；50-200 章 1-3 小时；>200 章需多轮会话。

#### `story-short-analyze` — 短篇拆文

```
/write-novel:story-short-analyze
```

**做什么：** 拆解爆款短篇的故事核、结构、情感线、反转设计、写作手法。5 阶段全量管道（Stage 2-6）。

**与长篇拆文的区别：** 短篇靠共鸣和爆点驱动，管道更精简。产出包括 `_meta.json`（结构计数）供下游 `story-short-write` 消费。字数 ≥ 15000 时进入灰区询问用户。

---

### 写作

#### `story-long-write` — 长篇写作

```
/write-novel:story-long-write
```

**触发场景：**

| 场景 | 触发词 | 说明 |
|------|--------|------|
| 开书 | "帮我开书" | 完整 Phase 1→5，从选题到正文 |
| 日更续写 | "日更" / "续写" | 加载日更 workflow，串行批量写新章 |
| 大修 | "修改第X章" / "回炉" | 加载修订 workflow |

**Phase 概览：**

| Phase | 内容 | 关键动作 |
|-------|------|----------|
| 1 | 选题方向 | 读取 `选题决策.md` 或询问用户 |
| 2 | 核心设定 | 建立世界观骨架、角色设定、核心冲突 |
| 3 | 大纲搭建 | 卷级大纲 + 章细纲（渐进式，先建 10 章） |
| 4 | 正文写作 | 上下文加载 → Prewrite Gate → 生成 → Precommit Gate → 落盘 → 追踪更新 |
| 5 | 质量检查 | 情绪交付 + 禁词扫描 + 一致性检查 |

**单章写作流程（Phase 4 核心循环）：**
```
细纲检查 → 上下文加载 → 体裁画像加载 → Prewrite Gate → 准备层 → 写作 → 
字数验证 → 禁词扫描 → Precommit Gate → 追踪更新 → Postcommit Gate
```

**重要约束：**
- 默认最低 3000 字/章，细纲另有标注时以细纲为准
- 每章必有细纲文件，不允许跳章
- 前 10 章细纲锁定，后续滚动细纲可微调
- 每连续写完 3 章执行中途快照

#### `story-short-write` — 短篇写作

```
/write-novel:story-short-write
```

**做什么：** 完成一篇完整短篇小说（8000-20000 字），从情绪目标出发，以反转为核心。

**Phase 概览：**

| Phase | 内容 |
|-------|------|
| 1 | 确定情绪目标（意难平 / 反转震撼 / 爽感释放 / 治愈温暖 / 细思极恐 / 共鸣感动） |
| 2 | 构思核心框架（梗概、反转设计、情绪曲线、人设速写） |
| 3 | 逐场景写作（开头段 → 铺垫段 → 升级段 → 反转段 → 结尾段） |
| 4 | 精修打磨（钩子、情绪曲线、AI 腔排查） |

**硬约束：**
- 每节 ≥ 800 字（高信息密度题材 ≥ 500 字）
- 整篇 ≥ 8000 字
- 节数 = 小节大纲规划节数，不得合并
- 默认第一人称
- 正文为单文件 `正文.md`

---

### 导入

#### `story-import` — 逆向导入

```
/write-novel:story-import
```

**做什么：** 将已有小说（半成品或完本）反向解析为标准项目结构，使其可无缝接入 `story-long-write` / `story-short-write` 续写。

**流程：**
1. 确认导入源（文件路径 / 直接贴文本）
2. 篇幅自动检测（长篇 / 短篇）
3. 调用 analyze 管道深度拆解 → 产出 `拆文库/{书名}/`
4. 结构迁移：拆文产物 → 标准项目结构（设定/大纲/正文/追踪）
5. 项目激活，可直接续写

**关键设计：** 复用 analyze 管道，不重复发明拆解逻辑。>200 章的大型作品采用增量导入策略。

---

### 质量控制

#### `story-review` — 多视角审查

```
/write-novel:story-review [full|lean|solo]
```

**三种模式：**

| 模式 | Agent 配置 | 适用场景 |
|------|-----------|----------|
| full | story-architect + character-designer + narrative-writer + reviewer | 批次完成后的全面审查 |
| lean | story-architect + reviewer | 快速结构+事实审查 |
| solo | 不 spawn Agent | 单章快速自检、Agent 不可用时 |

**审查维度：** 结构 / 角色 / 文字 / 一致性 / 平台适配 / 事实冲突 / 格式

**问题严重度：** S1（阻塞主线）→ S2（影响效果）→ S3（局部问题）→ S4（建议）

**降级策略：** Agent 缺失或异常时自动降级为 solo，报告中明确标注 fallback 原因。

#### `story-deslop` — 去 AI 味

```
/write-novel:story-deslop
```

**做什么：** 检测并清除文本中的 AI 写作痕迹，让文字回归自然。

**四阶段：**

| Phase | 内容 |
|-------|------|
| 1. 扫描 | 快速标记 AI 味浓重位置 |
| 2. 诊断 | 量化分级（轻度/中度/重度），6 项客观指标 |
| 3. 清除 | 六关递进处理（A 禁词 → B 句式 → C 心理外化 → D 节奏 → E 对话 → F 结尾） |
| 4. 报告 | 输出修改统计 + 润色后全文 |

**六关 Gate：**

| Gate | 检测内容 | 处理方式 |
|------|----------|----------|
| A | 禁用词（5 星分级） | 5/4 星必须替换，3 星 ≤1 次/章 |
| B | 句式套路（7 种最毒句式） | "不是A而是B"等出现即替换 |
| C | 心理描写抽象化 | 外化为具体身体反应和动作 |
| D | 节奏工整 / 对称段落 | 打碎排比、句长混用 |
| E | 对话腔调雷同 | 注入口语化、动作穿插 |
| F | 章末总结升华 | 章末 200 字扫码切除 |

**字数约束：** 删除比例按等级控制（轻度 ≤15%、中度 ≤25%、重度 ≤35%）。

**使用场景：**
- 贴一段文字说"太 AI 了" → 完整检测 + 润色
- "帮我润色" → 先检测再润色
- "检查下有没有 AI 味" → 只检测不修改

---

### 实用工具

#### `story-query` — 状态查询

```
/write-novel:story-query
```

**支持查询：**
- 角色状态（"沈栀什么境界"）
- 伏笔状态（"F001 回收了没"）
- 写作进度（"写到第几章了"）
- 设定查询（"力量体系是什么"）
- 紧急度分析（"有没有什么紧急的"）

**原则：** 只提取相关字段，不加载完整文件，用作者语言简短回复。

#### `story-doctor` — 项目诊断

```
/write-novel:story-doctor
```

**两大功能：**
- **项目体检：** 只读诊断目录结构、核心文件、章节完整性、伏笔状态、角色一致性、律条合规
- **模式学习：** 从会话中提取成功写作模式并写入项目记忆（`/write-novel:story-doctor` + 描述模式）

#### `story-cover` — 封面生成

```
/write-novel:story-cover
```

**做什么：** 根据书名、作者名、目标平台，调用 GPT-Image-2 直接生成含标题和署名的专业网文封面。

**需要环境变量：** `GPT_IMAGE_API_KEY`

---

### 路由入口

#### `story` — 智能路由

```
/story
```

**做什么：** 根据自然语言意图自动分发到对应 skill。不知道该用哪个命令时，直接说你想做什么即可。

**路由示例：**
- "我想写小说" → 询问长篇/短篇后路由
- "帮我审一下第 5 章" → `/write-novel:story-review`
- "这段太 AI 了" → `/write-novel:story-deslop`
- "查一下林动的境界" → `/write-novel:story-query`

## 常见场景

### 场景一：从零开始写一本长篇

```
/write-novel:story-setup                    # 部署环境
/write-novel:story-long-scan                # 扫榜，确定写什么方向
/write-novel:story-long-analyze             # 拆 1-2 本对标书
/write-novel:story-long-write + "开书"      # 从选题到大纲到正文
# ... 写到第 5 章 ...
/write-novel:story-review                   # 审查已写章节
/write-novel:story-deslop                   # 去 AI 味
/write-novel:story-long-write + "日更"      # 继续写
```

### 场景二：续写已有长篇

```
/write-novel:story + "日更"                 # 自动定位当前进度，加载上下文，写下一章
```

### 场景三：导入已有作品继续写

```
/write-novel:story-import                   # 导入原文 → 分析 → 重建项目
/write-novel:story-long-write + "续写"      # 从断点继续
```

### 场景四：写一篇知乎盐言短篇

```
/write-novel:story-short-scan               # 看什么情绪方向火
/write-novel:story-short-analyze            # 拆 1 篇对标短篇
/write-novel:story-short-write              # 从情绪目标到成稿
/write-novel:story-review                   # 审查
```

### 场景五：修改已写章节

```
/write-novel:story-long-write + "修改第 8 章"  # 进入大修流程
```

### 场景六：批量质量检查

```
/write-novel:story-review full              # 全面审查
# 根据 S1/S2 问题修改
/write-novel:story-deslop                   # 去 AI 味
/write-novel:story-query + "进度"           # 确认状态
```

## 文件体系

### 用户写作项目结构

```
{书名}/
├── 设定/
│   ├── MASTER_SETTING.md       # 全局设定契约
│   ├── 题材定位.md              # 核心梗 + 对标书清单
│   ├── 角色/{角色名}.md
│   ├── 势力/{势力名}.md
│   └── 关系.md
├── 大纲/
│   ├── 大纲.md                  # 全书卷级鸟瞰
│   ├── 卷纲_第X卷.md
│   └── 细纲_第XXX章.md
├── 正文/
│   └── 第XXX章_章名.md
├── 追踪/
│   ├── state.md                 # 当前写作状态
│   ├── 上下文.md                # 三层上下文结构
│   ├── 角色状态.md              # 角色当前状态快照
│   ├── 伏笔.md                  # 伏笔状态表
│   ├── 时间线.md                # 故事时间线
│   └── run-ledger.md            # 操作日志（断点续传）
├── 对标/{书名}/                 # 对标书引用视图
│   ├── 文风.md
│   ├── 拆文报告.md
│   ├── 剧情/
│   └── 角色/
└── 选题决策.md                  # 扫榜产出，开书前置
```

### 拆文库结构（analyze 产出）

```
拆文库/{书名}/
├── 原文/                        # 原始文本备份
├── 概要.md                      # 全书概要
├── 快速预览.md                  # Stage 1 停靠交付
├── 章节/
│   ├── 第N章_深度拆解.md        # 仅黄金三章
│   └── 第N章_摘要.md            # 全部章节
├── 角色/
│   ├── {角色名}.md
│   └── 角色关系.md
├── 剧情/
│   ├── {剧情线}.md
│   └── 故事线.md
├── 设定/
│   ├── 世界观/
│   └── 势力/
├── 拆文报告.md                  # Stage 5 汇总
├── 文风.md                      # Stage 6 文风分析
└── _progress.md                 # 管道进度（断点续跑）
```

### Reference 文件架构

```
write-novel/references/
├── methodology/                 # ★ 权威共享副本（唯一事实来源）
│   ├── banned-words.md          #   各 skill 通过 symlink 引用
│   ├── anti-ai-writing.md       #   不再维护多份拷贝
│   ├── quality-checklist.md
│   ├── hooks-chapter.md
│   ├── ... (28 个文件)
│   ├── banned-words-star-rating.md
│   ├── toxic-sentence-patterns.md
│   └── genre-profile-configs.md
├── shared/                      # 共享约定与格式
│   ├── run-ledger-format.md
│   └── context-format.md
├── rules/                       # 项目规则
├── taxonomy/                    # 分类体系
└── 索引.md
```

**原则：** `references/methodology/` 是唯一权威来源。各 skill 的 `references/` 目录通过 symlink 引用权威副本。仅在 skill 确有定制需求（如短篇专用质量检查清单）时才保留独立副本。

## Agent 体系

7 个 Agent，三级模型分配，由 skill 按需 spawn：

| 层级 | Agent | 模型 | 职责 | 调用者 |
|------|-------|------|------|--------|
| 架构 | story-architect | Opus→Sonnet | 架构、大纲、钩子/反转设计 | story-long-write, story-review |
| 创作 | narrative-writer | Sonnet→Haiku | 正文起草、去AI味、格式合规 | story-long-write, story-short-write |
| 创作 | character-designer | Sonnet→Haiku | 角色设计、对话创作 | story-long-write, story-short-write |
| 创作 | deconstruction-agent | Sonnet→Haiku | 拆文分析、章节摘要提取 | story-long-analyze |
| 检查 | reviewer | Haiku | 事实冲突扫描、S1-S4 分级 | story-review |
| 检查 | story-researcher | Haiku | 项目只读查询 + 外部资料搜索 | 按需 |

Agent 由 `story-setup` 部署到 `.claude/agents/`，skill 使用前先检查 agent 文件是否存在，缺失时自动降级为主线程执行。

## FAQ

### 不知道用什么命令怎么办？

直接用 `/write-novel:story` + 自然语言描述意图，路由会自动分发。例如：`/write-novel:story` + "我想写一本修仙小说"。

### 长篇和短篇怎么选？

- **长篇**（>2 万字）：适合起点/番茄/晋江连载，需要世界观搭建、多线叙事、伏笔管理
- **短篇**（8000-20000 字）：适合知乎盐言/黑岩/点众，靠单次情绪体验和反转驱动

不确定时，先想好目标平台，平台决定了篇幅。

### 拆文必须跑完吗？

长篇拆文 Stage 1（黄金三章）后会自动停靠，你可以选择"就到这里"。但日更写作前需要 `文风.md`（Stage 6 产出），缺失会被 fail-fast 拦截。建议至少跑完一本对标书的 Stage 6。

### 字数不达标怎么办？

阶段写作流程内置字数验证（Python 字符统计），不达标会自动回到细纲补充子事件。禁止跳过未达标章节。

### 如何恢复中断的写作？

读取 `追踪/run-ledger.md` 找到最后一条记录，自动诊断恢复点。Compact 恢复后先读 `追踪/上下文.md` 重建状态。

### 已有项目想迁移进来？

使用 `/write-novel:story-import`，支持单文件/多文件/目录导入，自动分析并重建标准项目结构。

### 想写多本书怎么管理？

项目支持多书并存。`/write-novel:story` + "切书" 列出所有书，选择即可切换。`.active-book` 文件记录当前活跃书。
