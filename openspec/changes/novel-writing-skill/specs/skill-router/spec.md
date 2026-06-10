## ADDED Requirements

### Requirement: 路由入口自动分发

系统 SHALL 提供一个名为 `write-novel` 的顶层 skill，作为网文工具箱的唯一路由入口。当用户输入包含模糊写作意图时（如"写网文""帮我写书"），该 skill MUST 解析用户意图并分发到对应的子 skill。

#### Scenario: 用户输入模糊写作意图
- **WHEN** 用户输入"我想写小说"或"/write-novel"
- **THEN** 系统加载 `write-novel` skill，分析意图关键词，匹配路由表，调用对应子 skill

#### Scenario: 用户输入明确子命令
- **WHEN** 用户输入"/写长篇"或"续写"或"/去AI味"
- **THEN** 系统直接调用对应子 skill（`write-novel-long-write`、`write-novel-deslop` 等），跳过路由入口

#### Scenario: 无法匹配任何路由
- **WHEN** 用户输入无法匹配路由表中任何条目
- **THEN** 系统展示路由表选项，让用户选择意图

### Requirement: 路由表覆盖所有子技能

路由表 MUST 包含以下所有意图到 skill 的映射：

| 意图 | 路由目标 |
|------|---------|
| 写长篇（开书/大纲/日更/续写/修改/回炉） | `write-novel-long-write` |
| 长篇拆文/分析 | `write-novel-long-analyze` |
| 长篇扫榜/选题 | `write-novel-long-scan` |
| 去 AI 味 | `write-novel-deslop` |
| 多视角审查 | `write-novel-review` |
| 环境部署 | `write-novel-setup` |
| 封面生成 | `write-novel-cover` |

#### Scenario: 路由表完整性检查
- **WHEN** 任一子 skill 被添加或移除
- **THEN** 路由表 MUST 同步更新，确保所有可用 skill 都有对应的路由条目

### Requirement: 项目状态感知

路由 skill 在分发前 MUST 检查当前项目是否已初始化（是否存在包含 `人物/` 或 `世界设定/` 目录的项目结构）。

#### Scenario: 项目未初始化时请求写作
- **WHEN** 用户请求写作但项目无 `人物/` 或 `世界设定/` 目录
- **THEN** 系统先引导用户运行 `write-novel-setup` 初始化环境

#### Scenario: 项目已初始化时请求写作
- **WHEN** 用户请求写作且项目已有完整目录结构
- **THEN** 系统直接路由到对应写作 skill
