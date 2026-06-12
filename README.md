# write-novel

> 200万字长线剧情，尽在本地全中文 Markdown 卡片——每一笔设定、每一条伏线，都受你掌控。

AI 辅助长篇小说创作工具。核心理念：**Markdown-First**，彻底抛弃 JSON/YAML/数据库，所有数据以全中文 Markdown 文件存储。

**当前版本：v0.2.0** (2026-06-12) · [更新日志](CHANGELOG.md)

## 快速开始

### 1. 安装依赖

```bash
pip install -r scripts/requirements.txt
```

### 2. 初始化项目

```bash
python scripts/main.py init --project ./我的小说
```

这会在 `./我的小说` 下创建完整的项目目录树和模板文件。

### 3. 编辑你的设定

打开并编辑以下文件：

- `全局写作状态.md` — 填入主角信息、写作风格、高压线禁用词
- `世界设定/世界观.md` — 设计世界观和力量体系
- `人物/人物卡片模板.md` — 创建角色（支持 `[[人物/角色名]]` 双向链接）

### 4. 规划卷纲

调用 `/write-novel-plan` 执行10步规划流程：加载数据 → 补齐设定基线 → 确认卷范围 → 节拍表 → 时间线 → 卷纲骨架 → 批量章纲 → 回写设定 → 验证 → 更新状态。

### 5. 写正文

调用 `/write-novel-long-write`，自动加载相关角色/设定/伏笔上下文，按细纲写正文。

### 6. 审查与质量管道

调用 `/write-novel-review`，6维度审查（3 Blocking + 3 Warning）+ Phase 2 质量管道串行加工（去AI味 → 资深编辑 → 挑剔读者）。

---

## Skill 体系（15 Skills）

| Skill | 触发 | 功能 |
|-------|------|------|
| `write-novel` | `/write-novel` | 路由入口，按意图自动分发到子 skill |
| `write-novel-setup` | `/write-novel-setup` | 环境部署 + 38题材模板选择 |
| `write-novel-plan` | `/write-novel-plan` | 10步卷纲规划（节拍表/时间线/CBN-CPNs-CEN章纲） |
| `write-novel-long-write` | `/write-novel-long-write` | 5 Phase 长篇写作主流程 |
| `write-novel-short-write` | `/write-novel-short-write` | 短篇写作（情绪设计/反转构思/精修出稿） |
| `write-novel-query` | `/write-novel-query` | 查角色/伏笔/进度/实体关系 |
| `write-novel-review` | `/write-novel-review` | 6维审查 + 多Agent审稿 + 平台评分标准（起点/番茄/知乎） |
| `write-novel-deslop` | `/write-novel-deslop` | 去 AI 味（三遍去AI法 + 禁用词表） |
| `write-novel-analyze` | `/write-novel-analyze` | 6阶段深度拆文管道（概要→黄金三章→逐章摘要→聚合→设定→文风） |
| `write-novel-short-analyze` | `/write-novel-short-analyze` | 短篇拆文（故事核/结构/情感线/反转/写作手法/共鸣） |
| `write-novel-scan` | `/write-novel-scan` | 5平台扫榜（起点/番茄/晋江/七猫/刺猬猫） |
| `write-novel-import` | `/write-novel-import` | 逆向导入已有小说（逐章提取事件/角色/设定/伏笔） |
| `write-novel-cover` | `/write-novel-cover` | 封面生成 |
| `webnovel-learn` | `/webnovel-learn` | 项目经验记忆沉淀 |
| `webnovel-dashboard` | `/webnovel-dashboard` | 启动只读可视化面板 |

## Agent 体系（15 Agents，三级分工）

