# write-novel

> AI 辅助长篇小说创作工具。核心理念：**Markdown-First** —— 所有数据以全中文 Markdown 文件存储。

**当前版本：v0.3.0** (2026-06-14) · [更新日志](CHANGELOG.md)

## 快速开始

```bash
# 在 Claude Code 中
/story-setup          # 部署项目基础设施
/story-long-scan      # 扫榜选方向
/story-long-analyze   # 拆解对标书
/story-long-write     # 开书写正文
/story-review         # 审查已写章节
/story-deslop         # 去AI味
```

旧触发词（`/write-novel-*`、`/webnovel-*`）作为别名保留，自动路由到对应新 skill。

## Skill 体系（15 Skills）

| Skill | 触发 | 功能 |
|-------|------|------|
| `story` | `/story` | 路由入口，按意图自动分发到子 skill |
| `story-setup` | `/story-setup` | 环境部署 + agent/hooks/rules 安装 |
| `story-long-scan` | `/story-long-scan` | 多平台扫榜 + 选题决策 |
| `story-short-scan` | `/story-short-scan` | 短篇选题扫描 |
| `story-long-analyze` | `/story-long-analyze` | 6阶段深度拆文管道 |
| `story-short-analyze` | `/story-short-analyze` | 短篇拆文分析 |
| `story-long-write` | `/story-long-write` | 长篇写作：开书→大纲→正文→日更 |
| `story-short-write` | `/story-short-write` | 短篇写作 |
| `story-import` | `/story-import` | 逆向导入已有小说 |
| `story-deslop` | `/story-deslop` | 去AI味：六关检测（A/B/C/D/E/F） |
| `story-review` | `/story-review` | 多视角对抗式审查（full/lean/solo） |
| `story-cover` | `/story-cover` | 封面生成 |
| `story-query` | `/story-query` | 角色/伏笔/设定/进度查询 |
| `story-doctor` | `/story-doctor` | 项目诊断 + 模式学习 |

## Agent 体系（6 Agents，三级模型分配）

| 层级 | 模型 | Agent | 职责 |
|------|------|-------|------|
| 架构级 | Opus→Sonnet | `story-architect` | 故事架构、大纲结构、钩子/反转设计 |
| 创作级 | Sonnet→Haiku | `narrative-writer` | 正文起草、去AI味、格式合规 |
| 创作级 | Sonnet→Haiku | `character-designer` | 角色设计、语言风格、对话创作 |
| 创作级 | Sonnet→Haiku | `deconstruction-agent` | 拆文分析、章节摘要提取 |
| 检查级 | Haiku | `reviewer` | 事实冲突扫描、一致性审查、S1-S4分级 |
| 检查级 | Haiku | `story-researcher` | 项目内只读查询 + 外部资料搜索 |

合并自旧版 15 个 agent：context-agent→story-architect、chapter-extractor→deconstruction-agent、consistency-checker→reviewer、data-agent+story-explorer→story-researcher。

## 项目目录结构

### 用户写作项目（Contract → Commit → Projection）

```
{书名}/
├── 设定/
│   ├── MASTER_SETTING.md       # 全局设定契约（YAML frontmatter）
│   ├── 角色/{角色名}.md
│   └── 势力/{势力名}.md
├── 大纲/
│   ├── Volume-1.md             # 卷契约（YAML frontmatter）
│   └── Chapter-001.md          # 章契约（CBN/CPNs/CEN）
├── 正文/
│   └── Chapter-001.md          # 正文 commit（YAML frontmatter）
├── 追踪/                       # 投影层
│   ├── state.md                # 当前写作状态
│   ├── progress.md             # 进度摘要
│   ├── characters.md           # 角色状态
│   ├── foreshadowing.md        # 伏笔状态
│   └── run-ledger.md           # 操作日志（断点续传）
├── 对标/{对标书名}/
└── 备份/
```

### 插件开发目录

```
write-novel/
├── README.md
├── CHANGELOG.md
├── write-novel/
│   ├── agents/                 # 6 个规范 Agent 定义
│   ├── dashboard/              # FastAPI + React 静态面板
│   ├── evals/                  # 行为评估模块
│   ├── hooks/                  # 自动化 hooks
│   ├── references/             # 方法论与 CSV 参考数据库
│   ├── scripts/                # Python 脚本与 CLI
│   ├── skills/                 # 15 个规范 Skill 定义
│   └── templates/              # 37 题材模板 + 输出模板
```

## 核心能力

### 故事系统（Contract → Commit → Projection）

三层 Markdown 契约链：**Contract**（设定约束）→ **Commit**（正文落盘）→ **Projection**（派生追踪）。每章写作前经三阶段写门校验：

```
Prewrite Gate（写前）→ Precommit Gate（提交前）→ Postcommit Gate（提交后）
```

### 追读力体系

钩子五分类法（危机/悬念/欲望/情绪/选择）× 分题材偏好参数，保障每章爽点密度和期待链不断裂。

### 多线叙事节奏

Quest（主线）/ Fire（支线）/ Constellation（伏笔）三线标注，硬约束：Fire 连续≤2章、Constellation 连续≤1章。

### 去AI味六关检测

A（禁词）→ B（句式）→ C（心理外化）→ D（节奏）→ E（对话）→ F（结尾），三级强度控制（轻量/标准/深度）。`deai_check.py` 自动化 A/B/D 关。

### 断点续传

`追踪/run-ledger.md` 记录每次操作，中断后自动诊断恢复点并重建上下文。

## 命令行参考

| 命令 | 说明 |
|------|------|
| `python scripts/main.py init --project ./项目` | 初始化新项目 |
| `python scripts/main.py search <关键词> --project ./项目` | BM25 关键词检索 |
| `python scripts/main.py project --project ./项目` | 从 Markdown 重建派生数据 |
| `python scripts/main.py doctor --project ./项目` | 项目健康诊断 |
| `python scripts/main.py preflight -c 5 -v 1 --project ./项目` | 写前预检 |
| `python scripts/main.py write-gate -s gate-2 -c 5 --project ./项目` | 写门校验 |
| `python scripts/main.py dashboard --project ./项目` | 生成静态 HTML 面板 |
| `python scripts/main.py status --project ./项目` | 查看项目进度 |
| `python scripts/deai_check.py <文件> --json` | 去AI味自动检测（A/B/D关） |

## 技术栈

- **语言**：Python 3.10+
- **依赖**：PyYAML, rank-bm25, jieba
- **存储**：纯 Markdown 文件（YAML Frontmatter）
- **编码**：NFC/NFD 自动兼容，中文路径安全

## 设计原则

1. **Markdown-First**：所有数据以 `.md` 文件存储，人类和 AI 均可直接阅读编辑
2. **Contract → Commit → Projection**：三层分离，契约驱动写作，投影从正文重建
3. **Skill > Script**：优先用 SKILL.md + references 规范驱动，脚本仅做确定性自动化
4. **状态透明**：项目状态在任何编辑器中打开文件即可查看，无需特殊工具
5. **作者控制**：你随时可以手动编辑任何文件；脚本只修改结构化字段
