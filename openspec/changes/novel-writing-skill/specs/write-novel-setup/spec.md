## ADDED Requirements

### Requirement: 一键部署写作项目

`write-novel-setup` skill SHALL 在当前工作目录下创建完整的写作项目结构，包括：目录树、模板文件、hooks、agents、CLAUDE.md 配置。

#### Scenario: 初始化新项目
- **WHEN** 用户输入"/准备写书"或"搭建环境"
- **THEN** 系统在当前目录创建：`人物/`、`世界设定/`、`分卷大纲/`、`章节草稿/`、`伏笔与线索回收池.md`、`历史章节摘要/`、`全局设定/` 目录，以及所有模板文件

#### Scenario: 已有项目增量部署
- **WHEN** 目标目录已存在部分文件
- **THEN** 系统只补充缺失的文件和目录，不覆盖已有内容

### Requirement: Claude Code 基础设施部署

部署流程 MUST 将 skill 定义、agent 定义写入项目根目录的 `skills/` 和 `agents/`，将 hooks 配置写入 `.claude/`。

#### Scenario: 部署 skills、agents 和 hooks
- **WHEN** write-novel-setup 执行基础设施部署
- **THEN** 系统将 skill 定义写入项目根 `skills/` 目录，Agent 定义写入项目根 `agents/` 目录，必要的 hooks 配置写入 `.claude/settings.local.json`

### Requirement: 部署后验证

部署完成后 MUST 返回验证报告，列出创建的文件、跳过的文件（已存在）、以及后续操作指引。

#### Scenario: 输出部署报告
- **WHEN** write-novel-setup 完成
- **THEN** 输出包含已创建文件列表、模板路径、下一步操作建议的 Markdown 摘要