| 层级 | 模型 | Agent | 职责 |
|------|------|-------|------|
| 架构级 | Opus | `story-architect` | 故事架构、大纲结构、钩子/反转设计、情绪弧线 |
| 架构级 | Opus | `context-agent` | 写前上下文策略组装，创作任务书生成 |
| 创作级 | Sonnet | `narrative-writer` | 正文起草、去AI味、格式合规 |
| 创作级 | Sonnet | `senior-editor` | 资深编辑审稿 |
| 创作级 | Sonnet | `character-designer` | 角色设计、语言风格、动机链、对话创作 |
| 创作级 | Sonnet | `data-agent` | 事实提取、投影驱动、state/index/summary 更新 |
| 检查级 | Haiku | `reviewer` | 六维一致性审查（爽点/一致性/节奏/OOC/连贯性/追读力） |
| 检查级 | Haiku | `picky-reader` | 挑剔读者体验 |
| 检查级 | Haiku | `chapter-extractor` | 批量提取章节情节点和角色 |
| 检查级 | Haiku | `explorer` | 项目内只读查询（角色/伏笔/设定/进度） |
| 检查级 | Haiku | `researcher` | 外部资料搜索，多源交叉验证 |
| 检查级 | Haiku | `deslop-agent` | 深度去 AI 味 |
| 检查级 | Haiku | `deconstruction-agent` | 拆文分析 |
| 检查级 | Haiku | `consistency-checker` | 事实冲突扫描、伏笔追踪、S1-S4 分级报告 |
| — | — | `查询协议与契约.md` | Agent 协作协议定义 |

## 项目目录结构

### 插件开发目录

```
write-novel/
├── CHANGELOG.md
├── LICENSE
├── README.md
├── CLAUDE.md
├── pytest.ini
├── sitecustomize.py
├── requirements.txt
├── docs/                         # 文档中心（本地保留，不提交 git）
│   ├── architecture/             # 架构设计文档
│   ├── guides/                   # 使用指南
│   ├── operations/               # 运维文档
│   └── superpowers/              # specs + plans
├── releases/                     # 发版笔记
└── write-novel/                  # 代码层
    ├── agents/                   # Agent 定义（15 agents，三级分工）
    ├── dashboard/                # FastAPI 实时看板 + 前端
    │   └── frontend/             # React 前端（dist + src）
    ├── evals/                    # 行为评估
    ├── hooks/                    # 自动化 hooks（7 个）
    ├── references/               # 共享引用数据
    │   ├── csv/                  # 8 个 CSV 技法数据库
    │   ├── shared/               # 共享参考文档
    │   ├── taxonomy/             # 题材分类体系
    │   ├── methodology/          # 写作方法论（27 文件）
    │   └── rules/                # 写作规范（4 文件）
    ├── scripts/                  # Python 脚本与 CLI
    ├── skills/                   # Skill 定义（31 skills，后续去重）
    └── templates/                # 题材模板（37 题材 + 输出模板）
```

### 用户写作项目目录（四维分离）

```
{书名}/
├── 全局写作状态.md               # 宏观注意力控制中枢
│
├── 设定/                         # 世界观 + 角色 + 势力 + 关系
│   ├── 世界观/                   # 背景、力量体系等
│   ├── 角色/                     # 每人一个文件（[[双向链接]]）
│   │   ├── 林动.md
│   │   └── 沈清雪.md
│   ├── 势力/                     # 每个势力/组织一个文件
│   ├── 关系.md                   # 角色关系映射
│   ├── 题材定位.md               # 题材核心梗 + 对标分析
│   └── 文风.md                   # 日更前读取，保持文风一致
│
├── 大纲/                         # 大纲 + 卷纲 + 细纲
│   ├── 大纲.md                   # 全书卷级结构
│   ├── 卷纲_第1卷.md             # 爽点节奏 + 情绪弧线 + 伏笔 + 反转
│   └── 细纲_第1章.md             # 事件 + 钩子 + 爽点 + 悬念
│
├── 正文/                         # 章节正文
│   └── 第1章_序章.md
│
├── 对标/                         # 从拆文库同步的结构化参考
│   └── {对标书名}/
│       ├── 文风.md
│       ├── 角色/
│       ├── 剧情/
│       └── 拆文报告.md
│
├── 追踪/                         # 连续性管理（分层追踪）
│   ├── 上下文.md                 # compact 恢复用上下文
│   ├── 伏笔.md                   # 伏笔埋设/回收状态表
│   ├── 时间线.md                 # 故事内时间线
│   └── 角色状态.md               # 角色当前状态快照
│
├── 审查报告/                     # 章节审查报告
├── 章节提交记录/                 # 每章提交时的新增设定记录
├── 历史章节摘要/                 # 每章 ~200 字摘要
├── 伏笔与线索回收池.md           # 伏笔生命周期追踪
│
└── .write-novel/                 # 派生数据（搜索索引/状态/伏笔状态 JSON，可重建）
```

