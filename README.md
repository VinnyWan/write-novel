# write-novel

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.3.2-brightgreen.svg)](write-novel/.claude-plugin/plugin.json)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Compatible-purple.svg)](https://claude.ai/claude-code)
[![Marketplace](https://img.shields.io/badge/Claude%20Code-Marketplace-black.svg)](.claude-plugin/marketplace.json)

AI 辅助中文长篇网络小说创作插件。从扫榜、拆文、大纲到正文日更，覆盖超长篇网文创作全流程。内置 13 个 Skills、8 个 Agents、9 个 Hook 条目（覆盖 5 类事件），纯 Markdown 驱动，所有状态文件均可直接阅读编辑。

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
/write-novel:write-novel-setup       # 1. 部署项目基础设施（首次必执行）
/write-novel:write-novel-scan        # 2. 扫榜选方向
/write-novel:write-novel-analyze     # 3. 拆解对标书
/write-novel:write-novel-long-write  # 4. 开书写正文
/write-novel:write-novel-review      # 5. 审查已写章节
/write-novel:write-novel-deslop      # 6. 去AI味
```

也可以直接说「我想写小说」，`write-novel` 路由 skill 会自动分发到对应子 skill。

**完整流水线**：`扫榜 → 拆文 → 写作 → 审查 → 去AI味 → 封面`。详细流程见 [USAGE.md](USAGE.md)。

## Skill 体系（13 个）

| Skill | 使用方式 | 功能 |
|-------|---------|------|
| `write-novel` | `/write-novel:write-novel` | 路由入口，按意图自动分发 |
| `write-novel-setup` | `/write-novel:write-novel-setup` | 环境部署 + 模板安装 |
| `write-novel-scan` | `/write-novel:write-novel-scan` | 多平台扫榜 + 选题决策（长/短篇统一） |
| `write-novel-analyze` | `/write-novel:write-novel-analyze` | 深度拆文分析（长/短篇统一） |
| `write-novel-long-write` | `/write-novel:write-novel-long-write` | 长篇写作：开书 → 大纲 → 正文 → 日更 |
| `write-novel-short-write` | `/write-novel:write-novel-short-write` | 短篇写作 |
| `write-novel-import` | `/write-novel:write-novel-import` | 逆向导入已有小说 |
| `write-novel-deslop` | `/write-novel:write-novel-deslop` | 去 AI 味：六关检测 + 3-pass 润色 |
| `write-novel-review` | `/write-novel:write-novel-review` | 多视角对抗式审查 |
| `write-novel-cover` | `/write-novel:write-novel-cover` | 封面生成 |
| `write-novel-query` | `/write-novel:write-novel-query` | 角色/伏笔/设定/进度查询 + 数据面板 |
| `write-novel-doctor` | `/write-novel:write-novel-doctor` | 项目诊断 + 模式学习 |
| `browser-cdp` | `/write-novel:browser-cdp` | 浏览器操控，CDP 协议复用登录态采集数据 |

> 另保留 4 个向后兼容别名 skill（`write-novel-long-scan`、`write-novel-short-scan`、`write-novel-long-analyze`、`write-novel-short-analyze`），已分别合并至 `write-novel-scan` / `write-novel-analyze`，不计入规范 13 个。

## Agent 体系（8 个）

| 层级 | Agent | 职责 |
|------|-------|------|
| 架构级 | `write-novel-story-architect` | 故事架构、大纲结构、钩子/反转设计 |
| 创作级 | `write-novel-narrative-writer` | 正文起草、去 AI 味、格式合规 |
| 创作级 | `write-novel-character-designer` | 角色设计、语言风格、对话创作 |
| 创作级 | `write-novel-deconstruction-agent` | 拆文分析、章节摘要提取（含原 chapter-extractor 并行拆文） |
| 检查级 | `write-novel-reviewer` | 多维主观审查（结构/角色/文字/平台适配） |
| 检查级 | `write-novel-consistency-checker` | 客观事实冲突扫描（时间线/战力/地点/伏笔） |
| 检查级 | `write-novel-story-researcher` | 外部资料搜索 + 多源交叉验证 |
| 查询级 | `write-novel-story-explorer` | 项目内只读查询（角色/伏笔/进度） |

## Hooks（自动化守护）

按 `hooks/hooks.json` 实际配置，覆盖 5 类事件、9 个 hook 条目：

| 事件 | 触发时机 | 挂载脚本 | 功能 |
|------|---------|---------|------|
| SessionStart | 会话启动 | `session_start.py` / `session_start.sh` / `detect_story_gaps.sh` | 显示大纲缓冲/伏笔状态/上次操作 + 设定/大纲/伏笔缺口检测 |
| SessionEnd | 会话结束 | `session_end.sh` | 保存会话状态 |
| PreCompact | Compact 前 | `pre_compact.sh` | 保存写作状态到追踪文件 |
| PostCompact | Compact 后 | `post_compact.sh` | 恢复上下文状态 |
| PreToolUse | 写操作/Bash 前 | `guard_runtime_write.py` / `guard-outline-before-prose.sh` | 运行时写作守护 + 无对应细纲则阻断正文写入 |

> `hooks/validate_story_commit.sh` 为 Git 提交校验脚本（YAML frontmatter 必填字段检查），由 Git pre-commit 调用，不在 Claude Code `hooks.json` 条目内。

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
    ├── skills/                       # 13 个规范 skill + 4 个兼容别名（SKILL.md）
    ├── agents/                       # 8 个 agent 定义
    ├── hooks/                        # hooks.json + 脚本
    ├── references/                   # 方法论与参考数据
    ├── templates/                    # 37 题材模板 + 输出模板
    ├── scripts/                      # 静态检查链 + 行为 eval 运行器（发版与 CI 守护）
    ├── dashboard/                    # Web 可视化面板（前端依赖不入库，首次运行需 cd dashboard/frontend && npm install && npm run build）
    └── evals/                        # 行为评估契约 + fixtures
```

### 用户写作项目

安装插件后，`write-novel-setup` 会在你的小说目录下创建：

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

- [USAGE.md](USAGE.md) — 完整使用文档（流水线、场景、FAQ、开发与质量检查）
- [CHANGELOG.md](CHANGELOG.md) — 版本更新日志

## 开发与 CI

插件结构与行为契约由一组静态检查脚本守护，push 与 PR 时由 `.github/workflows/plugin-check.yml` 自动运行（静态检查链 + 版本一致性 + 行为 eval），本地可复现、无需 secrets。脚本与 eval 契约说明详见 [USAGE.md「开发与质量检查」](USAGE.md#开发与质量检查)。

## 许可

MIT · [VinnyWan](https://github.com/VinnyWan)
