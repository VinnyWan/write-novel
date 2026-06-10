## Context

本项目处于"已有数据模型和 Python 工具，缺少 AI 原生 skill 编排层"的状态。现有资产包括：

- **模板体系**：`人物卡片模板.md`、`分卷大纲模板.md`、`分卷与单章细纲模板.md`、`世界设定模板.md`、`伏笔与线索回收池.md`、`全局写作状态.md`——全部使用中文文件名和 Frontmatter 键名
- **Python 脚本**：`scripts/` 目录下有 prompt 组装、伏笔追踪、状态更新、双语链解析等工具
- **参考项目 A**（`webnovel-writer`）：成熟的 Python CLI，完整的 docs/architecture 文档
- **参考项目 B**（`oh-story-claudecode`）：成熟的 Claude Code skill 组（12 个 skill），完整的写作方法论参考文件（题材目录、写作公式、禁用词表、审查 schema 等）

设计目标：用 Claude Code 的 skill/agent/hook 机制替代 Python CLI 的编排角色，让 AI 直接以文件系统为"内存"，作者在任何编辑器打开项目文件即可理解全貌。

## Goals / Non-Goals

**Goals:**
- 建立 6 个 Claude Code skill，覆盖网文写作全链路（路由→写作→去味→审查→部署→封面）
- 建立 5 个 Agent：2 个常驻（write-novel-explorer、write-novel-researcher）+ 3 个质量管道 Agent（write-novel-deslop-agent、write-novel-senior-editor、write-novel-picky-reader）
- 全中文路径生态系统：目录/文件/Frontmatter 键名 100% 中文
- 三项护城河功能（双语链接、伏笔追踪、全局状态中枢）以 Claude Code 原生方式实现
- 从 oh-story-claudecode 继承写作方法论参考文件，适配中文路径约定
- Python 脚本保留为 fallback，skill 优先

**Non-Goals:**
- 不重写 Python 脚本；保留但不作为主工作流
- 不实现 Web UI；纯 Claude Code CLI 交互
- 不处理封面图片生成（`write-novel-cover` 为轻量占位 skill）
- 不处理发布/部署到网文平台（那是 gstack 的职责）
- 不修改 oh-story-claudecode 原项目

## Decisions

### 1. Skill 架构：Router Pattern

```
write-novel (路由入口)
├── write-novel-long-write (长篇写作主流程)
│   ├── Phase 1: 选题确认
│   ├── Phase 2: 设定搭建
│   ├── Phase 3: 大纲细纲
│   ├── Phase 4: 正文写作
│   │   └── [write-novel-explorer] 按需加载上下文
│   └── Phase 5: 续航闭环
│       ├── 章节存档 / 摘要生成 / 状态更新 / 伏笔追踪
│       └── [质量管道，可选触发]
│           ├── ① 4 Review Agents（并行审查）→ 综合裁决
│           ├── ② write-novel-deslop-agent（去 AI 味）
│           ├── ③ write-novel-senior-editor（资深编辑审稿）
│           └── ④ write-novel-picky-reader（挑剔读者体验）
├── write-novel-deslop (去 AI 味，独立 skill)
├── write-novel-review (多视角审查 skill，编排质量管道)
├── write-novel-setup (环境部署)
└── write-novel-cover (封面生成，轻量占位)
```

**为什么选 Router Pattern 而非 Monolith Skill**：oh-story-claudecode 已验证此模式。路由 skill 保持简洁（~60 行路由表），子 skill 各自独立维护。用户可以说模糊指令（"写网文"）由路由分发，也可以直接调用子 skill（"续写"）跳过路由。

### 2. 数据模型：全中文 Markdown + YAML Frontmatter

决策：所有结构化数据以 YAML Frontmatter 嵌在 `.md` 文件头部，正文区域为人类可读的 Markdown。

**为什么不继续用独立 YAML/JSON 文件**：
- Markdown 文件可在任何编辑器打开即读
- Frontmatter 既可被脚本解析（结构化），也可被人直接阅读修改
- 单一文件 = 单一真相来源，消除数据同步问题
- Claude Code 的 Read 工具直接读取 .md 文件，无需额外序列化

**中文 Frontmatter 键名约定**：

| 文件 | 核心 Frontmatter 键 |
|------|-------------------|
| `全局写作状态.md` | `当前分卷`, `当前章节`, `已完成章数`, `总目标字数`, `已完成字数`, `主角姓名`, `主角当前境界`, `主角当前位置` |
| `人物卡片.md` | `姓名`, `性别`, `年龄`, `当前境界`, `功法`, `长线剧情目标`, `性格弱点`, `关联角色`, `当前状态`, `首次出场章节` |
| `分卷大纲.md` | `卷序号`, `卷标题`, `计划章数`, `已完成章数`, `分卷完成度百分比`, `分卷状态` |
| `单章细纲.md` | `所属分卷`, `章节序号`, `本章核心冲突`, `出场角色`, `埋下伏笔`, `期待感钩子`, `字数预期`, `关联伏笔ID` |
| `伏笔与线索回收池.md` | `总伏笔数`, `已回收数`, `发展中数`, `逾期未回收数`, `最后更新时间` |

### 3. 写作状态机：文件系统即数据库

