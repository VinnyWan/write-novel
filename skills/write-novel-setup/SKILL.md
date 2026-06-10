---
name: write-novel-setup
description: |
  网文写作工具集基础设施部署。将 hooks/rules/agents/CLAUDE.md 等基础设施部署到用户项目目录。
  触发方式：/write-novel-setup、「准备写书」「帮我搭一下环境」「配置写作项目」
---

# write-novel-setup：环境部署

你负责将写作工具集的基础设施部署到当前工作目录。

## 部署流程

### 阶段 1：检查已有文件

1. 扫描当前目录，检查是否已有 `人物/` 或 `世界设定/` 目录。
2. 如果已有部分文件，进入**增量模式**；否则进入**全新部署模式**。

### 阶段 2：创建目录树

在项目根目录下创建以下目录（不覆盖已有目录）：

```
项目根目录/
├── 人物/                    # 角色卡片
├── 世界设定/                # 世界观 & 力量体系
├── 全局设定/                # 跨卷全局设定（预留）
├── 分卷大纲/                # 分卷 & 单章细纲
├── 章节草稿/                # 已生成的章节正文
├── 历史章节摘要/            # 每章 ~200 字摘要
├── 对标/                    # 对标书数据（预留）
├── skills/                  # 写作 skill 定义
└── agents/                  # Agent 定义
```

### 阶段 3：写入模板文件

**全新部署**：写入以下模板文件（从 `references/` 目录获取内容）：

| 文件 | 模板来源 |
|------|---------|
| `全局写作状态.md` | 项目内置模板 |
| `伏笔与线索回收池.md` | 项目内置模板 |
| `人物卡片模板.md` | 项目内置模板 |
| `世界设定模板.md` | 项目内置模板 |
| `分卷大纲模板.md` | 项目内置模板 |
| `分卷与单章细纲模板.md` | 项目内置模板 |

**增量部署**：只补充不存在的文件。**绝不覆盖已有内容**。

### 阶段 4：部署 skills 和 agents

1. 检查 `.claude/settings.local.json` 是否存在，不存在则创建（用于 Claude Code 权限配置）。
2. 将 skill 定义写入项目 `skills/` 目录。
3. 将以下 Agent 定义写入项目 `agents/` 目录：

| Agent | 文件 | 功能 |
|-------|------|------|
| `write-novel-explorer` | `agents/write-novel-explorer.md` | 只读项目查询 |
| `write-novel-researcher` | `agents/write-novel-researcher.md` | 外部资料搜索 |
| `write-novel-deslop-agent` | `agents/write-novel-deslop-agent.md` | 深度去 AI 味 |
| `write-novel-senior-editor` | `agents/write-novel-senior-editor.md` | 资深编辑审稿 |
| `write-novel-picky-reader` | `agents/write-novel-picky-reader.md` | 挑剔读者体验 |

### 阶段 5：验证

部署完成后遍历所有预期目录和文件，生成部署报告。

## 部署报告格式

```
## 部署完成

### 创建的文件
- [NEW] 人物/
- [NEW] 世界设定/
- ...

### 跳过的文件（已存在）
- [SKIP] 全局写作状态.md

### 下一步
1. 编辑 `全局写作状态.md` → 填入主角信息和写作风格
2. 编辑 `世界设定/世界观.md` → 设计世界观和力量体系
3. 创建 `人物/` 下的角色卡片
4. 在 `分卷大纲/` 下创建分卷大纲和单章细纲
```

## 增量部署规则

1. **目录**：不存在的才创建。
2. **模板文件**：不存在的才写入，存在则跳过。
3. **`全局写作状态.md` 中的用户保护区**：`<!-- USER_AREA_START -->` 和 `<!-- USER_AREA_END -->` 之间的内容永不修改。
4. **`.claude/` 配置**：如 settings.local.json 已存在，合并而非覆盖。
5. **`skills/` 和 `agents/`**：如文件已存在，跳过不覆盖。
