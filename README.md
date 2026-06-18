# write-novel

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.1.0-brightgreen.svg)](write-novel/.claude-plugin/plugin.json)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-purple.svg)](https://claude.ai/claude-code)
[![Marketplace](https://img.shields.io/badge/Claude%20Code-Marketplace-black.svg)](.claude-plugin/marketplace.json)

AI 辅助中文长篇网络小说创作插件。从扫榜、拆文、大纲到正文日更，覆盖超长篇网文创作全流程。内置 15 个 Skills、9 个 Agents、10 个 Hooks，纯 Markdown 驱动，所有状态文件均可直接阅读编辑。

## 安装

### 从自有市场安装（推荐）

```bash
# 添加自有市场
claude plugin marketplace add VinnyWan/write-novel --scope user

# 安装插件
claude plugin install write-novel@write-novel-marketplace --scope user
```

### 从社区市场安装

```bash
# 添加社区市场
claude plugin marketplace add anthropics/claude-plugins-community

# 安装插件
claude plugin install write-novel@claude-community
```

### 本地开发安装

```bash
git clone https://github.com/VinnyWan/write-novel.git
claude --plugin-dir ./write-novel
```

安装后运行 `/reload-plugins` 加载所有 skills。

## 快速开始

安装插件后，在 Claude Code 中：

```bash
/write-novel:story-setup       # 1. 部署项目基础设施（首次必执行）
/write-novel:story-long-scan   # 2. 扫榜选方向
/write-novel:story-long-analyze # 3. 拆解对标书
/write-novel:story-long-write  # 4. 开书写正文
/write-novel:story-review      # 5. 审查已写章节
/write-novel:story-deslop      # 6. 去AI味
```

也可以直接说「我想写小说」，story skill 会自动路由到对应子 skill。

**完整流水线**：`扫榜 → 拆文 → 写作 → 审查 → 去AI味 → 封面`。详细流程见 [USAGE.md](USAGE.md)。

## Skill 体系（14 个）

| Skill | 使用方式 | 功能 |
|-------|---------|------|
| `story` | `/write-novel:story` | 路由入口，按意图自动分发 |
| `story-setup` | `/write-novel:story-setup` | 环境部署 + 模板安装 |
| `story-long-scan` | `/write-novel:story-long-scan` | 多平台扫榜 + 选题决策 |
| `story-short-scan` | `/write-novel:story-short-scan` | 短篇选题扫描 |
| `story-long-analyze` | `/write-novel:story-long-analyze` | 6 阶段深度拆文 |
| `story-short-analyze` | `/write-novel:story-short-analyze` | 短篇拆文分析 |
| `story-long-write` | `/write-novel:story-long-write` | 长篇写作：开书 → 大纲 → 正文 → 日更 |
| `story-short-write` | `/write-novel:story-short-write` | 短篇写作 |
| `story-import` | `/write-novel:story-import` | 逆向导入已有小说 |
| `story-deslop` | `/write-novel:story-deslop` | 去 AI 味：六关检测 + 3-pass 润色 |
| `story-review` | `/write-novel:story-review` | 多视角对抗式审查 |
| `story-cover` | `/write-novel:story-cover` | 封面生成 |
| `story-query` | `/write-novel:story-query` | 角色/伏笔/设定/进度查询 |
| `story-doctor` | `/write-novel:story-doctor` | 项目诊断 + 模式学习 |
| `browser-cdp` | `/write-novel:browser-cdp` | 浏览器操控，CDP 协议复用登录态采集数据 |

## Agent 体系（6 个）

| 层级 | Agent | 职责 |
|------|-------|------|
| 架构级 | `story-architect` | 故事架构、大纲结构、钩子/反转设计 |
| 创作级 | `narrative-writer` | 正文起草、去 AI 味、格式合规 |
| 创作级 | `character-designer` | 角色设计、语言风格、对话创作 |
| 创作级 | `deconstruction-agent` | 拆文分析、章节摘要提取 |
| 检查级 | `reviewer` | 多维主观审查（结构/角色/文字/平台适配） |
| 检查级 | `consistency-checker` | 客观事实冲突扫描（时间线/战力/地点/伏笔） |
| 检查级 | `story-researcher` | 外部资料搜索 + 多源交叉验证 |
| 查询级 | `story-explorer` | 项目内只读查询（角色/伏笔/进度） |
| 提取级 | `chapter-extractor` | 章节摘要提取 + 情节点 + 角色提及（并行拆文） |

## Hooks（自动化守护）

| Hook | 触发时机 | 功能 |
|------|---------|------|
| SessionStart | 会话启动 | 显示大纲缓冲、伏笔状态、上次操作 |
| SessionEnd | 会话结束 | 保存会话状态 |
| PreCompact | Compact 前 | 保存写作状态到追踪文件 |
| PostCompact | Compact 后 | 恢复上下文状态 |
| PreToolUse | 写操作前 | 运行时写作守护校验 |
| PreCompact | Compact 前 | 保存写作状态到追踪文件 |
| PostCompact | Compact 后 | 恢复上下文状态 |
| guard-outline-before-prose | 正文写入前 | 阻断式检查：无对应细纲则拒绝写入 |
| detect-story-gaps | 会话启动 | 设定/大纲/伏笔缺口检测 |
| PreCommit | Git commit 前 | YAML frontmatter 必填字段检查 |

## 核心能力

### 故事系统（Contract → Commit → Projection）

三层 Markdown 契约链驱动写作：**Contract**（设定约束）→ **Commit**（正文落盘）→ **Projection**（派生追踪）。每章写作前经三阶段写门校验，防止设定吃书。

### 情绪驱动写作

7 种情绪类型（爽感释放 / 悬念紧张 / 虐心压抑 / 意外反转 / 温暖治愈 / 细思极恐 / 共鸣感动）× 每章情绪锚点设计 × 章尾 5 类钩子（危机 / 悬念 / 欲望 / 情绪 / 选择）。

### 追读力体系

钩子五分类法 × 分题材偏好参数，保障每章爽点密度和期待链不断裂。

### 多线叙事节奏

Quest（主线）/ Fire（支线）/ Constellation（伏笔）三线标注，硬约束：Fire 连续 ≤ 2 章、Constellation 连续 ≤ 1 章。

### 去 AI 味六关检测

A（禁词）→ B（句式）→ C（心理外化）→ D（节奏）→ E（对话）→ F（结尾），三级强度控制（轻量 / 标准 / 深度）。3-pass 方法论：去泛化 → 去书面化 → 回自然感。

### 断点续传

`追踪/run-ledger.md` 记录每次操作，中断后自动诊断恢复点并重建上下文。

### 情节框架操作手册

`references/methodology/plot-frameworks.md` — 决策路由表 + 23 个框架操作方法，涵盖玄幻、系统文、追妻、重生、悬疑等 10 种题材的框架选择和指令级操作指引。

### 爽点工程体系

`references/methodology/cool-points-guide.md` — 六种爽点执行模式（装逼打脸/扮猪吃虎/越级反杀/打脸权威/反派翻车/甜蜜超预期）+ 三段式结构（铺垫30%/兑现40%/微反转30%）+ 压扬比例控制 + 题材适配表。

### 日更续写工作流

`references/shared/workflow-daily.md` — 日更场景的完整操作流程：上下文快速加载（三层分层摘要，30章以上自动压缩）→ 串行批量写作（状态筛选/文风召回/标题预检/细纲阻断）→ 追踪文件更新 → 恢复中断指引。

## 项目结构

### 插件目录

```
write-novel/                          # 仓库根（市场根）
├── .claude-plugin/
│   └── marketplace.json              # 市场清单
├── README.md
├── CHANGELOG.md
├── LICENSE
├── USAGE.md
│
└── write-novel/                      # 插件根
    ├── .claude-plugin/
    │   └── plugin.json               # 插件清单
    ├── skills/                       # 14 个 skill（SKILL.md）
    ├── agents/                       # 6 个 agent 定义
    ├── hooks/                        # hooks.json + 脚本
    ├── references/                   # 方法论与参考数据
    ├── templates/                    # 37 题材模板 + 输出模板
    ├── scripts/                      # Python/JS 工具脚本
    ├── dashboard/                    # Web 可视化面板
    └── evals/                        # 行为评估
```

### 用户写作项目

安装插件后，`story-setup` 会在你的小说目录下创建：

```
{书名}/
├── 设定/
│   ├── MASTER_SETTING.md        # 全局设定契约
│   ├── 角色/{角色名}.md
│   └── 势力/{势力名}.md
├── 大纲/
│   ├── Volume-1.md              # 卷契约
│   └── Chapter-001.md           # 章契约
├── 正文/
│   └── Chapter-001.md           # 正文
├── 追踪/
│   ├── state.md                 # 写作状态
│   ├── characters.md            # 角色状态
│   ├── foreshadowing.md         # 伏笔状态
│   └── run-ledger.md            # 操作日志
├── 对标/{对标书名}/
└── 备份/
```

## 进一步阅读

- [USAGE.md](USAGE.md) — 完整使用文档（流水线、场景、FAQ）
- [CHANGELOG.md](CHANGELOG.md) — 版本更新日志

## 许可

MIT · [VinnyWan](https://github.com/VinnyWan)
