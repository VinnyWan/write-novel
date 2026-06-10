## Why

现有的 `webnovel-writer`（Python CLI 管道）和 `oh-story-claudecode`（Claude Code skills）各自只解决了长篇网文创作链路中的一部分——前者提供了精良的 Markdown 数据模型和双语链/Prompt 组装/伏笔追踪等护城河功能，但缺乏 AI 原生编排层；后者提供了成熟的 skill 路由体系和写作方法论，但其内部数据模型仍耦合了 JSON 状态文件和英文目录名。本项目将两者优势融合，构建一套**纯 Markdown-First、全中文路径、Claude Code 原生**的长篇网文创作 skill 组，让 AI 直接以文件系统为"内存"，作者在任何编辑器中都能读懂项目状态的每一行。

## What Changes

- **新建 6 个 Claude Code skill**：`write-novel`（路由入口）、`write-novel-long-write`（长篇写作主流程）、`write-novel-deslop`（去 AI 味）、`write-novel-review`（多视角审查）、`write-novel-setup`（环境部署）、`write-novel-cover`（封面生成）
- **新建 5 个 Agent**：`write-novel-explorer`（只读查询代理，按需读取人物/设定/伏笔/进度文件）、`write-novel-researcher`（外部资料搜索代理）、`write-novel-deslop-agent`（深度去 AI 味，逐句改写修正）、`write-novel-senior-editor`（资深编辑，以最严苛标准审核文本质量）、`write-novel-picky-reader`（挑剔读者，从真实读者体验角度挑刺）
- **目录结构全中文化**：所有数据目录和文件名使用中文（`人物/`、`世界设定/`、`分卷大纲/`、`伏笔与线索回收池.md` 等），Frontmatter 键名同步使用中文
- **数据格式统一为 Markdown + YAML Frontmatter**：彻底清除独立 JSON/YAML 配置文件，结构化数据全部放入 `.md` 文件的 `---` 头部
- **写作工作流落地为 skill**：开书（Phase 1→2→3→4→5）、日更续写、大修/回炉三大场景，在 `write-novel-long-write` 中实现，并继承 oh-story-claudecode 的情绪驱动方法论和扫榜/拆文/对标体系
- **三项护城河功能从 Python 脚本迁移为 Claude Code 原生实现**：双语链按需加载（`[[人物/林动]]` → Agent 自动读取）、伏笔生命周期追踪（三态状态机，Markdown 表格驱动）、全局写作状态中枢（Frontmatter 自动更新 + 用户保护区）
- **配置部署 skill**（`write-novel-setup`）：一键部署 hooks/rules/agents/CLAUDE.md 到用户项目目录

## Capabilities

### New Capabilities

- `skill-router`: 网文工具箱路由入口 skill，根据用户意图自动分发到写作/拆文/扫榜/去 AI 味/封面/部署等子 skill
- `long-write-workflow`: 长篇写作主流程，覆盖开书（选题→设定→大纲→细纲→正文）、日更续写、大修/回炉三大场景
- `deslop`: 去 AI 味 skill，检测并清除文本中的 AI 写作痕迹
- `write-novel-review`: 多视角对抗式审查 skill，4 个 Agent 并行从结构/文风/连贯性/爽点角度审查文本
- `write-novel-setup`: 环境部署 skill，将 hooks/rules/agents/CLAUDE.md 部署到用户项目
- `markdown-state-machine`: Markdown 文件驱动的写作状态机，包含 Frontmatter 进度字段、伏笔三态追踪、双语链按需加载、用户保护区
- `chinese-path-ecosystem`: 全中文文件系统约定，目录/文件/Frontmatter 键名 100% 中文

### Modified Capabilities

<!-- 无现有 spec 需要修改，这是全新的能力集 -->

## Impact

- **新增文件**：项目根目录 `skills/` 下新建 6 个 skill 目录，每个包含 `SKILL.md` 和 `references/` 参考文件
- **新增 Agent**：项目根目录 `agents/write-novel-explorer.md`、`agents/write-novel-researcher.md`、`agents/write-novel-deslop-agent.md`、`agents/write-novel-senior-editor.md`、`agents/write-novel-picky-reader.md`
- **项目数据模板**：完善已有的 Markdown 模板（`人物卡片模板.md`、`分卷大纲模板.md` 等）
- **参考项目依赖**：从 `oh-story-claudecode` 继承参考文件（写作方法论、题材目录、禁用词表等），从 `webnovel-writer` 继承数据模型设计
- **Python 脚本**：现有 `scripts/` 中的 Python 工具保留为 fallback（用于需要精确文本处理的场景），但主工作流由 Claude Code skill 驱动