## 核心能力

### 1. Markdown 事实源 + 派生索引

所有写作数据以 `.md` 文件存储，人类和 AI 均可直接阅读编辑。`python scripts/main.py project` 一键从 Markdown 重建 `.write-novel/` 下的搜索索引和状态快照。

### 2. BM25 上下文检索 + CSV 技法搜索

写新章节前，`search` 命令自动检索相关角色、设定、伏笔、历史章节，注入写作上下文。`reference_search.py` 支持从 8 个 CSV 技法数据库关键词检索写作技巧。

### 3. 三段写门校验

```
gate-1（写前）→ gate-2（提交前）→ gate-3（提交后）
```

每道门校验必需的 Markdown 文件，不通过则阻断流程。

### 4. 伏笔生命周期追踪

`伏笔与线索回收池.md` 追踪每条伏笔的完整状态转换：
- 🟡已埋 → 🟠发展中 → 🟢已回收
- `doctor` 命令自动检测逾期未回收的伏笔

### 5. 六维度章节审查 + 平台评分标准

审查覆盖 6 个维度：事实一致性、角色 OOC、伏笔合规（Blocking）+ 节奏感、追读力、AI 味（Warning）。支持起点/番茄/知乎三大平台的特定评分标准加载。

### 6. 深度拆文管道

6阶段拆解任意网文：概要提取 → 黄金三章 → 逐章摘要 → 聚合分析 → 设定+关系 → 文风。提取可复用的结构模式。

### 7. 多平台扫榜

支持起点/番茄/晋江/七猫/刺猬猫 5 大平台的排行榜扫描和趋势分析，辅助选题决策。

### 8. 38 题材模板库

覆盖修仙/系统流/都市异能/古言/末世/电竞/科幻/无限流/悬疑灵异/克苏鲁/规则怪谈等 38 大题材，初始化时按选题自动注入对应写作框架。

### 9. 实时写作看板

`python -m dashboard --project-root ./项目` 启动 FastAPI 实时看板，覆盖进度概览、角色状态、伏笔追踪、文件浏览、健康诊断 5 大板块。

## 命令行参考

| 命令 | 说明 |
|------|------|
| `python scripts/main.py init --project ./项目` | 初始化新项目（目录 + 模板文件） |
| `python scripts/main.py search 打脸 --project ./项目` | BM25 关键词检索上下文 |
| `python scripts/main.py search -c 5 -v 1 --project ./项目` | 基于章纲自动检索上下文 |
| `python scripts/main.py project --project ./项目` | 从 Markdown 重建所有 `.write-novel/` 派生数据 |
| `python scripts/main.py doctor --project ./项目` | 全面项目健康诊断 |
| `python scripts/main.py preflight -c 5 -v 1 --project ./项目` | 写前预检（细纲/索引就绪） |
| `python scripts/main.py write-gate -s gate-2 -c 5 --project ./项目` | 三段写门校验 |
| `python scripts/main.py dashboard --project ./项目` | 生成静态 HTML 面板 |
| `python -m dashboard --project-root ./项目` | 启动实时看板服务器（FastAPI） |
| `python scripts/main.py status --project ./项目` | 查看项目进度与状态 |

## 技术栈

- **语言**：Python 3.10+
- **依赖**：PyYAML, rank-bm25, jieba
- **存储**：纯 Markdown 文件（YAML Frontmatter）
- **编码**：NFC/NFD 自动兼容，中文路径安全

## 设计原则

1. **Markdown-First**：所有数据以 `.md` 文件存储，人类和 AI 均可直接阅读编辑
2. **全中文路径**：目录名、文件名、Frontmatter 键名 100% 使用中文
3. **状态透明**：项目状态在任何编辑器中打开文件即可查看，无需特殊工具
4. **作者控制**：你随时可以手动编辑任何文件；脚本只修改结构化字段
5. **渐进增强**：不强行替代你现有工作流；从一个大纲文件开始即可
