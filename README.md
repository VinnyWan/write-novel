# write-novel

> 200万字长线剧情，尽在本地全中文 Markdown 卡片——每一笔设定、每一条伏线，都受你掌控。

AI 辅助长篇小说创作工具。核心理念：**Markdown-First**，彻底抛弃 JSON/YAML/数据库，所有数据以全中文 Markdown 文件存储。

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

### 4. 写大纲

在 `分卷大纲/` 下创建分卷大纲和每章细纲：

- `分卷大纲/第1卷_大纲.md` — 分卷主线与章节列表
- `分卷大纲/第1卷_细纲_第1章.md` — 单章硬性剧本任务

### 5. 检索写作上下文

```bash
# 关键词检索——自动找到相关角色/设定/伏笔/章节
python scripts/main.py search 打脸 --project ./我的小说

# 基于章节细纲自动检索（用于写前准备）
python scripts/main.py search --chapter 5 --volume 1 --project ./我的小说
```

### 6. 写前预检与写门校验

```bash
# 写前预检：细纲是否就绪、索引是否最新
python scripts/main.py preflight --chapter 5 --volume 1 --project ./我的小说

# 三段写门校验（gate-1 写前 / gate-2 提交前 / gate-3 提交后）
python scripts/main.py write-gate --stage gate-1 --chapter 5 --project ./我的小说
```

### 7. 项目健康诊断与状态

```bash
# 全面诊断：文件结构、Wikilink、伏笔逾期、索引状态
python scripts/main.py doctor --project ./我的小说

# 速览进度
python scripts/main.py status --project ./我的小说
```

### 8. 重建派生数据与看板

```bash
# 从 Markdown 重建所有 .write-novel/ 派生数据
python scripts/main.py project --project ./我的小说

# 生成只读 HTML 面板
python scripts/main.py dashboard --project ./我的小说
```

## 项目目录结构

```
项目根目录/
├── README.md
├── 全局写作状态.md          # 宏观注意力控制中枢（含系统提示词、高压线）
│
├── skills/                   # Claude Code skill 定义
│   ├── write-novel-setup/    # 环境部署 + 题材模板选择
│   ├── write-novel-review/   # 6 维度审查（3 blocking + 3 warning）
│   ├── write-novel-deslop/   # 去 AI 味
│   └── write-novel-cover/    # 封面生成
│
├── agents/                   # Agent 定义
│   ├── write-novel-explorer.md
│   ├── write-novel-researcher.md
│   ├── write-novel-deslop-agent.md
│   ├── write-novel-senior-editor.md
│   └── write-novel-picky-reader.md
│
├── 题材模板/                 # 所选题材的写作框架参考
│
├── 世界设定/                 # 世界观 & 力量体系
│   └── 世界观.md
│
├── 人物/                     # 角色卡片（Wikilink 双向链接）
│   ├── 林动.md
│   └── 沈清雪.md
│
├── 分卷大纲/                 # 分卷 & 单章细纲
│   ├── 第1卷_大纲.md
│   └── 第1卷_细纲_第1章.md
│
├── 章节草稿/                 # 已生成的章节正文
│   └── 第1章_序章.md
│
├── 章节提交记录/             # 每章提交时的新增设定记录
│
├── 历史章节摘要/             # 每章 ~200 字摘要
│
├── 伏笔与线索回收池.md       # 伏笔生命周期追踪（🟡已埋 → 🟠发展中 → 🟢已回收）
│
└── .write-novel/              # 派生数据（搜索索引/状态/伏笔状态 JSON，可重建）
```

## 核心文件模板

### 人物卡片

```yaml
---
姓名: 林动
性别: 男
年龄: 18
当前境界: 筑基期
功法: 九转玄功
长线剧情目标: 成为最强修仙者
性格弱点: 过于重情义
关联角色:
  - [[人物/沈清雪]]
  - [[人物/萧炎]]
---
```

### 分卷与单章细纲

```yaml
---
所属分卷: 1
章节序号: 5
本章核心冲突: 入门考核遇袭
出场角色:
  - 林动
  - 沈清雪
埋下伏笔:
  - F005
期待感钩子: 黑袍人的真实身份
字数预期: 3000
关联伏笔ID:
  - F001
---
```

### 伏笔回收池

使用 Markdown 表格 + 三态标记追踪每条伏笔的完整生命周期：

```
🟡已埋 → 🟠发展中 → 🟢已回收
```

## 核心能力

### 1. Markdown 事实源 + 派生索引

所有写作数据以 `.md` 文件存储，人类和 AI 均可直接阅读编辑。`python scripts/main.py project` 一键从 Markdown 重建 `.write-novel/` 下的搜索索引和状态快照。Markdown 是唯一真相源，JSON 只是可再生缓存。

### 2. BM25 上下文检索

写新章节前，`search` 命令自动检索相关角色、设定、伏笔、历史章节，注入写作上下文。中文分词基于 jieba，纯本地运行，无需外部 API。

### 3. 三段写门校验

```
gate-1（写前）→ gate-2（提交前）→ gate-3（提交后）
```

每道门校验必需的 Markdown 文件（细纲/草稿/审查结论/提交记录），不通过则阻断流程。

### 4. 伏笔生命周期追踪

`伏笔与线索回收池.md` 追踪每条伏笔的完整状态转换：
- 🟡已埋 → 🟠发展中 → 🟢已回收
- `doctor` 命令自动检测逾期未回收的伏笔

### 5. 六维度章节审查

审查覆盖 6 个维度：事实一致性、角色 OOC、伏笔合规（Blocking）+ 节奏感、追读力、AI 味（Warning）。Blocking 全通过才能标记 `审查通过: true`。

### 6. 题材模板库

支持 6 大题材（修仙/系统流/都市异能/种田基建/规则怪谈/宫斗宅斗），初始化时按选题自动注入对应写作框架。

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
| `python scripts/main.py dashboard --project ./项目` | 生成只读 HTML 面板 |
| `python scripts/main.py status --project ./项目` | 查看项目进度与状态 |

## 技术栈

- **语言**：Python 3.10+
- **依赖**：PyYAML
- **存储**：纯 Markdown 文件（YAML Frontmatter）
- **编码**：NFC/NFD 自动兼容，中文路径安全

## 设计原则

1. **Markdown-First**：所有数据以 `.md` 文件存储，人类和 AI 均可直接阅读编辑
2. **全中文路径**：目录名、文件名、Frontmatter 键名 100% 使用中文
3. **状态透明**：项目状态在任何编辑器中打开文件即可查看，无需特殊工具
4. **作者控制**：你随时可以手动编辑任何文件；脚本只修改结构化字段
5. **渐进增强**：不强行替代你现有工作流；从一个大纲文件开始即可