不再维护内存状态或 JSON 状态文件。所有状态通过 Markdown 文件的 Frontmatter 字段表达：

**进度追踪**：`全局写作状态.md` 的 `当前分卷` + `当前章节` + `已完成章数` + `已完成字数`
**伏笔状态机**：`伏笔与线索回收池.md` 的 Markdown 表格，状态列三态：🟡已埋 → 🟠发展中 → 🟢已回收
**双语链接解析**：正则 `\[\[(.+?)\]\]` 匹配 → Read 对应文件 → 注入当前上下文
**用户保护区**：`<!-- USER_AREA_START -->` ... `<!-- USER_AREA_END -->` 之间内容永不被 AI 修改

### 4. Agent 设计：最小化上下文加载 + 质量管道

#### 4.1 常驻 Agent（2 个）

**write-novel-explorer**：只读 Agent，接收"查询类型 + 参数"（如"角色:林动"、"伏笔:所有逾期"、"进度:当前"），Read 对应文件，返回精确信息。绝不做写操作。

**write-novel-researcher**：外部搜索 Agent，调用 WebSearch 查找资料（如"筑基期修炼体系参考"、"古代官制等级"）。只返回搜索结果摘要。

**设计原则**：写每章时只加载"不知道就会写错"的信息——涉及角色的状态、待回收的伏笔、相关设定片段。其余留在文件系统里，由 Agent 按需读取。

#### 4.2 质量管道 Agent（3 个，串行执行）

审查完成后的深度加工流水线，串行触发，上一轮输出作为下一轮输入：

```
4 Review Agents (并行审查) → 综合裁决报告
         ↓
[write-novel-deslop-agent]   去 AI 味：逐句扫描，改写模板化表达
         ↓
[write-novel-senior-editor]  资深编辑：商业向审稿，节奏/爽点/钩子全检
         ↓
[write-novel-picky-reader]   挑剔读者：真实读者体验，代入感/弃书风险评估
```

**write-novel-deslop-agent**（去 AI 味）：接收审查报告 + 正文，逐句扫描并改写 AI 痕迹。使用 `references/banned-words.md` 和 `references/anti-ai-writing.md` 作为规则源。不仅标记问题，而是直接输出改写后的清洁文本。约束：不改变剧情内容、不增删关键信息、保留作者风格。

**write-novel-senior-editor**（资深编辑）：以终点线精修编辑的身份审核清洁后的文本。关注维度：商业吸引力（开篇钩子是否够强）、节奏控制（有无拖沓/过快的段落）、爽点密度（每 3000 字至少一个情绪释放点）、人物辨识度（角色对话是否能区分）。输出编辑审稿意见 + 具体修改建议。

**write-novel-picky-reader**（挑剔读者）：模拟真实挑剔网文读者的阅读体验。关注维度：第一句话能不能抓住人、前三段有没有让我想继续读、有没有让我出戏的 bug、情绪有没有打到我。以读者视角写一段"读后真实感受"（不讲术语，只讲感觉），指出哪里想弃书、哪里爽到了。

### 5. 参考文件继承策略

从 oh-story-claudecode 的 `skills/story-long-write/references/` 继承以下类别：

- **题材方法论**：`genre-catalog.md`、`genre-writing-formulas.md`、`genre-core-mechanics.md`
- **写作技巧**：`hooks-chapter.md`、`hooks-paragraph.md`、`hooks-suspense.md`、`emotional-methods.md`、`emotional-arc-design.md`、`dialogue-mastery.md`
- **人物设计**：`character-design-methods.md`、`character-relations.md`
- **质量管控**：`banned-words.md`、`anti-ai-writing.md`、`format-and-structure.md`
- **商业意识**：`commercial-core-methods.md`
- **输出规范**：`artifact-protocols.md`

每个 skill 的 `references/` 目录只保留该 skill 实际需要的参考文件，避免加载无关文件。

### 6. Python 脚本的角色：Fallback

现有 Python 脚本保留在 `scripts/`，但默认不参与主工作流。仅在以下场景使用：
- 需要精确字数统计时（`chapter_summarizer.py`）
- 需要 NFC/NFD Unicode 标准化时（`encoding_utils.py`）
- 作者手动调用 `python scripts/main.py status` 查看统计

主工作流中的 prompt 组装、状态更新、伏笔追踪全部由 Claude Code skill 通过文件读写完成。

## Risks / Trade-offs

- **[上下文窗口膨胀]** → 缓解：Agent 按需加载 + Wikilink 只解析当前章节中实际出现的引用
- **[Markdown 文件并发写冲突]** → 缓解：Claude Code 单会话单线程操作，不存在并发；跨会话通过文件系统锁自然串行
- **[全中文路径在终端/脚本中的兼容性]** → 缓解：Python 脚本已有 NFC/NFD 兼容和中文路径安全处理，所有路径使用正斜杠
- **[oh-story-claudecode 参考文件版本漂移]** → 缓解：初始复制后标记版本，后续手动同步
- **[大规模项目（200万字、数百章）文件数量爆炸]** → 缓解：分卷子目录（`分卷大纲/第1卷/`）、章节摘要自动归档（`历史章节摘要/`），单目录文件数控制在 200 以内
