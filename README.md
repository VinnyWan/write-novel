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
- `世界设定/世界设定模板.md` — 设计世界观和力量体系
- `人物/人物卡片模板.md` — 创建角色（支持 `[[人物/角色名]]` 双向链接）

### 4. 写大纲

在 `分卷大纲/` 下创建分卷大纲和每章细纲：

- `分卷大纲/第1卷_大纲.md` — 分卷主线与章节列表
- `分卷大纲/第1卷_细纲_第1章.md` — 单章硬性剧本任务

### 5. 组装 Prompt

```bash
python scripts/main.py assemble --chapter 1 --volume 1
```

生成的 `当前Prompt.xml` 可直接发送给大模型。

### 6. 执行续航闭环

```bash
# 模型生成章节后，将正文保存为文件
python scripts/main.py continue --chapter-body-file ./第1章正文.txt --chapter 1 --volume 1 --title "序章"
```

续航闭环自动完成：章节存档 → 摘要生成 → 状态更新 → 伏笔追踪。

### 7. 查看状态

```bash
python scripts/main.py status
```

## 项目目录结构

```
项目根目录/
├── README.md
├── 全局写作状态.md          # 宏观注意力控制中枢（含系统提示词、高压线）
├── 当前Prompt.xml            # 最新一次组装的 Prompt（自动生成）
│
├── skills/                   # Claude Code skill 定义（6 个）
│   ├── write-novel/          # 路由入口
│   ├── write-novel-long-write/  # 长篇写作主流程
│   ├── write-novel-deslop/   # 去 AI 味
│   ├── write-novel-review/   # 多视角审查 + 质量管道
│   ├── write-novel-setup/    # 环境部署
│   └── write-novel-cover/    # 封面生成
│
├── agents/                   # Agent 定义（5 个）
│   ├── write-novel-explorer.md
│   ├── write-novel-researcher.md
│   ├── write-novel-deslop-agent.md
│   ├── write-novel-senior-editor.md
│   └── write-novel-picky-reader.md
│
├── 全局设定/                 # 跨卷全局设定（预留）
│
├── 世界设定/                 # 世界观 & 力量体系
│   └── 世界观.md
│
├── 人物/                     # 角色卡片（双向链接目标）
│   ├── 林动.md
│   └── 沈清雪.md
│
├── 分卷大纲/                 # 分卷 & 单章细纲
│   ├── 分卷大纲模板.md
│   ├── 第1卷_大纲.md
│   └── 第1卷_细纲_第1章.md
│
├── 章节草稿/                 # 已生成的章节正文
│   └── 第1章_序章.md
│
├── 伏笔与线索回收池.md       # 伏笔生命周期追踪（状态机）
│
└── 历史章节摘要/             # 每章 ~200 字摘要
    └── 第1章_摘要.md
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

## 三项护城河功能

### 1. 双向链接按需加载

正文或细纲中出现 `[[人物/林动]]` 时，脚本自动加载对应文件内容到 Prompt `<参考文件>` 区域。精准控制上下文窗口，避免无关信息污染。

### 2. 伏笔生命周期追踪

`伏笔与线索回收池.md` 自动追踪每条伏笔的状态转换：
- 新伏笔 → `🟡已埋`
- 后续章节引用 → `🟠发展中`
- 揭晓完成 → `🟢已回收`
- 超过预期回收章节 → 下次 Prompt 中加入回收提醒

### 3. 全局写作状态中枢

`全局写作状态.md` 是 AI 行为的单一真相来源。包含：
- Frontmatter 进度字段（自动更新）
- 全局系统提示词（注入每章 Prompt）
- 高压线禁用词（硬性过滤）
- 用户自定义指令区（`<!-- USER_AREA_START -->` 保护，脚本永不修改）

## 命令行参考

| 命令 | 说明 |
|------|------|
| `python scripts/main.py init --project ./项目` | 初始化新项目 |
| `python scripts/main.py assemble -c 5 -v 1` | 组装第1卷第5章的 XML Prompt |
| `python scripts/main.py continue -f ch5.txt -c 5 -v 1` | 执行续航闭环 |
| `python scripts/main.py status` | 查看写作进度 |

## 技术栈

- **语言**：Python 3.10+
- **依赖**：PyYAML、python-frontmatter
- **存储**：纯 Markdown 文件（YAML Frontmatter）
- **编码**：NFC/NFD 自动兼容，中文路径安全

## 设计原则

1. **Markdown-First**：所有数据以 `.md` 文件存储，人类和 AI 均可直接阅读编辑
2. **全中文路径**：目录名、文件名、Frontmatter 键名 100% 使用中文
3. **状态透明**：项目状态在任何编辑器中打开文件即可查看，无需特殊工具
4. **作者控制**：你随时可以手动编辑任何文件；脚本只修改结构化字段
5. **渐进增强**：不强行替代你现有工作流；从一个大纲文件开始即可
